# Gemini実装計画: デバイス配置機能

**作成日**: 2025年8月2日
**担当**: Gemini AI Assistant
**目標**: ユーザー操作によるデバイスの配置・削除・状態変更機能の完成

---

### **概要**
ユーザーがデバイスパレットで選択したデバイスを、マウスの左クリックでグリッド上に配置し、右クリックで状態を変更できるようにする。この一連の操作が、内部データ（`GridSystem`）と画面描画の両方に正しく反映されることを目標とする。

---

### **Phase 1: 中核機能の実装 (データの更新)**

このフェーズでは、ユーザーの入力に応じて、まず内部データを正しく変更するロジックを構築します。

1.  **左クリックによるデバイス配置処理**
    *   **担当ファイル**: `main.py`
    *   **修正箇所**: `_handle_device_placement()` メソッド
    *   **作業内容**:
        *   `pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)` を検出する。
        *   `self.mouse_state` から、マウスがホバーしているグリッド座標 `(row, col)` を取得する。
        *   `self.device_palette.get_selected_device_type()` から、現在選択されているデバイスの種類を取得する。
        *   取得した情報を使って `self.grid_system.place_device(row, col, device_type, ...)` を呼び出し、`GridSystem` の `grid_data` を更新する。
        *   **アドレス**: `place_device` に渡すアドレスは、ひとまず `f"DEV_{row}_{col}"` のような仮の文字列で実装する（アドレス管理は後のフェーズ）。

2.  **左クリックによるデバイス削除処理**
    *   **担当ファイル**: `main.py`
    *   **修正箇所**: `_handle_device_placement()` メソッド
    *   **作業内容**:
        *   上記「配置処理」の続きとして、もし選択されているデバイスが `DeviceType.DEL` だった場合は、`place_device` の代わりに `self.grid_system.remove_device(row, col)` を呼び出すロジックを追加する。

3.  **右クリックによるデバイス状態のトグル**
    *   **担当ファイル**: `main.py`
    *   **修正箇所**: `_handle_device_placement()` メソッド
    *   **作業内容**:
        *   `pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT)` を検出する。
        *   `self.grid_system.get_device(row, col)` でクリックされた位置のデバイスオブジェクトを取得する。
        *   デバイスが存在すれば、そのデバイスの `state` 属性を `not device.state` のように反転させる。これはA接点/B接点のON/OFFテストに利用します。

---

### **Phase 2: 回路の再解析**

デバイスが変更された後に、回路の状態を即座に更新します。

1.  **通電解析の実行**
    *   **担当ファイル**: `main.py`
    *   **修正箇所**: `update()` メソッド
    *   **作業内容**:
        *   `_handle_device_placement()` が実行された**後**に、`self.circuit_analyzer.solve_ladder()` が呼び出されることを確認する。（現在の実装でおそらく問題ありませんが、念のため）
        *   これにより、デバイスを配置/削除した直後に通電状態が再計算され、描画に反映されるようになります。

---

### **Phase 3: 視覚的フィードバックの強化 (描画)**

ユーザーが何をしているか分かりやすくするための、描画に関する改善です。

1.  **配置済みデバイスの描画**
    *   **担当ファイル**: `core/grid_system.py`
    *   **修正箇所**: `_draw_devices()` メソッド
    *   **作業内容**:
        *   この部分は既に実装済みです。`grid_data` の内容（デバイスの種類と `is_energized` 状態）に基づいて、`SpriteManager` を使って正しいスプライトが描画されることを、Phase 1, 2 の実装と合わせて最終確認します。

2.  **プレビュー（ゴースト）スプライトの実装**
    *   **担当ファイル**: `main.py`
    *   **修正箇所**: `_draw_cursor_and_status()` メソッド
    *   **作業内容**:
        *   現在選択されているデバイスのスプライトを、マウスカーソル位置に半透明または少し暗い色で描画するロジックを追加します。
        *   `self.device_palette.get_selected_device_type()` で選択中のデバイスを取得します。
        *   `sprite_manager.get_sprite_coords(...)` でスプライト座標を取得します。
        *   `pyxel.blt` の透明色キー（`colkey`）を使い、マウスカーソル位置（`self.mouse_state.hovered_pos`）にゴーストとして描画します。
        *   このゴーストは、グリッドの編集可能エリアにスナップしている時のみ表示します。

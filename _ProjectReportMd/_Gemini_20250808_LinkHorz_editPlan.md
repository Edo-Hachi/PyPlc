### 調査結果

## ユーザーアプローチ
マウスのドラッグで一気に配置したいデバイスはLink_Horzだけなので、このデバイスが選択されている時のみ、マウスの入力状態をフックすればよいと考えています。

---

はい、この機能は**実現可能**です。

現在のアーキテクチャを調査したところ、以下の2つの主要なファイルを変更することで実装できます。

1.  **`main.py`**: アプリケーションのメインループがあり、マウスの入力状態（押した瞬間、ドラッグ中、離した瞬間）を最も検知しやすい場所です。ここでドラッグ操作の開始から終了までを管理します。
2.  **`core/grid_system.py`**: `place_device` メソッドを持っており、グリッドにデバイスを配置する責務を担っています。ドラッグ中にこのメソッドを連続して呼び出すことで、`LINK_HORZ` を配置します。

現在の実装は、マウスクリックの「押した瞬間」(`pyxel.btnp`) のみを使ってデバイスを単体で配置しています。これを拡張し、「押している間」(`pyxel.btn`) と「離した瞬間」(`pyxel.btnr`) の状態を利用することで、ドラッグ操作を実装します。

---

### 設計プラン

`LINK_HORZ` のドラッグ配置機能を、既存の単体配置機能と共存させる形で設計します。

#### 1. 状態管理の追加

まず、ドラッグ操作中であることを示すための状態変数を `main.py` の `App` クラスに追加します。

*   `self.is_dragging_link`: `bool`
    *   `LINK_HORZ` のドラッグが開始されたら `True` になるフラグ。
*   `self.drag_start_pos`: `tuple(int, int)` or `None`
    *   ドラッグを開始したグリッド座標 `(row, col)` を保持します。
*   `self.last_drag_pos`: `tuple(int, int)` or `None`
    *   最後に `LINK_HORZ` を配置したグリッド座標。同じセルに何度も配置しないようにするため。

#### 2. 入力処理ロジックの変更 (`main.py` 内)

`App` クラスの `_handle_device_placement` のような、マウス入力を処理しているメソッドを以下のように変更します。

**A. マウスボタンを押した時 (`pyxel.btnp`)**

1.  デバイスパレットで `LINK_HORZ` が選択されているかチェックします。
2.  **もし `LINK_HORZ` なら:**
    *   `self.is_dragging_link = True` に設定します。
    *   現在のマウスカーソル下のグリッド座標 `(row, col)` を取得し、`self.drag_start_pos` と `self.last_drag_pos` に保存します。
    *   `grid_system.place_device()` を呼び出し、開始点に最初の `LINK_HORZ` を配置します。
3.  **`LINK_HORZ` 以外なら:**
    *   これまで通りの単体配置ロジックを実行します。

**B. マウスドラッグ中 (`update` メソッド内、`pyxel.btn` で判定)**

1.  `self.is_dragging_link` が `True` かどうかをチェックします。
2.  もし `True` なら:
    *   現在のマウスカーソル下のグリッド座標 `(current_row, current_col)` を取得します。
    *   **重要**: `current_row` が `self.drag_start_pos` の `row` と同じであること、かつ、`(current_row, current_col)` が `self.last_drag_pos` と異なることを確認します（横方向のドラッグのみを許可するため）。
    *   条件を満たしていれば、`drag_start_pos` から `current_col` までの間のすべてのセルに `grid_system.place_device(row, col, DeviceType.LINK_HORZ)` を呼び出して `LINK_HORZ` を配置します。
        *   *補足: 始点から現在地までを毎回描画することで、ドラッグで行ったり来たりしても線が途切れないようにします。*
    *   `self.last_drag_pos` を現在の座標で更新します。

**C. マウスボタンを離した時 (`pyxel.btnr`)**

1.  `self.is_dragging_link` が `True` かどうかをチェックします。
2.  もし `True` なら:
    *   すべてのドラッグ関連の状態をリセットします (`is_dragging_link = False`, `drag_start_pos = None` など)。
    *   最後に `circuit_analyzer.solve_ladder()` を呼び出し、回路全体の通電状態を再計算させます。

#### 3. `core/grid_system.py` の変更

基本的には `place_device` をそのまま利用できるため、大きな変更は不要です。ただし、ドラッグによって連続で `place_device` が呼ばれた際のパフォーマンスや、既存の自動接続ロジックとの干渉を最小限にするため、`place_device` 内のロジックを微調整する必要があるかもしれません（例：`LINK_HORZ` が配置される場合は、周囲の自動更新をスキップするなど）。

---

### 実装に向けたTODOリスト

1.  **[main.py] `App` クラスに状態変数を追加**
    *   `self.is_dragging_link = False`
    *   `self.drag_start_pos = None`
    *   `self.last_drag_pos = None`

2.  **[main.py] マウス入力処理を修正**
    *   `_handle_device_placement` メソッド（または同等のメソッド）を特定し、リファクタリングします。
    *   `pyxel.btnp` (マウスボタンを押した時) のロジックを実装します。
        *   選択中デバイスが `LINK_HORZ` かどうかで処理を分岐させます。
        *   `LINK_HORZ` の場合は、ドラッグ開始のフラグと座標を設定し、最初の1つを配置します。

3.  **[main.py] ドラッグ中のロジックを `update` に追加**
    *   `if self.is_dragging_link:` のブロックを追加します。
    *   現在のマウス座標を取得し、始点と同じ行で、かつ最後に配置したセルと違う場合のみ処理を実行するロジックを実装します。
    *   始点から現在地までのセルをループで処理し、`grid_system.place_device()` を呼び出します。

4.  **[main.py] マウスボタンを離した時の処理を追加**
    *   `pyxel.btnr` を使って、ドラッグ状態をリセットし、回路を再解析するロジックを実装します。

5.  **[core/grid_system.py] `place_device` の確認と微調整（任意）**
    *   ドラッグによる連続呼び出しで問題が発生しないか確認します。まずは `main.py` の実装を完了させてから、必要に応じて調整します。

6.  **テスト**
    *   `LINK_HORZ` のドラッグ配置が正しく機能することを確認します。
    *   ドラッグで行ったり来たりした場合でも、線が正しく描画・削除されることを確認します。
    *   他のデバイス（接点やコイル）の単体配置が、これまで通り問題なく動作することを確認します（デグレード防止）。

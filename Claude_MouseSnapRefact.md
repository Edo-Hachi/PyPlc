# マウススナップモード実装計画書

## 概要
CTRLキーを押しっぱなしにしている間、マウスカーソルをグリッド交点にスナップさせる機能を実装する。

## 現在の動作
- マウスがグリッド範囲内にある時、最も近い交点に自動的にスナップ
- グリッド範囲外では表示されない

## 新しい動作仕様
- **通常モード**: マウスはフリーに移動、グリッド近くでもスナップしない
- **スナップモード（CTRL押下時）**: 指定しきい値内でグリッド交点にスナップ

## TODO リスト

### Phase 1: 基盤機能追加 ✅ 計画済み
1. **CTRLキー状態追跡フラグ追加**
   - `self.snap_mode: bool` フラグを初期化部分に追加
   
2. **スナップしきい値設定**
   - `SNAP_THRESHOLD = 5` (ピクセル) を DrawingConstants に追加

### Phase 2: 核心機能実装 ✅ 計画済み
3. **_update_mouse()メソッド修正**
   - CTRLキー状態チェック `pyxel.btn(pyxel.KEY_CTRL)`
   - `self.snap_mode` フラグ更新

4. **_screen_to_grid()メソッド大幅修正**
   - 通常モード: 厳密なグリッド範囲チェック
   - スナップモード: しきい値内での最近接交点検索

### Phase 3: 視覚的フィードバック ✅ 計画済み
5. **カーソル表示ロジック修正**
   - スナップモード時のみカーソル表示
   - 通常モードでは非表示

6. **ステータスバー表示拡張**
   - 現在のモード表示（Normal/Snap）
   - スナップ距離表示

## 詳細な変更案

### 1. 初期化部分への追加
```python
# Initialize mouse state / マウス状態初期化
self.mouse_grid_pos = None  # マウスのグリッド座標
self.show_cursor = False    # カーソル表示フラグ
self.snap_mode = False      # スナップモード（CTRL押下時）
```

### 2. DrawingConstants クラス拡張
```python
class DrawingConstants:
    """描画関連の定数定義"""
    DEVICE_SIZE = 8           # デバイス矩形サイズ
    DEVICE_HALF_SIZE = 4      # デバイス中央配置用オフセット
    SYMBOL_OFFSET = 2         # シンボル描画オフセット
    NAME_OFFSET_Y = 10        # 名前表示Y方向オフセット
    NAME_OFFSET_X = -4        # 名前表示X方向オフセット
    SNAP_THRESHOLD = 5        # スナップしきい値（ピクセル）
```

### 3. _update_mouse()メソッド修正
```python
def _update_mouse(self) -> None:
    """Update mouse state / マウス状態更新"""
    # CTRLキー状態チェック
    self.snap_mode = pyxel.btn(pyxel.KEY_CTRL)
    
    mouse_x = pyxel.mouse_x
    mouse_y = pyxel.mouse_y
    
    # Convert screen coordinates to grid coordinates / スクリーン座標をグリッド座標に変換
    grid_pos = self._screen_to_grid(mouse_x, mouse_y)
    
    if grid_pos and self._is_editable_position(grid_pos[0], grid_pos[1]):
        self.mouse_grid_pos = grid_pos
        self.show_cursor = self.snap_mode  # スナップモード時のみ表示
    else:
        self.mouse_grid_pos = None
        self.show_cursor = False
```

### 4. _screen_to_grid()メソッド完全書き換え
```python
def _screen_to_grid(self, screen_x: int, screen_y: int) -> tuple[int, int] | None:
    """Convert screen coordinates to grid coordinates / スクリーン座標をグリッド座標に変換"""
    grid_x = self.config.grid_origin_x
    grid_y = self.config.grid_origin_y
    cell_size = self.config.grid_cell_size
    
    if not self.snap_mode:
        # 通常モード: グリッド範囲外では何も返さない
        return None
    
    # スナップモード: 最も近い交点を検索
    closest_row = -1
    closest_col = -1
    min_distance = float('inf')
    
    for row in range(self.config.grid_rows):
        for col in range(self.config.grid_cols):
            # 交点座標計算
            intersection_x = grid_x + col * cell_size
            intersection_y = grid_y + row * cell_size
            
            # マウスとの距離計算
            distance = ((screen_x - intersection_x) ** 2 + (screen_y - intersection_y) ** 2) ** 0.5
            
            if distance < DrawingConstants.SNAP_THRESHOLD and distance < min_distance:
                min_distance = distance
                closest_row = row
                closest_col = col
    
    # 有効な交点が見つかった場合
    if closest_row >= 0 and closest_col >= 0:
        return (closest_row, closest_col)  # grid[row][col] # [y座標][x座標] の順序
    
    return None
```

### 5. ステータスバー表示拡張
```python
def _draw_status_bar(self) -> None:
    """Draw status bar with mouse position / マウス位置情報を含むステータスバー描画"""
    # ステータスバーの位置（画面下部）
    status_y = self.config.window_height - 20
    
    # 背景を黒でクリア
    pyxel.rect(0, status_y, self.config.window_width, 20, pyxel.COLOR_BLACK)
    
    # スナップモード表示
    mode_text = "SNAP MODE" if self.snap_mode else "FREE MODE"
    mode_color = pyxel.COLOR_YELLOW if self.snap_mode else pyxel.COLOR_WHITE
    pyxel.text(200, status_y + 2, mode_text, mode_color)
    
    # マウス位置情報表示
    if self.mouse_grid_pos:
        row, col = self.mouse_grid_pos
        position_text = f"Grid Position: Row={row}, Col={col} [grid[{row}][{col}]]"
        pyxel.text(10, status_y + 5, position_text, pyxel.COLOR_WHITE)
        
        # 編集可能かどうか表示
        if self._is_editable_position(row, col):
            pyxel.text(10, status_y + 12, "Editable: YES", pyxel.COLOR_GREEN)
        else:
            pyxel.text(10, status_y + 12, "Editable: NO (Bus area)", pyxel.COLOR_RED)
    else:
        # グリッド外またはスナップ範囲外の場合
        mouse_x, mouse_y = pyxel.mouse_x, pyxel.mouse_y
        if self.snap_mode:
            pyxel.text(10, status_y + 5, f"Mouse: ({mouse_x}, {mouse_y}) - No snap target", pyxel.COLOR_GRAY)
            pyxel.text(10, status_y + 12, "Editable: NO (Outside snap range)", pyxel.COLOR_RED)
        else:
            pyxel.text(10, status_y + 5, f"Mouse: ({mouse_x}, {mouse_y}) - Free movement", pyxel.COLOR_GRAY)
            pyxel.text(10, status_y + 12, "Hold CTRL to enable snap mode", pyxel.COLOR_CYAN)
```

### 6. 操作説明の更新
```python
def _draw_controls(self) -> None:
    """Draw control information / 操作情報描画"""
    control_y = self.config.control_info_y
    pyxel.text(10, control_y, "Hold CTRL: Snap to grid, Mouse: Free movement, Q-Quit", pyxel.COLOR_WHITE)
```

## 実装の利点
1. **直感的な操作**: CTRLキーでスナップモードの切り替え
2. **精密な配置**: 必要な時だけグリッドにスナップ
3. **自由な移動**: 通常時はフリーなマウス移動
4. **視覚的フィードバック**: モード状態の明確な表示
5. **設定可能**: スナップしきい値の調整が容易

## テスト項目
- [ ] CTRLキー押下でスナップモード切り替え
- [ ] スナップモード時の交点吸着動作
- [ ] 通常モード時のフリー移動
- [ ] しきい値設定の動作確認
- [ ] ステータスバー表示の正確性
- [ ] 編集可能領域の制限動作

## リスク要因
- **パフォーマンス**: 全交点との距離計算によるCPU負荷
- **操作性**: スナップしきい値の調整が必要な可能性
- **視覚性**: カーソル表示タイミングの調整

## 実装順序
1. Phase 1: 基盤機能（フラグ、定数）
2. Phase 2: 核心機能（マウス処理、座標変換）
3. Phase 3: 視覚的フィードバック（表示、ステータス）
4. テスト・調整・バグ修正

---
*作成日: 2025-01-28*
*対象ファイル: main.py*
*推定作業時間: 30-45分*
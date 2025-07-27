"""
PyPlc UI Components Module

UIの描画処理とマウス入力処理を管理するモジュール。
- UIRenderer: UI描画システム
- MouseHandler: マウス入力処理システム
"""

import pyxel
from typing import Dict, Optional, Tuple
from config import Layout, Colors, DeviceType, SimulatorMode, PLCRunState
from plc_logic import ContactA, ContactB, Coil, Timer, Counter


class UIRenderer:
    """UI描画システム"""
    
    def __init__(self, sprites: Dict, device_palette: list):
        self.sprites = sprites
        self.device_palette = device_palette
        self.status_message = ""  # ステータスバーメッセージ
    
#    def draw_title(self):
#        """タイトル描画"""
#        #pyxel.text(Layout.TITLE_X, Layout.TITLE_Y, "PLC Ladder Simulator", Colors.TEXT)
    
    def draw_device_palette(self, selected_device_type, mouse_handler=None, palette_row=0, selected_device_index=0):
        """デバイスパレット描画（3段システム対応）"""
        # 12個のデバイスを5個ずつ3段に分けて表示
        devices_per_row = 5
        
        for row in range(3):  # 上段(0)、中段(1)、下段(2)
            if row == 0:
                y_pos = Layout.PALETTE_Y
            elif row == 1:
                y_pos = Layout.PALETTE_Y_MIDDLE
            else:
                y_pos = Layout.PALETTE_Y_LOWER
            
            # アクティブな段に白い枠を描画（段ごとに1回だけ）
            if row == palette_row:
                row_start_x = Layout.PALETTE_START_X - 2
                row_width = devices_per_row * Layout.PALETTE_DEVICE_WIDTH + 4
                pyxel.rectb(row_start_x, y_pos - 2, row_width, 12, Colors.TEXT)
            
            for col in range(devices_per_row):
                device_index = row * devices_per_row + col
                if device_index >= len(self.device_palette):
                    break
                
                device = self.device_palette[device_index]
                x_pos = Layout.PALETTE_START_X + col * Layout.PALETTE_DEVICE_WIDTH
                
                # マウスオーバー時の視覚的フィードバック
                mouse_x, mouse_y = pyxel.mouse_x, pyxel.mouse_y
                is_mouse_over = (x_pos <= mouse_x <= x_pos + 8 and 
                               y_pos <= mouse_y <= y_pos + 8)
                
                # マウスオーバー時にステータスメッセージを更新
                if is_mouse_over:
                    key_num = col + 1 if col < 9 else 0  # 0は10番目
                    self.status_message = f"{device['name']} (Key: {key_num})"
                
                # 現在選択中の段と位置かどうかをチェック
                is_selected_row = (row == palette_row)
                is_selected_device = (device_index == selected_device_index and device["type"] == selected_device_type)
                
                # 選択中のデバイスは明確に表示
                if is_selected_device:
                    # 選択中は白い枠線のみ（8x8サイズ）
                    pyxel.rectb(x_pos - 1, y_pos - 1, 10, 10, Colors.TEXT)
                elif is_mouse_over:
                    # マウスオーバー時は薄い背景 + 白い枠線（8x8サイズ）
                    pyxel.rect(x_pos - 1, y_pos - 1, 10, 10, pyxel.COLOR_NAVY)
                    pyxel.rectb(x_pos - 1, y_pos - 1, 10, 10, Colors.TEXT)
                
                # デバイススプライト表示
                if device["sprite"]:
                    sprite = self.sprites[device["sprite"]]
                    pyxel.blt(x_pos, y_pos, 0, sprite.x, sprite.y, 8, 8, 0)
                
                # デバイス番号表示（1-5の形式、0は5番目として表示）
                key_num = col + 1 if col < 4 else 0  # 0は5番目
                pyxel.text(x_pos + 8, y_pos + Layout.PALETTE_NUMBER_OFFSET_Y, str(key_num), Colors.TEXT)
    
    def draw_device_grid(self, grid_manager, electrical_system, mouse_handler):
        """デバイスグリッド描画"""
        # グリッド線描画
        for row in range(Layout.GRID_ROWS + 1):
            y = Layout.GRID_START_Y + row * Layout.GRID_SIZE
            pyxel.line(Layout.GRID_START_X, y, Layout.GRID_START_X + Layout.GRID_COLS * Layout.GRID_SIZE, y, Colors.GRID_LINE)
        
        for col in range(Layout.GRID_COLS + 1):
            x = Layout.GRID_START_X + col * Layout.GRID_SIZE
            if col == 0:
                # 左端の縦線（HOTバス）はオレンジの太線で表示
                pyxel.rect(x - 1, Layout.GRID_START_Y, 3, Layout.GRID_ROWS * Layout.GRID_SIZE + 1, Colors.BUSBAR)
            elif col == Layout.GRID_COLS:
                # 右端の縦線（COLDバス）は水色の太線で表示
                pyxel.rect(x - 1, Layout.GRID_START_Y, 3, Layout.GRID_ROWS * Layout.GRID_SIZE + 1, pyxel.COLOR_CYAN)
            else:
                # その他の縦線は通常のグリッド線
                pyxel.line(x, Layout.GRID_START_Y, x, Layout.GRID_START_Y + Layout.GRID_ROWS * Layout.GRID_SIZE, Colors.GRID_LINE)
        
        # HOT/COLDラベル描画
        hot_x = Layout.GRID_START_X
        cold_x = Layout.GRID_START_X + Layout.GRID_COLS * Layout.GRID_SIZE
        label_y = Layout.GRID_START_Y - 12
        pyxel.text(hot_x - 8, label_y, "HOT", Colors.BUSBAR)
        pyxel.text(cold_x - 12, label_y, "COLD", pyxel.COLOR_CYAN)
        
        # 配置済みデバイス描画
        self._draw_grid_devices(grid_manager)
        
        # 電気的配線描画
        self._draw_electrical_wiring(electrical_system)
        self._draw_vertical_wiring(electrical_system)
        
        # マウスプレビュー描画
        self._draw_device_placement_preview(mouse_handler)
    
    def _draw_grid_devices(self, grid_manager):
        """グリッド上のデバイス描画"""
        for row in grid_manager.grid:
            for device in row:
                if device.device_type != DeviceType.EMPTY:
                    # グリッド座標をピクセル座標に変換（元のコードと同じ計算）
                    px = Layout.GRID_START_X + device.grid_x * Layout.GRID_SIZE
                    py = Layout.GRID_START_Y + device.grid_y * Layout.GRID_SIZE
                    
                    # スプライト描画
                    sprite_name = device.get_sprite_name()
                    if sprite_name and sprite_name in self.sprites:
                        sprite = self.sprites[sprite_name]
                        pyxel.blt(px - 4, py - 4, 0, sprite.x, sprite.y, 8, 8, 0)
                    elif device.device_type == DeviceType.LINK_UP:
                        sprite = self.sprites["LINK_UP"]  # LINK_UP（↑）スプライト - 下のラインに配置
                        pyxel.blt(px - 4, py - 4, 0, sprite.x, sprite.y, 8, 8, 0)
                    elif device.device_type == DeviceType.LINK_DOWN:
                        sprite = self.sprites["LINK_DOWN"]  # LINK_DOWN（↓）スプライト - 上のラインに配置
                        pyxel.blt(px - 4, py - 4, 0, sprite.x, sprite.y, 8, 8, 0)
                    
                    # デバイスアドレス表示
                    if device.device_address:
                        pyxel.text(px - 8, py + 6, device.device_address, Colors.TEXT)
    
    def _draw_electrical_wiring(self, electrical_system):
        """横方向電気配線描画（手動ワイヤーのみ）"""
        # 自動セグメント描画を無効化
        # 代わりに明示的に配置されたワイヤーデバイスのみを描画
        pass  # 自動線描画は無効化
    
    def _draw_vertical_wiring(self, electrical_system):
        """縦方向電気配線描画"""
        segments = electrical_system.get_vertical_wire_segments()
        
        for grid_x, up_y, down_y, is_energized in segments:
            color = Colors.WIRE_ON if is_energized else Colors.WIRE_OFF
            
            # 配線の描画位置計算（元のコードと同じ）
            x = Layout.GRID_START_X + grid_x * Layout.GRID_SIZE
            start_py = Layout.GRID_START_Y + up_y * Layout.GRID_SIZE
            end_py = Layout.GRID_START_Y + down_y * Layout.GRID_SIZE
            
            # 縦方向バスライン描画（太線で視認性向上）
            line_width = 2  # 2ピクセル幅の太線
            for i in range(line_width):
                pyxel.line(x - line_width//2 + i, start_py, x - line_width//2 + i, end_py, color)
    
    def _draw_device_placement_preview(self, mouse_handler):
        """デバイス配置プレビュー描画"""
        if not mouse_handler.show_preview:
            return
            
        grid_x, grid_y = mouse_handler.preview_grid_pos
        if grid_x < 0 or grid_x >= Layout.GRID_COLS or grid_y < 0 or grid_y >= Layout.GRID_ROWS:
            return
        
        px = Layout.GRID_START_X + grid_x * Layout.GRID_SIZE
        py = Layout.GRID_START_Y + grid_y * Layout.GRID_SIZE
        
        # プレビュー色決定
        preview_color = mouse_handler.preview_color
        
        # プレビュー表示
        pyxel.circb(px, py, 6, preview_color)
        
        # 配置予定デバイス名表示
        device_name = mouse_handler.selected_device_name
        if device_name:
            pyxel.text(px - len(device_name) * 2, py - 12, device_name, preview_color)
    
    def draw_sprite_test(self):
        """スプライトテスト描画"""
        x, y = Layout.SPRITE_TEST_X, Layout.SPRITE_TEST_Y
        pyxel.text(x, y - 8, "Sprite Test:", Colors.TEXT)
        
        # A接点テスト
        sprite_a_on = self.sprites.get("TYPE_A_ON")
        sprite_a_off = self.sprites.get("TYPE_A_OFF")
        if sprite_a_on and sprite_a_off:
            pyxel.blt(x, y, 0, sprite_a_on.x, sprite_a_on.y, 8, 8, 0)
            pyxel.blt(x + 16, y, 0, sprite_a_off.x, sprite_a_off.y, 8, 8, 0)
            pyxel.text(x, y + 10, "A_ON", Colors.TEXT)
            pyxel.text(x + 16, y + 10, "A_OFF", Colors.TEXT)
    
    def draw_traditional_ladder(self, ladder_program):
        """従来ラダー図描画"""
        y_pos = 50
        for line in ladder_program.lines:
            x_pos = 10
            
            # 左バスバー
            pyxel.line(x_pos, y_pos, x_pos, y_pos + 8, Colors.TEXT)
            x_pos += 5
            
            for element in line.elements:
                # 素子の描画
                if isinstance(element, ContactA):
                    color = 11 if element.last_result else 1
                    pyxel.rect(x_pos, y_pos, 8, 8, color)
                    pyxel.text(x_pos + 1, y_pos + 2, "A", Colors.BLACK)
                    pyxel.text(x_pos, y_pos - 8, element.device_address, Colors.TEXT)
                    
                elif isinstance(element, ContactB):
                    color = 11 if element.last_result else 1
                    pyxel.rect(x_pos, y_pos, 8, 8, color)
                    pyxel.text(x_pos + 1, y_pos + 2, "B", Colors.BLACK)
                    pyxel.text(x_pos, y_pos - 8, element.device_address, Colors.TEXT)
                    
                elif isinstance(element, Coil):
                    color = 11 if element.last_result else 1
                    pyxel.circ(x_pos + 4, y_pos + 4, 3, color)
                    pyxel.text(x_pos, y_pos - 8, element.device_address, Colors.TEXT)
                    
                elif isinstance(element, Timer):
                    color = 11 if element.last_result else 1
                    pyxel.rect(x_pos, y_pos, 10, 8, color)
                    pyxel.text(x_pos + 1, y_pos + 2, "T", Colors.BLACK)
                    pyxel.text(x_pos, y_pos - 8, element.device_address, Colors.TEXT)
                    
                elif isinstance(element, Counter):
                    color = 11 if element.last_result else 1
                    pyxel.rect(x_pos, y_pos, 10, 8, color)
                    pyxel.text(x_pos + 1, y_pos + 2, "C", Colors.BLACK)
                    pyxel.text(x_pos, y_pos - 8, element.device_address, Colors.TEXT)
                
                # 接続線
                if x_pos > 15:  # 最初の素子でない場合
                    line_color = 11 if element.last_result else 1
                    pyxel.line(x_pos - 5, y_pos + 4, x_pos, y_pos + 4, line_color)
                
                x_pos += 15
                
            y_pos += 20
    
    def draw_status_bar(self, current_mode: SimulatorMode = SimulatorMode.EDIT, plc_run_state: PLCRunState = PLCRunState.STOPPED):
        """ステータスバー描画（画面下部）"""
        # ステータスバー背景
        pyxel.rect(Layout.STATUS_BAR_X, Layout.STATUS_BAR_Y, Layout.STATUS_BAR_WIDTH, Layout.STATUS_BAR_HEIGHT, Colors.STATUS_BAR_BG)
        
        # ステータスメッセージ表示（左側）
        if self.status_message:
            pyxel.text(Layout.STATUS_BAR_X + 2, Layout.STATUS_BAR_Y + 1, self.status_message, Colors.TEXT)
        
        # PLC実行状態表示（中央）
        if current_mode == SimulatorMode.RUN:
            plc_text = f"PLC: {plc_run_state.value}"
            plc_color = Colors.PLC_RUNNING if plc_run_state == PLCRunState.RUNNING else Colors.PLC_STOPPED
            pyxel.text(Layout.STATUS_BAR_X + 100, Layout.STATUS_BAR_Y + 1, plc_text, plc_color)
            
            # F5キーヒント表示
            if plc_run_state == PLCRunState.STOPPED:
                pyxel.text(Layout.STATUS_BAR_X + 150, Layout.STATUS_BAR_Y + 1, "F5:Start", Colors.TEXT)
            else:
                pyxel.text(Layout.STATUS_BAR_X + 150, Layout.STATUS_BAR_Y + 1, "F5:Stop", Colors.TEXT)
        
        # モード表示（右端）
        mode_text = current_mode.value
        mode_color = Colors.MODE_EDIT if current_mode == SimulatorMode.EDIT else Colors.MODE_RUN
        pyxel.text(Layout.MODE_DISPLAY_X, Layout.STATUS_BAR_Y + 1, mode_text, mode_color)
    
    def clear_status_message(self):
        """ステータスメッセージをクリア"""
        self.status_message = ""


class MouseHandler:
    """マウス入力処理システム"""
    
    def __init__(self, device_palette: list, selected_device_type):
        self.device_palette = device_palette
        self.selected_device_type = selected_device_type
        self.show_preview = False
        self.preview_grid_pos = (0, 0)
        self.preview_color = Colors.TEXT
        self.selected_device_name = ""
    
    def get_grid_position_from_mouse(self) -> Optional[Tuple[int, int]]:
        """マウス座標をグリッド座標に変換"""
        mouse_x = pyxel.mouse_x
        mouse_y = pyxel.mouse_y
        
        # グリッド範囲内かチェック
        if (Layout.GRID_START_X <= mouse_x <= Layout.GRID_START_X + Layout.GRID_COLS * Layout.GRID_SIZE and
            Layout.GRID_START_Y <= mouse_y <= Layout.GRID_START_Y + Layout.GRID_ROWS * Layout.GRID_SIZE):
            
            # 最も近いグリッド交点を計算（元のコードに合わせてround使用）
            grid_x = round((mouse_x - Layout.GRID_START_X) / Layout.GRID_SIZE)
            grid_y = round((mouse_y - Layout.GRID_START_Y) / Layout.GRID_SIZE)
            
            # 範囲チェック + HOT/COLDバス領域除外
            if (1 <= grid_x < Layout.GRID_COLS and 0 <= grid_y < Layout.GRID_ROWS):  # デバイス配置可能領域は列1-9
                return (grid_x, grid_y)
        
        return None
    
    def handle_mouse_input(self, grid_manager, device_manager):
        """マウス入力処理"""
        # マウスプレビュー更新
        self._update_preview(grid_manager)
        
        # 左クリック処理
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mouse_x, mouse_y = pyxel.mouse_x, pyxel.mouse_y
            
            # デバイスパレット選択判定（2段対応）
            selected_device_index = None
            
            # 上段チェック
            if Layout.PALETTE_Y <= mouse_y <= Layout.PALETTE_Y + 8:
                for col in range(5):  # 上段は0-4列
                    x_pos = Layout.PALETTE_START_X + col * Layout.PALETTE_DEVICE_WIDTH
                    if x_pos <= mouse_x <= x_pos + 8:
                        selected_device_index = col  # 上段: 0-4
                        break
            
            # 中段チェック
            elif Layout.PALETTE_Y_MIDDLE <= mouse_y <= Layout.PALETTE_Y_MIDDLE + 8:
                for col in range(5):  # 中段は5-9列
                    x_pos = Layout.PALETTE_START_X + col * Layout.PALETTE_DEVICE_WIDTH
                    if x_pos <= mouse_x <= x_pos + 8:
                        selected_device_index = 5 + col  # 中段: 5-9
                        break
            
            # 下段チェック
            elif Layout.PALETTE_Y_LOWER <= mouse_y <= Layout.PALETTE_Y_LOWER + 8:
                for col in range(5):  # 下段は10-14列
                    x_pos = Layout.PALETTE_START_X + col * Layout.PALETTE_DEVICE_WIDTH
                    if x_pos <= mouse_x <= x_pos + 8:
                        selected_device_index = 10 + col  # 下段: 10-14
                        break
            
            # デバイス選択が確定した場合
            if selected_device_index is not None and selected_device_index < len(self.device_palette):
                device = self.device_palette[selected_device_index]
                self.selected_device_type = device["type"]
                return (device["type"], selected_device_index)  # デバイスタイプとインデックスを返す
            else:
                # グリッド上でのデバイス配置処理
                self._handle_grid_placement(grid_manager, device_manager)
        
        # 右クリック処理（グリッド上のデバイス設定）
        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            grid_pos = self.get_grid_position_from_mouse()
            if grid_pos:
                grid_x, grid_y = grid_pos
                device = grid_manager.get_device(grid_x, grid_y)
                if device and device.device_type != DeviceType.EMPTY:
                    return ("DEVICE_CONFIG", device)  # デバイス設定要求を返す
        
        return None  # 何も選択されなかった場合
    
    def handle_run_mode_input(self, grid_manager, device_manager):
        """RUNモード用マウス入力処理"""
        # 右クリック処理（グリッド上のデバイス操作）
        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            grid_pos = self.get_grid_position_from_mouse()
            if grid_pos:
                grid_x, grid_y = grid_pos
                device = grid_manager.get_device(grid_x, grid_y)
                if device and device.device_type != DeviceType.EMPTY:
                    return ("DEVICE_OPERATION", device)  # デバイス操作要求を返す
        
        return None  # 何も操作されなかった場合
    
    def _update_preview(self, grid_manager):
        """マウスプレビュー更新"""
        grid_pos = self.get_grid_position_from_mouse()
        if grid_pos:
            self.show_preview = True
            self.preview_grid_pos = grid_pos
            grid_x, grid_y = grid_pos
            
            # 配置可能性のチェック（バスバー領域は既にget_grid_position_from_mouseで除外済み）
            # 既存デバイスがある場合は赤色、ない場合は黄色
            existing_device = grid_manager.get_device(grid_x, grid_y)
            if existing_device and existing_device.device_type != DeviceType.EMPTY:
                self.preview_color = 8  # 赤色（上書き警告）
            else:
                self.preview_color = 10  # 黄色（配置可能）
            
            # 選択中デバイス名
            for device in self.device_palette:
                if device["type"] == self.selected_device_type:
                    self.selected_device_name = device["name"]
                    break
        else:
            self.show_preview = False
    
    def _handle_grid_placement(self, grid_manager, device_manager):
        """グリッド配置処理"""
        # 有効なデバイスが選択されているかチェック
        if self.selected_device_type == DeviceType.EMPTY:
            return
        
        # マウス位置からグリッド座標を取得
        grid_pos = self.get_grid_position_from_mouse()
        if not grid_pos:
            return
            
        grid_x, grid_y = grid_pos
        
        # DELデバイスの場合は削除処理
        if self.selected_device_type == DeviceType.DEL:
            grid_manager.remove_device(grid_x, grid_y)
            return
        
        # デバイス配置処理
        device_address = self._generate_device_address(self.selected_device_type, grid_x, grid_y)
        grid_manager.place_device(grid_x, grid_y, self.selected_device_type, device_address)
    
    def _generate_device_address(self, device_type: DeviceType, grid_x: int, grid_y: int) -> Optional[str]:
        """デバイスアドレス生成"""
        if device_type == DeviceType.TYPE_A or device_type == DeviceType.TYPE_B:
            return f"X{grid_x:03d}"
        elif device_type == DeviceType.COIL:
            return f"Y{grid_x:03d}"
        elif device_type == DeviceType.TIMER:
            return f"T{grid_y:03d}"
        elif device_type == DeviceType.COUNTER:
            return f"C{grid_y:03d}"
        return None
    
    def handle_device_selection(self, key_pressed: int):
        """デバイス選択処理"""
        if 1 <= key_pressed <= len(self.device_palette):
            self.selected_device_type = self.device_palette[key_pressed - 1]["type"]
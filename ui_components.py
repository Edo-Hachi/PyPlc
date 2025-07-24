"""
PyPlc UI Components Module

UIの描画処理とマウス入力処理を管理するモジュール。
- UIRenderer: UI描画システム
- MouseHandler: マウス入力処理システム
"""

import pyxel
from typing import Dict, Optional, Tuple
from config import Layout, Colors, DeviceType
from plc_logic import ContactA, ContactB, Coil, Timer, Counter


class UIRenderer:
    """UI描画システム"""
    
    def __init__(self, sprites: Dict, device_palette: list):
        self.sprites = sprites
        self.device_palette = device_palette
    
    def draw_title(self):
        """タイトル描画"""
        pyxel.text(Layout.TITLE_X, Layout.TITLE_Y, "PLC Ladder Simulator", Colors.TEXT)
    
    def draw_device_palette(self, selected_device_type, mouse_handler=None):
        """デバイスパレット描画（Y=16ライン）"""
        pyxel.text(Layout.PALETTE_START_X, Layout.PALETTE_Y - 8, "Device Palette:", Colors.TEXT)
        
        for i, device in enumerate(self.device_palette):
            x_pos = Layout.PALETTE_START_X + i * Layout.PALETTE_DEVICE_WIDTH
            
            # マウスオーバー時の視覚的フィードバック
            mouse_x, mouse_y = pyxel.mouse_x, pyxel.mouse_y
            is_mouse_over = (x_pos - 2 <= mouse_x <= x_pos + 18 and 
                           Layout.PALETTE_Y - 2 <= mouse_y <= Layout.PALETTE_Y + 10)
            
            # 選択中のデバイスは明確に表示
            if device["type"] == selected_device_type:
                # 選択中は黄色の背景 + 白い枠線
                pyxel.rect(x_pos - 2, Layout.PALETTE_Y - 2, 20, 12, Colors.SELECTED_BG)
                pyxel.rectb(x_pos - 2, Layout.PALETTE_Y - 2, 20, 12, Colors.TEXT)
            elif is_mouse_over:
                # マウスオーバー時は薄い背景 + 白い枠線
                pyxel.rect(x_pos - 2, Layout.PALETTE_Y - 2, 20, 12, 5)  # ダークグレー背景
                pyxel.rectb(x_pos - 2, Layout.PALETTE_Y - 2, 20, 12, Colors.TEXT)
            
            # デバイススプライト表示
            if device["sprite"]:
                sprite = self.sprites[device["sprite"]]
                pyxel.blt(x_pos, Layout.PALETTE_Y, 0, sprite.x, sprite.y, 8, 8, 0)
            else:
                # スプライトがない場合は記号で表示
                if device["type"] == DeviceType.BUSBAR:
                    pyxel.rect(x_pos + 2, Layout.PALETTE_Y - 2, 4, 12, Colors.BUSBAR)
            
            # デバイス番号表示
            pyxel.text(x_pos + 8, Layout.PALETTE_Y + Layout.PALETTE_NUMBER_OFFSET_Y, str(i + 1), Colors.TEXT)
    
    def draw_device_grid(self, grid_manager, electrical_system, mouse_handler):
        """デバイスグリッド描画"""
        # グリッド線描画
        for row in range(Layout.GRID_ROWS + 1):
            y = Layout.GRID_START_Y + row * Layout.GRID_SIZE
            pyxel.line(Layout.GRID_START_X, y, Layout.GRID_START_X + Layout.GRID_COLS * Layout.GRID_SIZE, y, Colors.GRID_LINE)
        
        for col in range(Layout.GRID_COLS + 1):
            x = Layout.GRID_START_X + col * Layout.GRID_SIZE
            pyxel.line(x, Layout.GRID_START_Y, x, Layout.GRID_START_Y + Layout.GRID_ROWS * Layout.GRID_SIZE, Colors.GRID_LINE)
        
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
                    elif device.device_type == DeviceType.BUSBAR:
                        # バスバーは白い縦線で表示
                        pyxel.line(px, py - 6, px, py + 6, Colors.BUSBAR)
                    elif device.device_type == DeviceType.LINK_UP:
                        sprite = self.sprites["LINK_UP"]
                        pyxel.blt(px - 4, py - 4, 0, sprite.x, sprite.y, 8, 8, 0)
                    elif device.device_type == DeviceType.LINK_DOWN:
                        sprite = self.sprites["LINK_DOWN"]
                        pyxel.blt(px - 4, py - 4, 0, sprite.x, sprite.y, 8, 8, 0)
                    
                    # デバイスアドレス表示
                    if device.device_address:
                        pyxel.text(px - 8, py + 6, device.device_address, Colors.TEXT)
    
    def _draw_electrical_wiring(self, electrical_system):
        """横方向電気配線描画"""
        for rung in electrical_system.rungs.values():
            segments = rung.get_power_segments()
            
            for start_x, end_x, is_energized in segments:
                color = Colors.WIRE_ON if is_energized else Colors.WIRE_OFF
                
                # 配線の描画位置計算（元のコードと同じ）
                y = Layout.GRID_START_Y + rung.grid_y * Layout.GRID_SIZE
                start_px = Layout.GRID_START_X + start_x * Layout.GRID_SIZE
                end_px = Layout.GRID_START_X + end_x * Layout.GRID_SIZE
                
                # 横線描画
                if start_px < end_px:
                    pyxel.line(start_px, y, end_px, y, color)
    
    def _draw_vertical_wiring(self, electrical_system):
        """縦方向電気配線描画"""
        segments = electrical_system.get_vertical_wire_segments()
        
        for grid_x, up_y, down_y, is_energized in segments:
            color = Colors.WIRE_ON if is_energized else Colors.WIRE_OFF
            
            # 配線の描画位置計算（元のコードと同じ）
            x = Layout.GRID_START_X + grid_x * Layout.GRID_SIZE
            start_py = Layout.GRID_START_Y + up_y * Layout.GRID_SIZE
            end_py = Layout.GRID_START_Y + down_y * Layout.GRID_SIZE
            
            # 縦線描画
            pyxel.line(x, start_py, x, end_py, color)
    
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
            pyxel.line(x_pos, y_pos, x_pos, y_pos + 8, 7)
            x_pos += 5
            
            for element in line.elements:
                # 素子の描画
                if isinstance(element, ContactA):
                    color = 11 if element.last_result else 1
                    pyxel.rect(x_pos, y_pos, 8, 8, color)
                    pyxel.text(x_pos + 1, y_pos + 2, "A", 0)
                    pyxel.text(x_pos, y_pos - 8, element.device_address, 7)
                    
                elif isinstance(element, ContactB):
                    color = 11 if element.last_result else 1
                    pyxel.rect(x_pos, y_pos, 8, 8, color)
                    pyxel.text(x_pos + 1, y_pos + 2, "B", 0)
                    pyxel.text(x_pos, y_pos - 8, element.device_address, 7)
                    
                elif isinstance(element, Coil):
                    color = 11 if element.last_result else 1
                    pyxel.circ(x_pos + 4, y_pos + 4, 3, color)
                    pyxel.text(x_pos, y_pos - 8, element.device_address, 7)
                    
                elif isinstance(element, Timer):
                    color = 11 if element.last_result else 1
                    pyxel.rect(x_pos, y_pos, 10, 8, color)
                    pyxel.text(x_pos + 1, y_pos + 2, "T", 0)
                    pyxel.text(x_pos, y_pos - 8, element.device_address, 7)
                    
                elif isinstance(element, Counter):
                    color = 11 if element.last_result else 1
                    pyxel.rect(x_pos, y_pos, 10, 8, color)
                    pyxel.text(x_pos + 1, y_pos + 2, "C", 0)
                    pyxel.text(x_pos, y_pos - 8, element.device_address, 7)
                
                # 接続線
                if x_pos > 15:  # 最初の素子でない場合
                    line_color = 11 if element.last_result else 1
                    pyxel.line(x_pos - 5, y_pos + 4, x_pos, y_pos + 4, line_color)
                
                x_pos += 15
                
            y_pos += 20


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
            
            # 範囲チェック
            if 0 <= grid_x < Layout.GRID_COLS and 0 <= grid_y < Layout.GRID_ROWS:
                return (grid_x, grid_y)
        
        return None
    
    def handle_mouse_input(self, grid_manager, device_manager):
        """マウス入力処理"""
        # マウスプレビュー更新
        self._update_preview(grid_manager)
        
        # クリック処理
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mouse_x, mouse_y = pyxel.mouse_x, pyxel.mouse_y
            
            # デバイスパレット選択判定
            if Layout.PALETTE_Y - 2 <= mouse_y <= Layout.PALETTE_Y + 10:
                for i, device in enumerate(self.device_palette):
                    x_pos = Layout.PALETTE_START_X + i * Layout.PALETTE_DEVICE_WIDTH
                    if x_pos - 2 <= mouse_x <= x_pos + 18:
                        # デバイスタイプを選択
                        self.selected_device_type = device["type"]
                        break
            else:
                # グリッド上でのデバイス配置処理
                self._handle_grid_placement(grid_manager, device_manager)
    
    def _update_preview(self, grid_manager):
        """マウスプレビュー更新"""
        grid_pos = self.get_grid_position_from_mouse()
        if grid_pos:
            self.show_preview = True
            self.preview_grid_pos = grid_pos
            grid_x, grid_y = grid_pos
            
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
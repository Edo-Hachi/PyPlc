"""
PyPlc Renderer Module
描画系機能を分離したモジュール

Phase 1 リファクタリング: 描画系分離
- グリッド描画
- デバイス描画  
- UI描画
- マウスカーソル描画
"""

import pyxel
from typing import List, Dict, Any, Optional, Tuple
from core.constants import DeviceType
from core.config_manager import PyPlcConfig
from core.logic_element import LogicElement


class PyPlcRenderer:
    """PyPlc描画システム / PyPlc Rendering System"""
    
    def __init__(self, config: PyPlcConfig):
        """
        レンダラー初期化
        
        Args:
            config: PyPlc設定オブジェクト
        """
        self.config = config
        
        # 描画定数
        self.DEVICE_SIZE = 8
        self.DEVICE_HALF_SIZE = 4
        self.SYMBOL_OFFSET = 2
        self.NAME_OFFSET_Y = 10
        self.NAME_OFFSET_X = -4
        
        # デバイスシンボルマッピング
        self.DEVICE_SYMBOLS = {
            DeviceType.CONTACT_A: "A",
            DeviceType.CONTACT_B: "B", 
            DeviceType.COIL: "O",
            DeviceType.TIMER: "T"
        }
    
    def draw_grid(self) -> None:
        """Draw grid lines / グリッド線描画（交点ベース）"""
        grid_x = self.config.grid_origin_x
        grid_y = self.config.grid_origin_y
        cell_size = self.config.grid_cell_size
        rows = self.config.grid_rows
        cols = self.config.grid_cols
        
        # 縦線描画（列線）/ Draw vertical lines (column lines)
        for col in range(cols):
            x = grid_x + col * cell_size
            y_start = grid_y
            y_end = grid_y + (rows - 1) * cell_size
            
            # バス線は太線で描画 / Draw bus lines with thick lines
            if col == 0:  # 左バス（電源）/ Left bus (power)
                pyxel.rect(x, y_start, 2, y_end - y_start + 1, pyxel.COLOR_YELLOW)
            elif col == cols - 1:  # 右バス（ニュートラル）/ Right bus (neutral)
                pyxel.rect(x, y_start, 2, y_end - y_start + 1, pyxel.COLOR_LIGHT_BLUE)
            else:  # 通常のグリッド線 / Normal grid lines
                pyxel.line(x, y_start, x, y_end, pyxel.COLOR_DARK_BLUE)
        
        # 横線描画（行線）/ Draw horizontal lines (row lines)
        for row in range(rows):
            y = grid_y + row * cell_size
            x_start = grid_x
            x_end = grid_x + (cols - 1) * cell_size
            pyxel.line(x_start, y, x_end, y, pyxel.COLOR_DARK_BLUE)
    
    def draw_devices(self, grid_manager) -> None:
        """Draw all devices / 全デバイス描画（交点ベース）"""
        drawable_devices = self._get_drawable_devices(grid_manager)
        for device in drawable_devices:
            self._draw_single_device(device)
    
    def _get_drawable_devices(self, grid_manager) -> List[LogicElement]:
        """Get devices that should be drawn / 描画対象デバイス取得"""
        return [device for device in grid_manager.get_all_devices() 
                if not device.is_bus_device()]
    
    def _draw_single_device(self, device: LogicElement) -> None:
        """Draw a single device / 単一デバイス描画"""
        device_rect = self._calculate_device_rect(device)
        color = self._get_device_color(device)
        symbol = self._get_device_symbol(device)
        
        # Draw device rectangle / デバイス矩形描画
        pyxel.rect(device_rect['x'], device_rect['y'], self.DEVICE_SIZE, self.DEVICE_SIZE, color)
        
        # Draw device symbol / デバイスシンボル描画
        self._draw_device_symbol(device_rect, symbol)
        
        # Draw device name / デバイス名描画
        self._draw_device_name(device_rect, device.name)
    
    def _calculate_device_rect(self, device: LogicElement) -> Dict[str, int]:
        """Calculate device rectangle position / デバイス矩形位置計算"""
        grid_x = self.config.grid_origin_x
        grid_y = self.config.grid_origin_y
        cell_size = self.config.grid_cell_size
        
        # Calculate intersection position / 交点位置計算
        intersection_x = grid_x + device.grid_col * cell_size
        intersection_y = grid_y + device.grid_row * cell_size
        
        # Center device on intersection / 交点中央にデバイス配置
        device_x = intersection_x - self.DEVICE_HALF_SIZE
        device_y = intersection_y - self.DEVICE_HALF_SIZE
        
        return {'x': device_x, 'y': device_y}
    
    def _get_device_color(self, device: LogicElement) -> int:
        """Get device color based on state / デバイス状態に基づく色取得"""
        return pyxel.COLOR_GREEN if device.active else pyxel.COLOR_RED
    
    def _get_device_symbol(self, device: LogicElement) -> str:
        """Get device symbol / デバイスシンボル取得"""
        return self.DEVICE_SYMBOLS.get(device.device_type, "?")
    
    def _draw_device_symbol(self, device_rect: Dict[str, int], symbol: str) -> None:
        """Draw device symbol / デバイスシンボル描画"""
        symbol_x = device_rect['x'] + self.SYMBOL_OFFSET
        symbol_y = device_rect['y'] + self.SYMBOL_OFFSET
        pyxel.text(symbol_x, symbol_y, symbol, pyxel.COLOR_WHITE)
    
    def _draw_device_name(self, device_rect: Dict[str, int], name: str) -> None:
        """Draw device name / デバイス名描画"""
        name_x = device_rect['x'] + self.NAME_OFFSET_X
        name_y = device_rect['y'] + self.NAME_OFFSET_Y
        pyxel.text(name_x, name_y, name, pyxel.COLOR_WHITE)
    
    def draw_device_info(self, grid_manager) -> None:
        """Draw device information / デバイス情報描画"""
        info_y = self.config.status_area_y
        
        pyxel.text(10, info_y, "Device Status:", pyxel.COLOR_WHITE)
        
        # List key devices / 主要デバイスリスト表示
        y_offset = 0
        for device in grid_manager.get_all_devices():
            if not device.is_bus_device():
                status = "ON" if device.active else "OFF"
                pyxel.text(10, info_y + 12 + y_offset, f"{device.name}: {status}", pyxel.COLOR_WHITE)
                y_offset += 10
                if y_offset > 20:  # Limit display / 表示制限
                    break
    
    def draw_mouse_cursor(self, mouse_grid_pos: Optional[Tuple[int, int]], show_cursor: bool) -> None:
        """Draw mouse cursor at editable positions / 編集可能位置にマウスカーソル描画"""
        if not show_cursor or not mouse_grid_pos:
            return
        
        row, col = mouse_grid_pos
        grid_x = self.config.grid_origin_x
        grid_y = self.config.grid_origin_y
        cell_size = self.config.grid_cell_size
        
        # Calculate intersection position / 交点位置計算
        intersection_x = grid_x + col * cell_size
        intersection_y = grid_y + row * cell_size
        
        # Draw cursor as a small circle / カーソルを小さな円で描画
        pyxel.circb(intersection_x, intersection_y, 3, pyxel.COLOR_YELLOW)
        
        # Draw crosshair / 十字線描画
        pyxel.line(intersection_x - 5, intersection_y, intersection_x + 5, intersection_y, pyxel.COLOR_YELLOW)
        pyxel.line(intersection_x, intersection_y - 5, intersection_x, intersection_y + 5, pyxel.COLOR_YELLOW)
    
    def draw_controls(self) -> None:
        """Draw control information / 操作情報描画"""
        control_y = self.config.control_info_y
        pyxel.text(10, control_y, "CTRL: Snap, 1: Toggle X001, F5-F8: Scan(50/100/200/500ms), Q: Quit", pyxel.COLOR_WHITE)
    
    def draw_status_bar(self, mouse_grid_pos: Optional[Tuple[int, int]], snap_mode: bool, is_editable_func) -> None:
        """Draw status bar with mouse position / マウス位置情報を含むステータスバー描画"""
        # ステータスバーの位置（画面下部）
        status_y = self.config.window_height - 20
        
        # 背景を黒でクリア
        pyxel.rect(0, status_y, self.config.window_width, 20, pyxel.COLOR_BLACK)
        
        # スナップモード表示
        mode_text = "SNAP MODE" if snap_mode else "FREE MODE"
        mode_color = pyxel.COLOR_YELLOW if snap_mode else pyxel.COLOR_WHITE
        pyxel.text(200, status_y + 2, mode_text, mode_color)
        
        # マウス位置情報表示
        if mouse_grid_pos:
            row, col = mouse_grid_pos
            position_text = f"Grid Position: Row={row}, Col={col} [grid[{row}][{col}]]"
            pyxel.text(10, status_y + 5, position_text, pyxel.COLOR_WHITE)
            
            # 編集可能かどうか表示
            if is_editable_func(row, col):
                pyxel.text(10, status_y + 12, "Editable: YES", pyxel.COLOR_GREEN)
            else:
                pyxel.text(10, status_y + 12, "Editable: NO (Bus area)", pyxel.COLOR_RED)
        else:
            # グリッド外またはスナップ範囲外の場合
            mouse_x, mouse_y = pyxel.mouse_x, pyxel.mouse_y
            if snap_mode:
                pyxel.text(10, status_y + 5, f"Mouse: ({mouse_x}, {mouse_y}) - No snap target", pyxel.COLOR_GRAY)
                pyxel.text(10, status_y + 12, "Editable: NO (Outside snap range)", pyxel.COLOR_RED)
            else:
                pyxel.text(10, status_y + 5, f"Mouse: ({mouse_x}, {mouse_y}) - Free movement", pyxel.COLOR_GRAY)
                pyxel.text(10, status_y + 12, "Hold CTRL to enable snap mode", pyxel.COLOR_CYAN)

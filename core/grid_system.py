"""
PyPlc Ver3 Grid System Module
作成日: 2025-01-29
目標: 回路データの中核管理（デバイスの配置・削除・接続）
"""

import pyxel
from typing import Optional, Tuple, List

from config import GridConfig, GridConstraints, DeviceType
from core.device_base import PLCDevice

class GridSystem:
    """
    PLCラダー図のグリッドと、その上に配置されたデバイスを管理するクラス。
    - 回路データの保持、操作（配置、削除）、描画を担当する。
    """
    
    def __init__(self):
        """GridSystemの初期化"""
        self.rows: int = GridConfig.GRID_ROWS
        self.cols: int = GridConfig.GRID_COLS
        self.cell_size: int = GridConfig.GRID_CELL_SIZE
        self.origin_x: int = GridConfig.GRID_ORIGIN_X
        self.origin_y: int = GridConfig.GRID_ORIGIN_Y
        
        self.grid_data: List[List[Optional[PLCDevice]]] = [
            [None for _ in range(self.cols)] for _ in range(self.rows)
        ]
        self._initialize_bus_bars()

    def _initialize_bus_bars(self):
        """左右のバスバーをグリッドに配置する"""
        for r in range(self.rows):
            self.place_device(r, GridConstraints.get_left_bus_col(), DeviceType.L_SIDE, f"L_BUS_{r}")
            self.place_device(r, GridConstraints.get_right_bus_col(), DeviceType.R_SIDE, f"R_BUS_{r}")

    def get_device(self, row: int, col: int) -> Optional[PLCDevice]:
        """指定した座標のデバイスを取得する"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid_data[row][col]
        return None

    def place_device(self, row: int, col: int, device_type: DeviceType, address: str = "") -> Optional[PLCDevice]:
        """指定した座標に新しいデバイスを配置し、接続を更新する"""
        if self.get_device(row, col) is not None and device_type not in [DeviceType.L_SIDE, DeviceType.R_SIDE]:
            return None

        new_device = PLCDevice(device_type=device_type, position=(row, col), address=address)
        self.grid_data[row][col] = new_device
        self._update_connections(new_device)
        return new_device

    def remove_device(self, row: int, col: int) -> bool:
        """指定した座標のデバイスを削除し、接続を更新する"""
        device_to_remove = self.get_device(row, col)
        if device_to_remove is None or device_to_remove.device_type in [DeviceType.L_SIDE, DeviceType.R_SIDE]:
            return False

        for direction, neighbor_pos in device_to_remove.connections.items():
            if neighbor_pos:
                neighbor_device = self.get_device(neighbor_pos[0], neighbor_pos[1])
                if neighbor_device:
                    reverse_direction = self._get_reverse_direction(direction)
                    neighbor_device.connections[reverse_direction] = None
        
        self.grid_data[row][col] = None
        return True

    def _update_connections(self, device: PLCDevice) -> None:
        """指定されたデバイスとその周囲のデバイスの接続情報を更新する"""
        row, col = device.position
        neighbor_positions = {
            'up': (row - 1, col), 'down': (row + 1, col),
            'left': (row, col - 1), 'right': (row, col + 1),
        }
        for direction, pos in neighbor_positions.items():
            neighbor_device = self.get_device(pos[0], pos[1])
            if neighbor_device:
                device.connections[direction] = neighbor_device.position
                reverse_direction = self._get_reverse_direction(direction)
                neighbor_device.connections[reverse_direction] = device.position

    def _get_reverse_direction(self, direction: str) -> str:
        reverses = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}
        return reverses[direction]

    def reset_all_energized_states(self) -> None:
        """バスバーを除く全デバイスの通電状態をリセットする"""
        for r in range(self.rows):
            for c in range(self.cols):
                device = self.get_device(r, c)
                if device:
                    device.is_energized = (device.device_type == DeviceType.L_SIDE)

    def draw(self) -> None:
        """グリッド線、バスバー、そして配置されたデバイスを描画する"""
        self._draw_grid_lines()
        self._draw_devices()

    def _draw_grid_lines(self) -> None:
        """グリッド線とバスバーを描画する"""
        for col in range(self.cols):
            x = self.origin_x + col * self.cell_size
            y_start, y_end = self.origin_y, self.origin_y + (self.rows - 1) * self.cell_size
            if not (col == GridConstraints.get_left_bus_col() or col == GridConstraints.get_right_bus_col()):
                 pyxel.line(x, y_start, x, y_end, pyxel.COLOR_DARK_BLUE)

        for row in range(self.rows):
            y = self.origin_y + row * self.cell_size
            x_start, x_end = self.origin_x, self.origin_x + (self.cols - 1) * self.cell_size
            pyxel.line(x_start, y, x_end, y, pyxel.COLOR_DARK_BLUE)

    def _draw_devices(self) -> None:
        """グリッド上のすべてのデバイスを描画する"""
        for r in range(self.rows):
            for c in range(self.cols):
                device = self.get_device(r, c)
                if device:
                    x = self.origin_x + c * self.cell_size
                    y = self.origin_y + r * self.cell_size
                    
                    if device.device_type == DeviceType.L_SIDE:
                        pyxel.rect(x, y - self.cell_size // 2, 2, self.cell_size, pyxel.COLOR_YELLOW)
                    elif device.device_type == DeviceType.R_SIDE:
                        pyxel.rect(x, y - self.cell_size // 2, 2, self.cell_size, pyxel.COLOR_LIGHT_BLUE)
                    else:
                        # --- 描画ロジックの修正 ---
                        # 全てのデバイスの色は、is_energized（通電状態）のみを正とする
                        color = pyxel.COLOR_GREEN if device.is_energized else pyxel.COLOR_RED
                        
                        # 仮のデバイス描画
                        pyxel.rect(x - 3, y - 3, 7, 7, color)
                        
                        # (デバッグ用) 接点のstateを文字で表示
                        if device.device_type in [DeviceType.CONTACT_A, DeviceType.CONTACT_B]:
                            state_char = "T" if device.state else "F"
                            pyxel.text(x - 8, y - 4, state_char, 13)

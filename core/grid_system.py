"""
PyPlc Ver3 Grid System Module
作成日: 2025-01-29
目標: 回路データの中核管理（デバイスの配置・削除・接続）
"""

import pyxel
import csv
import io
from datetime import datetime
from typing import Optional, Tuple, List

from config import GridConfig, GridConstraints, DeviceType
from core.device_base import PLCDevice
from core.SpriteManager import sprite_manager # SpriteManagerをインポート

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

    def _calculate_display_state(self, device: PLCDevice) -> bool:
        """
        デバイスの表示状態を計算（PLC標準準拠）
        接点：論理状態と通電状態の組み合わせで点灯判定
        その他：通電状態をそのまま使用
        """
        if device.device_type == DeviceType.CONTACT_A:
            # A接点: ONかつ通電時のみ点灯
            return device.state and device.is_energized
        elif device.device_type == DeviceType.CONTACT_B:
            # B接点: OFFかつ通電時のみ点灯  
            return (not device.state) and device.is_energized
        else:
            # その他のデバイス（コイル、配線等）: 通電状態をそのまま表示
            return device.is_energized

    def reset_all_energized_states(self) -> None:
        """全デバイスの通電状態をリセット（配置は維持）"""
        for row in range(self.rows):
            for col in range(self.cols):
                device = self.get_device(row, col)
                if device:
                    device.is_energized = False
        # 左バスバー（電源）のみTrueに設定
        for row in range(self.rows):
            left_bus = self.get_device(row, GridConstraints.get_left_bus_col())
            if left_bus:
                left_bus.is_energized = True

    def draw(self) -> None:
        """グリッド線、バスバー、そして配置されたデバイスを描画する"""
        self._draw_grid_lines() # 背景グリッド線を先に描画
        self._draw_devices()

    def _draw_grid_lines(self) -> None:
        """グリッド線を描画する"""
        # 水平線
        for r in range(self.rows):
            y = self.origin_y + r * self.cell_size
            x1 = self.origin_x + (GridConstraints.get_left_bus_col()) * self.cell_size
            x2 = self.origin_x + (GridConstraints.get_right_bus_col()) * self.cell_size
            pyxel.line(x1, y, x2, y, pyxel.COLOR_NAVY)
        
        # 垂直線
        for c in range(GridConstraints.get_left_bus_col() + 1, GridConstraints.get_right_bus_col()):
            x = self.origin_x + c * self.cell_size
            y1 = self.origin_y
            y2 = self.origin_y + (self.rows - 1) * self.cell_size
            pyxel.line(x, y1, x, y2, pyxel.COLOR_NAVY)

    def _draw_devices(self) -> None:
        """グリッド上のすべてのデバイスをスプライトで描画する"""
        sprite_size = sprite_manager.sprite_size
        
        # デバッグ用: 描画されるデバイス数をカウント（開発用、本来は不要）
        device_count = 0
        
        for r in range(self.rows):
            for c in range(self.cols):
                device = self.get_device(r, c)
                if device:
                    draw_x = self.origin_x + c * self.cell_size - sprite_size // 2
                    draw_y = self.origin_y + r * self.cell_size - sprite_size // 2

                    # --- バスバーは当面の間、旧描画方式を維持 ---
                    if device.device_type == DeviceType.L_SIDE:
                        # バスバーの描画位置をグリッド線に合わせる
                        bar_x = self.origin_x + c * self.cell_size
                        pyxel.rect(bar_x -1, self.origin_y-8, 3, (self.rows) * self.cell_size, pyxel.COLOR_YELLOW)
                        continue
                    elif device.device_type == DeviceType.R_SIDE:
                        bar_x = self.origin_x + c * self.cell_size
                        pyxel.rect(bar_x - 1, self.origin_y-8, 3, (self.rows) * self.cell_size, pyxel.COLOR_LIGHT_BLUE)
                        continue
                    
                    # --- デバイスのスプライト描画 ---
                    # 接点の表示状態は論理状態と通電状態の組み合わせで決定
                    display_energized = self._calculate_display_state(device)
                    coords = sprite_manager.get_sprite_coords(device.device_type, display_energized)
                    if coords:
                        pyxel.blt(draw_x, draw_y, 0, coords[0], coords[1], sprite_size, sprite_size, 0)
                        device_count += 1  # 描画カウント
                    else:
                        # スプライトが見つからない場合のフォールバック
                        pyxel.rect(draw_x, draw_y, sprite_size, sprite_size, pyxel.COLOR_PINK)
                        device_count += 1  # 描画カウント（フォールバックも含む）
        
        # デバッグ用描画情報（画面下部に表示）
        if device_count > 2:  # バスバー以外のデバイスがある場合のみ表示
            pyxel.text(10, 360, f"Drawing {device_count} devices", pyxel.COLOR_WHITE)

    def to_csv(self) -> str:
        """
        現在のグリッド状態をCSV形式の文字列として出力
        バスバー（L_SIDE/R_SIDE）は除外し、配置されたデバイスのみを出力
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # ヘッダー情報（コメント形式）
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output.write(f"# PyPlc Ver3 Circuit Data\n")
        output.write(f"# Format: row,col,device_type,address,state\n")
        output.write(f"# Created: {current_time}\n")
        
        # CSVヘッダー
        writer.writerow(['row', 'col', 'device_type', 'address', 'state'])
        
        # デバイスデータ出力（バスバー除外）
        for row in range(self.rows):
            for col in range(self.cols):
                device = self.get_device(row, col)
                if device and device.device_type not in [DeviceType.L_SIDE, DeviceType.R_SIDE]:
                    writer.writerow([
                        row,
                        col, 
                        device.device_type.value,
                        device.address,
                        device.state
                    ])
        
        return output.getvalue()

    def from_csv(self, csv_data: str) -> bool:
        """
        CSV形式の文字列からグリッド状態を復元
        現在のグリッドをクリアしてからデータを読み込む
        """
        try:
            print(f"CSV Import Started - Data length: {len(csv_data)} chars")
            
            # 現在のグリッドをクリア（バスバー以外）
            self._clear_user_devices()
            print("User devices cleared")
            
            # CSV読み込み（コメント行を事前除去）
            lines = csv_data.strip().split('\n')
            csv_lines = []
            for line in lines:
                if not line.strip().startswith('#'):
                    csv_lines.append(line)
            
            # コメント除去後のCSVデータを再構築
            clean_csv_data = '\n'.join(csv_lines)
            print(f"Clean CSV data (after comment removal): {len(clean_csv_data)} chars")
            
            input_stream = io.StringIO(clean_csv_data)
            reader = csv.DictReader(input_stream, skipinitialspace=True)
            
            loaded_count = 0
            for line_num, row_data in enumerate(reader, start=1):
                try:
                    # データ解析
                    row = int(row_data['row'])
                    col = int(row_data['col'])
                    device_type_str = row_data['device_type']
                    address = row_data['address']
                    state_str = row_data['state']
                    
                    print(f"Processing line {line_num}: [{row}][{col}] = {device_type_str}")
                    
                    # DeviceType変換
                    device_type = DeviceType(device_type_str)
                    
                    # state変換（True/False文字列をboolに）
                    state = state_str.lower() == 'true'
                    
                    # デバイス配置
                    new_device = self.place_device(row, col, device_type, address)
                    if new_device:
                        new_device.state = state
                        loaded_count += 1
                        print(f"  Device placed: {device_type_str} at [{row}][{col}] state={state}")
                    else:
                        print(f"  Failed to place device at [{row}][{col}]")
                    
                except (ValueError, KeyError) as e:
                    print(f"Warning: CSV line {line_num} skipped due to error: {e}")
                    print(f"    Row data: {row_data}")
                    continue
            
            print(f"CSV Import Complete - {loaded_count} devices loaded")
            return True
            
        except Exception as e:
            print(f"Error loading CSV data: {e}")
            return False

    def _clear_user_devices(self) -> None:
        """
        ユーザー配置デバイスをクリア（バスバーは保持）
        """
        for row in range(self.rows):
            for col in range(self.cols):
                device = self.get_device(row, col)
                if device and device.device_type not in [DeviceType.L_SIDE, DeviceType.R_SIDE]:
                    self.grid_data[row][col] = None

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
        接点：device.stateがスプライト表示状態を直接決定
        コイル・配線：通電状態をそのまま表示
        """
        if device.device_type in [DeviceType.CONTACT_A, DeviceType.CONTACT_B]:
            # 接点（A/B）: stateがONなら導通スプライト、OFFなら開放スプライト表示
            # 右クリックでの状態変更を直接反映
            return device.state
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
                        
                        # タイマー・カウンター現在値表示（PLC標準準拠）
                        self._draw_timer_counter_value(device, draw_x, draw_y, sprite_size)
                        
                    else:
                        # スプライトが見つからない場合のフォールバック
                        pyxel.rect(draw_x, draw_y, sprite_size, sprite_size, pyxel.COLOR_PINK)
                        device_count += 1  # 描画カウント（フォールバックも含む）
        
        # デバッグ用描画情報（画面下部に表示）
        if device_count > 2:  # バスバー以外のデバイスがある場合のみ表示
            pyxel.text(10, 360, f"Drawing {device_count} devices", pyxel.COLOR_WHITE)

    def _draw_timer_counter_value(self, device: PLCDevice, draw_x: int, draw_y: int, sprite_size: int) -> None:
        """
        タイマー・カウンター現在値表示（PLC標準準拠）
        現在値をデバイススプライトの下部に数値で表示
        
        Args:
            device: 描画対象デバイス
            draw_x: スプライト描画X座標
            draw_y: スプライト描画Y座標
            sprite_size: スプライトサイズ
        """
        if device.device_type not in [DeviceType.TIMER_TON, DeviceType.COUNTER_CTU]:
            return
        
        # 現在値表示位置計算（スプライト下部中央）
        value_x = draw_x + sprite_size // 4  # スプライト中央寄り
        value_y = draw_y + sprite_size + 1   # スプライト下部に少し間隔
        
        # 現在値テキスト生成（半角英数字のみ）
        if device.device_type == DeviceType.TIMER_TON:
            # タイマー: 現在値/プリセット値形式で表示
            current_val = getattr(device, 'current_value', 0)
            preset_val = getattr(device, 'preset_value', 0)
            value_text = f"{current_val}/{preset_val}"
            text_color = pyxel.COLOR_PURPLE  # 常時パープルで見やすく
            
        elif device.device_type == DeviceType.COUNTER_CTU:
            # カウンター: 現在値/プリセット値形式で表示
            current_val = getattr(device, 'current_value', 0)
            preset_val = getattr(device, 'preset_value', 0)
            value_text = f"{current_val}/{preset_val}"
            text_color = pyxel.COLOR_PURPLE  # 常時パープルで見やすく
            
        elif device.device_type == DeviceType.DATA_REGISTER:
            # データレジスタ: アドレス=値形式で表示
            address = getattr(device, 'address', 'D?')
            data_val = getattr(device, 'data_value', 0)
            value_text = f"{address}={data_val}"
            text_color = pyxel.COLOR_CYAN  # シアンで見やすく
        else:
            return
        
        # 現在値表示（背景付き）
        text_width = len(value_text) * 4
        pyxel.rect(value_x - 1, value_y - 1, text_width + 2, 7, pyxel.COLOR_BLACK)
        pyxel.text(value_x, value_y, value_text, text_color)

    def to_csv(self) -> str:
        """
        現在のグリッド状態をCSV形式の文字列として出力
        バスバー（L_SIDE/R_SIDE）は除外し、配置されたデバイスのみを出力
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # ヘッダー情報（コメント形式）
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output.write(f"# PyPlc Ver3 Circuit Data (Extended Format)\n")
        output.write(f"# Format: row,col,device_type,address,state,preset_value,current_value,timer_active,last_input_state\n")
        output.write(f"# Created: {current_time}\n")
        
        # CSVヘッダー（拡張フォーマット）
        writer.writerow(['row', 'col', 'device_type', 'address', 'state', 'preset_value', 'current_value', 'timer_active', 'last_input_state'])
        
        # デバイスデータ出力（バスバー除外）
        for row in range(self.rows):
            for col in range(self.cols):
                device = self.get_device(row, col)
                if device and device.device_type not in [DeviceType.L_SIDE, DeviceType.R_SIDE]:
                    # タイマー・カウンター特有の値を取得（存在しない場合はデフォルト値）
                    preset_value = getattr(device, 'preset_value', 0)
                    current_value = getattr(device, 'current_value', 0)
                    timer_active = getattr(device, 'timer_active', False)
                    last_input_state = getattr(device, 'last_input_state', False)
                    
                    writer.writerow([
                        row,
                        col, 
                        device.device_type.value,
                        device.address,
                        device.state,
                        preset_value,
                        current_value,
                        timer_active,
                        last_input_state
                    ])
        
        return output.getvalue()

    def from_csv(self, csv_data: str) -> bool:
        """
        CSV形式の文字列からグリッド状態を復元
        現在のグリッドをクリアしてからデータを読み込む
        """
        try:
            # 現在のグリッドをクリア（バスバー以外）
            self._clear_user_devices()
            
            # CSV読み込み（コメント行を事前除去）
            lines = csv_data.strip().split('\n')
            csv_lines = []
            for line in lines:
                if not line.strip().startswith('#'):
                    csv_lines.append(line)
            
            # コメント除去後のCSVデータを再構築
            clean_csv_data = '\n'.join(csv_lines)
            
            input_stream = io.StringIO(clean_csv_data)
            reader = csv.DictReader(input_stream, skipinitialspace=True)
            
            loaded_count = 0
            for line_num, row_data in enumerate(reader, start=1):
                try:
                    # データ解析（基本フィールド - 複数フォーマット対応）
                    # フォーマット1: row,col,device_type,address,state (Ver3標準)
                    # フォーマット2: Row,Col,DeviceType,DeviceID,IsEnergized,State (旧フォーマット)
                    
                    if 'row' in row_data:
                        row = int(row_data['row'])
                        col = int(row_data['col'])
                        device_type_str = row_data['device_type']
                        address = row_data['address']
                        state_str = row_data['state']
                    elif 'Row' in row_data:
                        # 旧フォーマット対応
                        row = int(row_data['Row'])
                        col = int(row_data['Col'])
                        device_type_str = row_data['DeviceType']
                        address = row_data['DeviceID']
                        state_str = row_data['State']
                    else:
                        # 不明なフォーマット
                        continue
                    
                    # DeviceType変換
                    device_type = DeviceType(device_type_str)
                    
                    # state変換（True/False文字列をboolに）
                    state = state_str.lower() == 'true'
                    
                    # 拡張フィールド解析（後方互換性確保）
                    preset_value = 0
                    current_value = 0
                    timer_active = False
                    last_input_state = False
                    
                    # 拡張フィールドが存在する場合は取得
                    if 'preset_value' in row_data:
                        preset_value = int(row_data['preset_value']) if row_data['preset_value'] else 0
                    if 'current_value' in row_data:
                        current_value = int(row_data['current_value']) if row_data['current_value'] else 0
                    if 'timer_active' in row_data:
                        timer_active = row_data['timer_active'].lower() == 'true' if row_data['timer_active'] else False
                    if 'last_input_state' in row_data:
                        last_input_state = row_data['last_input_state'].lower() == 'true' if row_data['last_input_state'] else False
                    
                    # デバイス配置
                    new_device = self.place_device(row, col, device_type, address)
                    if new_device:
                        new_device.state = state
                        
                        # タイマー・カウンター特有の値を設定
                        if device_type in [DeviceType.TIMER_TON, DeviceType.COUNTER_CTU]:
                            new_device.preset_value = preset_value
                            new_device.current_value = current_value
                            new_device.timer_active = timer_active
                            new_device.last_input_state = last_input_state
                        
                        loaded_count += 1
                    
                except (ValueError, KeyError) as e:
                    continue
            
            return True
            
        except Exception as e:
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

    def update_device_address(self, row: int, col: int, new_address: str) -> bool:
        """
        指定した座標のデバイスのアドレスを更新
        
        Args:
            row: 行番号
            col: 列番号
            new_address: 新しいデバイスアドレス
            
        Returns:
            bool: 更新成功時True、失敗時False
        """
        device = self.get_device(row, col)
        if device:
            device.address = new_address
            return True
        else:
            return False

    def find_devices_by_address(self, target_address: str) -> List[Tuple[int, int]]:
        """
        指定アドレスと一致する全デバイスの座標を返す
        同アドレスハイライト機能で使用
        
        Args:
            target_address: 検索対象アドレス（例: "X001", "M100"）
            
        Returns:
            List[Tuple[int, int]]: 一致デバイスの(row, col)座標リスト
        """
        if not target_address or target_address.strip() == "":
            return []
        
        matching_positions: List[Tuple[int, int]] = []
        normalized_target = target_address.upper().strip()
        
        # 全グリッドをスキャンして同アドレスデバイスを検索
        for row in range(self.rows):
            for col in range(self.cols):
                device = self.get_device(row, col)
                if (device and 
                    device.address and 
                    device.address.upper().strip() == normalized_target and
                    device.device_type not in [DeviceType.L_SIDE, DeviceType.R_SIDE]):
                    matching_positions.append((row, col))
        
        return matching_positions

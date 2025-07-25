"""
PyPlc Grid System Module

グリッドベースのデバイス配置システムを管理するモジュール。
- GridDevice: グリッド上に配置されるロジックデバイス
- GridDeviceManager: グリッド上のデバイス配置管理
"""

from typing import List, Optional
from config import DeviceType, BusbarDirection


class GridDevice:
    """グリッド上に配置されるロジックデバイス"""
    def __init__(self, device_type: DeviceType = DeviceType.EMPTY, grid_x: int = 0, grid_y: int = 0):
        self.device_type = device_type
        self.grid_x = grid_x
        self.grid_y = grid_y
        
        # デバイス共通状態
        self.active = False          # 動作状態（通電状態）
        self.device_address = None   # デバイスアドレス（X001, Y001等）
        
        # デバイス固有の状態
        self.timer_preset = 0.0      # タイマープリセット値
        self.timer_current = 0.0     # タイマー現在値
        self.timer_state = "STANBY"  # タイマー状態（STANBY/CNTUP/ON）
        self.counter_preset = 0      # カウンタープリセット値
        self.counter_current = 0     # カウンター現在値
        self.contact_state = False   # 接点状態（A/B接点用）
        self.coil_energized = False  # コイル励磁状態
        
        # バスバー専用
        self.busbar_direction = BusbarDirection.NONE  # 接続方向
        
        # 配線専用
        self.wire_energized = False  # 配線通電状態
    
    def get_sprite_name(self) -> Optional[str]:
        """デバイスタイプと状態に応じたスプライト名を返す"""
        if self.device_type == DeviceType.TYPE_A:
            return "TYPE_A_ON" if self.active else "TYPE_A_OFF"
        elif self.device_type == DeviceType.TYPE_B:
            return "TYPE_B_ON" if self.active else "TYPE_B_OFF"
        elif self.device_type == DeviceType.COIL:
            # 正式なOUTCOIL_NMLスプライトを使用（|Y01|形式）
            return "OUTCOIL_NML_ON" if self.coil_energized else "OUTCOIL_NML_OFF"
        elif self.device_type == DeviceType.INCOIL:
            # 入力コイルスプライト（内部処理用）
            return "INCOIL_ON" if self.coil_energized else "INCOIL_OFF"
        elif self.device_type == DeviceType.TIMER:
            # 3状態スプライト切り替え
            if self.timer_state == "STANBY":
                return "TIMER_STANBY"
            elif self.timer_state == "CNTUP":
                return "TIMER_CNTUP"
            elif self.timer_state == "ON":
                return "TIMER_ON"
            else:
                return "TIMER_STANBY"  # デフォルト
        elif self.device_type == DeviceType.COUNTER:
            return "TYPE_A_ON" if self.active else "TYPE_A_OFF"  # 仮のスプライト
        elif self.device_type == DeviceType.LINK_UP:
            return "LINK_UP"
        elif self.device_type == DeviceType.LINK_DOWN:
            return "LINK_DOWN"
        elif self.device_type == DeviceType.DEL:
            return "DEL"
        return None
    
    def update_state(self, device_manager):
        """デバイス状態を更新"""
        if self.device_address and self.device_type in [DeviceType.TYPE_A, DeviceType.TYPE_B]:
            plc_device = device_manager.get_device(self.device_address)
            if self.device_type == DeviceType.TYPE_A:
                self.contact_state = plc_device.value
                self.active = self.contact_state
            elif self.device_type == DeviceType.TYPE_B:
                self.contact_state = plc_device.value
                self.active = not self.contact_state  # B接点は反転
        elif self.device_address and self.device_type == DeviceType.COIL:
            plc_device = device_manager.get_device(self.device_address)
            self.coil_energized = plc_device.value
            self.active = self.coil_energized
        elif self.device_address and self.device_type == DeviceType.INCOIL:
            plc_device = device_manager.get_device(self.device_address)
            self.coil_energized = plc_device.value
            self.active = self.coil_energized


class GridDeviceManager:
    """グリッド上のデバイス配置を管理するクラス"""
    def __init__(self, grid_cols: int = 10, grid_rows: int = 10):
        self.grid_cols = grid_cols
        self.grid_rows = grid_rows
        # 2次元配列でグリッドデバイスを管理
        self.grid: List[List[GridDevice]] = []
        
        # グリッドを初期化
        for row in range(grid_rows):
            grid_row = []
            for col in range(grid_cols):
                grid_row.append(GridDevice(DeviceType.EMPTY, col, row))
            self.grid.append(grid_row)
    
    def place_device(self, grid_x: int, grid_y: int, device_type: DeviceType, device_address: str = None) -> bool:
        """指定位置にデバイスを配置"""
        if 0 <= grid_x < self.grid_cols and 0 <= grid_y < self.grid_rows:
            device = self.grid[grid_y][grid_x]
            device.device_type = device_type
            device.device_address = device_address
            device.grid_x = grid_x
            device.grid_y = grid_y
            return True
        return False
    
    def get_device(self, grid_x: int, grid_y: int) -> Optional[GridDevice]:
        """指定位置のデバイスを取得"""
        if 0 <= grid_x < self.grid_cols and 0 <= grid_y < self.grid_rows:
            return self.grid[grid_y][grid_x]
        return None
    
    def remove_device(self, grid_x: int, grid_y: int) -> bool:
        """指定位置のデバイスを削除"""
        if 0 <= grid_x < self.grid_cols and 0 <= grid_y < self.grid_rows:
            device = self.grid[grid_y][grid_x]
            device.device_type = DeviceType.EMPTY
            device.device_address = None
            device.active = False
            return True
        return False
    
    def update_all_devices(self, device_manager):
        """全デバイスの状態を更新"""
        for row in self.grid:
            for device in row:
                if device.device_type != DeviceType.EMPTY:
                    device.update_state(device_manager)
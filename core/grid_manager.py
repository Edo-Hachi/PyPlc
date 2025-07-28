"""
PyPlc-v2 Grid Device Manager
10x10グリッドデバイス管理システム
"""

from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from core.constants import DeviceType, GridConstraints
from core.config_manager import PyPlcConfig
from core.logic_element import LogicElement, create_logic_element, validate_connection_compatibility


@dataclass
class GridPosition:
    """Grid position helper / グリッド位置ヘルパー"""
    row: int
    col: int
    
    def __post_init__(self):
        if self.row < 0 or self.col < 0:
            raise ValueError(f"Grid position must be non-negative: ({self.row}, {self.col})")
    
    def to_tuple(self) -> Tuple[int, int]:
        return (self.row, self.col)
    
    def to_id(self) -> str:
        return f"{self.row:03d}_{self.col:03d}"


class GridDeviceManager:
    """
    10x10グリッドデバイス管理クラス
    Grid device management for 10x10 matrix
    """
    
    def __init__(self, config: PyPlcConfig):
        """Initialize grid manager / グリッドマネージャー初期化"""
        self.config = config
        self.grid_rows = config.grid_rows
        self.grid_cols = config.grid_cols
        
        # Initialize empty grid / 空グリッド初期化
        self.grid: List[List[Optional[LogicElement]]] = [
            [None for _ in range(self.grid_cols)] 
            for _ in range(self.grid_rows)
        ]
        
        # Device lookup by ID / IDによるデバイス検索
        self.devices: Dict[str, LogicElement] = {}
        
        # Initialize with bus devices / バスデバイス初期化
        self._initialize_bus_devices()
    
    def _initialize_bus_devices(self) -> None:
        """Initialize left and right bus devices / 左右バスデバイス初期化"""
        for row in range(self.grid_rows):
            # Left bus (L_SIDE) / 左バス
            left_bus = create_logic_element(row, 0, DeviceType.L_SIDE, f"L{row:03d}")
            self._place_device_internal(left_bus)
            
            # Right bus (R_SIDE) / 右バス
            right_col = self.grid_cols - 1
            right_bus = create_logic_element(row, right_col, DeviceType.R_SIDE, f"R{row:03d}")
            self._place_device_internal(right_bus)
    
    def _place_device_internal(self, device: LogicElement) -> None:
        """Internal device placement without validation / バリデーションなしの内部デバイス配置"""
        self.grid[device.grid_row][device.grid_col] = device
        self.devices[device.id] = device
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is valid / 位置が有効かチェック"""
        return (0 <= row < self.grid_rows and 
                0 <= col < self.grid_cols)
    
    def is_position_empty(self, row: int, col: int) -> bool:
        """Check if position is empty / 位置が空かチェック"""
        if not self.is_valid_position(row, col):
            return False
        return self.grid[row][col] is None
    
    def can_place_device(self, row: int, col: int, device_type: DeviceType) -> bool:
        """Check if device can be placed at position / 位置にデバイス配置可能かチェック"""
        # Check basic validity / 基本妥当性チェック
        if not self.is_valid_position(row, col):
            return False
        
        # Check if position is occupied / 位置が占有されているかチェック
        if not self.is_position_empty(row, col):
            return False
        
        # Check device-specific placement rules / デバイス固有配置ルールチェック
        return GridConstraints.validate_device_placement(row, col, device_type, self.grid_cols)
    
    def place_device(self, row: int, col: int, device_type: DeviceType, name: Optional[str] = None) -> bool:
        """
        Place device at specified position / 指定位置にデバイス配置
        Returns True if successful / 成功時True
        """
        if not self.can_place_device(row, col, device_type):
            return False
        
        # Create device / デバイス作成
        device = create_logic_element(row, col, device_type, name)
        
        # Place device / デバイス配置
        self._place_device_internal(device)
        
        # Update connections / 接続更新
        self._update_device_connections(device)
        
        return True
    
    def remove_device(self, row: int, col: int) -> bool:
        """
        Remove device at specified position / 指定位置のデバイス削除
        Returns True if successful / 成功時True
        """
        if not self.is_valid_position(row, col):
            return False
        
        device = self.grid[row][col]
        if device is None:
            return False
        
        # Cannot remove bus devices / バスデバイスは削除不可
        if device.is_bus_device():
            return False
        
        # Remove connections to this device / このデバイスへの接続削除
        self._remove_device_connections(device)
        
        # Remove from grid and lookup / グリッドと検索から削除
        self.grid[row][col] = None
        del self.devices[device.id]
        
        return True
    
    def get_device(self, row: int, col: int) -> Optional[LogicElement]:
        """Get device at position / 位置のデバイス取得"""
        if not self.is_valid_position(row, col):
            return None
        return self.grid[row][col]
    
    def get_device_by_id(self, device_id: str) -> Optional[LogicElement]:
        """Get device by ID / IDでデバイス取得"""
        return self.devices.get(device_id)
    
    def get_adjacent_positions(self, row: int, col: int) -> Dict[str, Tuple[int, int]]:
        """Get adjacent positions / 隣接位置取得"""
        positions = {}
        
        # Left / 左
        if col > 0:
            positions['left'] = (row, col - 1)
        
        # Right / 右
        if col < self.grid_cols - 1:
            positions['right'] = (row, col + 1)
        
        # Up / 上
        if row > 0:
            positions['up'] = (row - 1, col)
        
        # Down / 下
        if row < self.grid_rows - 1:
            positions['down'] = (row + 1, col)
        
        return positions
    
    def get_adjacent_devices(self, row: int, col: int) -> Dict[str, Optional[LogicElement]]:
        """Get adjacent devices / 隣接デバイス取得"""
        adjacent_positions = self.get_adjacent_positions(row, col)
        adjacent_devices = {}
        
        for direction, (adj_row, adj_col) in adjacent_positions.items():
            adjacent_devices[direction] = self.get_device(adj_row, adj_col)
        
        return adjacent_devices
    
    def _update_device_connections(self, device: LogicElement) -> None:
        """Update connections for a device / デバイスの接続更新"""
        adjacent_devices = self.get_adjacent_devices(device.grid_row, device.grid_col)
        
        for direction, adjacent_device in adjacent_devices.items():
            if adjacent_device is not None:
                # Set connection from this device to adjacent / このデバイスから隣接への接続設定
                device.set_connection(direction, adjacent_device.id)
                
                # Set reverse connection from adjacent to this device / 隣接からこのデバイスへの逆接続設定
                reverse_direction = self._get_reverse_direction(direction)
                adjacent_device.set_connection(reverse_direction, device.id)
    
    def _remove_device_connections(self, device: LogicElement) -> None:
        """Remove all connections to/from a device / デバイスへの/からの全接続削除"""
        adjacent_devices = self.get_adjacent_devices(device.grid_row, device.grid_col)
        
        for direction, adjacent_device in adjacent_devices.items():
            if adjacent_device is not None:
                # Remove connection from adjacent device / 隣接デバイスから接続削除
                reverse_direction = self._get_reverse_direction(direction)
                adjacent_device.remove_connection(reverse_direction)
    
    def _get_reverse_direction(self, direction: str) -> str:
        """Get reverse direction / 逆方向取得"""
        reverse_map = {
            'left': 'right',
            'right': 'left',
            'up': 'down',
            'down': 'up'
        }
        return reverse_map.get(direction, '')
    
    def get_all_devices(self) -> List[LogicElement]:
        """Get all devices in grid / グリッド内全デバイス取得"""
        return list(self.devices.values())
    
    def get_devices_by_type(self, device_type: DeviceType) -> List[LogicElement]:
        """Get devices by type / タイプ別デバイス取得"""
        return [device for device in self.devices.values() 
                if device.device_type == device_type]
    
    def get_devices_in_row(self, row: int) -> List[LogicElement]:
        """Get all devices in a row / 行内全デバイス取得"""
        if not (0 <= row < self.grid_rows):
            return []
        
        return [device for device in self.grid[row] if device is not None]
    
    def get_devices_in_column(self, col: int) -> List[LogicElement]:
        """Get all devices in a column / 列内全デバイス取得"""
        if not (0 <= col < self.grid_cols):
            return []
        
        return [self.grid[row][col] for row in range(self.grid_rows) 
                if self.grid[row][col] is not None]
    
    def clear_grid(self) -> None:
        """Clear all non-bus devices / バス以外の全デバイス削除"""
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                device = self.grid[row][col]
                if device is not None and not device.is_bus_device():
                    self.remove_device(row, col)
    
    def reset_all_device_states(self) -> None:
        """Reset all device states / 全デバイス状態リセット"""
        for device in self.devices.values():
            device.reset_state()
        
        # Bus devices should always be powered / バスデバイスは常に通電
        for device in self.get_devices_by_type(DeviceType.L_SIDE):
            device.powered = True
            device.active = True
    
    def validate_grid_integrity(self) -> bool:
        """Validate grid integrity / グリッド整合性検証"""
        for device in self.devices.values():
            # Check if device is in correct grid position / デバイスが正しいグリッド位置にあるかチェック
            grid_device = self.grid[device.grid_row][device.grid_col]
            if grid_device != device:
                return False
            
            # Check bidirectional connections / 双方向接続チェック
            for direction, connected_id in device.get_connections().items():
                if connected_id is not None:
                    connected_device = self.get_device_by_id(connected_id)
                    if connected_device is None:
                        return False
                    
                    # Check reverse connection / 逆接続チェック
                    reverse_direction = self._get_reverse_direction(direction)
                    reverse_connection = connected_device.get_connections().get(reverse_direction)
                    if reverse_connection != device.id:
                        return False
        
        return True
    
    def get_grid_size(self) -> Tuple[int, int]:
        """Get grid size / グリッドサイズ取得"""
        return (self.grid_rows, self.grid_cols)
    
    def resize_grid(self, new_rows: int, new_cols: int) -> bool:
        """
        Resize grid (experimental) / グリッドリサイズ（実験的）
        Returns True if successful / 成功時True
        """
        if new_rows < 3 or new_cols < 3:
            return False
        
        # Save current devices in editable area / 編集可能エリアの現在デバイス保存
        saved_devices = []
        for row in range(1, min(self.grid_rows - 1, new_rows - 1)):
            for col in range(1, min(self.grid_cols - 1, new_cols - 1)):
                device = self.grid[row][col]
                if device is not None and not device.is_bus_device():
                    saved_devices.append(device)
        
        # Update grid size / グリッドサイズ更新
        self.grid_rows = new_rows
        self.grid_cols = new_cols
        
        # Recreate grid / グリッド再作成
        self.grid = [
            [None for _ in range(self.grid_cols)] 
            for _ in range(self.grid_rows)
        ]
        self.devices.clear()
        
        # Reinitialize bus devices / バスデバイス再初期化
        self._initialize_bus_devices()
        
        # Restore saved devices / 保存デバイス復元
        for device in saved_devices:
            if (device.grid_row < new_rows - 1 and 
                device.grid_col < new_cols - 1):
                self._place_device_internal(device)
                self._update_device_connections(device)
        
        return True
    
    def __str__(self) -> str:
        """String representation / 文字列表現"""
        device_count = len(self.devices)
        return f"GridDeviceManager({self.grid_rows}x{self.grid_cols}, {device_count} devices)"
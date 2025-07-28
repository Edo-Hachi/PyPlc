"""
PyPlc-v2 Logic Element Module
論理素子基底クラス - 4方向接続システム
"""

from typing import Optional
from dataclasses import dataclass
from core.constants import DeviceType


@dataclass
class LogicElement:
    """
    統一デバイス表現 - すべてのPLCデバイスの基底クラス
    Unified device representation - Base class for all PLC devices
    """
    
    # Basic Info / 基本情報
    id: str                           # "ROW_COL" format (e.g., "003_005") / "行_列"形式
    name: str                         # User-visible name (e.g., "X001", "Y010") / ユーザー表示名
    device_type: DeviceType           # Device type from enum / デバイス種別
    grid_row: int                     # Row coordinate (0-based) / 行座標
    grid_col: int                     # Column coordinate (0-based) / 列座標
    
    # Connection (Bidirectional) / 接続（双方向）
    left_dev: Optional[str] = None    # Left device ID / 左デバイスID
    right_dev: Optional[str] = None   # Right device ID / 右デバイスID
    up_dev: Optional[str] = None      # Upper device ID / 上デバイスID
    down_dev: Optional[str] = None    # Lower device ID / 下デバイスID
    
    # State / 状態
    powered: bool = False             # Power state (electrical) / 通電状態（電気的）
    active: bool = False              # Operation state (logical) / 動作状態（論理的）
    
    # Device-specific Properties / デバイス固有プロパティ
    timer_preset: float = 3.0         # Timer preset value (seconds) / タイマープリセット値
    timer_current: float = 0.0        # Timer current value / タイマー現在値
    counter_preset: int = 5           # Counter preset value / カウンタープリセット値
    counter_current: int = 0          # Counter current value / カウンター現在値
    
    def __post_init__(self):
        """Post-initialization validation / 初期化後バリデーション"""
        self._validate_coordinates()
        self._validate_device_type()
    
    def _validate_coordinates(self) -> None:
        """Validate grid coordinates / グリッド座標検証"""
        if self.grid_row < 0 or self.grid_col < 0:
            raise ValueError(f"Grid coordinates must be non-negative: ({self.grid_row}, {self.grid_col})")
    
    def _validate_device_type(self) -> None:
        """Validate device type / デバイス種別検証"""
        if not isinstance(self.device_type, DeviceType):
            raise ValueError(f"Invalid device type: {self.device_type}")
    
    def get_position(self) -> tuple[int, int]:
        """Get grid position as tuple / グリッド位置をタプルで取得"""
        return (self.grid_row, self.grid_col)
    
    def get_connections(self) -> dict[str, Optional[str]]:
        """Get all connections as dictionary / 全接続を辞書で取得"""
        return {
            'left': self.left_dev,
            'right': self.right_dev,
            'up': self.up_dev,
            'down': self.down_dev
        }
    
    def set_connection(self, direction: str, device_id: Optional[str]) -> None:
        """Set connection in specified direction / 指定方向の接続設定"""
        direction = direction.lower()
        
        if direction == 'left':
            self.left_dev = device_id
        elif direction == 'right':
            self.right_dev = device_id
        elif direction == 'up':
            self.up_dev = device_id
        elif direction == 'down':
            self.down_dev = device_id
        else:
            raise ValueError(f"Invalid direction: {direction}")
    
    def remove_connection(self, direction: str) -> None:
        """Remove connection in specified direction / 指定方向の接続削除"""
        self.set_connection(direction, None)
    
    def has_connection(self, direction: str) -> bool:
        """Check if connection exists in direction / 指定方向に接続があるかチェック"""
        connections = self.get_connections()
        return connections.get(direction.lower()) is not None
    
    def get_connected_device_ids(self) -> list[str]:
        """Get list of all connected device IDs / 接続された全デバイスIDのリスト取得"""
        connections = self.get_connections()
        return [dev_id for dev_id in connections.values() if dev_id is not None]
    
    def is_bus_device(self) -> bool:
        """Check if this is a bus device / バスデバイスかチェック"""
        return self.device_type in [DeviceType.L_SIDE, DeviceType.R_SIDE]
    
    def is_contact_device(self) -> bool:
        """Check if this is a contact device / 接点デバイスかチェック"""
        return self.device_type in [DeviceType.CONTACT_A, DeviceType.CONTACT_B]
    
    def is_coil_device(self) -> bool:
        """Check if this is a coil device / コイルデバイスかチェック"""
        return self.device_type in [DeviceType.COIL, DeviceType.INCOIL, DeviceType.OUTCOIL_REV]
    
    def is_function_device(self) -> bool:
        """Check if this is a function device / 機能デバイスかチェック"""
        return self.device_type in [DeviceType.TIMER, DeviceType.COUNTER]
    
    def is_wire_device(self) -> bool:
        """Check if this is a wire device / 配線デバイスかチェック"""
        return self.device_type in [DeviceType.WIRE_H, DeviceType.WIRE_V, DeviceType.LINK_UP, DeviceType.LINK_DOWN]
    
    def reset_state(self) -> None:
        """Reset device state to initial values / デバイス状態を初期値にリセット"""
        self.powered = False
        self.active = False
        self.timer_current = 0.0
        self.counter_current = 0
    
    def update_timer(self, delta_time: float) -> None:
        """Update timer state / タイマー状態更新"""
        if self.device_type == DeviceType.TIMER and self.powered:
            self.timer_current += delta_time
            self.active = self.timer_current >= self.timer_preset
        elif not self.powered:
            # Reset timer when power is removed / 電力が切れた時にタイマーリセット
            self.timer_current = 0.0
            self.active = False
    
    def update_counter(self, trigger_edge: bool) -> None:
        """Update counter state / カウンター状態更新"""
        if self.device_type == DeviceType.COUNTER and trigger_edge:
            self.counter_current += 1
            self.active = self.counter_current >= self.counter_preset
    
    def reset_counter(self) -> None:
        """Reset counter to zero / カウンターをゼロにリセット"""
        if self.device_type == DeviceType.COUNTER:
            self.counter_current = 0
            self.active = False
    
    def evaluate_logic(self) -> bool:
        """
        Evaluate device logic based on type / タイプに基づくデバイス論理評価
        Returns the output state / 出力状態を返す
        """
        if not self.powered:
            return False
        
        # Contact logic / 接点論理
        if self.device_type == DeviceType.CONTACT_A:
            return self.active  # A接点：アクティブ時通電
        elif self.device_type == DeviceType.CONTACT_B:
            return not self.active  # B接点：非アクティブ時通電
        
        # Coil logic / コイル論理
        elif self.device_type in [DeviceType.COIL, DeviceType.INCOIL]:
            self.active = True  # コイル励磁
            return True
        elif self.device_type == DeviceType.OUTCOIL_REV:
            self.active = False  # 反転コイル
            return False
        
        # Function logic / 機能論理
        elif self.device_type == DeviceType.TIMER:
            return self.active  # タイマー完了時出力
        elif self.device_type == DeviceType.COUNTER:
            return self.active  # カウンター完了時出力
        
        # Wire logic / 配線論理
        elif self.is_wire_device():
            return True  # 配線は常に通電
        
        # Bus logic / バス論理
        elif self.device_type == DeviceType.L_SIDE:
            return True  # 左バスは常に通電
        elif self.device_type == DeviceType.R_SIDE:
            return False  # 右バスは電力吸収
        
        return False
    
    def __str__(self) -> str:
        """String representation / 文字列表現"""
        connection_count = len(self.get_connected_device_ids())
        state_str = f"powered={self.powered}, active={self.active}"
        return f"LogicElement({self.name}@{self.grid_row},{self.grid_col}, {self.device_type.value}, connections={connection_count}, {state_str})"
    
    def __repr__(self) -> str:
        """Detailed representation / 詳細表現"""
        return self.__str__()


def create_logic_element(
    row: int, 
    col: int, 
    device_type: DeviceType, 
    name: Optional[str] = None
) -> LogicElement:
    """
    Factory function for creating LogicElement instances
    LogicElementインスタンス生成用ファクトリ関数
    """
    # Generate ID from coordinates / 座標からID生成
    element_id = f"{row:03d}_{col:03d}"
    
    # Auto-generate name if not provided / 名前が未指定なら自動生成
    if name is None:
        if device_type in [DeviceType.CONTACT_A, DeviceType.CONTACT_B]:
            name = f"X{row:03d}"
        elif device_type in [DeviceType.COIL, DeviceType.INCOIL, DeviceType.OUTCOIL_REV]:
            name = f"Y{col:03d}"
        elif device_type == DeviceType.TIMER:
            name = f"T{row:03d}"
        elif device_type == DeviceType.COUNTER:
            name = f"C{row:03d}"
        else:
            name = f"{device_type.value}_{element_id}"
    
    return LogicElement(
        id=element_id,
        name=name,
        device_type=device_type,
        grid_row=row,
        grid_col=col
    )


def validate_connection_compatibility(
    device1: LogicElement, 
    device2: LogicElement, 
    direction: str
) -> bool:
    """
    Validate if two devices can be connected
    2つのデバイスが接続可能かバリデーション
    """
    # Check grid adjacency / グリッド隣接チェック
    row_diff = abs(device1.grid_row - device2.grid_row)
    col_diff = abs(device1.grid_col - device2.grid_col)
    
    if direction.lower() in ['left', 'right']:
        # Horizontal connection / 水平接続
        return row_diff == 0 and col_diff == 1
    elif direction.lower() in ['up', 'down']:
        # Vertical connection / 垂直接続
        return row_diff == 1 and col_diff == 0
    
    return False
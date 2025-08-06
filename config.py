"""
PyPlc Ver3 Configuration Module
Ver3 Configuration Constants, Constraints, and Definition Management
PLC Standard Specification Compliant System Configuration
"""

from enum import Enum


# =============================================================================
# Display Configuration  
# =============================================================================
class DisplayConfig:
    """Display Configuration Constants"""
    WINDOW_WIDTH: int = 384
    WINDOW_HEIGHT: int = 384
    TARGET_FPS: int = 30  # Ver3: 30FPSで十分


# =============================================================================
# Grid Configuration
# =============================================================================
class GridConfig:
    """Grid Configuration Constants"""
    GRID_ROWS: int = 15
    GRID_COLS: int = 20
    GRID_CELL_SIZE: int = 16
    
    # Grid display area
    GRID_ORIGIN_X: int = 16
    GRID_ORIGIN_Y: int = 80


# =============================================================================
# UI Configuration
# =============================================================================
class UIConfig:
    """UI Configuration Constants"""
    # Palette settings
    PALETTE_Y: int = 12
    
    # Status display area
    STATUS_AREA_Y: int = 280
    CONTROL_INFO_Y: int = 300
    
    # マウス操作
    SNAP_THRESHOLD: float = 7.0 # Threshold for mouse-to-grid snap processing


# =============================================================================
# UI Behavior Configuration
# =============================================================================
class UIBehaviorConfig:
    """UI Behavior Configuration Constants"""
    # Snap mode control settings
    ALWAYS_SNAP_MODE: bool = True  # True: Always snap mode, False: CTRL toggle mode
    
    # Future feature expansion settings
    SHOW_GRID_LINES: bool = True    # Grid line display ON/OFF
    SHOW_DEBUG_INFO: bool = False   # Debug info display ON/OFF


# =============================================================================
# Color Configuration
# =============================================================================
# Note: Use pyxel.COLOR_xxx directly during rendering
# Do not redefine, specify directly in code


# =============================================================================
# PLC Configuration
# =============================================================================
class PLCConfig:
    """PLC Operation Configuration Constants"""
    # Scan time settings
    DEFAULT_SCAN_TIME_MS: int = 100
    MIN_SCAN_TIME_MS: int = 50
    MAX_SCAN_TIME_MS: int = 500
    
    # Device settings
    MAX_DEVICES: int = 100
    AUTO_GENERATE_ADDRESS: bool = True
    
    # デフォルトプリセット値
    DEFAULT_TIMER_PRESET: float = 3.0
    DEFAULT_COUNTER_PRESET: int = 5


# =============================================================================
# Grid Constraints (Ver3 PLC Standard Compliant)
# =============================================================================
class GridConstraints:
    """Grid Placement Constraint Management"""
    
    @staticmethod
    def get_left_bus_col() -> int:
        """左バス列取得（常に0列目）- 電源バス"""
        return 0
    
    @staticmethod
    def get_right_bus_col() -> int:
        """右バス列取得（常に最終列）- ニュートラルバス"""
        return GridConfig.GRID_COLS - 1
    
    @staticmethod
    def is_editable_position(row: int, col: int) -> bool:
        """Editable Position Check"""
        # All rows editable, columns 1 to (cols-2) only editable
        return 1 <= col <= GridConfig.GRID_COLS - 2
    
    @staticmethod
    def get_editable_area() -> tuple[int, int, int, int]:
        """Get Editable Area (start_col, end_col, start_row, end_row)"""
        return (1, GridConfig.GRID_COLS - 2, 0, GridConfig.GRID_ROWS - 1)


# =============================================================================
# Device Type Definition (Ver3: PLC Standard Compliant)
# =============================================================================
class DeviceType(Enum):
    """Device Type Definition - PLC Standard Specification Compliant"""
    
    # Basic states
    EMPTY = "EMPTY"
    
    # バスシステム
    L_SIDE = "L_SIDE"          # 電源バス（左側）
    R_SIDE = "R_SIDE"          # ニュートラルバス（右側）
    
    # Contact series (PLC standard: input condition representation)
    CONTACT_A = "CONTACT_A"    # A接点（ノーマルオープン）-| |-
    CONTACT_B = "CONTACT_B"    # B接点（ノーマルクローズ）-|/|-
    
    # Coil series (PLC standard: output result representation)
    COIL_STD = "COIL_STD"      # Standard coil -( )-
    COIL_REV = "COIL_REV"      # 反転コイル -(/)-
    
    # Function series
    TIMER = "TIMER"            # タイマー
    COUNTER = "COUNTER"        # カウンター
    
    # 配線系（Ver3: 明示的配線システム）
    LINK_HORZ = "LINK_HORZ"    # Horizontal wiring (Ver3 new feature: essential for self-holding circuits)
    LINK_BRANCH = "LINK_BRANCH" # 分岐点（右・上・下の3方向分配）
    LINK_VIRT = "LINK_VIRT"           # 垂直配線（上下双方向伝播）
    
    # システム
    DEL = "DEL"                # 削除


# =============================================================================
# Simulator Mode Definition (Ver3: Edit/Run Mode System)
# =============================================================================
class SimulatorMode(Enum):
    """Simulator Mode Definition - Inheriting Ver1's Excellent Design"""
    EDIT = "EDIT"              # Circuit construction mode (device placement/editing enabled)
    RUN = "RUN"                # Simulation execution mode (editing locked, PLC operation)


class PLCRunState(Enum):
    """PLC Execution State Definition - Controlled by F5 Key"""
    STOPPED = "STOPPED"        # Stopped (editing enabled state)
    RUNNING = "RUNNING"        # Running (real-time circuit analysis)


# =============================================================================
# Device Palette Definitions (Ver3: Order changeable/editable)
# =============================================================================

# Device Palette Definition - Changing this order changes screen layout
DEVICE_PALETTE_DEFINITIONS = {
    # Upper row device definition (normal operation, no Shift)
    "top_row": [
        # (device_type, display_name, key_bind, description)
        (DeviceType.CONTACT_A, "A_CNTC", 1, "A接点"),
        (DeviceType.CONTACT_B, "B_CNTC", 2, "B接点"),
        (DeviceType.COIL_STD, "COIL_S", 3, "Standard Coil"),
        (DeviceType.COIL_REV, "COIL_R", 4, "反転コイル"),
        (DeviceType.LINK_HORZ, "LINK -", 5, "水平配線"),
        (DeviceType.LINK_BRANCH, "BRANCH", 6, "リンクブランチポイント"),
        (DeviceType.EMPTY, "", 7, "未定義"),
        (DeviceType.LINK_VIRT, "LINK |", 8, "垂直配線"),
        (DeviceType.EMPTY, "", 9, "未定義"),
        (DeviceType.DEL, "DELETE", 0, "削除コマンド"),
    ],
    
    # Lower row device definition (extended operation, Shift+key) for future expansion
    "bottom_row": [
        (DeviceType.EMPTY, "", 1, "Undefined (Timer planned)"),
        (DeviceType.EMPTY, "", 2, "Undefined (Counter planned)"),
        (DeviceType.EMPTY, "", 3, "Undefined"),
        (DeviceType.EMPTY, "", 4, "未定義"),
        (DeviceType.EMPTY, "", 5, "未定義"),
        (DeviceType.EMPTY, "", 6, "未定義"),
        (DeviceType.EMPTY, "", 7, "未定義"),
        (DeviceType.EMPTY, "", 8, "未定義"),
        (DeviceType.EMPTY, "", 9, "未定義"),
        (DeviceType.EMPTY, "", 0, "未定義"),
    ]
}

# パレットレイアウト設定
PALETTE_LAYOUT_CONFIG = {
    "device_width": 28,      # デバイス表示幅
    "device_height": 10,     # デバイス表示高さ
    "row_spacing": 3,       # 行間隔
    "palette_x": 16,         # パレット開始X座標
    "palette_y": 12,         # パレット開始Y座標
}


# =============================================================================
# Device Address Ranges
# =============================================================================
class DeviceAddressRanges:
    """デバイスアドレス範囲定義"""
    
    # 入力デバイス
    X_MIN: int = 0
    X_MAX: int = 377
    
    # 出力デバイス
    Y_MIN: int = 0
    Y_MAX: int = 377
    
    # 内部リレー
    M_MIN: int = 0
    M_MAX: int = 7999
    
    # タイマー
    T_MIN: int = 0
    T_MAX: int = 255
    
    # カウンター
    C_MIN: int = 0
    C_MAX: int = 255
    
    # データレジスタ
    D_MIN: int = 0
    D_MAX: int = 7999
    
    @staticmethod
    def validate_address(device_type: str, address_num: int) -> bool:
        """アドレス範囲妥当性チェック"""
        ranges = {
            'X': (DeviceAddressRanges.X_MIN, DeviceAddressRanges.X_MAX),
            'Y': (DeviceAddressRanges.Y_MIN, DeviceAddressRanges.Y_MAX),
            'M': (DeviceAddressRanges.M_MIN, DeviceAddressRanges.M_MAX),
            'T': (DeviceAddressRanges.T_MIN, DeviceAddressRanges.T_MAX),
            'C': (DeviceAddressRanges.C_MIN, DeviceAddressRanges.C_MAX),
            'D': (DeviceAddressRanges.D_MIN, DeviceAddressRanges.D_MAX),
        }
        
        if device_type not in ranges:
            return False
        
        min_val, max_val = ranges[device_type]
        return min_val <= address_num <= max_val
    
    @staticmethod
    def format_device_address(device_type: str, address_num: int) -> str:
        """デバイスアドレスフォーマット"""
        if not DeviceAddressRanges.validate_address(device_type, address_num):
            return ""
        
        # 3桁ゼロパディング
        return f"{device_type}{address_num:03d}"


# =============================================================================
# Ver3システム情報
# =============================================================================
class SystemInfo:
    """Ver3システム情報"""
    VERSION: str = "3.0"
    BUILD_DATE: str = "2025-01-28"
    DESCRIPTION: str = "PLC標準仕様完全準拠ラダー図シミュレーター"
    
    # Ver2からの主要変更点
    MAJOR_CHANGES = [
        "PLC標準準拠のデバイス体系",
        "明示的配線システム（LINK_HORZ）",
        "接点/コイル概念の正しい実装",
        "30FPS最適化",
    ]
"""
PyPlc Ver3 Configuration Module
Ver3 Configuration Constants, Constraints, and Definition Management
PLC Standard Specification Compliant System Configuration
"""

from enum import Enum
import pyxel


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

class DialogConfig:
    """Dialog System Configuration Constants"""
    # Device ID input dialog settings
    MAX_DEVICE_ID_LENGTH: int = 8  # Maximum input length for device IDs


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
    
    # Function series (PLC standard timer/counter)
    TIMER_TON = "TIMER_TON"    # Timer ON-Delay (TON)
    COUNTER_CTU = "COUNTER_CTU" # Counter UP (CTU)
    RST = "RST"               # Reset command (Mitsubishi RST)
    ZRST = "ZRST"             # Range Reset command (Mitsubishi ZRST)
    
    # Data series (PLC standard data handling)
    DATA_REGISTER = "DATA_REGISTER"    # データレジスタ（Dデバイス）
    COMPARE_DEVICE = "COMPARE_DEVICE"  # 比較演算子デバイス
    
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
        (DeviceType.CONTACT_A, "A_CNTC", 1, "Contact_A"),
        (DeviceType.CONTACT_B, "B_CNTC", 2, "Contact_B"),
        (DeviceType.COIL_STD, "COIL_S", 3, "Standard Coil"),
        (DeviceType.COIL_REV, "COIL_R", 4, "Reverse Coil"),
        (DeviceType.EMPTY, "", 5, "UNDEF"),
        (DeviceType.LINK_HORZ, "LINK -", 6, "Horizontal Link"),
        (DeviceType.LINK_VIRT, "LINK |", 7, "Virtical Link"),
        (DeviceType.LINK_BRANCH, "BRANCH", 8, "Branch Link"),
        (DeviceType.EMPTY, "", 9, "UNDEF"),
        (DeviceType.DEL, "DELETE", 0, "Delete Command"),
    ],
    
    # Lower row device definition (extended operation, Shift+key) 
    "bottom_row": [
        (DeviceType.TIMER_TON, "TIMER", 1, "Timer ON-Delay"),
        (DeviceType.COUNTER_CTU, "COUNT", 2, "Counter UP"),
        (DeviceType.RST, "RESET", 3, "Reset Command"),
        (DeviceType.ZRST, "ZRST", 4, "Range Reset Command"),
        (DeviceType.EMPTY, "", 5, "UNDEF"),
        (DeviceType.DATA_REGISTER, "D_DEV", 6, "Data Register"),
        (DeviceType.COMPARE_DEVICE, "COMP", 7, "Compare Device"),
        (DeviceType.EMPTY, "", 8, "UNDEF"),
        (DeviceType.EMPTY, "", 9, "UNDEF"),
        (DeviceType.EMPTY, "", 0, "UNDEF"),
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
# Timer/Counter Configuration (PLC Standard)
# =============================================================================
class TimerConfig:
    """タイマー設定定数（PLC標準準拠 - 1ms単位）"""
    MIN_PRESET = 0         # 最小プリセット値（0ms）
    MAX_PRESET = 32767     # 最大プリセット値（32767ms = 32.767秒）
    TIME_UNIT = 1          # 時間単位（1ms）
    DEFAULT_PRESET = 1000  # デフォルトプリセット値（1000ms = 1.0秒）
    FRAME_THRESHOLD = 990  # 990ms超過で1秒完了判定（30FPS対応）

class CounterConfig:
    """カウンター設定定数（PLC標準準拠）"""
    MIN_PRESET = 0         # 最小プリセット値
    MAX_PRESET = 65535     # 最大プリセット値（16bit符号なし）
    DEFAULT_PRESET = 10    # デフォルトプリセット値

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
    BUILD_DATE: str = "2025-06-28"
    DESCRIPTION: str = "PLC 標準仕様完全準拠ラダー図シミュレーター"
    
    # Ver2からの主要変更点
    MAJOR_CHANGES = [
        "PLC標準準拠のデバイス体系",
        "明示的配線システム（LINK_HORZ）",
        "接点/コイル概念の正しい実装",
        "30FPS最適化",
    ]


# =============================================================================
# DropdownControl Configuration (WindSurf改善組み込み版)
# =============================================================================
class DropdownControlConfig:
    """ドロップダウンコントロール設定（WindSurf提案）"""
    
    # デフォルトサイズ
    DEFAULT_WIDTH = 200
    DEFAULT_HEIGHT = 25
    DEFAULT_ITEM_HEIGHT = 20
    
    # 色設定（テーマ対応準備）
    BACKGROUND_COLOR = pyxel.COLOR_DARK_BLUE
    BORDER_COLOR = pyxel.COLOR_WHITE
    TEXT_COLOR = pyxel.COLOR_WHITE
    HOVER_COLOR = pyxel.COLOR_GRAY
    SELECTED_COLOR = pyxel.COLOR_DARK_BLUE
    ERROR_COLOR = pyxel.COLOR_RED
    
    # UI設定
    MAX_VISIBLE_ITEMS = 5
    TEXT_PADDING = 4
    DROPDOWN_ICON = "▼"
    DROPUP_ICON = "▲"


# =============================================================================
# Data Operation Configuration (データ演算機能)
# =============================================================================
class DataOperationConfig:
    """データレジスタ演算機能設定"""
    
    # デフォルト値
    DEFAULT_OPERATION = "MOV"
    DEFAULT_OPERAND = 0
    
    # データ値範囲（16bit符号付き整数）
    MAX_DATA_VALUE = 32767
    MIN_DATA_VALUE = -32768
    
    # 演算タイプ定義（ドロップダウン用）
    OPERATION_OPTIONS = [
        {"value": "MOV", "label": "MOV - Data Transfer"},
        {"value": "ADD", "label": "ADD - Addition"},
        {"value": "SUB", "label": "SUB - Subtraction"},  
        {"value": "MUL", "label": "MUL - Multiplication"},
        {"value": "DIV", "label": "DIV - Division"}
    ]
    
    # 演算エラーメッセージ
    ERROR_MESSAGES = {
        "OVERFLOW": "Value overflow",
        "UNDERFLOW": "Value underflow", 
        "DIV_BY_ZERO": "Division by zero",
        "INVALID_OPERAND": "Invalid operand value"
    }
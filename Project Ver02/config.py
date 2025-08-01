"""
PyPlc-v2 Configuration Module
設定定数・制約・定義管理
"""

from enum import Enum


# =============================================================================
# Grid Configuration
# =============================================================================
class GridConfig:
    """グリッド設定定数"""
    GRID_ROWS = 15
    GRID_COLS = 20
    GRID_CELL_SIZE = 16


# =============================================================================
# Display Configuration  
# =============================================================================
class DisplayConfig:
    """表示設定定数"""
    WINDOW_WIDTH = 384
    WINDOW_HEIGHT = 384
    GRID_ORIGIN_X = 16
    GRID_ORIGIN_Y = 80


# =============================================================================
# Device Configuration
# =============================================================================
class DeviceConfig:
    """デバイス設定定数"""
    AUTO_GENERATE_ADDRESS = True
    DEFAULT_TIMER_PRESET = 3.0
    DEFAULT_COUNTER_PRESET = 5


# =============================================================================
# UI Configuration
# =============================================================================
class UIConfig:
    """UI設定定数"""
    PALETTE_Y = 12
    STATUS_AREA_Y = 280
    CONTROL_INFO_Y = 300
    SNAP_THRESHOLD = 7.0


# =============================================================================
# Performance Configuration
# =============================================================================
class PerformanceConfig:
    """パフォーマンス設定定数"""
    TARGET_FPS = 60
    MAX_DEVICES = 100
    SCAN_TIME_MS = 100


# =============================================================================
# Grid Constraints
# =============================================================================
class GridConstraints:
    """グリッド配置制約管理"""
    
    @staticmethod
    def get_left_bus_col() -> int:
        """左バス列取得（常に0列目）"""
        return 0
    
    @staticmethod
    def get_right_bus_col() -> int:
        """右バス列取得（常に最終列）"""
        return GridConfig.GRID_COLS - 1
    
    @staticmethod
    def is_editable_position(row: int, col: int) -> bool:
        """編集可能位置判定"""
        # 行は全て編集可能、列は1〜(cols-2)のみ編集可能
        return 1 <= col <= GridConfig.GRID_COLS - 2
    
    @staticmethod
    def validate_device_placement(row: int, col: int, device_type: 'DeviceType') -> bool:
        """デバイス配置妥当性検証"""
        # L_SIDEは0列目のみ
        if device_type == DeviceType.L_SIDE:
            return col == 0
        
        # R_SIDEは最終列のみ
        if device_type == DeviceType.R_SIDE:
            return col == GridConfig.GRID_COLS - 1
        
        # その他のデバイスは編集可能領域のみ
        if device_type not in [DeviceType.L_SIDE, DeviceType.R_SIDE]:
            return GridConstraints.is_editable_position(row, col)
        
        return False
    
    @staticmethod
    def get_editable_area() -> tuple[int, int, int, int]:
        """編集可能領域取得 (start_col, end_col, start_row, end_row)"""
        return (1, GridConfig.GRID_COLS - 2, 0, GridConfig.GRID_ROWS - 1)


class DeviceType(Enum):
    """デバイス種別定義"""
    # 基本状態
    EMPTY = "EMPTY"
    
    # バスシステム
    L_SIDE = "L_SIDE"          # 電源バス（左側）
    R_SIDE = "R_SIDE"          # ニュートラルバス（右側）
    
    # 接点系
    CONTACT_A = "CONTACT_A"    # A接点（ノーマルオープン）
    CONTACT_B = "CONTACT_B"    # B接点（ノーマルクローズ）
    
    # コイル系
    COIL = "COIL"              # 出力コイル
    INCOIL = "INCOIL"          # 入力コイル
    OUTCOIL_REV = "OUTCOIL_REV"  # 反転出力コイル
    
    # 機能系
    TIMER = "TIMER"            # タイマー
    COUNTER = "COUNTER"        # カウンター
    
    # 配線系
    WIRE_H = "WIRE_H"          # 水平配線
    WIRE_V = "WIRE_V"          # 垂直配線
    LINK_UP = "LINK_UP"        # 上方向結線
    LINK_DOWN = "LINK_DOWN"    # 下方向結線
    
    # システム
    DEL = "DEL"                # 削除


class GridConstraints:
    """グリッド配置制約管理"""
    
    @staticmethod
    def get_left_bus_col() -> int:
        """左バス列取得（常に0列目）"""
        return 0
    
    @staticmethod
    def get_right_bus_col(grid_cols: int) -> int:
        """右バス列取得（常に最終列）"""
        return grid_cols - 1
    
    @staticmethod
    def is_editable_position(row: int, col: int, grid_cols: int) -> bool:
        """編集可能位置判定"""
        # 行は全て編集可能、列は1〜(cols-2)のみ編集可能
        return 1 <= col <= grid_cols - 2
    
    @staticmethod
    def validate_device_placement(row: int, col: int, device_type: DeviceType, grid_cols: int) -> bool:
        """デバイス配置妥当性検証"""
        # L_SIDEは0列目のみ
        if device_type == DeviceType.L_SIDE:
            return col == 0
        
        # R_SIDEは最終列のみ
        if device_type == DeviceType.R_SIDE:
            return col == grid_cols - 1
        
        # その他のデバイスは編集可能領域のみ
        if device_type not in [DeviceType.L_SIDE, DeviceType.R_SIDE]:
            return GridConstraints.is_editable_position(row, col, grid_cols)
        
        return False


    # class Colors:
    #     """色定義"""
    #     # 基本色
    #     BLACK = 0
    #     WHITE = 7
    #     RED = 8
    #     GREEN = 11
    #     BLUE = 12
    #     YELLOW = 10
    #     GRAY = 13
        
    #     # 機能別色
    #     BACKGROUND = BLACK
    #     GRID_LINE = GRAY
    #     POWER_ON = GREEN        # 通電状態
    #     POWER_OFF = GRAY        # 非通電状態
    #     SELECTED = YELLOW       # 選択状態
    #     ERROR = RED             # エラー状態
    #     TEXT = WHITE            # テキスト


class Layout:
    """レイアウト定数"""
    # ウィンドウサイズ
    WINDOW_WIDTH = 256
    WINDOW_HEIGHT = 256
    
    # グリッド表示領域
    GRID_ORIGIN_X = 16
    GRID_ORIGIN_Y = 32
    GRID_DISPLAY_WIDTH = 160
    GRID_DISPLAY_HEIGHT = 160
    
    # UI領域
    PALETTE_Y = 16
    STATUS_AREA_Y = 200
    CONTROL_INFO_Y = 240


class DeviceAddressRanges:
    """デバイスアドレス範囲定義"""
    
    # 入力デバイス
    X_MIN = 0
    X_MAX = 377
    
    # 出力デバイス
    Y_MIN = 0
    Y_MAX = 377
    
    # 内部リレー
    M_MIN = 0
    M_MAX = 7999
    
    # タイマー
    T_MIN = 0
    T_MAX = 255
    
    # カウンター
    C_MIN = 0
    C_MAX = 255
    
    # データレジスタ
    D_MIN = 0
    D_MAX = 7999
    
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


# シンプルな定数ベース設定 - JSONファイル不要
"""
PyPlc Ver3 Configuration Module
Ver3専用設定定数・制約・定義管理
PLC標準仕様準拠システム用設定
"""

from enum import Enum


# =============================================================================
# Display Configuration  
# =============================================================================
class DisplayConfig:
    """表示設定定数"""
    WINDOW_WIDTH: int = 384
    WINDOW_HEIGHT: int = 384
    TARGET_FPS: int = 30  # Ver3: 30FPSで十分


# =============================================================================
# Grid Configuration
# =============================================================================
class GridConfig:
    """グリッド設定定数"""
    GRID_ROWS: int = 15
    GRID_COLS: int = 20
    GRID_CELL_SIZE: int = 16
    
    # グリッド表示領域
    GRID_ORIGIN_X: int = 16
    GRID_ORIGIN_Y: int = 80


# =============================================================================
# UI Configuration
# =============================================================================
class UIConfig:
    """UI設定定数"""
    # パレット設定
    PALETTE_Y: int = 12
    
    # ステータス表示領域
    STATUS_AREA_Y: int = 280
    CONTROL_INFO_Y: int = 300
    
    # マウス操作
    SNAP_THRESHOLD: float = 7.0 #マウスとグリッド交点とのスナップ処理を行うためのしきい値


# =============================================================================
# UI Behavior Configuration
# =============================================================================
class UIBehaviorConfig:
    """UI動作設定定数"""
    # スナップモード制御設定
    ALWAYS_SNAP_MODE: bool = True  # True: 常時スナップモード, False: CTRL切り替えモード
    
    # 将来の機能拡張用設定
    SHOW_GRID_LINES: bool = True    # グリッド線表示ON/OFF
    SHOW_DEBUG_INFO: bool = False   # デバッグ情報表示ON/OFF


# =============================================================================
# Color Configuration
# =============================================================================
# 注意: 色はpyxel.COLOR_xxxを描画時に直接使用すること
# 再定義は一切行わず、コード内で直接指定する


# =============================================================================
# PLC Configuration
# =============================================================================
class PLCConfig:
    """PLC動作設定定数"""
    # スキャンタイム設定
    DEFAULT_SCAN_TIME_MS: int = 100
    MIN_SCAN_TIME_MS: int = 50
    MAX_SCAN_TIME_MS: int = 500
    
    # デバイス設定
    MAX_DEVICES: int = 100
    AUTO_GENERATE_ADDRESS: bool = True
    
    # デフォルトプリセット値
    DEFAULT_TIMER_PRESET: float = 3.0
    DEFAULT_COUNTER_PRESET: int = 5


# =============================================================================
# Grid Constraints（Ver3でPLC標準準拠）
# =============================================================================
class GridConstraints:
    """グリッド配置制約管理"""
    
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
        """編集可能位置判定"""
        # 行は全て編集可能、列は1〜(cols-2)のみ編集可能
        return 1 <= col <= GridConfig.GRID_COLS - 2
    
    @staticmethod
    def get_editable_area() -> tuple[int, int, int, int]:
        """編集可能領域取得 (start_col, end_col, start_row, end_row)"""
        return (1, GridConfig.GRID_COLS - 2, 0, GridConfig.GRID_ROWS - 1)


# =============================================================================
# Device Type Definition（Ver3: PLC標準準拠）
# =============================================================================
class DeviceType(Enum):
    """デバイス種別定義 - PLC標準仕様準拠"""
    
    # 基本状態
    EMPTY = "EMPTY"
    
    # バスシステム
    L_SIDE = "L_SIDE"          # 電源バス（左側）
    R_SIDE = "R_SIDE"          # ニュートラルバス（右側）
    
    # 接点系（PLC標準: 入力条件表現）
    CONTACT_A = "CONTACT_A"    # A接点（ノーマルオープン）-| |-
    CONTACT_B = "CONTACT_B"    # B接点（ノーマルクローズ）-|/|-
    
    # コイル系（PLC標準: 出力結果表現）
    COIL_STD = "COIL_STD"      # 標準コイル -( )-
    COIL_REV = "COIL_REV"      # 反転コイル -(/)-
    
    # 機能系
    TIMER = "TIMER"            # タイマー
    COUNTER = "COUNTER"        # カウンター
    
    # 配線系（Ver3: 明示的配線システム）
    LINK_HORZ = "LINK_HORZ"    # 水平配線（Ver3新機能: 自己保持回路に必須）
    LINK_BRANCH = "LINK_BRANCH" # 分岐点（右・上・下の3方向分配）
    LINK_VIRT = "LINK_VIRT"           # 垂直配線（上下双方向伝播）
    
    # システム
    DEL = "DEL"                # 削除


# =============================================================================
# Simulator Mode Definition（Ver3: Edit/Runモードシステム）
# =============================================================================
class SimulatorMode(Enum):
    """シミュレーターモード定義 - Ver1の優秀設計を継承"""
    EDIT = "EDIT"              # 回路構築モード（デバイス配置・編集可能）
    RUN = "RUN"                # シミュレーション実行モード（編集ロック・PLC動作）


class PLCRunState(Enum):
    """PLC実行状態定義 - F5キーで制御"""
    STOPPED = "STOPPED"        # 停止中（編集可能状態）
    RUNNING = "RUNNING"        # 実行中（リアルタイム回路解析中）


# =============================================================================
# Device Palette Definitions (Ver3: 順序変更・編集可能)
# =============================================================================

# デバイスパレット定義 - この順序を変更することで画面上の配置が変わります
DEVICE_PALETTE_DEFINITIONS = {
    # 上段デバイス定義（通常操作・Shiftなし）
    "top_row": [
        # (device_type, display_name, key_bind, description)
        (DeviceType.CONTACT_A, "A_CNTC", 1, "A接点"),
        (DeviceType.CONTACT_B, "B_CNTC", 2, "B接点"),
        (DeviceType.COIL_STD, "COIL_S", 3, "標準コイル"),
        (DeviceType.COIL_REV, "COIL_R", 4, "反転コイル"),
        (DeviceType.LINK_HORZ, "LINK -", 5, "水平配線"),
        (DeviceType.LINK_BRANCH, "BRANCH", 6, "リンクブランチポイント"),
        (DeviceType.EMPTY, "", 7, "未定義"),
        (DeviceType.LINK_VIRT, "LINK |", 8, "垂直配線"),
        (DeviceType.EMPTY, "", 9, "未定義"),
        (DeviceType.DEL, "DELETE", 0, "削除コマンド"),
    ],
    
    # 下段デバイス定義（拡張操作・Shift+キー）将来拡張用
    "bottom_row": [
        (DeviceType.EMPTY, "", 1, "未定義（タイマー予定）"),
        (DeviceType.EMPTY, "", 2, "未定義（カウンター予定）"),
        (DeviceType.EMPTY, "", 3, "未定義"),
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
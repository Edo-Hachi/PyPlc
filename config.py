"""
PyPlc-v2 Configuration Module
設定定数・制約・定義管理
"""

from typing import Optional
from enum import Enum
from dataclasses import dataclass
import json


@dataclass
class PyPlcConfig:
    """PyPlc設定クラス - PyPlc.jsonの完全管理"""
    # グリッド設定
    grid_rows: int = 10
    grid_cols: int = 10
    grid_cell_size: int = 16
    
    # 表示設定
    window_width: int = 256
    window_height: int = 256
    grid_origin_x: int = 16
    grid_origin_y: int = 32
    
    # デバイス設定
    auto_generate_address: bool = True
    default_timer_preset: float = 3.0
    default_counter_preset: int = 5
    
    # UI設定
    palette_y: int = 16
    status_area_y: int = 200
    control_info_y: int = 240
    snap_threshold: float = 5.0
    
    # パフォーマンス設定
    target_fps: int = 60
    max_devices: int = 100
    
    @classmethod
    def load_from_file(cls, config_path: str = "PyPlc.json") -> 'PyPlcConfig':
        """設定ファイルから読み込み"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 各セクションからデータ抽出
            grid = data.get('grid', {})
            display = data.get('display', {})
            devices = data.get('devices', {})
            ui = data.get('ui', {})
            performance = data.get('performance', {})
            
            return cls(
                # グリッド設定
                grid_rows=grid.get('rows', 10),
                grid_cols=grid.get('cols', 10),
                grid_cell_size=grid.get('cell_size', 16),
                
                # 表示設定
                window_width=display.get('window_width', 256),
                window_height=display.get('window_height', 256),
                grid_origin_x=display.get('grid_origin_x', 16),
                grid_origin_y=display.get('grid_origin_y', 32),
                
                # デバイス設定
                auto_generate_address=devices.get('auto_generate_address', True),
                default_timer_preset=devices.get('default_timer_preset', 3.0),
                default_counter_preset=devices.get('default_counter_preset', 5),
                
                # UI設定
                palette_y=ui.get('palette_y', 16),
                status_area_y=ui.get('status_area_y', 200),
                control_info_y=ui.get('control_info_y', 240),
                snap_threshold=ui.get('snap_threshold', 5),
                
                # パフォーマンス設定
                target_fps=performance.get('target_fps', 60),
                max_devices=performance.get('max_devices', 100)
            )
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"設定ファイル読み込みエラー: {e}")
            print("デフォルト設定を使用します")
            return cls()
    
    def save_to_file(self, config_path: str = "PyPlc.json") -> bool:
        """設定ファイルに保存"""
        try:
            data = {
                "grid": {
                    "rows": self.grid_rows,
                    "cols": self.grid_cols,
                    "cell_size": self.grid_cell_size
                },
                "display": {
                    "window_width": self.window_width,
                    "window_height": self.window_height,
                    "grid_origin_x": self.grid_origin_x,
                    "grid_origin_y": self.grid_origin_y
                },
                "devices": {
                    "auto_generate_address": self.auto_generate_address,
                    "default_timer_preset": self.default_timer_preset,
                    "default_counter_preset": self.default_counter_preset
                },
                "ui": {
                    "palette_y": self.palette_y,
                    "status_area_y": self.status_area_y,
                    "control_info_y": self.control_info_y,
                    "snap_threshold": self.snap_threshold
                },
                "performance": {
                    "target_fps": self.target_fps,
                    "max_devices": self.max_devices
                }
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"設定ファイル保存完了: {config_path}")
            return True
            
        except Exception as e:
            print(f"設定ファイル保存エラー: {e}")
            return False
    
    def update_grid_size(self, rows: int, cols: int) -> bool:
        """グリッドサイズ更新（妥当性チェック付き）"""
        if rows < 3 or cols < 3:
            print("グリッドサイズは最低3x3必要です")
            return False
        
        if rows > 50 or cols > 50:
            print("グリッドサイズは最大50x50です")
            return False
        
        self.grid_rows = rows
        self.grid_cols = cols
        print(f"グリッドサイズ更新: {rows}x{cols}")
        return True
    
    def get_editable_area(self) -> tuple[int, int, int, int]:
        """編集可能領域取得 (start_col, end_col, start_row, end_row)"""
        return (1, self.grid_cols - 2, 0, self.grid_rows - 1)


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


# モジュール初期化時にグリッド設定読み込み
DEFAULT_CONFIG = PyPlcConfig.load_from_file()
"""
PyPlc Configuration Manager Module
設定管理システムを分離したモジュール

シンプルな定数ベース設定システム
"""

from typing import Optional
from dataclasses import dataclass
from core.constants import AppConstants
from config import GridConfig, DisplayConfig, DeviceConfig, UIConfig, PerformanceConfig, GridConstraints


@dataclass
class PyPlcConfig:
    """PyPlc設定クラス - シンプルな定数ベース"""
    # グリッド設定
    grid_rows: int = GridConfig.GRID_ROWS
    grid_cols: int = GridConfig.GRID_COLS
    grid_cell_size: int = GridConfig.GRID_CELL_SIZE
    
    # 表示設定
    window_width: int = DisplayConfig.WINDOW_WIDTH
    window_height: int = DisplayConfig.WINDOW_HEIGHT
    grid_origin_x: int = DisplayConfig.GRID_ORIGIN_X
    grid_origin_y: int = DisplayConfig.GRID_ORIGIN_Y
    
    # デバイス設定
    auto_generate_address: bool = DeviceConfig.AUTO_GENERATE_ADDRESS
    default_timer_preset: float = DeviceConfig.DEFAULT_TIMER_PRESET
    default_counter_preset: int = DeviceConfig.DEFAULT_COUNTER_PRESET
    
    # UI設定
    palette_y: int = UIConfig.PALETTE_Y
    status_area_y: int = UIConfig.STATUS_AREA_Y
    control_info_y: int = UIConfig.CONTROL_INFO_Y
    snap_threshold: float = UIConfig.SNAP_THRESHOLD
    
    # パフォーマンス設定
    target_fps: int = PerformanceConfig.TARGET_FPS
    max_devices: int = PerformanceConfig.MAX_DEVICES
    scan_time_ms: int = PerformanceConfig.SCAN_TIME_MS
    
    def update_grid_size(self, rows: int, cols: int) -> bool:
        """グリッドサイズ更新（妥当性チェック付き）"""
        if rows < 3 or cols < 3 or rows > 50 or cols > 50:
            return False
        
        self.grid_rows = rows
        self.grid_cols = cols
        return True
    
    def get_editable_area(self) -> tuple[int, int, int, int]:
        """編集可能領域取得 (start_col, end_col, start_row, end_row)"""
        return GridConstraints.get_editable_area()


class PyPlcConfigManager:
    """PyPlc設定管理システム - シンプル版"""
    
    def __init__(self):
        """設定管理システム初期化"""
        self._config = PyPlcConfig()
    
    def get_config(self) -> PyPlcConfig:
        """現在の設定を取得"""
        return self._config
    
    def update_grid_size(self, rows: int, cols: int) -> bool:
        """グリッドサイズ更新"""
        return self._config.update_grid_size(rows, cols)
    
    def update_scan_time(self, scan_time_ms: int) -> bool:
        """PLCスキャンタイム更新"""
        if 10 <= scan_time_ms <= 1000:
            self._config.scan_time_ms = scan_time_ms
            return True
        return False
    
    def update_snap_threshold(self, threshold: float) -> bool:
        """スナップしきい値更新"""
        if 1.0 <= threshold <= 20.0:
            self._config.snap_threshold = threshold
            return True
        return False
    
    def get_config_summary(self) -> dict:
        """設定サマリー取得"""
        return {
            'grid_size': f"{self._config.grid_rows}x{self._config.grid_cols}",
            'window_size': f"{self._config.window_width}x{self._config.window_height}",
            'scan_time_ms': self._config.scan_time_ms,
            'snap_threshold': self._config.snap_threshold,
            'max_devices': self._config.max_devices,
            'target_fps': self._config.target_fps
        }

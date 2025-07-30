"""
PyPlc Configuration Manager Module
設定管理システムを分離したモジュール

Phase 4 リファクタリング: 設定・データ管理分離
- 設定の読み込み・保存・管理
- 設定妥当性チェック
- 動的設定変更
"""

import json
from typing import Optional
from dataclasses import dataclass
from core.constants import AppConstants


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
    grid_origin_y: int = 80  # パレット用に48px下にずらす（16+32）
    
    # デバイス設定
    auto_generate_address: bool = True
    default_timer_preset: float = 3.0
    default_counter_preset: int = 5
    
    # UI設定
    palette_y: int = 12  # パレット表示開始Y座標
    status_area_y: int = 200
    control_info_y: int = 240
    snap_threshold: float = 5.0
    
    # パフォーマンス設定
    target_fps: int = 60
    max_devices: int = 100
    scan_time_ms: int = 100  # PLCスキャンタイム（ミリ秒）
    
    def update_grid_size(self, rows: int, cols: int) -> bool:
        """グリッドサイズ更新（妥当性チェック付き）"""
        if rows < 3 or cols < 3 or rows > 20 or cols > 20:
            return False
        
        self.grid_rows = rows
        self.grid_cols = cols
        return True
    
    def get_editable_area(self) -> tuple[int, int, int, int]:
        """編集可能領域取得 (start_col, end_col, start_row, end_row)"""
        return (1, self.grid_cols - 2, 0, self.grid_rows - 1)


class PyPlcConfigManager:
    """PyPlc設定管理システム"""
    
    def __init__(self, config_path: str = "PyPlc.json"):
        """
        設定管理システム初期化
        
        Args:
            config_path: 設定ファイルパス
        """
        self.config_path = config_path
        self._config: Optional[PyPlcConfig] = None
        self._load_config()
    
    def _load_config(self) -> None:
        """設定ファイルから読み込み（内部用）"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 各セクションからデータ抽出
            grid = data.get('grid', {})
            display = data.get('display', {})
            devices = data.get('devices', {})
            ui = data.get('ui', {})
            performance = data.get('performance', {})
            
            self._config = PyPlcConfig(
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
                snap_threshold=ui.get('snap_threshold', 5.0),
                
                # パフォーマンス設定
                target_fps=performance.get('target_fps', AppConstants.TARGET_FPS),
                max_devices=performance.get('max_devices', AppConstants.MAX_DEVICES),
                scan_time_ms=performance.get('scan_time_ms', AppConstants.DEFAULT_SCAN_TIME_MS)
            )
            
            print(f"設定ファイル読み込み完了: {self.config_path}")
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"設定ファイル読み込みエラー: {e}")
            print("デフォルト設定を使用します")
            self._config = PyPlcConfig()
    
    def get_config(self) -> PyPlcConfig:
        """現在の設定を取得"""
        if self._config is None:
            self._load_config()
        return self._config
    
    def save_config(self) -> bool:
        """設定ファイルに保存"""
        if self._config is None:
            return False
        
        try:
            data = {
                "grid": {
                    "rows": self._config.grid_rows,
                    "cols": self._config.grid_cols,
                    "cell_size": self._config.grid_cell_size
                },
                "display": {
                    "window_width": self._config.window_width,
                    "window_height": self._config.window_height,
                    "grid_origin_x": self._config.grid_origin_x,
                    "grid_origin_y": self._config.grid_origin_y
                },
                "devices": {
                    "auto_generate_address": self._config.auto_generate_address,
                    "default_timer_preset": self._config.default_timer_preset,
                    "default_counter_preset": self._config.default_counter_preset
                },
                "ui": {
                    "palette_y": self._config.palette_y,
                    "status_area_y": self._config.status_area_y,
                    "control_info_y": self._config.control_info_y,
                    "snap_threshold": self._config.snap_threshold
                },
                "performance": {
                    "target_fps": self._config.target_fps,
                    "max_devices": self._config.max_devices,
                    "scan_time_ms": self._config.scan_time_ms
                }
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"設定ファイル保存完了: {self.config_path}")
            return True
            
        except Exception as e:
            print(f"設定ファイル保存エラー: {e}")
            return False
    
    def reload_config(self) -> None:
        """設定ファイルを再読み込み"""
        self._load_config()
    
    def update_grid_size(self, rows: int, cols: int) -> bool:
        """グリッドサイズ更新"""
        if self._config is None:
            return False
        
        if self._config.update_grid_size(rows, cols):
            return self.save_config()
        return False
    
    def update_scan_time(self, scan_time_ms: int) -> bool:
        """PLCスキャンタイム更新"""
        if self._config is None:
            return False
        
        if 10 <= scan_time_ms <= 1000:  # 10ms〜1000msの範囲
            self._config.scan_time_ms = scan_time_ms
            return self.save_config()
        return False
    
    def update_snap_threshold(self, threshold: float) -> bool:
        """スナップしきい値更新"""
        if self._config is None:
            return False
        
        if 1.0 <= threshold <= 20.0:  # 1.0〜20.0の範囲
            self._config.snap_threshold = threshold
            return self.save_config()
        return False
    
    def validate_config(self) -> list[str]:
        """設定妥当性チェック"""
        if self._config is None:
            return ["設定が読み込まれていません"]
        
        errors = []
        
        # グリッドサイズチェック
        if not (3 <= self._config.grid_rows <= 20):
            errors.append(f"グリッド行数が範囲外: {self._config.grid_rows} (3-20)")
        
        if not (3 <= self._config.grid_cols <= 20):
            errors.append(f"グリッド列数が範囲外: {self._config.grid_cols} (3-20)")
        
        # ウィンドウサイズチェック
        if not (128 <= self._config.window_width <= 1024):
            errors.append(f"ウィンドウ幅が範囲外: {self._config.window_width} (128-1024)")
        
        if not (128 <= self._config.window_height <= 1024):
            errors.append(f"ウィンドウ高さが範囲外: {self._config.window_height} (128-1024)")
        
        # スキャンタイムチェック
        if not (10 <= self._config.scan_time_ms <= 1000):
            errors.append(f"スキャンタイムが範囲外: {self._config.scan_time_ms} (10-1000ms)")
        
        return errors
    
    def get_config_summary(self) -> dict:
        """設定サマリー取得"""
        if self._config is None:
            return {}
        
        return {
            'grid_size': f"{self._config.grid_rows}x{self._config.grid_cols}",
            'window_size': f"{self._config.window_width}x{self._config.window_height}",
            'scan_time_ms': self._config.scan_time_ms,
            'snap_threshold': self._config.snap_threshold,
            'max_devices': self._config.max_devices,
            'target_fps': self._config.target_fps
        }

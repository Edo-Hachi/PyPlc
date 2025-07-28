"""
PyPlc PLC Controller Module
PLCロジック系機能を分離したモジュール

Phase 3 リファクタリング: PLCロジック系分離
- PLCスキャンサイクル実行
- スキャンタイム管理・動的変更
- タイミング制御
"""

import pyxel
from typing import Optional
from dataclasses import dataclass
from core.config_manager import PyPlcConfig


@dataclass
class PlcScanState:
    """PLCスキャン状態管理用データクラス / PLC scan state management data class"""
    last_scan_time: int          # 最後のスキャン実行時刻 / Last scan execution time
    scan_interval_frames: int    # スキャン間隔（フレーム数）/ Scan interval in frames
    scan_time_ms: int           # スキャンタイム（ミリ秒）/ Scan time in milliseconds


class PyPlcController:
    """PyPlc PLCロジック制御システム / PyPlc PLC Logic Control System"""
    
    def __init__(self, config: PyPlcConfig, target_fps: int):
        """
        PLCコントローラー初期化
        
        Args:
            config: PyPlc設定オブジェクト
            target_fps: 目標フレームレート
        """
        self.config = config
        self.target_fps = target_fps
        
        # Initialize PLC scan state / PLCスキャン状態初期化
        self.scan_state = PlcScanState(
            last_scan_time=pyxel.frame_count,
            scan_interval_frames=self._calculate_scan_interval(config.scan_time_ms),
            scan_time_ms=config.scan_time_ms
        )
    
    def _calculate_scan_interval(self, scan_time_ms: int) -> int:
        """
        スキャンタイムからフレーム間隔を計算
        Calculate frame interval from scan time
        
        Args:
            scan_time_ms: スキャンタイム（ミリ秒）
            
        Returns:
            int: フレーム間隔
        """
        return int(scan_time_ms * self.target_fps / 1000)
    
    def update_scan_cycle(self, current_frame: int, grid_manager) -> bool:
        """
        PLCスキャンサイクル更新・タイミング制御
        Update PLC scan cycle and timing control
        
        Args:
            current_frame: 現在のフレーム数
            grid_manager: グリッドマネージャー
            
        Returns:
            bool: スキャンが実行された場合True / True if scan was executed
        """
        # Check if scan should be executed / スキャン実行判定
        if current_frame - self.scan_state.last_scan_time >= self.scan_state.scan_interval_frames:
            # Execute PLC scan / PLCスキャン実行
            self.execute_scan(grid_manager)
            
            # Update last scan time / 最後のスキャン時刻更新
            self.scan_state.last_scan_time = current_frame
            
            return True
        
        return False
    
    def execute_scan(self, grid_manager) -> None:
        """
        PLCスキャンサイクル実行
        Execute PLC scan cycle
        
        Args:
            grid_manager: グリッドマネージャー
        """
        # PLC logic execution / PLCロジック実行処理
        # For now, just update device states / 現在はデバイス状態更新のみ
        
        # Example: Update all devices based on their logic / 例：全デバイスをロジックに基づいて更新
        for device in grid_manager.get_all_devices():
            if not device.is_bus_device():
                # Placeholder for actual PLC logic / 実際のPLCロジックのプレースホルダー
                # Future implementation:
                # - Contact logic evaluation
                # - Coil state updates
                # - Timer/Counter processing
                # - Power flow calculation
                pass
        
        # Debug output for scan execution / スキャン実行のデバッグ出力
        # print(f"PLC scan executed at frame {pyxel.frame_count}")
    
    def set_scan_time(self, scan_time_ms: int) -> None:
        """
        PLCスキャンタイムを動的に設定
        Set PLC scan time dynamically
        
        Args:
            scan_time_ms: 新しいスキャンタイム（ミリ秒）
        """
        # Update configuration / 設定更新
        self.config.scan_time_ms = scan_time_ms
        
        # Update scan state / スキャン状態更新
        self.scan_state.scan_time_ms = scan_time_ms
        self.scan_state.scan_interval_frames = self._calculate_scan_interval(scan_time_ms)
        
        # Debug output / デバッグ出力
        print(f"PLC scan time changed to {scan_time_ms}ms ({self.scan_state.scan_interval_frames} frames)")
    
    def get_scan_info(self) -> dict:
        """
        スキャン情報取得
        Get scan information
        
        Returns:
            dict: スキャン情報辞書
        """
        return {
            'scan_time_ms': self.scan_state.scan_time_ms,
            'scan_interval_frames': self.scan_state.scan_interval_frames,
            'last_scan_time': self.scan_state.last_scan_time,
            'current_frame': pyxel.frame_count,
            'frames_until_next_scan': max(0, self.scan_state.scan_interval_frames - 
                                        (pyxel.frame_count - self.scan_state.last_scan_time))
        }
    
    def reset_scan_timing(self) -> None:
        """
        スキャンタイミングをリセット
        Reset scan timing
        """
        self.scan_state.last_scan_time = pyxel.frame_count
    
    def is_scan_due(self, current_frame: int) -> bool:
        """
        スキャン実行タイミングかチェック
        Check if scan execution is due
        
        Args:
            current_frame: 現在のフレーム数
            
        Returns:
            bool: スキャン実行タイミングの場合True
        """
        return current_frame - self.scan_state.last_scan_time >= self.scan_state.scan_interval_frames

"""
PyPlc Input Handler Module
入力系機能を分離したモジュール

Phase 2 リファクタリング: 入力系分離
- マウス・キーボード入力処理
- 座標変換機能（最適化版・旧版）
- 編集可能性判定
- マウス状態管理
"""

import pyxel
from typing import Optional, Tuple
from dataclasses import dataclass
from config import PyPlcConfig


@dataclass
class MouseState:
    """マウス状態管理用データクラス / Mouse state management data class"""
    grid_pos: Optional[Tuple[int, int]]  # グリッド座標 (row, col) / Grid coordinates
    show_cursor: bool                    # カーソル表示フラグ / Cursor display flag
    snap_mode: bool                      # スナップモード / Snap mode


class PyPlcInputHandler:
    """PyPlc入力処理システム / PyPlc Input Processing System"""
    
    def __init__(self, config: PyPlcConfig):
        """
        入力ハンドラー初期化
        
        Args:
            config: PyPlc設定オブジェクト
        """
        self.config = config
    
    def update_mouse_state(self) -> MouseState:
        """
        マウス状態更新 / Update mouse state
        
        Returns:
            MouseState: 更新されたマウス状態
        """
        # CTRLキー状態チェック / Check CTRL key state
        snap_mode = pyxel.btn(pyxel.KEY_CTRL)
        
        # マウス座標取得 / Get mouse coordinates
        mouse_x = pyxel.mouse_x
        mouse_y = pyxel.mouse_y
        
        # スクリーン座標をグリッド座標に変換 / Convert screen coordinates to grid coordinates
        grid_pos = self.screen_to_grid(mouse_x, mouse_y, snap_mode)
        
        # 編集可能位置かチェック / Check if position is editable
        if grid_pos and self.is_editable_position(grid_pos[0], grid_pos[1]):
            show_cursor = snap_mode  # スナップモード時のみ表示 / Show cursor only in snap mode
        else:
            grid_pos = None
            show_cursor = False
        
        return MouseState(
            grid_pos=grid_pos,
            show_cursor=show_cursor,
            snap_mode=snap_mode
        )
    
    def screen_to_grid(self, screen_x: int, screen_y: int, snap_mode: bool) -> Optional[Tuple[int, int]]:
        """
        スクリーン座標をグリッド座標に変換（最適化版：O(1)最近隣計算）
        Convert screen coordinates to grid coordinates (Optimized: O(1) nearest neighbor)
        
        Args:
            screen_x: スクリーンX座標
            screen_y: スクリーンY座標
            snap_mode: スナップモード有効フラグ
            
        Returns:
            Optional[Tuple[int, int]]: グリッド座標 (row, col) または None
        """
        if not snap_mode:
            # 通常モード: グリッド範囲外では何も返さない / Normal mode: return nothing outside grid
            return None
        
        grid_x = self.config.grid_origin_x
        grid_y = self.config.grid_origin_y
        cell_size = self.config.grid_cell_size
        
        # 最も近いグリッド交点を数学的に直接計算（O(1)）/ Calculate nearest grid intersection mathematically (O(1))
        nearest_col = round((screen_x - grid_x) / cell_size)
        nearest_row = round((screen_y - grid_y) / cell_size)
        
        # グリッド範囲内チェック / Check within grid bounds
        if not (0 <= nearest_row < self.config.grid_rows and 0 <= nearest_col < self.config.grid_cols):
            return None
        
        # 最近隣交点との距離をチェック（平方根計算を回避して高速化）/ Check distance to nearest intersection (avoid sqrt for speed)
        intersection_x = grid_x + nearest_col * cell_size
        intersection_y = grid_y + nearest_row * cell_size
        
        # 平方根計算を避けて二乗比較で高速化（2-3倍高速）/ Use squared comparison to avoid sqrt (2-3x faster)
        distance_squared = (screen_x - intersection_x) ** 2 + (screen_y - intersection_y) ** 2
        threshold_squared = self.config.snap_threshold ** 2
        
        if distance_squared < threshold_squared:
            return (nearest_row, nearest_col)  # grid[row][col] # [y座標][x座標] の順序 / [y,x] order
        
        return None
    
    def screen_to_grid_legacy(self, screen_x: int, screen_y: int) -> Optional[Tuple[int, int]]:
        """
        スクリーン座標をグリッド座標に変換（旧版）
        Convert screen coordinates to grid coordinates (Legacy version)
        
        Args:
            screen_x: スクリーンX座標
            screen_y: スクリーンY座標
            
        Returns:
            Optional[Tuple[int, int]]: グリッド座標 (row, col) または None
            
        Note:
            参考実装として保持。通常は screen_to_grid() を使用。
            Kept as reference implementation. Normally use screen_to_grid().
        """
        grid_x = self.config.grid_origin_x
        grid_y = self.config.grid_origin_y
        cell_size = self.config.grid_cell_size
        
        # マウスがグリッド範囲内かチェック / Check if mouse is within grid bounds
        if (grid_x <= screen_x <= grid_x + self.config.grid_cols * cell_size and
            grid_y <= screen_y <= grid_y + self.config.grid_rows * cell_size):
            
            # 最も近いグリッド交点を計算 / Calculate nearest grid intersection
            col = round((screen_x - grid_x) / cell_size)
            row = round((screen_y - grid_y) / cell_size)
            
            # 有効範囲内かチェック / Ensure within valid range
            if 0 <= row < self.config.grid_rows and 0 <= col < self.config.grid_cols:
                return (row, col)  # grid[row][col] # [y座標][x座標] の順序 / [y,x] order
        
        return None
    
    def is_editable_position(self, row: int, col: int) -> bool:
        """
        位置が編集可能かチェック / Check if position is editable
        
        Args:
            row: 行座標 / Row coordinate
            col: 列座標 / Column coordinate
            
        Returns:
            bool: 編集可能な場合True / True if editable
        """
        # 列0（左バス）と列終端は編集不可 / Column 0 (left bus) and end column are not editable
        return 1 <= col <= self.config.grid_cols - 2
    
    def get_key_input(self) -> dict:
        """
        キー入力状態を取得 / Get key input state
        
        Returns:
            dict: キー入力状態の辞書 / Dictionary of key input states
        """
        return {
            'quit': pyxel.btnp(pyxel.KEY_Q),
            'scan_time_f5': pyxel.btnp(pyxel.KEY_F5),
            'scan_time_f6': pyxel.btnp(pyxel.KEY_F6), 
            'scan_time_f7': pyxel.btnp(pyxel.KEY_F7),
            'scan_time_f8': pyxel.btnp(pyxel.KEY_F8),
            'toggle_device_1': pyxel.btnp(pyxel.KEY_1),
            'ctrl_pressed': pyxel.btn(pyxel.KEY_CTRL)
        }

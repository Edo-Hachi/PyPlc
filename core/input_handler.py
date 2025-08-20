"""
PyPlc Ver3 Input Handler Module
作成日: 2025-01-28
目標: 操作基盤の確立（Claude案 Phase 1-Stage 2）
"""

import pyxel
from typing import Optional, Tuple
from dataclasses import dataclass

# core.grid_systemからGridSystemをインポート
from core.grid_system import GridSystem
# configからUI設定とグリッド制約をインポート
from config import UIConfig, UIBehaviorConfig, GridConstraints


@dataclass
class MouseState:
    """マウスの状態を管理するデータクラス"""
    hovered_pos: Optional[Tuple[int, int]] = None  # ホバー中のグリッド座標 (row, col)
    is_snapped: bool = False                      # グリッド交点にスナップしているか
    on_editable_area: bool = False                # 編集可能領域にいるか
    snap_mode: bool = False                       # スナップモード状態（CTRLキー制御）


class InputHandler:
    """
    マウス・キーボード入力を処理し、アプリケーションの状態に変換するクラス。
    - マウス座標からグリッド座標への変換を担当します。
    - ユーザーの操作（ホバー、クリック）を解釈します。
    """
    
    def __init__(self, grid_system: GridSystem):
        """InputHandlerの初期化"""
        # 座標計算の基準としてGridSystemのインスタンスを受け取る
        self.grid = grid_system

        #マウスカーソル、グリッドの距離判定のしきい値（Sqrtしないために予め２乗してる）
        self.snap_threshold_sq = UIConfig.SNAP_THRESHOLD ** 2

    def update_mouse_state(self) -> MouseState:
        """
        マウスの状態を更新し、MouseStateオブジェクトとして返す
        設定可能: 常時スナップモード or CTRL切り替えモード
        """
        mouse_x, mouse_y = pyxel.mouse_x, pyxel.mouse_y
        
        # スナップモード制御（設定による切り替え）
        if UIBehaviorConfig.ALWAYS_SNAP_MODE:
            snap_mode = True  # 常時スナップモード
        else:
            snap_mode = pyxel.btn(pyxel.KEY_CTRL)  # CTRL切り替えモード
        
        # スナップモード設定が完了
        
        if not snap_mode:
            # スナップモード無効時は座標変換を行わない（パフォーマンス向上）
            return MouseState(snap_mode=False)
        
        # スナップモード有効時のみ座標変換実行
        # 1. スクリーン座標をグリッド座標に変換
        hovered_pos = self._screen_to_grid(mouse_x, mouse_y)
        
        if hovered_pos is None:
            # グリッド範囲外の場合もスナップモード状態は保持
            return MouseState(snap_mode=True)

        # 2. スナップ状態を判定
        is_snapped = self._is_snapped(mouse_x, mouse_y, hovered_pos)
        
        # 3. 編集可能領域にいるか判定
        on_editable_area = GridConstraints.is_editable_position(hovered_pos[0], hovered_pos[1])
        
        return MouseState(
            hovered_pos=hovered_pos,
            is_snapped=is_snapped,
            on_editable_area=on_editable_area,
            snap_mode=True
        )

    def _screen_to_grid(self, screen_x: int, screen_y: int) -> Optional[Tuple[int, int]]:
        """
        スクリーン座標を最も近いグリッド座標(row, col)に変換する。
        Ver2の最適化ロジックを継承し、常に計算を行う。
        """
        # グリッドの原点とセルサイズをGridSystemインスタンスから取得
        grid_x, grid_y = self.grid.origin_x, self.grid.origin_y
        cell_size = self.grid.cell_size
        
        # 最も近いグリッドの列(col)と行(row)を計算
        # grid[row][col] = [y座標][x座標] の順序を維持
        nearest_col = round((screen_x - grid_x) / cell_size)
        nearest_row = round((screen_y - grid_y) / cell_size)
        
        # 計算結果がグリッドの範囲内かチェック
        if not (0 <= nearest_row < self.grid.rows and 0 <= nearest_col < self.grid.cols):
            return None
        
        return (nearest_row, nearest_col)

    def _is_snapped(self, screen_x: int, screen_y: int, grid_pos: Tuple[int, int]) -> bool:
        """
        マウスカーソルがグリッド交点に十分に近く、スナップしているかを判定する。
        Ver2の効率的な二乗距離比較を継承。
        """
        row, col = grid_pos
        
        # グリッド交点のスクリーン座標を計算
        intersection_x = self.grid.origin_x + col * self.grid.cell_size
        intersection_y = self.grid.origin_y + row * self.grid.cell_size
        
        # マウス座標と交点との距離の二乗を計算（sqrtを避けるため）
        distance_sq = (screen_x - intersection_x) ** 2 + (screen_y - intersection_y) ** 2
        
        # しきい値の二乗と比較してスナップ状態を返す（sqrtを避けるため）
        return distance_sq < self.snap_threshold_sq

    def check_quit_command(self) -> bool:
        """アプリケーションの終了コマンドが入力されたかチェックする"""
        #debug 最終的には終了前にY/Nしたいね
        return pyxel.btnp(pyxel.KEY_F12)

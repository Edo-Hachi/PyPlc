"""
PyPlc Ver3 Grid System Module
作成日: 2025-01-28
目標: 視覚的基盤の確立（Claude案 Phase 1-Stage 1）
"""

import pyxel
from config import GridConfig, GridConstraints

class GridSystem:
    """
    PLCラダー図のグリッドを管理・描画するクラス。
    - グリッド線とバスバーの描画を担当します。
    - 座標系の基準となり、内部データと表示の統一を保証します。
    - (将来) グリッド上のデバイス配置データを保持します。
    """
    
    def __init__(self):
        """GridSystemの初期化"""
        # config.pyから設定値を読み込み、インスタンス変数として保持
        self.rows: int = GridConfig.GRID_ROWS
        self.cols: int = GridConfig.GRID_COLS
        self.cell_size: int = GridConfig.GRID_CELL_SIZE
        self.origin_x: int = GridConfig.GRID_ORIGIN_X
        self.origin_y: int = GridConfig.GRID_ORIGIN_Y
        
        # Ver1の教訓: 座標系は常に[y座標][x座標]で統一する
        # データアクセス時: self.grid_data[row][col]
        
        # (将来の実装) デバイス配置データを保持する2次元配列
        # self.grid_data = [[None for _ in range(self.cols)] for _ in range(self.rows)]

    def draw(self) -> None:
        """グリッド線とバスバーを描画する"""
        
        # 1. 垂直線（列）の描画
        for col in range(self.cols):
            # 線のX座標を計算
            x = self.origin_x + col * self.cell_size
            y_start = self.origin_y
            y_end = self.origin_y + (self.rows - 1) * self.cell_size
            
            # バスバーの描画（Ver2の実装を参考）
            if col == GridConstraints.get_left_bus_col():
                # 左バスバー (L_SIDE): 黄色で太く描画
                pyxel.rect(x, y_start, 2, y_end - y_start + 1, pyxel.COLOR_YELLOW)
            elif col == GridConstraints.get_right_bus_col():
                # 右バスバー (R_SIDE): 水色で太く描画
                pyxel.rect(x, y_start, 2, y_end - y_start + 1, pyxel.COLOR_LIGHT_BLUE)
            else:
                # 通常のグリッド線: 暗い青色
                pyxel.line(x, y_start, x, y_end, pyxel.COLOR_DARK_BLUE)

        # 2. 水平線（行）の描画
        for row in range(self.rows):
            # 線のY座標を計算
            y = self.origin_y + row * self.cell_size
            x_start = self.origin_x
            x_end = self.origin_x + (self.cols - 1) * self.cell_size
            
            # 水平線はすべて同じスタイル
            pyxel.line(x_start, y, x_end, y, pyxel.COLOR_DARK_BLUE)


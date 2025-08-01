#!/usr/bin/env python3
"""
PyPlc-v2 Debug Test
デバッグテスト - 最小限の表示確認
"""

import pyxel
from config import PyPlcConfig, DeviceType, Colors

class DebugTest:
    def __init__(self):
        print("Starting debug test...")
        
        # 設定読み込み
        self.config = PyPlcConfig.load_from_file()
        print(f"Config loaded: {self.config.window_width}x{self.config.window_height}")
        
        # Pyxel初期化
        pyxel.init(self.config.window_width, self.config.window_height, title="Debug Test")
        print("Pyxel initialized")
        
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            print("Quitting...")
            pyxel.quit()
    
    def draw(self):
        # 背景クリア
        pyxel.cls(Colors.BACKGROUND)
        
        # 基本テキスト
        pyxel.text(10, 10, "Debug Test", Colors.TEXT)
        
        # 簡単な図形
        pyxel.rect(50, 50, 20, 20, Colors.GREEN)
        
        # グリッド原点確認
        grid_x = self.config.grid_origin_x
        grid_y = self.config.grid_origin_y
        pyxel.rect(grid_x, grid_y, 8, 8, Colors.YELLOW)
        
        # (1,0)位置確認
        cell_size = self.config.grid_cell_size
        test_x = grid_x + 0 * cell_size  # col=0
        test_y = grid_y + 1 * cell_size  # row=1
        pyxel.rect(test_x - 4, test_y - 4, 8, 8, Colors.RED)
        
        print("Draw called")  # 毎フレーム出力（重い）

if __name__ == "__main__":
    DebugTest()
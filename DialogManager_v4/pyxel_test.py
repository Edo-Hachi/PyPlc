#!/usr/bin/env python3
"""
DialogManager v4 Pyxel環境テストランナー

pyxel run コマンド対応のテスト実行スクリプト
"""

import pyxel
import sys
import os

# DialogManager_v4のパスを追加
sys.path.insert(0, os.path.dirname(__file__))

from run_tests import main as run_all_tests


class PyxelTestApp:
    """Pyxel環境でのテスト実行アプリ"""
    
    def __init__(self):
        # 小さなウィンドウでPyxelを初期化
        pyxel.init(160, 120, title="DialogManager v4 Test", fps=10)
        
        # テスト実行
        self.test_success = False
        self.test_output = ""
        self.run_tests()
        
        # Pyxel実行開始
        pyxel.run(self.update, self.draw)
    
    def run_tests(self):
        """テスト実行"""
        try:
            print("\n" + "="*60)
            print("🎮 Pyxel環境でDialogManager v4テスト実行")
            print("="*60)
            
            # テスト実行
            result = run_all_tests()
            self.test_success = (result == 0)
            
            if self.test_success:
                self.test_output = "全テスト成功！"
                print("\n🎉 Pyxel環境テスト完了: 正常動作")
            else:
                self.test_output = "テスト失敗"
                print("\n❌ Pyxel環境テスト失敗")
                
        except Exception as e:
            self.test_success = False
            self.test_output = f"エラー: {e}"
            print(f"\n💥 テスト実行エラー: {e}")
    
    def update(self):
        """フレーム更新（ESCで終了）"""
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
    
    def draw(self):
        """画面描画"""
        pyxel.cls(0)  # 黒背景
        
        # タイトル
        pyxel.text(10, 10, "DialogManager v4", 7)
        pyxel.text(10, 20, "Test Runner", 7)
        
        # テスト結果表示
        if self.test_success:
            pyxel.text(10, 40, "Test Result:", 7)
            pyxel.text(10, 50, "SUCCESS!", 11)  # 明るい青
            pyxel.text(10, 70, "All tests passed", 7)
        else:
            pyxel.text(10, 40, "Test Result:", 7)
            pyxel.text(10, 50, "FAILED", 8)  # 赤
            pyxel.text(10, 70, self.test_output[:15], 7)
        
        # 操作説明
        pyxel.text(10, 100, "ESC: Exit", 6)


if __name__ == "__main__":
    PyxelTestApp()
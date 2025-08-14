#!/usr/bin/env python3
"""
DialogManager_v3ダイアログサイズ調整確認テスト
PyPlc Ver3ウィンドウサイズでのダイアログ表示テスト

作成日: 2025-08-14
目的: 調整後のダイアログサイズ確認
"""

import pyxel
import sys
from DialogManager_v3.dialogs.file_load_dialog import FileLoadDialogJSON

class DialogSizeTest:
    """ダイアログサイズテストクラス"""
    
    def __init__(self):
        """テスト初期化"""
        # PyPlc Ver3と同じサイズで初期化
        pyxel.init(384, 384, title="Dialog Size Test - PyPlc Ver3 Compatible", fps=30)
        pyxel.mouse(True)
        
        # テスト状態
        self.dialog = None
        self.show_dialog = False
        
        print("[Size Test] Dialog Size Test Started")
        print("[Size Test] Press SPACE to show adjusted dialog")
        print("[Size Test] Press ESC to exit")
        
        # テスト実行
        pyxel.run(self.update, self.draw)
    
    def update(self):
        """フレーム更新"""
        # SPACEキーでダイアログ表示
        if pyxel.btnp(pyxel.KEY_SPACE) and not self.show_dialog:
            self.start_dialog_test()
        
        # ESCキーで終了
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            if self.dialog and self.show_dialog:
                # ダイアログが表示中ならキャンセル
                self.dialog.cancelled = True
                self.dialog.visible = False
                self.show_dialog = False
            else:
                # テスト終了
                pyxel.quit()
        
        # ダイアログが表示中の場合の処理
        if self.show_dialog and self.dialog:
            # ダイアログ更新
            self.dialog.update()
            
            # ダイアログが閉じられたかチェック
            if not self.dialog.visible:
                self.show_dialog = False
    
    def start_dialog_test(self):
        """ダイアログテスト開始"""
        try:
            print("[Size Test] Creating resized FileLoadDialogJSON...")
            self.dialog = FileLoadDialogJSON(
                initial_dir=".",
                file_pattern="*.csv",
                title="Size Test Dialog"
            )
            
            print(f"[Size Test] Dialog size: {self.dialog.width}x{self.dialog.height}")
            print(f"[Size Test] Dialog position: ({self.dialog.x}, {self.dialog.y})")
            print(f"[Size Test] Window size: {pyxel.width}x{pyxel.height}")
            
            # サイズ確認
            if (self.dialog.x + self.dialog.width <= pyxel.width and 
                self.dialog.y + self.dialog.height <= pyxel.height):
                print("[Size Test] ✅ Dialog fits within window!")
            else:
                print("[Size Test] ❌ Dialog exceeds window boundaries!")
            
            self.show_dialog = True
            self.dialog.visible = True
            
        except Exception as e:
            print(f"[Size Test] Error creating dialog: {e}")
    
    def draw(self):
        """画面描画"""
        # 背景クリア
        pyxel.cls(pyxel.COLOR_NAVY)
        
        # PyPlc Ver3風の背景
        pyxel.rect(0, 0, 384, 80, pyxel.COLOR_BLACK)  # ヘッダー部分
        pyxel.rect(0, 80, 384, 240, pyxel.COLOR_DARK_BLUE)  # グリッド部分
        pyxel.rect(0, 320, 384, 64, pyxel.COLOR_BLACK)  # フッター部分
        
        # タイトル
        pyxel.text(10, 10, "DialogManager_v3 Size Test", pyxel.COLOR_WHITE)
        
        # 操作説明
        pyxel.text(10, 30, "SPACE: Show Resized Dialog", pyxel.COLOR_CYAN)
        pyxel.text(10, 40, "ESC: Exit", pyxel.COLOR_CYAN)
        
        # ウィンドウ情報
        pyxel.text(10, 60, f"Window: {pyxel.width}x{pyxel.height}", pyxel.COLOR_YELLOW)
        
        # ダイアログ情報
        if self.dialog:
            dialog_info = f"Dialog: {self.dialog.width}x{self.dialog.height} at ({self.dialog.x},{self.dialog.y})"
            pyxel.text(10, 340, dialog_info, pyxel.COLOR_GREEN)
        
        # ダイアログ表示中の処理
        if self.show_dialog and self.dialog:
            # ダイアログ描画
            self.dialog.draw()

if __name__ == "__main__":
    try:
        DialogSizeTest()
    except Exception as e:
        print(f"Size Test Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
#!/usr/bin/env python3
"""
TextBoxControl入力機能テスト
DialogManager_v3のTextBoxControlが正しく動作するかテスト
"""

import os
import sys
import pyxel

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from DialogManager_v3.dialogs.file_load_dialog import FileLoadDialogJSON
    from DialogManager_v3 import FileManagerV3
    from core.circuit_csv_manager import CircuitCsvManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Making relative imports...")
    from DialogManager_v3.dialogs.file_load_dialog import FileLoadDialogJSON

class TextBoxTestApp:
    """TextBoxControl入力機能テストアプリ"""
    
    def __init__(self):
        pyxel.init(400, 300, title="TextBox Input Test", fps=30)
        pyxel.mouse(True)
        
        # CSVマネージャー（ダミー）
        self.csv_manager = None
        try:
            from core.circuit_csv_manager import CircuitCsvManager
            from core.grid_system import GridSystem
            grid_system = GridSystem()
            self.csv_manager = CircuitCsvManager(grid_system)
        except:
            print("CSV manager not available - using None")
        
        # FileManagerV3
        try:
            from DialogManager_v3 import FileManagerV3
            self.file_manager = FileManagerV3(self.csv_manager)
        except ImportError:
            print("FileManagerV3 not available")
            self.file_manager = None
        
        # テスト状態
        self.dialog_open = False
        self.last_result = ""
        
        print("TextBox入力テスト準備完了")
        print("スペースキー: ファイルダイアログを開く")
        print("F12: 終了")
        
        pyxel.run(self.update, self.draw)
    
    def update(self):
        # F12で終了
        if pyxel.btnp(pyxel.KEY_F12):
            pyxel.quit()
            
        # スペースキーでダイアログを開く
        if pyxel.btnp(pyxel.KEY_SPACE) and not self.dialog_open:
            self.test_file_dialog()
    
    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)
        
        # タイトル
        pyxel.text(10, 10, "TextBox Input Test", pyxel.COLOR_WHITE)
        pyxel.text(10, 25, "Press SPACE to open file dialog", pyxel.COLOR_YELLOW)
        pyxel.text(10, 40, "Press F12 to quit", pyxel.COLOR_GRAY)
        
        # 結果表示
        if self.last_result:
            pyxel.text(10, 60, f"Last result: {self.last_result}", pyxel.COLOR_GREEN)
    
    def test_file_dialog(self):
        """ファイルダイアログのテスト"""
        try:
            self.dialog_open = True
            print("ファイルダイアログを開いています...")
            
            if self.file_manager:
                # FileManagerV3を使用
                success = self.file_manager.show_load_dialog()
                self.last_result = f"FileManagerV3: {success}"
            else:
                # 直接FileLoadDialogJSONを使用
                dialog = FileLoadDialogJSON(
                    initial_dir=os.getcwd(),
                    file_pattern="*.csv",
                    title="Test Dialog"
                )
                
                success, file_path = dialog.show_load_dialog()
                self.last_result = f"Direct: {success}, {file_path}"
            
            self.dialog_open = False
            print(f"ダイアログ結果: {self.last_result}")
            
        except Exception as e:
            print(f"ダイアログテストエラー: {e}")
            import traceback
            traceback.print_exc()
            self.last_result = f"Error: {str(e)}"
            self.dialog_open = False

if __name__ == "__main__":
    print("TextBoxControl入力機能テスト開始")
    TextBoxTestApp()
"""
File Dialog Example

PyPlc Ver3 ファイルダイアログの使用例
"""
import os
import sys
import pyxel
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

# 絶対インポートに変更
try:
    from DialogManager_v3.dialogs.file_load_dialog import show_file_load_dialog
except ImportError:
    # フォールバック用の簡易ファイルダイアログ
    def show_file_load_dialog(initial_dir=None, file_pattern="*", title="Open File"):
        print(f"File dialog display: {title}")
        print(f"Initial directory: {initial_dir}")
        print(f"Pattern: {file_pattern}")
        return "test_file.py"  # テスト用の戻り値

class FileDialogExample:
    def __init__(self):
        print("FileDialogExample starting...")
        try:
            # Pyxelの初期化
            print("Initializing Pyxel...")
            pyxel.init(640, 480, title="File Dialog Example",display_scale=2)
            print("Pyxel initialized successfully")
            pyxel.mouse(True)
            # アプリケーションの状態
            self.selected_file = "No file selected"
            self.show_dialog = False
            
            # デフォルトのPyxelカラーパレットを使用
            print("Using default Pyxel color palette...")
            
            # 実行
            print("Starting Pyxel run loop...")
            pyxel.run(self.update, self.draw)
            
        except Exception as e:
            print(f"Error in FileDialogExample: {e}")
            import traceback
            traceback.print_exc()
    
    def update(self):
        # スペースキーでファイルダイアログを表示
        if pyxel.btnp(pyxel.KEY_SPACE) and not self.show_dialog:
            self.show_dialog = True
            
            # ファイルダイアログを表示
            try:
                selected = show_file_load_dialog(
                    initial_dir=os.path.expanduser("~"),
                    file_pattern="*.py",
                    title="Select Python File"
                )
                
                # 結果を更新
                if selected:
                    self.selected_file = f"Selected: {selected}"
                else:
                    self.selected_file = "Cancelled"
                    
            except Exception as e:
                print(f"Dialog display error: {e}")
                self.selected_file = f"Error: {str(e)}"
                
            self.show_dialog = False
        
        # ESCキーで終了
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
    
    def draw(self):
        # 背景をクリア
        pyxel.cls(pyxel.COLOR_BLACK)
        
        # タイトル
        pyxel.text(10, 10, "File Dialog Example", pyxel.COLOR_PEACH)
        pyxel.text(10, 20, "Press SPACE to open file dialog", pyxel.COLOR_WHITE)
        pyxel.text(10, 30, "Press ESC to exit", pyxel.COLOR_RED)
        
        # 選択されたファイルを表示
        pyxel.text(10, 100, self.selected_file, pyxel.COLOR_PEACH)
        
        # ダイアログ表示中はメッセージを表示
        if self.show_dialog:
            pyxel.rect(100, 150, 440, 50, pyxel.COLOR_NAVY)
            pyxel.rectb(100, 150, 440, 50, pyxel.COLOR_WHITE)
            pyxel.text(120, 170, "Showing file dialog...", pyxel.COLOR_WHITE)

if __name__ == "__main__":
    FileDialogExample()

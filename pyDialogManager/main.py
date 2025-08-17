# PyPlcシステムにpyDialogManagerを移行後、このファイルは不要になります

import pyxel
from dialog_manager import DialogManager
from file_open_dialog import FileOpenDialogController
from file_save_dialog import FileSaveDialogController
from system_settings import settings

class App:
    def __init__(self):
        pyxel.init(256, 256, title="Dialog System Demo")

        # ダイアログマネージャーを初期化
        self.dialog_manager = DialogManager("dialogs.json")
        
        # ファイルオープンダイアログコントローラーを初期化（カレントディレクトリから開始）
        self.file_open_controller = FileOpenDialogController(self.dialog_manager, ".")
        
        # ファイル保存ダイアログコントローラーを初期化（カレントディレクトリから開始）
        self.file_save_controller = FileSaveDialogController(self.dialog_manager, ".")
        
        # 最初のダイアログを表示
        self.dialog_manager.show("IDD_MAIN_DIALOG")

        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        # 数字キーで表示するダイアログを切り替え
        if pyxel.btnp(pyxel.KEY_F1):
            self.dialog_manager.show("IDD_MAIN_DIALOG")
        if pyxel.btnp(pyxel.KEY_F2):
            # ファイルオープンダイアログを連携機能付きで表示
            self.file_open_controller.show_file_open_dialog()
        if pyxel.btnp(pyxel.KEY_F3):
            # ファイル保存ダイアログを連携機能付きで表示
            self.file_save_controller.show_save_dialog(default_filename="untitled", default_extension=".txt")
        if pyxel.btnp(pyxel.KEY_F4):
            self.dialog_manager.show("IDD_TEXT_INPUT")
        
        # 異なる拡張子でのテスト用ダイアログ
        if pyxel.btnp(pyxel.KEY_F5):
            # CSV保存ダイアログ（.csv拡張子付与）
            self.file_save_controller.show_save_dialog(default_filename="data", default_extension=".csv")
        if pyxel.btnp(pyxel.KEY_F6):
            # 拡張子なし保存ダイアログ（拡張子付与なし）
            self.file_save_controller.show_save_dialog(default_filename="script", default_extension="")
        
        # システム設定切り替えキー
        if pyxel.btnp(pyxel.KEY_TAB):
            settings.toggle_click_mode()
            print(f"Click mode switched to: {settings.get_click_mode()}")

        # ダイアログマネージャーの更新処理を呼び出す
        self.dialog_manager.update()
        
        # ファイルオープンダイアログコントローラーの更新
        self.file_open_controller.update()
        
        # ファイル保存ダイアログコントローラーの更新
        self.file_save_controller.update()

    def draw(self):
        # 背景を少し暗い色で塗りつぶし
        pyxel.cls(pyxel.COLOR_DARK_BLUE)

        # ダイアログマネージャーの描画処理を呼び出す
        self.dialog_manager.draw()
        
        # システム設定情報を画面下部に表示
        settings_text = settings.get_settings_info()
        pyxel.text(5, 240, settings_text, pyxel.COLOR_WHITE)
        pyxel.text(5, 250, "TAB: Toggle click mode", pyxel.COLOR_GRAY)

App()

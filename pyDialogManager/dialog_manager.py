import json
import pyxel
from .dialog import Dialog
from .widgets import LabelWidget, ButtonWidget, TextBoxWidget, ListBoxWidget, DropdownWidget, CheckboxWidget

class DialogManager:
    """
    dialogs.json を読み込み、ダイアログの生成と管理を行うクラス
    """
    def __init__(self, json_path):
        # JSONファイルからダイアログ定義を読み込む
        with open(json_path, 'r') as f:
            self.definitions = json.load(f)
        
        self.active_dialog = None

        # ウィジェットのタイプ名とクラスをマッピング
        self.widget_factory = {
            "label": LabelWidget,
            "button": ButtonWidget,
            "textbox": TextBoxWidget,
            "listbox": ListBoxWidget,
            "dropdown": DropdownWidget,
            "checkbox": CheckboxWidget,
        }

    def show(self, dialog_id):
        """指定されたIDのダイアログを表示する"""
        dialog_def = self.definitions.get(dialog_id)
        if not dialog_def:
            print(f"Error: Dialog definition for '{dialog_id}' not found.")
            return

        # Dialogインスタンスを先に仮作成（ウィジェットが親ダイアログを参照できるようにするため）
        # この時点ではウィジェットリストは空
        new_dialog = Dialog(dialog_def, [])

        # ウィジェット定義からインスタンスを作成
        widgets = []
        for widget_def in dialog_def.get("widgets", []):
            widget_type = widget_def.get("type")
            widget_class = self.widget_factory.get(widget_type)
            if widget_class:
                # ウィジェットのコンストラクタに、親となるダイアログインスタンスを渡す
                widgets.append(widget_class(new_dialog, widget_def))
            else:
                print(f"Warning: Widget type '{widget_type}' is not supported.")
        
        # 作成したウィジェットリストをダイアログに設定
        new_dialog.widgets = widgets
        
        self.active_dialog = new_dialog

    def close(self):
        """現在アクティブなダイアログを閉じる"""
        self.active_dialog = None

    def update(self):
        """アクティブなダイアログの更新処理を呼び出す"""
        if self.active_dialog:
            self.active_dialog.update()

    def draw(self):
        """アクティブなダイアログの描画処理を呼び出す"""
        if self.active_dialog:
            self.active_dialog.draw()

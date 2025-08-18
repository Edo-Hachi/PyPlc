import json
import pyxel
from .dialog import Dialog
from .widgets import LabelWidget, ButtonWidget, TextBoxWidget, ListBoxWidget, DropdownWidget, CheckboxWidget


def resolve_color(color_value):
    """
    色定義を解決する関数
    
    Args:
        color_value: 数値、"COLOR_xxx"文字列、またはNone
        
    Returns:
        int: pyxel色定数
    """
    if color_value is None:
        return None
        
    # すでに数値の場合はそのまま返す
    if isinstance(color_value, int):
        return color_value
    
    # 文字列の場合、COLOR_xxxからpyxel.COLOR_xxxに変換
    if isinstance(color_value, str) and color_value.startswith("COLOR_"):
        color_name = color_value  # "COLOR_RED" など
        
        # pyxel色定数マッピング
        color_map = {
            "COLOR_BLACK": pyxel.COLOR_BLACK,
            "COLOR_NAVY": pyxel.COLOR_NAVY,
            "COLOR_PURPLE": pyxel.COLOR_PURPLE,
            "COLOR_GREEN": pyxel.COLOR_GREEN,
            "COLOR_BROWN": pyxel.COLOR_BROWN,
            "COLOR_DARK_BLUE": pyxel.COLOR_DARK_BLUE,
            "COLOR_LIGHT_BLUE": pyxel.COLOR_LIGHT_BLUE,
            "COLOR_WHITE": pyxel.COLOR_WHITE,
            "COLOR_RED": pyxel.COLOR_RED,
            "COLOR_ORANGE": pyxel.COLOR_ORANGE,
            "COLOR_YELLOW": pyxel.COLOR_YELLOW,
            "COLOR_LIME": pyxel.COLOR_LIME,
            "COLOR_CYAN": pyxel.COLOR_CYAN,
            "COLOR_GRAY": pyxel.COLOR_GRAY,
            "COLOR_PINK": pyxel.COLOR_PINK,
            "COLOR_PEACH": pyxel.COLOR_PEACH,
        }
        
        return color_map.get(color_name, pyxel.COLOR_WHITE)  # デフォルトは白
    
    # その他の場合は白をデフォルトに
    return pyxel.COLOR_WHITE

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

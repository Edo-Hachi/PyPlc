import pyxel
from .widgets import LabelWidget, ButtonWidget, TextBoxWidget, ListBoxWidget, resolve_color

class Dialog:
    """
    ダイアログのウィンドウ自体を管理するクラス。
    ウィジェットのリストを保持し、それらの更新と描画を制御する。
    """
    def __init__(self, definition, widgets):
        self.x = definition.get("x", 0)
        self.y = definition.get("y", 0)
        self.width = definition.get("width", 100)
        self.height = definition.get("height", 100)
        self.title = definition.get("title", "Dialog")
        self.widgets = widgets
        self.is_active = True # モーダルなのでデフォルトでアクティブ
        
        # ダイアログレベルのカラープロパティ（COLOR_xxx文字列対応）
        self.bg_color = resolve_color(definition.get("bg_color", "COLOR_WHITE"))
        self.title_bg_color = resolve_color(definition.get("title_bg_color", "COLOR_NAVY"))
        self.title_text_color = resolve_color(definition.get("title_text_color", "COLOR_WHITE"))
        self.border_color = resolve_color(definition.get("border_color", "COLOR_BLACK"))

    def update(self):
        if not self.is_active:
            return

        # 管理しているウィジェットの更新処理を呼び出す
        for widget in self.widgets:
            widget.update()

    def draw(self):
        if not self.is_active:
            return

        # ダイアログの背景を描画（カラープロパティ対応）
        pyxel.rect(self.x, self.y, self.width, self.height, self.bg_color)
        
        # タイトルバー
        pyxel.rect(self.x, self.y, self.width, 12, self.title_bg_color)
        
        # 枠線
        pyxel.rectb(self.x, self.y, self.width, self.height, self.border_color)
        
        # タイトルテキスト
        pyxel.text(self.x + 4, self.y + 3, self.title, self.title_text_color)

        # 管理しているウィジェットの描画処理を呼び出す
        # ドロップダウンウィジェット以外を先に描画
        dropdown_widgets = []
        for widget in self.widgets:
            if hasattr(widget, '__class__') and widget.__class__.__name__ == 'DropdownWidget':
                dropdown_widgets.append(widget)
            else:
                widget.draw()
        
        # ドロップダウンウィジェットを最後に描画（Z-orderを最前面にするため）
        for dropdown in dropdown_widgets:
            dropdown.draw()
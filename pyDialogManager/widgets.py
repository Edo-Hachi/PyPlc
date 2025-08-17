import pyxel
import time
from system_settings import settings

class WidgetBase:
    """すべてのウィジェットの基底クラス"""
    def __init__(self, dialog, definition):
        self.dialog = dialog
        self.id = definition.get("id")
        self.x = definition.get("x", 0)
        self.y = definition.get("y", 0)
        self.width = definition.get("width", 0)
        self.height = definition.get("height", 0)
        self.text = definition.get("text", "")

    def update(self):
        pass

    def draw(self):
        pass

class LabelWidget(WidgetBase):
    """静的テキストを表示するラベルウィジェット"""
    def __init__(self, dialog, definition):
        super().__init__(dialog, definition)
        # テキストの長さに合わせて幅を自動調整（widthが未指定の場合）
        if self.width == 0:
            self.width = len(self.text) * pyxel.FONT_WIDTH
        if self.height == 0:
            self.height = pyxel.FONT_HEIGHT

    def draw(self):
        # ダイアログの座標系に合わせて描画
        pyxel.text(self.dialog.x + self.x, self.dialog.y + self.y, self.text, pyxel.COLOR_BLACK)

class ButtonWidget(WidgetBase):
    """クリック可能なボタンウィジェット"""
    def __init__(self, dialog, definition):
        super().__init__(dialog, definition)
        self.is_hover = False
        self.is_pressed = False

    def update(self):
        # マウスカーソルがボタンの領域内にあるかチェック
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        dx, dy = self.dialog.x, self.dialog.y
        
        self.is_hover = (dx + self.x <= mx < dx + self.x + self.width and
                         dy + self.y <= my < dy + self.y + self.height)

        # ホバー中に左クリックされたかチェック
        if self.is_hover and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.is_pressed = True
            # ここでコールバックなどを呼び出すことができる
            print(f"Button '{self.id}' pressed!")
        else:
            self.is_pressed = False

    def draw(self):
        dx, dy = self.dialog.x, self.dialog.y
        x, y = dx + self.x, dy + self.y
        
        # 状態に応じて色を変える
        bg_color = pyxel.COLOR_WHITE
        if self.is_hover:
            bg_color = pyxel.COLOR_GRAY
        if self.is_pressed:
            bg_color = pyxel.COLOR_DARK_BLUE

        # ボタンの描画
        pyxel.rect(x, y, self.width, self.height, bg_color)
        pyxel.rectb(x, y, self.width, self.height, pyxel.COLOR_BLACK)

        # テキストを中央に配置
        text_x = x + (self.width - len(self.text) * pyxel.FONT_WIDTH) / 2
        text_y = y + (self.height - pyxel.FONT_HEIGHT) / 2
        pyxel.text(text_x, text_y, self.text, pyxel.COLOR_BLACK)

class TextBoxWidget(WidgetBase):
    """テキスト入力が可能なテキストボックスウィジェット"""
    def __init__(self, dialog, definition):
        super().__init__(dialog, definition)
        self.has_focus = False
        self.cursor_pos = len(self.text)
        self.cursor_visible = True
        self.cursor_blink_timer = 0
        self.cursor_blink_interval = 0.5
        self.last_blink_time = time.time()
        self.max_length = definition.get("max_length", 50)
        self.readonly = definition.get("readonly", False)
        
        # デフォルトサイズ設定
        if self.width == 0:
            self.width = 100
        if self.height == 0:
            self.height = 20

    def update(self):
        # マウスクリックでフォーカス取得
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        dx, dy = self.dialog.x, self.dialog.y
        
        # フォーカス制御（読み取り専用の場合はフォーカスしない）
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if (dx + self.x <= mx < dx + self.x + self.width and
                dy + self.y <= my < dy + self.y + self.height):
                if not self.readonly:
                    self.has_focus = True
                    # クリック位置にカーソルを移動
                    click_x = mx - (dx + self.x) - 4  # パディングを考慮
                    char_index = max(0, min(click_x // 4, len(self.text)))  # 4は文字幅
                    self.cursor_pos = char_index
            else:
                self.has_focus = False

        # カーソル点滅制御
        if self.has_focus:
            current_time = time.time()
            if current_time - self.last_blink_time >= self.cursor_blink_interval:
                self.cursor_visible = not self.cursor_visible
                self.last_blink_time = current_time

        # フォーカス中のキー入力処理（読み取り専用でない場合のみ）
        if self.has_focus and not self.readonly:
            self._handle_keyboard_input()

    def _handle_keyboard_input(self):
        """キーボード入力を処理"""
        # Backspace処理
        if pyxel.btnp(pyxel.KEY_BACKSPACE) and self.cursor_pos > 0:
            self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
            self.cursor_pos -= 1
            self.cursor_visible = True
            self.last_blink_time = time.time()

        # Delete処理  
        if pyxel.btnp(pyxel.KEY_DELETE) and self.cursor_pos < len(self.text):
            self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
            self.cursor_visible = True
            self.last_blink_time = time.time()

        # 左矢印キー
        if pyxel.btnp(pyxel.KEY_LEFT) and self.cursor_pos > 0:
            self.cursor_pos -= 1
            self.cursor_visible = True
            self.last_blink_time = time.time()

        # 右矢印キー
        if pyxel.btnp(pyxel.KEY_RIGHT) and self.cursor_pos < len(self.text):
            self.cursor_pos += 1
            self.cursor_visible = True
            self.last_blink_time = time.time()

        # 文字入力処理（英数字、記号）
        for key in range(256):
            if pyxel.btnp(key):
                char = self._convert_key_to_char(key)
                if char and len(self.text) < self.max_length:
                    self.text = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
                    self.cursor_pos += 1
                    self.cursor_visible = True
                    self.last_blink_time = time.time()

    def _convert_key_to_char(self, key):
        """キーコードを文字に変換"""
        # 英字 (a-z)
        if pyxel.KEY_A <= key <= pyxel.KEY_Z:
            char = chr(ord('a') + (key - pyxel.KEY_A))
            if pyxel.btn(pyxel.KEY_SHIFT):
                return char.upper()
            return char
        
        # 数字 (0-9)
        if pyxel.KEY_0 <= key <= pyxel.KEY_9:
            if pyxel.btn(pyxel.KEY_SHIFT):
                # Shift+数字の記号
                shift_symbols = ')!@#$%^&*('
                return shift_symbols[key - pyxel.KEY_0]
            return chr(ord('0') + (key - pyxel.KEY_0))
        
        # 基本的な記号
        symbol_map = {
            pyxel.KEY_SPACE: ' ',
            pyxel.KEY_PERIOD: '.' if not pyxel.btn(pyxel.KEY_SHIFT) else '>',
            pyxel.KEY_COMMA: ',' if not pyxel.btn(pyxel.KEY_SHIFT) else '<',
            pyxel.KEY_MINUS: '-' if not pyxel.btn(pyxel.KEY_SHIFT) else '_',
            pyxel.KEY_EQUALS: '=' if not pyxel.btn(pyxel.KEY_SHIFT) else '+',
            pyxel.KEY_SLASH: '/' if not pyxel.btn(pyxel.KEY_SHIFT) else '?',
            pyxel.KEY_SEMICOLON: ';' if not pyxel.btn(pyxel.KEY_SHIFT) else ':',
            pyxel.KEY_QUOTE: "'" if not pyxel.btn(pyxel.KEY_SHIFT) else '"',
            pyxel.KEY_LEFTBRACKET: '[' if not pyxel.btn(pyxel.KEY_SHIFT) else '{',
            pyxel.KEY_RIGHTBRACKET: ']' if not pyxel.btn(pyxel.KEY_SHIFT) else '}',
            pyxel.KEY_BACKSLASH: '\\' if not pyxel.btn(pyxel.KEY_SHIFT) else '|',
            pyxel.KEY_BACKQUOTE: '`' if not pyxel.btn(pyxel.KEY_SHIFT) else '~',
        }
        
        return symbol_map.get(key)

    def draw(self):
        dx, dy = self.dialog.x, self.dialog.y
        x, y = dx + self.x, dy + self.y
        
        # テキストボックスの背景と枠
        bg_color = pyxel.COLOR_GRAY if self.readonly else pyxel.COLOR_WHITE
        pyxel.rect(x, y, self.width, self.height, bg_color)
        pyxel.rectb(x, y, self.width, self.height, pyxel.COLOR_BLACK)
        
        # フォーカス時は青い枠（読み取り専用でない場合のみ）
        if self.has_focus and not self.readonly:
            pyxel.rectb(x-1, y-1, self.width+2, self.height+2, pyxel.COLOR_LIGHT_BLUE)
        
        # テキスト描画
        text_x = x + 4  # 左パディング
        text_y = y + (self.height - pyxel.FONT_HEIGHT) // 2  # 垂直中央
        pyxel.text(text_x, text_y, self.text, pyxel.COLOR_BLACK)  # 黒テキスト
        
        # カーソル描画（フォーカス中かつ表示状態、読み取り専用でない場合のみ）
        if self.has_focus and self.cursor_visible and not self.readonly:
            cursor_x = text_x + self.cursor_pos * 4  # 4は文字幅
            cursor_y = y + 2
            pyxel.line(cursor_x, cursor_y, cursor_x, cursor_y + self.height - 4, pyxel.COLOR_BLACK)  # 黒いカーソル

class ListBoxWidget(WidgetBase):
    """複数項目から選択可能なリストボックスウィジェット"""
    def __init__(self, dialog, definition):
        super().__init__(dialog, definition)
        self.items = []  # 表示項目のリスト
        self.selected_index = -1  # 選択されたアイテムのインデックス
        self.scroll_offset = 0  # スクロールオフセット
        self.item_height = definition.get("item_height", 12)  # 1項目の高さ
        self.visible_items = (self.height - 4) // self.item_height  # 表示可能項目数
        self.hover_index = -1  # ホバー中のアイテムインデックス
        
        # ダブルクリック検出用
        self.last_click_time = 0
        self.last_clicked_index = -1
        
        # スクロールボタンホバー状態
        self.hovered_scroll_button = None  # "up5", "up1", "down1", "down5"
        
        # デフォルトサイズ設定
        if self.width == 0:
            self.width = 200
        if self.height == 0:
            self.height = 100

    def set_items(self, items):
        """リストアイテムを設定"""
        self.items = items
        self.selected_index = -1
        self.scroll_offset = 0
        self.hover_index = -1

    def get_selected_item(self):
        """選択されたアイテムを取得"""
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None

    def update(self):
        # マウス位置チェック
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        dx, dy = self.dialog.x, self.dialog.y
        
        # スクロールボタンの処理（項目数が表示可能数を超える場合）
        if len(self.items) > self.visible_items:
            button_width = 16
            button_height = 14
            scroll_area_x = dx + self.x + self.width - button_width
            
            # 4つのボタンの位置を計算
            up5_button_y = dy + self.y
            up1_button_y = up5_button_y + button_height
            down1_button_y = dy + self.y + self.height - button_height * 2
            down5_button_y = dy + self.y + self.height - button_height
            
            # ホバー状態とクリック処理
            self.hovered_scroll_button = None
            
            # 上5行ボタン
            if (scroll_area_x <= mx < scroll_area_x + button_width and
                up5_button_y <= my < up5_button_y + button_height):
                self.hovered_scroll_button = "up5"
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.scroll_up_fast()
                    return
            
            # 上1行ボタン
            elif (scroll_area_x <= mx < scroll_area_x + button_width and
                up1_button_y <= my < up1_button_y + button_height):
                self.hovered_scroll_button = "up1"
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.scroll_up()
                    return
            
            # 下1行ボタン
            elif (scroll_area_x <= mx < scroll_area_x + button_width and
                down1_button_y <= my < down1_button_y + button_height):
                self.hovered_scroll_button = "down1"
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.scroll_down()
                    return
            
            # 下5行ボタン
            elif (scroll_area_x <= mx < scroll_area_x + button_width and
                down5_button_y <= my < down5_button_y + button_height):
                self.hovered_scroll_button = "down5"
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.scroll_down_fast()
                    return
        
        # リストボックス内でのマウス処理（スクロールボタン領域を除く）
        list_width = self.width - (16 if len(self.items) > self.visible_items else 0)
        if (dx + self.x <= mx < dx + self.x + list_width and
            dy + self.y <= my < dy + self.y + self.height):
            
            # リスト内でのマウス位置を計算
            list_y = my - (dy + self.y + 2)  # パディングを考慮
            item_index = list_y // self.item_height + self.scroll_offset
            
            if 0 <= item_index < len(self.items):
                self.hover_index = item_index
                
                # クリックで選択
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    current_time = time.time()
                    is_double_click = False
                    
                    # ダブルクリック判定
                    if (self.last_clicked_index == item_index and 
                        current_time - self.last_click_time < settings.get_double_click_interval()):
                        is_double_click = True
                    
                    # 選択処理
                    old_selection = self.selected_index
                    self.selected_index = item_index
                    
                    # クリックモードに応じて処理を分岐
                    if settings.is_single_click_mode():
                        # シングルクリックモード: 即座にアクション実行
                        print(f"Single-click selected: {self.items[item_index]}")
                        if hasattr(self, 'on_item_activated'):
                            self.on_item_activated(self.selected_index)
                        
                        # 選択変更イベントも発火
                        if old_selection != self.selected_index and hasattr(self, 'on_selection_changed'):
                            self.on_selection_changed(self.selected_index)
                    
                    else:  # ダブルクリックモード
                        if is_double_click:
                            # ダブルクリック: アクション実行
                            print(f"Double-click activated: {self.items[item_index]}")
                            if hasattr(self, 'on_item_activated'):
                                self.on_item_activated(self.selected_index)
                        else:
                            # シングルクリック: 選択のみ
                            print(f"Selected item: {self.items[item_index]}")
                            if old_selection != self.selected_index and hasattr(self, 'on_selection_changed'):
                                self.on_selection_changed(self.selected_index)
                    
                    # ダブルクリック検出用の状態更新
                    self.last_click_time = current_time
                    self.last_clicked_index = item_index
            else:
                self.hover_index = -1
        else:
            self.hover_index = -1

    def scroll_to_item(self, index):
        """指定されたアイテムが見えるようにスクロール"""
        if index < self.scroll_offset:
            self.scroll_offset = index
        elif index >= self.scroll_offset + self.visible_items:
            self.scroll_offset = index - self.visible_items + 1
        
        # スクロール範囲制限
        max_scroll = max(0, len(self.items) - self.visible_items)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

    def scroll_up(self):
        """上にスクロール"""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1

    def scroll_down(self):
        """下にスクロール"""
        max_scroll = max(0, len(self.items) - self.visible_items)
        if self.scroll_offset < max_scroll:
            self.scroll_offset += 1

    def scroll_up_fast(self):
        """上に5行スクロール"""
        self.scroll_offset = max(0, self.scroll_offset - 5)

    def scroll_down_fast(self):
        """下に5行スクロール"""
        max_scroll = max(0, len(self.items) - self.visible_items)
        self.scroll_offset = min(max_scroll, self.scroll_offset + 5)

    def draw(self):
        dx, dy = self.dialog.x, self.dialog.y
        x, y = dx + self.x, dy + self.y
        
        # リストボックスの背景と枠
        pyxel.rect(x, y, self.width, self.height, pyxel.COLOR_WHITE)
        pyxel.rectb(x, y, self.width, self.height, pyxel.COLOR_BLACK)
        
        # 項目を描画
        for i in range(self.visible_items):
            item_index = i + self.scroll_offset
            if item_index >= len(self.items):
                break
                
            item_y = y + 2 + i * self.item_height
            item = self.items[item_index]
            
            # 選択状態の背景
            if item_index == self.selected_index:
                pyxel.rect(x + 1, item_y, self.width - 2, self.item_height, pyxel.COLOR_NAVY)
            elif item_index == self.hover_index:
                pyxel.rect(x + 1, item_y, self.width - 2, self.item_height, pyxel.COLOR_LIGHT_BLUE)
            
            # アイテムテキスト描画
            text_color = pyxel.COLOR_WHITE if item_index == self.selected_index else pyxel.COLOR_BLACK
            
            # テキストが長すぎる場合は切り詰め
            display_text = str(item)
            max_chars = (self.width - 8) // 4  # 4は文字幅
            if len(display_text) > max_chars:
                display_text = display_text[:max_chars-3] + "..."
            
            pyxel.text(x + 4, item_y + 2, display_text, text_color)
        
        # 上下スクロールボタン表示（項目数が表示可能数を超える場合）
        if len(self.items) > self.visible_items:
            self._draw_scroll_buttons(x, y)

    def _draw_scroll_buttons(self, x, y):
        """スクロールボタンを描画"""
        button_width = 16
        button_height = 14
        button_x = x + self.width - button_width
        
        # 4つのボタンの位置
        up5_button_y = y
        up1_button_y = up5_button_y + button_height
        down1_button_y = y + self.height - button_height * 2
        down5_button_y = y + self.height - button_height
        
        # 上5行ボタン（二重上矢印）
        bg_color = pyxel.COLOR_LIGHT_BLUE if self.hovered_scroll_button == "up5" else pyxel.COLOR_WHITE
        pyxel.rect(button_x, up5_button_y, button_width, button_height, bg_color)
        pyxel.rectb(button_x, up5_button_y, button_width, button_height, pyxel.COLOR_BLACK)
        self._draw_double_up_arrow(button_x + 8, up5_button_y + 7)
        
        # 上1行ボタン（単一上矢印）
        bg_color = pyxel.COLOR_LIGHT_BLUE if self.hovered_scroll_button == "up1" else pyxel.COLOR_WHITE
        pyxel.rect(button_x, up1_button_y, button_width, button_height, bg_color)
        pyxel.rectb(button_x, up1_button_y, button_width, button_height, pyxel.COLOR_BLACK)
        self._draw_up_arrow(button_x + 8, up1_button_y + 7)
        
        # 下1行ボタン（単一下矢印）
        bg_color = pyxel.COLOR_LIGHT_BLUE if self.hovered_scroll_button == "down1" else pyxel.COLOR_WHITE
        pyxel.rect(button_x, down1_button_y, button_width, button_height, bg_color)
        pyxel.rectb(button_x, down1_button_y, button_width, button_height, pyxel.COLOR_BLACK)
        self._draw_down_arrow(button_x + 8, down1_button_y + 7)
        
        # 下5行ボタン（二重下矢印）
        bg_color = pyxel.COLOR_LIGHT_BLUE if self.hovered_scroll_button == "down5" else pyxel.COLOR_WHITE
        pyxel.rect(button_x, down5_button_y, button_width, button_height, bg_color)
        pyxel.rectb(button_x, down5_button_y, button_width, button_height, pyxel.COLOR_BLACK)
        self._draw_double_down_arrow(button_x + 8, down5_button_y + 7)

    def _draw_up_arrow(self, cx, cy):
        """上向き矢印を描画（中心座標指定）"""
        # 塗りつぶし三角形: 上向き
        pyxel.tri(cx, cy - 3,           # 上頂点
                  cx - 3, cy + 1,       # 左下
                  cx + 3, cy + 1,       # 右下
                  pyxel.COLOR_BLACK)

    def _draw_down_arrow(self, cx, cy):
        """下向き矢印を描画（中心座標指定）"""
        # 塗りつぶし三角形: 下向き
        pyxel.tri(cx - 3, cy - 1,       # 左上
                  cx + 3, cy - 1,       # 右上
                  cx, cy + 3,           # 下頂点
                  pyxel.COLOR_BLACK)

    def _draw_double_up_arrow(self, cx, cy):
        """二重上向き矢印を描画"""
        self._draw_up_arrow(cx, cy - 1)  # 上の矢印
        self._draw_up_arrow(cx, cy + 2)  # 下の矢印

    def _draw_double_down_arrow(self, cx, cy):
        """二重下向き矢印を描画"""
        self._draw_down_arrow(cx, cy - 2)  # 上の矢印
        self._draw_down_arrow(cx, cy + 1)  # 下の矢印

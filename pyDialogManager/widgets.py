import pyxel
import time
from typing import List, Optional
from .system_settings import settings

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
        # 色の設定（デフォルトは黒）
        self.color = definition.get("color", pyxel.COLOR_BLACK)

    def draw(self):
        # ダイアログの座標系に合わせて描画
        if self.text:  # テキストが空でない場合のみ描画
            pyxel.text(self.dialog.x + self.x, self.dialog.y + self.y, self.text, self.color)

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


class DropdownWidget(WidgetBase):
    """ドロップダウン選択ウィジェット"""
    
    def __init__(self, dialog, definition):
        super().__init__(dialog, definition)
        
        # ドロップダウン固有の属性
        self.items = definition.get("items", [])
        self.selected_index = definition.get("selected_index", -1)
        self.is_open = False
        self.is_hover = False
        self.hover_item_index = -1
        
        # 表示設定
        self.item_height = definition.get("item_height", 12)
        self.max_visible_items = definition.get("max_visible_items", 5)
        
        # ドロップダウンリストの高さを計算
        visible_items = min(len(self.items), self.max_visible_items)
        self.dropdown_height = visible_items * self.item_height
        
        # イベントハンドラー（動的属性システム）
        # hasattr パターンでイベントハンドラーを実装
        
    def get_selected_value(self) -> Optional[str]:
        """現在選択されている値を取得"""
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None
        
    def get_display_text(self) -> str:
        """ボタンに表示するテキストを取得"""
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return "Select..." if self.items else "No items"
    
    def update(self):
        """マウス操作の処理"""
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        dx, dy = self.dialog.x, self.dialog.y
        
        # ドロップダウンボタンの範囲チェック
        button_x = dx + self.x
        button_y = dy + self.y
        
        self.is_hover = (button_x <= mx < button_x + self.width and 
                        button_y <= my < button_y + self.height)
        
        # ドロップダウンリストが開いている場合の処理
        if self.is_open:
            self._update_dropdown_list(mx, my, dx, dy)
        
        # クリック処理
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.is_hover:
                # ボタンクリック: ドロップダウンを開く/閉じる
                self.is_open = not self.is_open
                if self.is_open:
                    self.hover_item_index = self.selected_index
            elif self.is_open:
                # ドロップダウンリスト内のクリック処理
                self._handle_dropdown_click(mx, my, dx, dy)
            else:
                # 外部クリック: ドロップダウンを閉じる
                self.is_open = False
    
    def _update_dropdown_list(self, mx, my, dx, dy):
        """ドロップダウンリスト内のマウス処理"""
        list_x = dx + self.x
        list_y = dy + self.y + self.height
        
        self.hover_item_index = -1
        
        if (list_x <= mx < list_x + self.width and 
            list_y <= my < list_y + self.dropdown_height):
            
            # ホバー中のアイテムインデックスを計算
            relative_y = my - list_y
            item_index = relative_y // self.item_height
            
            if 0 <= item_index < len(self.items):
                self.hover_item_index = item_index
    
    def _handle_dropdown_click(self, mx, my, dx, dy):
        """ドロップダウンリスト内でのクリック処理"""
        list_x = dx + self.x
        list_y = dy + self.y + self.height
        
        if (list_x <= mx < list_x + self.width and 
            list_y <= my < list_y + self.dropdown_height):
            
            # クリックされたアイテムを計算
            relative_y = my - list_y
            clicked_index = relative_y // self.item_height
            
            if 0 <= clicked_index < len(self.items):
                # 選択を更新
                old_index = self.selected_index
                self.selected_index = clicked_index
                
                # イベント発火（動的属性システム）
                if hasattr(self, 'on_selection_changed'):
                    print(f"[DEBUG] DropdownWidget: Firing on_selection_changed event: index={self.selected_index}, value='{self.get_selected_value()}'")
                    self.on_selection_changed(self.selected_index, self.get_selected_value())
                else:
                    print(f"[DEBUG] DropdownWidget: No on_selection_changed handler found")
                
                # ドロップダウンを閉じる
                self.is_open = False
        else:
            # 外部クリック: ドロップダウンを閉じる
            self.is_open = False
    
    def draw(self):
        """ドロップダウンウィジェットの描画"""
        dx, dy = self.dialog.x, self.dialog.y
        
        # ドロップダウンボタンの描画
        self._draw_button(dx, dy)
        
        # ドロップダウンリストの描画（開いている場合のみ）
        if self.is_open:
            self._draw_dropdown_list(dx, dy)
    
    def _draw_button(self, dx, dy):
        """ドロップダウンボタンの描画"""
        x = dx + self.x
        y = dy + self.y
        
        # 背景色（ホバー状態に応じて変更）
        bg_color = pyxel.COLOR_LIGHT_BLUE if self.is_hover else pyxel.COLOR_WHITE
        
        # ボタン背景
        pyxel.rect(x, y, self.width, self.height, bg_color)
        pyxel.rectb(x, y, self.width, self.height, pyxel.COLOR_BLACK)
        
        # テキスト表示
        display_text = self.get_display_text()
        text_x = x + 2
        text_y = y + (self.height - pyxel.FONT_HEIGHT) // 2
        
        # テキストが長すぎる場合は切り詰め
        max_chars = (self.width - 20) // pyxel.FONT_WIDTH
        if len(display_text) > max_chars:
            display_text = display_text[:max_chars-3] + "..."
            
        pyxel.text(text_x, text_y, display_text, pyxel.COLOR_BLACK)
        
        # ドロップダウン矢印の描画
        arrow_x = x + self.width - 12
        arrow_y = y + self.height // 2
        
        if self.is_open:
            # 上向き矢印（閉じる）
            pyxel.tri(arrow_x, arrow_y - 2,
                     arrow_x - 3, arrow_y + 2,
                     arrow_x + 3, arrow_y + 2,
                     pyxel.COLOR_BLACK)
        else:
            # 下向き矢印（開く）
            pyxel.tri(arrow_x - 3, arrow_y - 2,
                     arrow_x + 3, arrow_y - 2,
                     arrow_x, arrow_y + 2,
                     pyxel.COLOR_BLACK)
    
    def _draw_dropdown_list(self, dx, dy):
        """ドロップダウンリストの描画"""
        list_x = dx + self.x
        list_y = dy + self.y + self.height
        
        # リスト背景
        pyxel.rect(list_x, list_y, self.width, self.dropdown_height, pyxel.COLOR_WHITE)
        pyxel.rectb(list_x, list_y, self.width, self.dropdown_height, pyxel.COLOR_BLACK)
        
        # 各アイテムの描画
        visible_items = min(len(self.items), self.max_visible_items)
        for i in range(visible_items):
            if i >= len(self.items):
                break
                
            item_y = list_y + i * self.item_height
            
            # アイテムの背景色（選択状態・ホバー状態に応じて変更）
            if i == self.selected_index:
                # 選択中のアイテム
                pyxel.rect(list_x + 1, item_y, self.width - 2, self.item_height, pyxel.COLOR_CYAN)
            elif i == self.hover_item_index:
                # ホバー中のアイテム
                pyxel.rect(list_x + 1, item_y, self.width - 2, self.item_height, pyxel.COLOR_LIGHT_BLUE)
            
            # アイテムテキスト
            text_x = list_x + 3
            text_y = item_y + (self.item_height - pyxel.FONT_HEIGHT) // 2
            
            item_text = self.items[i]
            max_chars = (self.width - 6) // pyxel.FONT_WIDTH
            if len(item_text) > max_chars:
                item_text = item_text[:max_chars-3] + "..."
                
            pyxel.text(text_x, text_y, item_text, pyxel.COLOR_BLACK)


class CheckboxWidget(WidgetBase):
    """チェックボックスウィジェット"""
    
    def __init__(self, dialog, definition):
        super().__init__(dialog, definition)
        
        # チェックボックス固有の属性
        self.is_checked = definition.get("checked", False)
        self.is_hover = False
        self.checkbox_size = definition.get("checkbox_size", 12)
        
        # デフォルトサイズ設定
        if self.width == 0:
            # テキスト幅 + チェックボックス + 余白
            text_width = len(self.text) * pyxel.FONT_WIDTH
            self.width = self.checkbox_size + 4 + text_width
        if self.height == 0:
            self.height = max(self.checkbox_size, pyxel.FONT_HEIGHT)
    
    def get_checked(self) -> bool:
        """チェック状態を取得"""
        return self.is_checked
    
    def set_checked(self, checked: bool):
        """チェック状態を設定"""
        if self.is_checked != checked:
            self.is_checked = checked
            # イベント発火（動的属性システム）
            if hasattr(self, 'on_checked_changed'):
                print(f"[DEBUG] CheckboxWidget: Firing on_checked_changed event: checked={self.is_checked}")
                self.on_checked_changed(self.is_checked)
    
    def update(self):
        """マウス操作の処理"""
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        dx, dy = self.dialog.x, self.dialog.y
        
        # チェックボックス全体の範囲チェック
        widget_x = dx + self.x
        widget_y = dy + self.y
        
        self.is_hover = (widget_x <= mx < widget_x + self.width and 
                        widget_y <= my < widget_y + self.height)
        
        # クリック処理
        if self.is_hover and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            # チェック状態を反転
            self.set_checked(not self.is_checked)
    
    def draw(self):
        """チェックボックスウィジェットの描画"""
        dx, dy = self.dialog.x, self.dialog.y
        x = dx + self.x
        y = dy + self.y
        
        # チェックボックスの描画
        checkbox_x = x
        checkbox_y = y + (self.height - self.checkbox_size) // 2
        
        # 背景色（ホバー状態に応じて変更）
        bg_color = pyxel.COLOR_LIGHT_BLUE if self.is_hover else pyxel.COLOR_WHITE
        
        # チェックボックス背景
        pyxel.rect(checkbox_x, checkbox_y, self.checkbox_size, self.checkbox_size, bg_color)
        pyxel.rectb(checkbox_x, checkbox_y, self.checkbox_size, self.checkbox_size, pyxel.COLOR_BLACK)
        
        # チェックマークの描画（チェックされている場合）
        if self.is_checked:
            # ✓マークを線で描画
            check_x = checkbox_x + 2
            check_y = checkbox_y + self.checkbox_size // 2
            
            # チェックマークの線（簡単な✓形状）
            pyxel.line(check_x, check_y, check_x + 3, check_y + 3, pyxel.COLOR_BLACK)
            pyxel.line(check_x + 3, check_y + 3, check_x + 8, check_y - 2, pyxel.COLOR_BLACK)
        
        # テキストの描画
        if self.text:
            text_x = checkbox_x + self.checkbox_size + 4  # チェックボックスの右側に余白
            text_y = y + (self.height - pyxel.FONT_HEIGHT) // 2
            pyxel.text(text_x, text_y, self.text, pyxel.COLOR_BLACK)

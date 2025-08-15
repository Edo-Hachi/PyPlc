"""
リストボックスコントロールを定義するモジュール（リファクタリング版）

スクロール可能なリストを表示し、ユーザーが項目を選択できるコントロールです。
複雑なスクロールバー実装を廃し、シンプルな上下ボタン方式に変更しました。
"""
import pyxel
from typing import List, Dict, Any, Optional, Tuple
from .control_base import ControlBase

class ListBoxControl(ControlBase):
    """
    リストボックスコントロール（シンプルスクロール版）
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, items: List[str] = None, **kwargs):
        super().__init__(x, y, width, height, **kwargs)
        
        self._items = items or []
        self.selected_index = -1
        self._hovered_index = -1
        self.item_height = kwargs.get('item_height', 12)
        self.color = kwargs.get('color', 0) # 黒
        self.bg_color = kwargs.get('bg_color', 13) # 明るいグレー
        self.hover_color = kwargs.get('hover_color', 11) # 明るい青
        self.selection_color = kwargs.get('selection_color', 5) # 紫
        
        self._scroll_offset = 0
        self._visible_item_count = self.height // self.item_height
        self._is_scrollbar_visible = False
        self._scrollbar_width = 10

        self._up_button_rect = (self.width - self._scrollbar_width, 0, self._scrollbar_width, 10)
        self._down_button_rect = (self.width - self._scrollbar_width, self.height - 10, self._scrollbar_width, 10)
        self.can_focus = True

        self._update_scroll_state()

    @property
    def items(self) -> List[str]:
        return self._items

    @items.setter
    def items(self, value: List[str]):
        if self._items != value:
            self._items = list(value) if value else []
            self.selected_index = -1
            self._hovered_index = -1
            self._scroll_offset = 0
            self._update_scroll_state()
            self._dirty = True

    def _update_scroll_state(self):
        """スクロール関連の状態を更新する"""
        self._visible_item_count = self.height // self.item_height
        self._is_scrollbar_visible = len(self._items) > self._visible_item_count

    def _ensure_visible(self, index: int):
        """指定インデックスが見えるようにスクロール位置を調整"""
        if index < self._scroll_offset:
            self._scroll_offset = index
        elif index >= self._scroll_offset + self._visible_item_count:
            self._scroll_offset = index - self._visible_item_count + 1
        self._scroll_offset = max(0, self._scroll_offset)

    def scroll(self, delta: int):
        """表示領域をスクロールする"""
        if not self._is_scrollbar_visible:
            return
        max_scroll = len(self._items) - self._visible_item_count
        self._scroll_offset = max(0, min(self._scroll_offset + delta, max_scroll))

    def _move_selection(self, delta: int):
        """選択項目を移動する"""
        if not self._items:
            return
        new_index = self.selected_index + delta
        self.selected_index = max(0, min(new_index, len(self._items) - 1))
        self.emit('select', {'index': self.selected_index, 'value': self.items[self.selected_index]})

    def on_click(self, local_x: int, local_y: int) -> bool:
        print(f"[DEBUG] ListBoxControl.on_click called: local_x={local_x}, local_y={local_y}")
        print(f"[DEBUG] ListBoxControl: item_height={self.item_height}, scroll_offset={self._scroll_offset}")
        print(f"[DEBUG] ListBoxControl: items count={len(self._items)}, selected_index={self.selected_index}")
        
        if not super().on_click(local_x, local_y):
            print(f"[DEBUG] ListBoxControl: Super on_click returned False")
            return False

        if self._is_scrollbar_visible:
            # Up button
            bx, by, bw, bh = self._up_button_rect
            if bx <= local_x < bx + bw and by <= local_y < by + bh:
                self.scroll(-1)
                return True
            # Down button
            bx, by, bw, bh = self._down_button_rect
            if bx <= local_x < bx + bw and by <= local_y < by + bh:
                self.scroll(1)
                return True

        item_index = self._scroll_offset + (local_y // self.item_height)
        print(f"[DEBUG] ListBoxControl: Calculated item_index={item_index} (scroll_offset={self._scroll_offset} + local_y={local_y} // item_height={self.item_height})")
        
        if 0 <= item_index < len(self._items):
            print(f"[DEBUG] ListBoxControl: Valid item_index, current selected_index={self.selected_index}")
            if self.selected_index == item_index:
                print(f"[DEBUG] ListBoxControl: Emitting 'activate' for item {item_index}: '{self._items[item_index]}'")
                self.emit('activate', {'index': item_index, 'value': self._items[item_index]})
            else:
                print(f"[DEBUG] ListBoxControl: Setting selected_index to {item_index}, emitting 'select' for item: '{self._items[item_index]}'")
                self.selected_index = item_index
                self.emit('select', {'index': item_index, 'value': self._items[item_index]})
            return True
        else:
            print(f"[DEBUG] ListBoxControl: Invalid item_index {item_index}, not in range 0-{len(self._items)-1}")
        return False

    def on_mouse_wheel(self, delta: int) -> bool:
        self.scroll(-delta) # Pyxelのホイール方向は逆
        return True

    def on_key(self, key: int) -> bool:
        if key == pyxel.KEY_UP:
            self._move_selection(-1)
            return True
        elif key == pyxel.KEY_DOWN:
            self._move_selection(1)
            return True
        elif key == pyxel.KEY_PAGEUP:
            self.scroll(-self._visible_item_count)
            return True
        elif key == pyxel.KEY_PAGEDOWN:
            self.scroll(self._visible_item_count)
            return True
        elif key == pyxel.KEY_HOME:
            self.selected_index = 0
            return True
        elif key == pyxel.KEY_END:
            self.selected_index = len(self._items) - 1 if self._items else 0
            return True
        elif key == pyxel.KEY_RETURN:
            if self.selected_index != -1:
                self.emit('activate', {'index': self.selected_index, 'value': self._items[self.selected_index]})
            return True
        return False

    def draw(self, offset_x: int, offset_y: int):
        if not self.visible:
            return

        x = offset_x + self.x
        y = offset_y + self.y

        pyxel.rect(x, y, self.width, self.height, self.bg_color)
        pyxel.rectb(x, y, self.width, self.height, 0)

        start_index = self._scroll_offset
        end_index = min(start_index + self._visible_item_count, len(self._items))

        for i in range(start_index, end_index):
            item_y = y + (i - start_index) * self.item_height
            item_rect_w = self.width - (self._scrollbar_width if self._is_scrollbar_visible else 0)
            
            bg_col = self.bg_color
            text_col = self.color

            if i == self.selected_index:
                bg_col = self.selection_color
                text_col = pyxel.COLOR_WHITE
            
            pyxel.rect(x, item_y, item_rect_w, self.item_height, bg_col)
            pyxel.text(x + 4, item_y + (self.item_height - 6) // 2, self._items[i], text_col)

        if self._is_scrollbar_visible:
            scrollbar_x = x + self.width - self._scrollbar_width
            pyxel.rect(scrollbar_x, y, self._scrollbar_width, self.height, pyxel.COLOR_NAVY)
            
            # Up button
            bx, by, bw, bh = self._up_button_rect
            pyxel.rect(x + bx, y + by, bw, bh, pyxel.COLOR_PURPLE)
            pyxel.text(x + bx + 2, y + by + 2, "^", pyxel.COLOR_WHITE)
            
            # Down button
            bx, by, bw, bh = self._down_button_rect
            pyxel.rect(x + bx, y + by, bw, bh, pyxel.COLOR_PURPLE)
            pyxel.text(x + bx + 2, y + by + 2, "v", pyxel.COLOR_WHITE)
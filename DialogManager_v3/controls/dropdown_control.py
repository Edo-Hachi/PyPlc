"""
ドロップダウンコントロールを定義するモジュール（最終リファクタリング版）

ユーザーが選択肢から1つを選ぶためのドロップダウンメニューを提供します。
イベントの連鎖を廃し、直接的な状態操作によるシンプルで堅牢な実装。
"""
import pyxel
from typing import List, Optional, Tuple
from .control_base import ControlBase
from .button_control import ButtonControl
from .listbox_control import ListBoxControl

class DropdownControl(ControlBase):
    """
    ドロップダウンメニューコントロール（自己完結・最終版）
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, items: List[str] = None, **kwargs):
        super().__init__(x, y, width, height, **kwargs)
        
        self._items = items or []
        self._selected_index = kwargs.get('selected_index', -1)
        self._is_open = False
        self.can_focus = True

        # --- 子コントロールの作成 ---
        self._button = ButtonControl(x=0, y=0, width=width, height=height, text=self._get_button_text(), **kwargs)
        self._button.parent = self

        list_height = min(len(self._items), kwargs.get('max_visible_items', 5)) * kwargs.get('item_height', 12)
        self._list_box = ListBoxControl(
            x=0, y=height, width=width, height=list_height,
            items=self._items,
            item_height=kwargs.get('item_height', 12)
        )
        self._list_box.parent = self
        self._list_box.visible = False
        # リストボックスからのイベントは受け取る
        self._list_box.on('select', self._on_listbox_select)
        self._list_box.on('activate', self._on_listbox_activate)

        if self._selected_index != -1:
            self._list_box.selected_index = self._selected_index

    @property
    def selected_index(self) -> int:
        return self._selected_index

    @selected_index.setter
    def selected_index(self, value: int):
        if 0 <= value < len(self._items) and self._selected_index != value:
            self._selected_index = value
            self._button.text = self._get_button_text()
            self.emit('change', {'index': value, 'value': self._items[value]})
            self._dirty = True

    def _get_button_text(self) -> str:
        if 0 <= self._selected_index < len(self._items):
            return self._items[self._selected_index]
        return "Select..."

    def is_inside(self, x: int, y: int) -> bool:
        """
        座標がDropdownControl内にあるかを判定（展開時はリストボックス範囲も含む）
        """
        # 基本のボタン部分の判定
        if self.x <= x < self.x + self.width and self.y <= y < self.y + self.height:
            return True
        
        # 展開中の場合はリストボックス範囲も含める
        if self._is_open and self._list_box.visible:
            list_x = self.x + self._list_box.x
            list_y = self.y + self._list_box.y
            list_w = self._list_box.width
            list_h = self._list_box.height
            
            if list_x <= x < list_x + list_w and list_y <= y < list_y + list_h:
                return True
        
        return False

    def _toggle_dropdown(self):
        """ドロップダウンの開閉を切り替える"""
        self._is_open = not self._is_open
        self._list_box.visible = self._is_open

    def _on_listbox_select(self, sender, data):
        """リストボックスで項目が選択された（シングルクリック）"""
        print(f"[DEBUG] DropdownControl._on_listbox_select called with data: {data}")
        self.selected_index = data.get('index', -1)
        print(f"[DEBUG] DropdownControl: Set selected_index to {self.selected_index}, closing dropdown")
        self._is_open = False
        self._list_box.visible = False

    def _on_listbox_activate(self, sender, data):
        """リストボックスで項目が決定された（ダブルクリック等）"""
        self.selected_index = data.get('index', -1)
        self._is_open = False
        self._list_box.visible = False

    def on_click(self, local_x: int, local_y: int) -> bool:
        print(f"[DEBUG] DropdownControl.on_click called: local_x={local_x}, local_y={local_y}")
        print(f"[DEBUG] DropdownControl: is_open={self._is_open}")
        print(f"[DEBUG] DropdownControl: button bounds: x={self._button.x}, y={self._button.y}, w={self._button.width}, h={self._button.height}")
        if self._is_open:
            print(f"[DEBUG] DropdownControl: listbox bounds: x={self._list_box.x}, y={self._list_box.y}, w={self._list_box.width}, h={self._list_box.height}")
        
        super().on_click(local_x, local_y)

        # リストが開いている場合
        if self._is_open:
            if self._list_box.is_inside(local_x, local_y):
                print(f"[DEBUG] DropdownControl: Click inside listbox, delegating to listbox")
                # リストボックス内がクリックされたら、リストボックスに処理を任せる
                list_local_x = local_x - self._list_box.x
                list_local_y = local_y - self._list_box.y
                print(f"[DEBUG] DropdownControl: Calling listbox.on_click({list_local_x}, {list_local_y})")
                return self._list_box.on_click(list_local_x, list_local_y)
            else:
                print(f"[DEBUG] DropdownControl: Click outside listbox, closing dropdown")
                # リストボックスの外側なら、問答無用で閉じる
                self._toggle_dropdown()
                return True

        # リストが閉じていて、ボタンの範囲内がクリックされた場合
        if self._button.is_inside(local_x, local_y):
            print(f"[DEBUG] DropdownControl: Click on button, toggling dropdown")
            self._toggle_dropdown() # 直接、開閉メソッドを呼び出す
            return True

        print(f"[DEBUG] DropdownControl: Click not handled")
        return False

    def on_key(self, key: int) -> bool:
        if self._is_open:
            return self._list_box.on_key(key)
        
        if key == pyxel.KEY_RETURN or key == pyxel.KEY_SPACE:
             self._toggle_dropdown()
             return True
        return False

    def draw(self, offset_x: int, offset_y: int):
        if not self.visible:
            return

        self._button.draw(offset_x + self.x, offset_y + self.y)

        arrow_x = offset_x + self.x + self.width - 12
        arrow_y = offset_y + self.y + (self.height // 2) - 2
        pyxel.tri(arrow_x, arrow_y, arrow_x + 8, arrow_y, arrow_x + 4, arrow_y + 4, pyxel.COLOR_WHITE)

        if self._is_open:
            self._list_box.draw(offset_x + self.x, offset_y + self.y)

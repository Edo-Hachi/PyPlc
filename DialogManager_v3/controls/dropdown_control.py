"""
ドロップダウンコントロールを定義するモジュール

ユーザーが選択肢から1つを選ぶためのドロップダウンメニューを提供します。
"""
from typing import List, Dict, Any, Optional, Tuple
from .control_base import ControlBase
from .button_control import ButtonControl
from .listbox_control import ListBoxControl  # 後で実装


class DropdownControl(ControlBase):
    """
    ドロップダウンメニューコントロール
    
    ユーザーが選択肢から1つを選ぶためのドロップダウンメニューを表示します。
    """
    
    def __init__(self, x: int, y: int, width: int, items: List[str] = None, **kwargs):
        """
        ドロップダウンコントロールを初期化します。
        
        Args:
            x: X座標
            y: Y座標
            width: コントロールの幅
            items: 選択肢のリスト
            **kwargs: 追加のプロパティ
        """
        # デフォルトの高さを設定
        height = kwargs.pop('height', 24)  # ドロップダウンの高さ
        
        super().__init__(x, y, width, height, **kwargs)
        
        self._items = items or []
        self._selected_index = -1
        self._is_open = False
        self._button_text = kwargs.get('button_text', 'Select...')
        self._item_height = kwargs.get('item_height', 20)
        self._max_visible_items = kwargs.get('max_visible_items', 5)
        self._color = kwargs.get('color', 7)  # デフォルトは白
        self._bg_color = kwargs.get('bg_color', 5)  # デフォルトは紫
        self._hover_color = kwargs.get('hover_color', 3)  # ホバー時の色
        self._disabled_color = kwargs.get('disabled_color', 13)  # 無効時の色
        self._drop_down_button = None  # type: Optional[ButtonControl]
        self._list_box = None  # type: Optional[ListBoxControl]
        self.can_focus = True
        
        # ドロップダウンボタンを作成
        self._create_dropdown_button()
    
    @property
    def items(self) -> List[str]:
        """ドロップダウンの選択肢を取得します。"""
        return self._items
    
    @items.setter
    def items(self, value: List[str]) -> None:
        """
        ドロップダウンの選択肢を設定します。
        
        Args:
            value: 選択肢のリスト
        """
        if self._items != value:
            self._items = list(value) if value else []
            self._selected_index = -1 if not self._items else 0
            self._update_button_text()
            self._dirty = True
    
    @property
    def selected_index(self) -> int:
        """選択されているアイテムのインデックスを取得します。"""
        return self._selected_index
    
    @selected_index.setter
    def selected_index(self, value: int) -> None:
        """
        選択するアイテムのインデックスを設定します。
        
        Args:
            value: 選択するアイテムのインデックス
        """
        if 0 <= value < len(self._items) and self._selected_index != value:
            self._selected_index = value
            self._update_button_text()
            self._dirty = True
            self.emit('change', {'index': value, 'value': self._items[value]})
    
    @property
    def selected_value(self) -> Optional[str]:
        """選択されているアイテムの値を取得します。"""
        if 0 <= self._selected_index < len(self._items):
            return self._items[self._selected_index]
        return None
    
    @selected_value.setter
    def selected_value(self, value: str) -> None:
        """
        選択するアイテムの値を設定します。
        
        Args:
            value: 選択するアイテムの値
        """
        if value in self._items:
            self.selected_index = self._items.index(value)
    
    def _create_dropdown_button(self) -> None:
        """ドロップダウンボタンを作成します。"""
        self._drop_down_button = ButtonControl(
            x=0,
            y=0,
            width=self.width,
            height=self.height,
            text=self._button_text,
            color=self._color,
            bg_color=self._bg_color,
            hover_color=self._hover_color,
            disabled_color=self._disabled_color
        )
        
        # ボタンのクリックイベントを設定
        self._drop_down_button.on('click', self._on_dropdown_button_click)
    
    def _update_button_text(self) -> None:
        """ボタンのテキストを更新します。"""
        if self._drop_down_button:
            if 0 <= self._selected_index < len(self._items):
                self._drop_down_button.text = self._items[self._selected_index]
            else:
                self._drop_down_button.text = self._button_text
    
    def _on_dropdown_button_click(self, sender: Any, data: Dict[str, Any]) -> None:
        """ドロップダウンボタンがクリックされたときの処理です。"""
        if self._is_open:
            self.close_dropdown()
        else:
            self.open_dropdown()
    
    def open_dropdown(self) -> None:
        """ドロップダウンメニューを開きます。"""
        if self._is_open or not self.enabled or not self.visible:
            return
            
        # ドロップダウンリストを作成
        list_height = min(len(self._items), self._max_visible_items) * self._item_height
        list_y = self.y + self.height
        
        # 画面からはみ出す場合は上に表示
        if self.parent and (list_y + list_height) > 160:  # 仮の画面高さ
            list_y = self.y - list_height
        
        self._list_box = ListBoxControl(
            x=0,
            y=self.height,  # ボタンの下に配置
            width=self.width,
            height=list_height,
            items=self._items,
            color=self._color,
            bg_color=0,  # 背景色
            hover_color=self._hover_color,
            selection_color=1,  # 選択色
            item_height=self._item_height
        )
        
        # リストボックスの選択イベントを設定
        self._list_box.on('select', self._on_listbox_select)
        
        # リストボックスをダイアログに追加
        if self.parent:
            self.parent.add_control(self._list_box)
            # リストボックスの位置を調整
            self._list_box.x = self.x
            self._list_box.y = list_y
        
        self._is_open = True
        self._dirty = True
    
    def close_dropdown(self) -> None:
        """ドロップダウンメニューを閉じます。"""
        if not self._is_open or not self._list_box:
            return
            
        # リストボックスを削除
        if self.parent:
            self.parent.remove_control(self._list_box)
        
        self._list_box = None
        self._is_open = False
        self._dirty = True
    
    def _on_listbox_select(self, sender: Any, data: Dict[str, Any]) -> None:
        """リストボックスでアイテムが選択されたときの処理です。"""
        if 'index' in data and 0 <= data['index'] < len(self._items):
            self.selected_index = data['index']
            self.close_dropdown()
    
    def on_click(self, local_x: int, local_y: int) -> bool:
        """
        クリックイベントを処理します。
        
        Args:
            local_x: コントロールからの相対X座標
            local_y: コントロールからの相対Y座標
            
        Returns:
            bool: イベントが処理された場合はTrue
        """
        if not super().on_click(local_x, local_y):
            # ドロップダウンの外側をクリックした場合は閉じる
            if self._is_open:
                self.close_dropdown()
                return True
            return False
            
        return True
    
    def on_gain_focus(self) -> None:
        """フォーカスを得たときに呼び出されます。"""
        super().on_gain_focus()
        if self._drop_down_button:
            self._drop_down_button.on_gain_focus()
    
    def on_lose_focus(self) -> None:
        """フォーカスを失ったときに呼び出されます。"""
        super().on_lose_focus()
        if self._drop_down_button:
            self._drop_down_button.on_lose_focus()
        
        # フォーカスを失ったらドロップダウンを閉じる
        self.close_dropdown()
    
    def update(self) -> None:
        """コントロールの状態を更新します。"""
        if self._drop_down_button:
            self._drop_down_button.update()
        
        if self._list_box:
            self._list_box.update()
    
    def draw(self, offset_x: int, offset_y: int) -> None:
        """
        ドロップダウンコントロールを描画します。
        
        Args:
            offset_x: 親要素のXオフセット
            offset_y: 親要素のYオフセット
        """
        if not self.visible:
            return
            
        # ドロップダウンボタンを描画
        if self._drop_down_button:
            self._drop_down_button.draw(offset_x + self.x, offset_y + self.y)
        
        # ドロップダウン矢印を描画
        arrow_x = offset_x + self.x + self.width - 12
        arrow_y = offset_y + self.y + (self.height // 2) - 2
        
        # 実際のPyxelのAPIに合わせて調整が必要
        # 下向き矢印を描画
        # pyxel.tri(arrow_x, arrow_y, arrow_x + 8, arrow_y, arrow_x + 4, arrow_y + 4, self._color)
        
        # ドロップダウンリストを描画
        if self._is_open and self._list_box and self.parent:
            self._list_box.draw(offset_x, offset_y)
    
    def set_enabled(self, enabled: bool) -> None:
        """
        コントロールの有効/無効を設定します。
        
        Args:
            enabled: 有効にする場合はTrue
        """
        super().set_enabled(enabled)
        if self._drop_down_button:
            self._drop_down_button.set_enabled(enabled)
        
        if not enabled and self._is_open:
            self.close_dropdown()

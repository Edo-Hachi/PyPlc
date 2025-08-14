"""
リストボックスコントロールを定義するモジュール

スクロール可能なリストを表示し、ユーザーが項目を選択できるコントロールです。
"""
from typing import List, Dict, Any, Optional, Tuple
from .control_base import ControlBase


class ListBoxControl(ControlBase):
    """
    リストボックスコントロール
    
    スクロール可能なリストを表示し、ユーザーが項目を選択できます。
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, items: List[str] = None, **kwargs):
        """
        リストボックスコントロールを初期化します。
        
        Args:
            x: X座標
            y: Y座標
            width: コントロールの幅
            height: コントロールの高さ
            items: 表示する項目のリスト
            **kwargs: 追加のプロパティ
        """
        super().__init__(x, y, width, height, **kwargs)
        
        self._items = items or []
        self._selected_index = -1
        self._hovered_index = -1
        self._item_height = kwargs.get('item_height', 20)
        self._color = kwargs.get('color', 7)  # デフォルトは白
        self._bg_color = kwargs.get('bg_color', 0)  # デフォルトは黒
        self._hover_color = kwargs.get('hover_color', 1)  # ホバー時の色
        self._selection_color = kwargs.get('selection_color', 4)  # 選択色
        self._scroll_offset = 0
        self._visible_item_count = self.height // self._item_height
        self._scrollbar_width = 8
        self._is_scrollbar_visible = len(self._items) > self._visible_item_count
        self._scrollbar_thumb_rect = (0, 0, 0, 0)  # スクロールバーのつまみの矩形
        self._is_scrollbar_dragging = False
        self._scrollbar_drag_offset = 0
        self.can_focus = True
    
    @property
    def items(self) -> List[str]:
        """リストボックスの項目を取得します。"""
        return self._items
    
    @items.setter
    def items(self, value: List[str]) -> None:
        """
        リストボックスの項目を設定します。
        
        Args:
            value: 表示する項目のリスト
        """
        if self._items != value:
            self._items = list(value) if value else []
            self._selected_index = -1
            self._hovered_index = -1
            self._scroll_offset = 0
            self._is_scrollbar_visible = len(self._items) > self._visible_item_count
            self._dirty = True
    
    @property
    def selected_index(self) -> int:
        """選択されている項目のインデックスを取得します。"""
        return self._selected_index
    
    @selected_index.setter
    def selected_index(self, value: int) -> None:
        """
        選択する項目のインデックスを設定します。
        
        Args:
            value: 選択する項目のインデックス
        """
        if -1 <= value < len(self._items) and self._selected_index != value:
            self._selected_index = value
            self._ensure_visible(value)
            self._dirty = True
            self.emit('select', {'index': value, 'value': self._items[value] if value != -1 else None})
    
    @property
    def selected_value(self) -> Optional[str]:
        """選択されている項目の値を取得します。"""
        if 0 <= self._selected_index < len(self._items):
            return self._items[self._selected_index]
        return None
    
    def _ensure_visible(self, index: int) -> None:
        """指定されたインデックスの項目が表示されるようにスクロール位置を調整します。"""
        if index < 0 or index >= len(self._items):
            return
            
        # 表示範囲外の場合はスクロール位置を調整
        if index < self._scroll_offset:
            self._scroll_offset = index
        elif index >= self._scroll_offset + self._visible_item_count:
            self._scroll_offset = index - self._visible_item_count + 1
        
        self._update_scrollbar_thumb()
    
    def _update_scrollbar_thumb(self) -> None:
        """スクロールバーのつまみの位置を更新します。"""
        if not self._is_scrollbar_visible or len(self._items) <= 1:
            return
            
        content_height = len(self._items) * self._item_height
        visible_height = self._visible_item_count * self._item_height
        
        # つまみの高さを計算（表示領域の割合に応じて）
        thumb_height = max(20, int((visible_height / content_height) * self.height))
        
        # つまみの位置を計算
        scroll_range = max(1, len(self._items) - self._visible_item_count)
        thumb_y = int((self._scroll_offset / scroll_range) * (self.height - thumb_height))
        
        # つまみの矩形を更新
        self._scrollbar_thumb_rect = (
            self.width - self._scrollbar_width + 1,  # x
            thumb_y,  # y
            self._scrollbar_width - 2,  # width
            thumb_height - 1  # height
        )
    
    def _get_item_at_position(self, local_x: int, local_y: int) -> int:
        """指定された座標にある項目のインデックスを取得します。"""
        if (local_x < 0 or local_x >= self.width - (self._scrollbar_width if self._is_scrollbar_visible else 0) or
                local_y < 0 or local_y >= self.height):
            return -1
            
        item_index = self._scroll_offset + (local_y // self._item_height)
        if 0 <= item_index < len(self._items):
            return item_index
        return -1
    
    def _is_in_scrollbar(self, local_x: int, local_y: int) -> bool:
        """指定された座標がスクロールバー上にあるかどうかを返します。"""
        if not self._is_scrollbar_visible:
            return False
            
        return (self.width - self._scrollbar_width <= local_x < self.width and
                0 <= local_y < self.height)
    
    def _is_in_scrollbar_thumb(self, local_x: int, local_y: int) -> bool:
        """指定された座標がスクロールバーのつまみ上にあるかどうかを返します。"""
        if not self._is_scrollbar_visible or not self._scrollbar_thumb_rect:
            return False
            
        thumb_x, thumb_y, thumb_w, thumb_h = self._scrollbar_thumb_rect
        return (thumb_x <= local_x < thumb_x + thumb_w and
                thumb_y <= local_y < thumb_y + thumb_h)
    
    def _scroll_to(self, local_y: int) -> None:
        """指定されたY座標にスクロールします。"""
        if not self._is_scrollbar_visible or len(self._items) <= 1:
            return
            
        # スクロール位置を計算
        scroll_range = max(1, len(self._items) - self._visible_item_count)
        thumb_height = self._scrollbar_thumb_rect[3]
        
        # つまみの中心を基準にスクロール位置を計算
        thumb_center = local_y - (thumb_height // 2)
        thumb_center = max(0, min(thumb_center, self.height - thumb_height))
        
        # スクロール位置を更新
        new_scroll_offset = int((thumb_center / (self.height - thumb_height)) * scroll_range)
        new_scroll_offset = max(0, min(new_scroll_offset, len(self._items) - self._visible_item_count))
        
        if new_scroll_offset != self._scroll_offset:
            self._scroll_offset = new_scroll_offset
            self._dirty = True
    
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
            return False
            
        # スクロールバーのクリック処理
        if self._is_scrollbar_visible and self._is_in_scrollbar(local_x, local_y):
            if self._is_in_scrollbar_thumb(local_x, local_y):
                # つまみをドラッグ開始
                self._is_scrollbar_dragging = True
                self._scrollbar_drag_offset = local_y - self._scrollbar_thumb_rect[1]
            else:
                # つまみ以外をクリックした場合はその位置にスクロール
                self._scroll_to(local_y)
            return True
        
        # 項目のクリック処理
        item_index = self._get_item_at_position(local_x, local_y)
        if item_index != -1:
            self.selected_index = item_index
            self.emit('click', {'index': item_index, 'value': self._items[item_index]})
            return True
            
        return True
    
    def on_mouse_move(self, local_x: int, local_y: int) -> None:
        """
        マウス移動イベントを処理します。
        
        Args:
            local_x: コントロールからの相対X座標
            local_y: コントロールからの相対Y座標
        """
        # スクロールバーのドラッグ処理
        if self._is_scrollbar_dragging:
            self._scroll_to(local_y - self._scrollbar_drag_offset)
            return
        
        # ホバー状態の更新
        new_hovered_index = self._get_item_at_position(local_x, local_y)
        if new_hovered_index != self._hovered_index:
            self._hovered_index = new_hovered_index
            self._dirty = True
    
    def on_mouse_up(self, local_x: int, local_y: int) -> None:
        """
        マウスボタン解放イベントを処理します。
        
        Args:
            local_x: コントロールからの相対X座標
            local_y: コントロールからの相対Y座標
        """
        # スクロールバーのドラッグを終了
        if self._is_scrollbar_dragging:
            self._is_scrollbar_dragging = False
    
    def on_mouse_wheel(self, delta: int) -> bool:
        """
        マウスホイールイベントを処理します。
        
        Args:
            delta: ホイールの移動量
            
        Returns:
            bool: イベントが処理された場合はTrue
        """
        if not self._is_scrollbar_visible:
            return False
            
        # スクロール位置を更新
        new_scroll_offset = self._scroll_offset - delta
        max_scroll = max(0, len(self._items) - self._visible_item_count)
        new_scroll_offset = max(0, min(new_scroll_offset, max_scroll))
        
        if new_scroll_offset != self._scroll_offset:
            self._scroll_offset = new_scroll_offset
            self._update_scrollbar_thumb()
            self._dirty = True
            return True
            
        return False
    
    def on_gain_focus(self) -> None:
        """フォーカスを得たときに呼び出されます。"""
        super().on_gain_focus()
        self._dirty = True
    
    def on_lose_focus(self) -> None:
        """フォーカスを失ったときに呼び出されます。"""
        super().on_lose_focus()
        self._dirty = True
    
    def update(self) -> None:
        """コントロールの状態を更新します。"""
        pass
    
    def draw(self, offset_x: int, offset_y: int) -> None:
        """
        リストボックスを描画します。
        
        Args:
            offset_x: 親要素のXオフセット
            offset_y: 親要素のYオフセット
        """
        if not self.visible:
            return
            
        # 描画位置を計算
        x = offset_x + self.x
        y = offset_y + self.y
        
        # 背景を描画
        # 実際のPyxelのAPIに合わせて調整が必要
        # pyxel.rect(x, y, self.width, self.height, self._bg_color)
        # pyxel.rectb(x, y, self.width, self.height, 7)  # 白い枠
        
        # スクロールバーを描画
        if self._is_scrollbar_visible:
            # スクロールバーの背景
            scrollbar_x = x + self.width - self._scrollbar_width
            # pyxel.rect(scrollbar_x, y, self._scrollbar_width, self.height, 13)  # グレーの背景
            
            # スクロールバーのつまみを描画
            if self._scrollbar_thumb_rect:
                thumb_x, thumb_y, thumb_w, thumb_h = self._scrollbar_thumb_rect
                # pyxel.rect(scrollbar_x + 1, y + thumb_y, thumb_w, thumb_h, 7)  # 白いつまみ
        
        # 表示範囲内の項目を描画
        start_index = self._scroll_offset
        end_index = min(start_index + self._visible_item_count, len(self._items))
        
        for i in range(start_index, end_index):
            item_y = y + (i - start_index) * self._item_height
            item_rect = (x + 1, item_y, self.width - (self._scrollbar_width if self._is_scrollbar_visible else 2), self._item_height - 1)
            
            # 選択状態またはホバー状態に応じた色を設定
            if i == self._selected_index:
                # 選択されている項目の背景を描画
                # pyxel.rect(*item_rect, self._selection_color)
                text_color = 7  # 白
            elif i == self._hovered_index:
                # ホバーされている項目の背景を描画
                # pyxel.rect(*item_rect, self._hover_color)
                text_color = 7  # 白
            else:
                text_color = self._color
            
            # テキストを描画
            text = self._items[i]
            text_x = x + 4
            text_y = item_y + (self._item_height - 8) // 2  # 垂直中央揃え
            # pyxel.text(text_x, text_y, text, text_color)
        
        # フォーカス表示（オプション）
        if self.parent and self.parent.focused_control == self:
            # pyxel.rectb(x-1, y-1, self.width+2, self.height+2, 7)  # フォーカス枠
            pass

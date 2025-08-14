"""
テキストボックスコントロールを定義するモジュール

ユーザーがテキストを入力・編集できるテキストボックスコンポーネントを提供します。
"""
import time
from typing import Optional, Dict, Any, List, Tuple
from .control_base import ControlBase


class TextBoxControl(ControlBase):
    """
    テキスト入力が可能なテキストボックスコントロール
    
    ユーザーがテキストを入力・編集できるテキストボックスを表示します。
    """
    
    def __init__(self, x: int, y: int, width: int, text: str = "", **kwargs):
        """
        テキストボックスコントロールを初期化します。
        
        Args:
            x: X座標
            y: Y座標
            width: テキストボックスの幅
            text: 初期テキスト
            **kwargs: 追加のプロパティ
        """
        # デフォルトの高さを設定
        height = kwargs.pop('height', 20)  # テキストボックスの高さ
        
        super().__init__(x, y, width, height, **kwargs)
        
        self._text = text
        self._cursor_pos = len(text)
        self._cursor_visible = True
        self._cursor_blink_timer = 0
        self._cursor_blink_interval = 0.5  # 秒単位のカーソル点滅間隔
        self._last_blink_time = time.time()
        self._color = kwargs.get('color', 7)  # デフォルトは白
        self._bg_color = kwargs.get('bg_color', 0)  # デフォルトは黒
        self._selection_start = None  # type: Optional[int]
        self._selection_end = None  # type: Optional[int]
        self._max_length = kwargs.get('max_length', 0)  # 0 = 制限なし
        self._readonly = kwargs.get('readonly', False)
        self._password_char = kwargs.get('password_char', None)  # パスワード表示用の文字
        self.can_focus = True
        
        # テキストの表示開始位置（スクロール用）
        self._scroll_offset = 0
    
    @property
    def text(self) -> str:
        """テキストボックスのテキストを取得します。"""
        return self._text
    
    @text.setter
    def text(self, value: str) -> None:
        """
        テキストボックスのテキストを設定します。
        
        Args:
            value: 設定するテキスト
        """
        if self._text != value:
            self._text = str(value)
            self._cursor_pos = min(self._cursor_pos, len(self._text))
            self._dirty = True
            self.emit('change', {'value': self._text})
    
    @property
    def cursor_position(self) -> int:
        """カーソル位置を取得します。"""
        return self._cursor_pos
    
    @cursor_position.setter
    def cursor_position(self, value: int) -> None:
        """
        カーソル位置を設定します。
        
        Args:
            value: 新しいカーソル位置
        """
        new_pos = max(0, min(value, len(self._text)))
        if self._cursor_pos != new_pos:
            self._cursor_pos = new_pos
            self._cursor_visible = True
            self._last_blink_time = time.time()
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
            
        # クリック位置に応じてカーソル位置を設定
        self._update_cursor_position(local_x)
        self._selection_start = None
        self._selection_end = None
        self._dirty = True
        return True
    
    def on_mouse_down(self, local_x: int, local_y: int) -> bool:
        """
        マウスボタン押下イベントを処理します。
        
        Args:
            local_x: コントロールからの相対X座標
            local_y: コントロールからの相対Y座標
            
        Returns:
            bool: イベントが処理された場合はTrue
        """
        if not self.enabled or not self.visible or self._readonly:
            return False
            
        # テキスト選択を開始
        self._update_cursor_position(local_x)
        self._selection_start = self._cursor_pos
        self._selection_end = self._cursor_pos
        self._dirty = True
        return True
    
    def on_mouse_drag(self, local_x: int, local_y: int) -> bool:
        """
        マウスドラッグイベントを処理します。
        
        Args:
            local_x: コントロールからの相対X座標
            local_y: コントロールからの相対Y座標
            
        Returns:
            bool: イベントが処理された場合はTrue
        """
        if not self.enabled or not self.visible or self._readonly or self._selection_start is None:
            return False
            
        # テキスト選択を更新
        old_pos = self._cursor_pos
        self._update_cursor_position(local_x)
        
        if self._cursor_pos != old_pos:
            self._selection_end = self._cursor_pos
            self._dirty = True
            
        return True
    
    def on_key(self, key: int) -> bool:
        """
        キーボード入力を処理します。
        
        Args:
            key: 押されたキーのコード
            
        Returns:
            bool: イベントが処理された場合はTrue
        """
        if not self.enabled or not self.visible or self._readonly:
            return False
            
        handled = True
        
        # 特殊キーの処理
        if key == 8:  # Backspace
            self._handle_backspace()
        elif key == 127:  # Delete
            self._handle_delete()
        elif key == 13:  # Enter
            self.emit('enter', {'value': self._text})
        elif key == 37:  # Left Arrow
            self._move_cursor(-1, False)
        elif key == 39:  # Right Arrow
            self._move_cursor(1, False)
        elif key == 36:  # Home
            self.cursor_position = 0
        elif key == 35:  # End
            self.cursor_position = len(self._text)
        else:
            handled = False
        
        # テキストが変更されたことを通知
        if handled:
            self.emit('change', {'value': self._text})
            
        return handled
    
    def on_text(self, char: str) -> bool:
        """
        テキスト入力を処理します。
        
        Args:
            char: 入力された文字
            
        Returns:
            bool: イベントが処理された場合はTrue
        """
        if not self.enabled or not self.visible or self._readonly:
            return False
            
        # 最大文字数チェック
        if self._max_length > 0 and len(self._text) >= self._max_length:
            return False
            
        # 選択範囲がある場合は削除
        if self._has_selection():
            self._delete_selection()
        
        # テキストを挿入
        self._text = self._text[:self._cursor_pos] + char + self._text[self._cursor_pos:]
        self._cursor_pos += len(char)
        self._dirty = True
        
        # 変更を通知
        self.emit('change', {'value': self._text})
        return True
    
    def on_gain_focus(self) -> None:
        """フォーカスを得たときに呼び出されます。"""
        super().on_gain_focus()
        self._cursor_visible = True
        self._last_blink_time = time.time()
        self._dirty = True
        self.emit('focus')
    
    def on_lose_focus(self) -> None:
        """フォーカスを失ったときに呼び出されます。"""
        super().on_lose_focus()
        self._cursor_visible = False
        self._selection_start = None
        self._selection_end = None
        self._dirty = True
        self.emit('blur')
    
    def update(self) -> None:
        """コントロールの状態を更新します。"""
        # カーソルの点滅を更新
        current_time = time.time()
        if current_time - self._last_blink_time >= self._cursor_blink_interval:
            self._cursor_visible = not self._cursor_visible
            self._last_blink_time = current_time
            self._dirty = True
    
    def draw(self, offset_x: int, offset_y: int) -> None:
        """
        テキストボックスを描画します。
        
        Args:
            offset_x: 親要素のXオフセット
            offset_y: 親要素のYオフセット
        """
        if not self.visible:
            return
            
        # 描画位置を計算
        x = offset_x + self.x
        y = offset_y + self.y
        
        # テキストボックスの背景を描画
        # 実際のPyxelのAPIに合わせて調整が必要
        # pyxel.rect(x, y, self.width, self.height, self._bg_color)
        # pyxel.rectb(x, y, self.width, self.height, 7)  # 白い枠
        
        # フォーカスがある場合はハイライト
        if self.parent and self.parent.focused_control == self:
            # pyxel.rectb(x-1, y-1, self.width+2, self.height+2, 7)  # フォーカス枠
            pass
        
        # テキストを描画
        text = self._get_display_text()
        text_x = x + 4  # 左パディング
        text_y = y + (self.height - 8) // 2  # 垂直中央揃え
        
        # 実際のPyxelのAPIに合わせて調整が必要
        # pyxel.text(text_x, text_y, text, self._color)
        
        # 選択範囲を描画
        if self._has_selection() and self._selection_start is not None and self._selection_end is not None:
            # 選択範囲の描画を実装
            pass
        
        # カーソルを描画
        if self._cursor_visible and self.parent and self.parent.focused_control == self:
            cursor_x = x + 4 + self._get_text_width(text[:self._cursor_pos])
            cursor_y = y + 2
            cursor_height = self.height - 4
            # pyxel.line(cursor_x, cursor_y, cursor_x, cursor_y + cursor_height - 1, 7)  # 白い縦線
    
    def _get_display_text(self) -> str:
        """表示用のテキストを取得します。"""
        if self._password_char:
            return self._password_char * len(self._text)
        return self._text
    
    def _get_text_width(self, text: str) -> int:
        """テキストの表示幅を取得します。"""
        return len(text) * 6  # 1文字6ピクセルを仮定
    
    def _update_cursor_position(self, local_x: int) -> None:
        """クリック位置に基づいてカーソル位置を更新します。"""
        # クリック位置に最も近い文字位置を計算
        text = self._get_display_text()
        click_x = local_x - 4  # 左パディングを考慮
        
        if click_x <= 0:
            self.cursor_position = 0
            return
            
        # 各文字の右端の位置を計算して、クリック位置を超える最初の位置を見つける
        total_width = 0
        for i, char in enumerate(text):
            char_width = 6  # 1文字6ピクセルを仮定
            if total_width + char_width / 2 > click_x:
                self.cursor_position = i
                return
            total_width += char_width
        
        self.cursor_position = len(text)
    
    def _move_cursor(self, direction: int, shift_pressed: bool) -> None:
        """カーソルを移動します。"""
        new_pos = self._cursor_pos + direction
        if 0 <= new_pos <= len(self._text):
            if shift_pressed:
                # シフトキーが押されている場合は選択範囲を拡張
                if self._selection_start is None:
                    self._selection_start = self._cursor_pos
                self._selection_end = new_pos
            else:
                # シフトキーが押されていない場合は選択を解除
                self._selection_start = None
                self._selection_end = None
                
            self.cursor_position = new_pos
    
    def _handle_backspace(self) -> None:
        """Backspaceキーの処理を行います。"""
        if self._has_selection():
            self._delete_selection()
        elif self._cursor_pos > 0:
            self._text = self._text[:self._cursor_pos - 1] + self._text[self._cursor_pos:]
            self.cursor_position -= 1
            self._dirty = True
    
    def _handle_delete(self) -> None:
        """Deleteキーの処理を行います。"""
        if self._has_selection():
            self._delete_selection()
        elif self._cursor_pos < len(self._text):
            self._text = self._text[:self._cursor_pos] + self._text[self._cursor_pos + 1:]
            self._dirty = True
    
    def _has_selection(self) -> bool:
        """テキストが選択されているかどうかを返します。"""
        return (self._selection_start is not None and 
                self._selection_end is not None and 
                self._selection_start != self._selection_end)
    
    def _delete_selection(self) -> None:
        """選択されているテキストを削除します。"""
        if not self._has_selection() or self._selection_start is None or self._selection_end is None:
            return
            
        start = min(self._selection_start, self._selection_end)
        end = max(self._selection_start, self._selection_end)
        
        self._text = self._text[:start] + self._text[end:]
        self.cursor_position = start
        self._selection_start = None
        self._selection_end = None
        self._dirty = True

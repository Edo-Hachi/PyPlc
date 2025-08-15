"""
ボタンコントロールを定義するモジュール

クリック可能なボタンコンポーネントを提供します。
"""
import pyxel
from typing import Optional, Dict, Any, Callable
from .control_base import ControlBase


class ButtonControl(ControlBase):
    """
    クリック可能なボタンコントロール
    
    ユーザーがクリックできるボタンを表示します。
    """
    
    def __init__(self, x: int, y: int, text: str = "", **kwargs):
        """
        ボタンコントロールを初期化します。
        
        Args:
            x: X座標
            y: Y座標
            text: ボタンに表示するテキスト
            **kwargs: 追加のプロパティ
        """
        # デフォルトのサイズを設定（テキストサイズに応じて自動調整）
        width = kwargs.pop('width', len(text) * 8 + 16)  # テキスト幅 + パディング
        height = kwargs.pop('height', 24)  # ボタンの高さ
        
        super().__init__(x, y, width, height, **kwargs)
        
        self._text = text
        self._color = kwargs.get('color', pyxel.COLOR_WHITE)
        self._bg_color = kwargs.get('bg_color', pyxel.COLOR_DARK_BLUE)
        self._hover_color = kwargs.get('hover_color', pyxel.COLOR_GREEN)
        self._pressed_color = kwargs.get('pressed_color', pyxel.COLOR_RED)
        self._disabled_color = kwargs.get('disabled_color', pyxel.COLOR_GRAY)
        self._is_pressed = False
        self._is_hovered = False
        self.can_focus = True
    
    @property
    def text(self) -> str:
        """ボタンに表示されるテキストを取得します。"""
        return self._text
    
    @text.setter
    def text(self, value: str) -> None:
        """
        ボタンに表示するテキストを設定します。
        
        Args:
            value: 表示するテキスト
        """
        if self._text != value:
            self._text = str(value)
            self._dirty = True
    
    def on_click(self, local_x: int, local_y: int) -> bool:
        if not super().on_click(local_x, local_y):
            return False
            
        self._is_pressed = True
        self._dirty = True
        self.emit('click')
        return True
    
    def on_mouse_enter(self) -> None:
        super().on_mouse_enter()
        self._is_hovered = True
        self._dirty = True
    
    def on_mouse_leave(self) -> None:
        super().on_mouse_leave()
        self._is_hovered = False
        self._is_pressed = False
        self._dirty = True
    
    def on_key(self, key: int) -> bool:
        if key == pyxel.KEY_RETURN or key == pyxel.KEY_SPACE:
            self._is_pressed = True
            self._dirty = True
            self.emit('click')
            return True
        return False
    
    def update(self) -> None:
        if self._is_pressed:
            self._is_pressed = False
            self._dirty = True
    
    def draw(self, offset_x: int, offset_y: int) -> None:
        if not self.visible:
            return
            
        x = offset_x + self.x
        y = offset_y + self.y
        
        # ボタンの状態に応じた色を決定
        if not self.enabled:
            color = self._disabled_color
        elif self._is_pressed:
            color = self._pressed_color
        elif self._is_hovered or self.has_focus: # 親に依存せず、自身のフォーカス状態を参照
            color = self._hover_color
        else:
            color = self._bg_color
        
        pyxel.rect(x, y, self.width, self.height, color)
        pyxel.rectb(x, y, self.width, self.height, pyxel.COLOR_WHITE)
        
        text_width = len(self._text) * 4
        text_x = x + (self.width - text_width) // 2
        text_y = y + (self.height - 6) // 2
        
        pyxel.text(text_x, text_y, self._text, self._color)
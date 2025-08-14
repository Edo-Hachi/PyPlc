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
        self._color = kwargs.get('color', 7)  # デフォルトは白
        self._bg_color = kwargs.get('bg_color', 2)  # デフォルトは緑
        self._hover_color = kwargs.get('hover_color', 3)  # ホバー時の色
        self._pressed_color = kwargs.get('pressed_color', 4)  # 押下時の色
        self._disabled_color = kwargs.get('disabled_color', 13)  # 無効時の色
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
            
        self._is_pressed = True
        self._dirty = True
        self.emit('click')
        return True
    
    def on_mouse_enter(self) -> None:
        """マウスがボタン上に入ったときに呼び出されます。"""
        super().on_mouse_enter()
        self._is_hovered = True
        self._dirty = True
    
    def on_mouse_leave(self) -> None:
        """マウスがボタンから出たときに呼び出されます。"""
        super().on_mouse_leave()
        self._is_hovered = False
        self._is_pressed = False
        self._dirty = True
    
    def on_gain_focus(self) -> None:
        """ボタンがフォーカスを得たときに呼び出されます。"""
        super().on_gain_focus()
        self._dirty = True
    
    def on_lose_focus(self) -> None:
        """ボタンがフォーカスを失ったときに呼び出されます。"""
        super().on_lose_focus()
        self._is_pressed = False
        self._dirty = True
    
    def on_key(self, key: int) -> bool:
        """
        キーボード入力を処理します。
        
        Args:
            key: 押されたキーのコード
            
        Returns:
            bool: イベントが処理された場合はTrue
        """
        # Enterキーまたはスペースキーでクリックをシミュレート
        if key == 13 or key == 32:  # Enter or Space
            self._is_pressed = True
            self._dirty = True
            self.emit('click')
            return True
            
        return False
    
    def update(self) -> None:
        """ボタンの状態を更新します。"""
        if self._is_pressed:
            self._is_pressed = False
            self._dirty = True
    
    def draw(self, offset_x: int, offset_y: int) -> None:
        """
        ボタンを描画します。
        
        Args:
            offset_x: 親要素のXオフセット
            offset_y: 親要素のYオフセット
        """
        if not self.visible:
            return
            
        # 描画位置を計算
        x = offset_x + self.x
        y = offset_y + self.y
        
        # ボタンの状態に応じた色を決定
        if not self.enabled:
            color = self._disabled_color
        elif self._is_pressed:
            color = self._pressed_color
        elif self._is_hovered or self.parent and self.parent.focused_control == self:
            color = self._hover_color
        else:
            color = self._bg_color
        
        # ボタンの背景を描画
        pyxel.rect(x, y, self.width, self.height, color)
        
        # ボタンの枠を描画
        pyxel.rectb(x, y, self.width, self.height, 7)  # 白い枠
        
        # テキストを中央揃えで描画
        text_width = len(self._text) * 6  # 1文字6ピクセルを仮定
        text_x = x + (self.width - text_width) // 2
        text_y = y + (self.height - 8) // 2  # フォントの高さを8ピクセルと仮定
        
        # テキストを描画
        pyxel.text(text_x, text_y, self._text, self._color)
        
        # フォーカス表示（オプション）
        if self.parent and self.parent.focused_control == self:
            # pyxel.rectb(x-1, y-1, self.width+2, self.height+2, 7)  # フォーカス枠
            pass

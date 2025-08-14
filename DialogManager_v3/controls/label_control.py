"""
ラベルコントロールを定義するモジュール

テキストを表示するためのシンプルなラベルコンポーネントです。
"""
import pyxel
from typing import Optional, Tuple, Dict, Any
from .control_base import ControlBase


class LabelControl(ControlBase):
    """
    テキストラベルを表示するコントロール
    
    シンプルなテキスト表示に使用します。
    """
    
    def __init__(self, x: int, y: int, text: str = "", **kwargs):
        """
        ラベルコントロールを初期化します。
        
        Args:
            x: X座標
            y: Y座標
            text: 表示するテキスト
            **kwargs: 追加のプロパティ
        """
        # デフォルトのサイズを設定（テキストサイズに応じて自動調整）
        width = kwargs.pop('width', len(text) * 6)  # 1文字6ピクセルを仮定
        height = kwargs.pop('height', 8)  # フォントの高さを8ピクセルと仮定
        
        super().__init__(x, y, width, height, **kwargs)
        
        self._text = text
        self._color = kwargs.get('color', 7)  # デフォルトは白
        self._align = kwargs.get('align', 'left')  # left, center, right
        self._shadow = kwargs.get('shadow', False)  # 影付きテキスト
        self._shadow_color = kwargs.get('shadow_color', 0)  # 影の色（デフォルトは黒）
        self._shadow_offset = kwargs.get('shadow_offset', (1, 1))  # 影のオフセット
    
    @property
    def text(self) -> str:
        """ラベルに表示されるテキストを取得します。"""
        return self._text
    
    @text.setter
    def text(self, value: str) -> None:
        """
        ラベルに表示するテキストを設定します。
        
        Args:
            value: 表示するテキスト
        """
        if self._text != value:
            self._text = str(value)
            self._dirty = True
    
    @property
    def color(self) -> int:
        """テキストの色を取得します。"""
        return self._color
    
    @color.setter
    def color(self, value: int) -> None:
        """
        テキストの色を設定します。
        
        Args:
            value: テキストの色（Pyxelのカラーインデックス）
        """
        if self._color != value:
            self._color = value
            self._dirty = True
    
    def draw(self, offset_x: int, offset_y: int) -> None:
        """
        ラベルを描画します。
        
        Args:
            offset_x: 親要素のXオフセット
            offset_y: 親要素のYオフセット
        """
        if not self.visible:
            return
            
        # 描画位置を計算
        x = offset_x + self.x
        y = offset_y + self.y
        
        # テキストの配置に応じてX座標を調整
        text_width = len(self._text) * 6  # 1文字6ピクセルを仮定
        if self._align == 'center':
            x += (self.width - text_width) // 2
        elif self._align == 'right':
            x = x + self.width - text_width
        
        # 影を描画
        if self._shadow:
            shadow_x = x + self._shadow_offset[0]
            shadow_y = y + self._shadow_offset[1]
            # Pyxelのテキスト描画関数を呼び出す
            # 実際のPyxelのAPIに合わせて調整が必要
            # pyxel.text(shadow_x, shadow_y, self._text, self._shadow_color)
        
        # テキストを描画
        pyxel.text(x, y, self._text, self._color)
        
        # デバッグ用に枠を描画
        # pyxel.rectb(offset_x + self.x, offset_y + self.y, self.width, self.height, 3)
    
    def get_preferred_size(self) -> Tuple[int, int]:
        """
        推奨サイズを取得します。
        
        Returns:
            Tuple[int, int]: (width, height) 推奨サイズ
        """
        text_width = len(self._text) * 6  # 1文字6ピクセルを仮定
        return (text_width, 8)  # フォントの高さを8ピクセルと仮定

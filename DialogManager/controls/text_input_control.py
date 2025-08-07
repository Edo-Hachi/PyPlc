"""
TextInputControl - テキスト入力コントロール

PyPlc Ver3 Dialog System - Phase 2 Implementation
カーソル制御・入力処理・疎結合イベント対応の本格的なテキスト入力フィールド
"""

import pyxel
from typing import Optional, Callable, List
import string


class TextInputControl:
    """
    本格的なテキスト入力コントロール
    
    機能:
    - テキスト入力・編集
    - カーソル制御（位置・点滅）
    - 選択範囲対応
    - 疎結合イベントシステム
    - バリデーション連携
    """
    
    def __init__(self, control_id: str, x: int, y: int, width: int, height: int, **kwargs):
        """
        TextInputControl初期化
        
        Args:
            control_id: コントロールID
            x, y: 相対座標
            width, height: サイズ
            **kwargs: 追加プロパティ
        """
        self.id = control_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # テキスト関連
        self.text = kwargs.get("value", "")
        self.placeholder = kwargs.get("placeholder", "")
        self.max_length = kwargs.get("max_length", 50)
        
        # 表示・スタイル
        self.visible = True
        self.enabled = True
        self.color = kwargs.get("color", 7)  # pyxel.COLOR_WHITE
        self.bg_color = kwargs.get("bg_color", 0)  # pyxel.COLOR_BLACK
        self.border_color = kwargs.get("border_color", 7)
        self.focus_border_color = kwargs.get("focus_border_color", 10)  # pyxel.COLOR_YELLOW
        
        # フォーカス・カーソル制御
        self.is_focused = False
        self.cursor_pos = len(self.text)
        self.cursor_blink_timer = 0
        self.cursor_visible = True
        self.cursor_blink_interval = 30  # フレーム数
        
        # 選択範囲（将来の拡張用）
        self.selection_start = -1
        self.selection_end = -1
        
        # 入力制限
        self.input_type = kwargs.get("input_type", "text")  # "text", "number", "device_address"
        self.allowed_chars = self._get_allowed_chars()
        
        # イベントコールバック
        self.event_callbacks = {
            "change": [],
            "focus": [],
            "blur": [],
            "enter": [],
            "validate": []
        }
        
        # バリデーション
        self.validator = None
        self.validation_error = None
        self.is_valid = True
        
        # 表示オフセット（長いテキストのスクロール用）
        self.display_offset = 0
    
    def _get_allowed_chars(self) -> str:
        """
        入力タイプに基づく許可文字を取得
        
        Returns:
            許可される文字の文字列
        """
        if self.input_type == "number":
            return string.digits + ".-"
        elif self.input_type == "device_address":
            # PLC標準デバイスアドレス形式: X0, Y10, M100, T0, C0等
            return string.ascii_uppercase + string.digits
        else:  # "text"
            return string.ascii_letters + string.digits + " ._-"
    
    def on(self, event_name: str, callback: Callable) -> None:
        """
        イベントコールバックを登録
        
        Args:
            event_name: イベント名
            callback: コールバック関数
        """
        if event_name in self.event_callbacks:
            self.event_callbacks[event_name].append(callback)
    
    def emit(self, event_name: str, *args, **kwargs) -> None:
        """
        イベントを発火
        
        Args:
            event_name: イベント名
            *args: イベント引数
            **kwargs: イベントキーワード引数
        """
        if event_name in self.event_callbacks:
            for callback in self.event_callbacks[event_name]:
                try:
                    callback(self, *args, **kwargs)
                except Exception as e:
                    print(f"TextInput event callback error: {e}")
    
    def set_validator(self, validator: Callable[[str], tuple]) -> None:
        """
        バリデーター関数を設定
        
        Args:
            validator: バリデーター関数 (text) -> (is_valid: bool, error_message: str)
        """
        self.validator = validator
    
    def validate(self) -> bool:
        """
        現在のテキストをバリデーション
        
        Returns:
            バリデーション結果
        """
        if self.validator:
            try:
                self.is_valid, self.validation_error = self.validator(self.text)
                self.emit("validate", self.is_valid, self.validation_error)
                return self.is_valid
            except Exception as e:
                self.is_valid = False
                self.validation_error = f"Validation error: {e}"
                return False
        else:
            self.is_valid = True
            self.validation_error = None
            return True
    
    def focus(self) -> None:
        """
        フォーカスを設定
        """
        if not self.is_focused:
            self.is_focused = True
            self.cursor_blink_timer = 0
            self.cursor_visible = True
            self.emit("focus")
    
    def blur(self) -> None:
        """
        フォーカスを解除
        """
        if self.is_focused:
            self.is_focused = False
            self.cursor_visible = False
            self.validate()  # フォーカス解除時にバリデーション実行
            self.emit("blur")
    
    def set_text(self, text: str) -> None:
        """
        テキストを設定
        
        Args:
            text: 設定するテキスト
        """
        old_text = self.text
        self.text = text[:self.max_length]  # 最大長制限
        self.cursor_pos = min(self.cursor_pos, len(self.text))
        self._update_display_offset()
        
        if old_text != self.text:
            self.emit("change", old_text, self.text)
    
    def get_text(self) -> str:
        """
        現在のテキストを取得
        
        Returns:
            現在のテキスト
        """
        return self.text
    
    def clear(self) -> None:
        """
        テキストをクリア
        """
        self.set_text("")
        self.cursor_pos = 0
    
    def handle_input(self, mouse_x: int, mouse_y: int, mouse_clicked: bool) -> None:
        """
        入力処理
        
        Args:
            mouse_x, mouse_y: マウス座標
            mouse_clicked: マウスクリック状態
        """
        if not self.enabled:
            return
        
        # マウスクリック処理（フォーカス制御）
        if mouse_clicked:
            # コントロール内クリックでフォーカス取得
            if self.point_in_control(mouse_x, mouse_y, 0, 0):  # 相対座標での判定
                self.focus()
                # カーソル位置をクリック位置に設定
                self._set_cursor_from_mouse(mouse_x)
            else:
                # コントロール外クリックでフォーカス解除
                self.blur()
        
        # キーボード入力処理（フォーカス時のみ）
        if self.is_focused:
            self._handle_keyboard_input()
        
        # カーソル点滅制御
        if self.is_focused:
            self.cursor_blink_timer += 1
            if self.cursor_blink_timer >= self.cursor_blink_interval:
                self.cursor_visible = not self.cursor_visible
                self.cursor_blink_timer = 0
    
    def _handle_keyboard_input(self) -> None:
        """
        キーボード入力処理
        """
        # 文字入力処理
        for key in range(32, 127):  # 印刷可能文字
            if pyxel.btnp(key):
                char = chr(key)
                
                # Shiftキー処理
                if pyxel.btn(pyxel.KEY_SHIFT):
                    char = self._apply_shift(char)
                
                # 許可文字チェック
                if char in self.allowed_chars:
                    self._insert_char(char)
        
        # 特殊キー処理
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            self._handle_backspace()
        elif pyxel.btnp(pyxel.KEY_DELETE):
            self._handle_delete()
        elif pyxel.btnp(pyxel.KEY_LEFT):
            self._move_cursor(-1)
        elif pyxel.btnp(pyxel.KEY_RIGHT):
            self._move_cursor(1)
        elif pyxel.btnp(pyxel.KEY_HOME):
            self.cursor_pos = 0
            self._update_display_offset()
        elif pyxel.btnp(pyxel.KEY_END):
            self.cursor_pos = len(self.text)
            self._update_display_offset()
        elif pyxel.btnp(pyxel.KEY_RETURN):
            self.emit("enter")
    
    def _apply_shift(self, char: str) -> str:
        """
        Shiftキー適用
        
        Args:
            char: 元の文字
            
        Returns:
            Shift適用後の文字
        """
        shift_map = {
            '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
            '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
            '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|',
            ';': ':', "'": '"', ',': '<', '.': '>', '/': '?',
            '`': '~'
        }
        
        if char.isalpha():
            return char.upper()
        else:
            return shift_map.get(char, char)
    
    def _insert_char(self, char: str) -> None:
        """
        文字を挿入
        
        Args:
            char: 挿入する文字
        """
        if len(self.text) < self.max_length:
            old_text = self.text
            self.text = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
            self.cursor_pos += 1
            self._update_display_offset()
            self.emit("change", old_text, self.text)
    
    def _handle_backspace(self) -> None:
        """
        Backspace処理
        """
        if self.cursor_pos > 0:
            old_text = self.text
            self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
            self.cursor_pos -= 1
            self._update_display_offset()
            self.emit("change", old_text, self.text)
    
    def _handle_delete(self) -> None:
        """
        Delete処理
        """
        if self.cursor_pos < len(self.text):
            old_text = self.text
            self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
            self._update_display_offset()
            self.emit("change", old_text, self.text)
    
    def _move_cursor(self, direction: int) -> None:
        """
        カーソル移動
        
        Args:
            direction: 移動方向（-1: 左, 1: 右）
        """
        self.cursor_pos = max(0, min(len(self.text), self.cursor_pos + direction))
        self._update_display_offset()
        self.cursor_visible = True
        self.cursor_blink_timer = 0
    
    def _set_cursor_from_mouse(self, mouse_x: int) -> None:
        """
        マウス位置からカーソル位置を設定
        
        Args:
            mouse_x: マウスX座標
        """
        # 簡易実装：文字幅4pixelとして計算
        relative_x = mouse_x - self.x - 2  # パディング考慮
        char_pos = max(0, relative_x // 4)
        self.cursor_pos = min(len(self.text), char_pos + self.display_offset)
        self.cursor_visible = True
        self.cursor_blink_timer = 0
    
    def _update_display_offset(self) -> None:
        """
        表示オフセットを更新（長いテキストのスクロール）
        """
        visible_chars = (self.width - 4) // 4  # パディング考慮
        
        if self.cursor_pos < self.display_offset:
            self.display_offset = self.cursor_pos
        elif self.cursor_pos >= self.display_offset + visible_chars:
            self.display_offset = self.cursor_pos - visible_chars + 1
        
        self.display_offset = max(0, self.display_offset)
    
    def draw(self, dialog_x: int, dialog_y: int) -> None:
        """
        描画処理
        
        Args:
            dialog_x, dialog_y: ダイアログの絶対座標
        """
        if not self.visible:
            return
        
        abs_x, abs_y, w, h = self.get_absolute_rect(dialog_x, dialog_y)
        
        # 背景描画
        pyxel.rect(abs_x, abs_y, w, h, self.bg_color)
        
        # 境界線描画（フォーカス状態で色変更）
        border_color = self.focus_border_color if self.is_focused else self.border_color
        if not self.is_valid:
            border_color = 8  # pyxel.COLOR_RED
        pyxel.rectb(abs_x, abs_y, w, h, border_color)
        
        # テキスト描画
        display_text = self.text[self.display_offset:self.display_offset + (w-4)//4]
        text_color = self.color if display_text else 13  # グレー（プレースホルダー用）
        
        if display_text:
            pyxel.text(abs_x + 2, abs_y + 2, display_text, text_color)
        elif self.placeholder and not self.is_focused:
            # プレースホルダー表示
            placeholder_text = self.placeholder[:((w-4)//4)]
            pyxel.text(abs_x + 2, abs_y + 2, placeholder_text, 13)
        
        # カーソル描画（フォーカス時かつ点滅表示時）
        if self.is_focused and self.cursor_visible:
            cursor_x = abs_x + 2 + (self.cursor_pos - self.display_offset) * 4
            if abs_x + 2 <= cursor_x <= abs_x + w - 2:
                pyxel.line(cursor_x, abs_y + 2, cursor_x, abs_y + h - 3, self.color)
        
        # バリデーションエラー表示
        if not self.is_valid and self.validation_error:
            error_y = abs_y + h + 2
            pyxel.text(abs_x, error_y, self.validation_error[:((w)//4)], 8)  # 赤色
    
    def get_absolute_rect(self, dialog_x: int, dialog_y: int) -> tuple:
        """
        絶対座標での矩形を取得
        
        Args:
            dialog_x, dialog_y: ダイアログの絶対座標
            
        Returns:
            (abs_x, abs_y, width, height)
        """
        return (dialog_x + self.x, dialog_y + self.y, self.width, self.height)
    
    def point_in_control(self, mouse_x: int, mouse_y: int, dialog_x: int, dialog_y: int) -> bool:
        """
        マウス座標がコントロール内にあるかチェック
        
        Args:
            mouse_x, mouse_y: マウス座標
            dialog_x, dialog_y: ダイアログの絶対座標
            
        Returns:
            コントロール内にある場合True
        """
        abs_x, abs_y, w, h = self.get_absolute_rect(dialog_x, dialog_y)
        return (abs_x <= mouse_x <= abs_x + w and 
                abs_y <= mouse_y <= abs_y + h)

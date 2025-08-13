"""
pyxdlg.py - Pyxelベースシンプルダイアログシステム
EDITモード用の入力ダイアログに特化したモーダルダイアログ実装

使用例:
    dialog = PyxDialog()
    result, text = dialog.input_text("Device Address", "X001")
    if result:  # OKが押された
        print(f"入力値: {text}")
    else:      # Cancelが押された
        print("キャンセルされました")
"""

import pyxel
import json
import os
from enum import Enum
from typing import Optional, Tuple, Dict, List, Any


class InputType(Enum):
    """入力タイプ定義"""
    TEXT = "text"                    # 英数字
    NUMBER = "number"                # 数字のみ
    DEVICE_ADDRESS = "device_address" # デバイスアドレス（X001等）


class DialogLabel:
    """ダイアログ内ラベルコントロール"""
    
    def __init__(self, x: int, y: int, text: str, color: int = pyxel.COLOR_WHITE):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.visible = True
    
    def draw(self):
        """ラベル描画"""
        if self.visible:
            pyxel.text(self.x, self.y, self.text, self.color)


class DialogControl:
    """ダイアログコントロール基底クラス"""
    
    def __init__(self, control_id: str, x: int, y: int, width: int = 0, height: int = 0):
        self.control_id = control_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.value = ""


class JsonDialogBuilder:
    """JSONからダイアログを構築するビルダークラス"""
    
    @staticmethod
    def load_dialog_definition(json_file: str) -> Dict[str, Any]:
        """JSONファイルからダイアログ定義を読み込み"""
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"Dialog definition file not found: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def create_dialog_from_json(dialog_def: Dict[str, Any]) -> 'PyxDialog':
        """JSON定義からダイアログを作成"""
        dialog = PyxDialog()
        
        # 基本設定
        dialog.title = dialog_def.get('title', '')
        dialog.dialog_w = dialog_def.get('width', 200)
        dialog.dialog_h = dialog_def.get('height', 120)
        
        # 中央配置計算
        dialog.dialog_x = (256 - dialog.dialog_w) // 2
        dialog.dialog_y = (256 - dialog.dialog_h) // 2
        
        # コントロール配置
        controls = dialog_def.get('controls', [])
        for control_def in controls:
            control_type = control_def.get('type', '').lower()
            
            if control_type == 'label':
                dialog._add_label_from_json(control_def)
            elif control_type == 'textinput':
                dialog._setup_textinput_from_json(control_def)
        
        # ボタン位置再計算
        dialog._recalculate_button_positions()
        
        return dialog
    
    @staticmethod
    def show_json_dialog(json_file: str, **kwargs) -> Tuple[bool, Dict[str, str]]:
        """JSONファイル指定でダイアログ表示"""
        dialog_def = JsonDialogBuilder.load_dialog_definition(json_file)
        
        # kwargs で初期値上書き
        for key, value in kwargs.items():
            if 'controls' in dialog_def:
                for control in dialog_def['controls']:
                    if control.get('id') == key:
                        control['value'] = value
        
        dialog = JsonDialogBuilder.create_dialog_from_json(dialog_def)
        result = dialog.show_modal()
        
        # 結果を辞書で返す
        values = {}
        if hasattr(dialog, 'control_values'):
            values = dialog.control_values
        else:
            values['text'] = dialog.input_text
        
        return result, values


class PyxDialog:
    """Pyxelベースシンプルモーダルダイアログ"""
    
    def __init__(self):
        self.active = False
        self.result = False  # True: OK, False: Cancel
        self.input_text = ""
        self.input_type = InputType.TEXT
        self.cursor_pos = 0
        self.cursor_blink = 0
        self.max_length = 10
        
        # ダイアログ設定
        self.title = ""
        self.prompt = ""
        self.placeholder = ""
        
        # ラベルリスト
        self.labels: List[DialogLabel] = []
        
        # コントロール値管理
        self.control_values: Dict[str, str] = {}
        
        # レイアウト（256x256画面中央）
        self.dialog_w = 200
        self.dialog_h = 120
        self.dialog_x = (256 - self.dialog_w) // 2
        self.dialog_y = (256 - self.dialog_h) // 2
        
        # ボタン配置
        self.ok_btn_x = self.dialog_x + 50
        self.ok_btn_y = self.dialog_y + self.dialog_h - 35
        self.ok_btn_w = 40
        self.ok_btn_h = 25
        
        self.cancel_btn_x = self.dialog_x + 110
        self.cancel_btn_y = self.dialog_y + self.dialog_h - 35
        self.cancel_btn_w = 50
        self.cancel_btn_h = 25
        
        # テキスト入力フィールド
        self.input_x = self.dialog_x + 10
        self.input_y = self.dialog_y + 50
        self.input_w = self.dialog_w - 20
        self.input_h = 20
        
        # 状態管理
        self.ok_hovered = False
        self.cancel_hovered = False
        self.ok_pressed = False
        self.cancel_pressed = False
    
    def input_text_dialog(self, title: str, prompt: str = "", 
                         placeholder: str = "", input_type: InputType = InputType.TEXT) -> Tuple[bool, str]:
        """
        テキスト入力ダイアログ表示
        
        Args:
            title: ダイアログタイトル
            prompt: 入力プロンプト
            placeholder: プレースホルダー
            input_type: 入力タイプ
            
        Returns:
            (True/False, 入力文字列): OKなら(True, text), CancelならFalse, "")
        """
        # 初期化
        self.title = title
        self.prompt = prompt
        self.placeholder = placeholder
        self.input_type = input_type
        self.input_text = placeholder
        self.cursor_pos = len(self.input_text)
        self.active = True
        self.result = False
        
        # 入力タイプ別の最大長設定
        if input_type == InputType.DEVICE_ADDRESS:
            self.max_length = 4  # X001形式
        elif input_type == InputType.NUMBER:
            self.max_length = 6  # 数値
        else:
            self.max_length = 20  # テキスト
        
        # モーダルループ
        while self.active:
            self._update()
            self._draw()
            pyxel.flip()
        
        return (self.result, self.input_text if self.result else "")
    
    def _update(self):
        """更新処理"""
        if not self.active:
            return
            
        # マウス状態更新
        self._update_mouse()
        
        # キー入力処理
        self._handle_key_input()
        
        # カーソル点滅
        self.cursor_blink = (self.cursor_blink + 1) % 60
        
        # ESCキーでキャンセル
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self._close_dialog(False)
        
        # ENTERキーでOK
        if pyxel.btnp(pyxel.KEY_RETURN):
            self._close_dialog(True)
    
    def _update_mouse(self):
        """マウス状態更新"""
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        
        # OKボタン
        self.ok_hovered = (self.ok_btn_x <= mx <= self.ok_btn_x + self.ok_btn_w and
                          self.ok_btn_y <= my <= self.ok_btn_y + self.ok_btn_h)
        
        # Cancelボタン
        self.cancel_hovered = (self.cancel_btn_x <= mx <= self.cancel_btn_x + self.cancel_btn_w and
                             self.cancel_btn_y <= my <= self.cancel_btn_y + self.cancel_btn_h)
        
        # マウスクリック処理
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.ok_hovered:
                self._close_dialog(True)
            elif self.cancel_hovered:
                self._close_dialog(False)
            elif (self.input_x <= mx <= self.input_x + self.input_w and
                  self.input_y <= my <= self.input_y + self.input_h):
                # テキストフィールドクリック
                relative_x = mx - self.input_x - 3
                self.cursor_pos = min(max(0, relative_x // 4), len(self.input_text))
        
        # ボタン押下状態
        self.ok_pressed = self.ok_hovered and pyxel.btn(pyxel.MOUSE_BUTTON_LEFT)
        self.cancel_pressed = self.cancel_hovered and pyxel.btn(pyxel.MOUSE_BUTTON_LEFT)
    
    def _handle_key_input(self):
        """キー入力処理"""
        # バックスペース
        if pyxel.btnp(pyxel.KEY_BACKSPACE) and self.cursor_pos > 0:
            self.input_text = self.input_text[:self.cursor_pos-1] + self.input_text[self.cursor_pos:]
            self.cursor_pos -= 1
            
        # デリート
        if pyxel.btnp(pyxel.KEY_DELETE) and self.cursor_pos < len(self.input_text):
            self.input_text = self.input_text[:self.cursor_pos] + self.input_text[self.cursor_pos+1:]
        
        # 文字入力（長さ制限）
        if len(self.input_text) < self.max_length:
            # 数字入力
            for i in range(10):
                if pyxel.btnp(pyxel.KEY_0 + i):
                    new_char = str(i)
                    new_text = self.input_text[:self.cursor_pos] + new_char + self.input_text[self.cursor_pos:]
                    if self._validate_input(new_text):
                        self.input_text = new_text
                        self.cursor_pos += 1
            
            # アルファベット入力
            for i in range(26):
                if pyxel.btnp(pyxel.KEY_A + i):
                    new_char = chr(ord('A') + i)  # 常に大文字
                    new_text = self.input_text[:self.cursor_pos] + new_char + self.input_text[self.cursor_pos:]
                    if self._validate_input(new_text):
                        self.input_text = new_text
                        self.cursor_pos += 1
        
        # カーソル移動
        if pyxel.btnp(pyxel.KEY_LEFT) and self.cursor_pos > 0:
            self.cursor_pos -= 1
        if pyxel.btnp(pyxel.KEY_RIGHT) and self.cursor_pos < len(self.input_text):
            self.cursor_pos += 1
        
        # Home/End
        if pyxel.btnp(pyxel.KEY_HOME):
            self.cursor_pos = 0
        if pyxel.btnp(pyxel.KEY_END):
            self.cursor_pos = len(self.input_text)
    
    def _validate_input(self, text: str) -> bool:
        """入力タイプ別バリデーション"""
        if self.input_type == InputType.NUMBER:
            return text.isdigit() or text == ""
        elif self.input_type == InputType.DEVICE_ADDRESS:
            # デバイスアドレス形式チェック（X001, M100等）
            if len(text) == 0:
                return True
            if len(text) == 1:
                return text.upper() in ['X', 'Y', 'M', 'T', 'C', 'D']
            # 完全形式チェック（文字+数字3桁）
            return (len(text) <= 4 and 
                    text[0].upper() in ['X', 'Y', 'M', 'T', 'C', 'D'] and
                    text[1:].isdigit())
        return True  # TEXT型は何でもOK
    
    def _draw(self):
        """描画処理"""
        if not self.active:
            return
            
        # 背景を半透明で暗くする効果（簡易実装）
        # 完全に塗りつぶすのではなく、縞模様で暗転効果
        for y in range(0, 256, 4):
            pyxel.line(0, y, 256, y, pyxel.COLOR_BLACK)
        for x in range(0, 256, 4):
            pyxel.line(x, 0, x, 256, pyxel.COLOR_BLACK)
        
        # ダイアログ背景
        pyxel.rect(self.dialog_x, self.dialog_y, self.dialog_w, self.dialog_h, pyxel.COLOR_DARK_BLUE)
        pyxel.rectb(self.dialog_x, self.dialog_y, self.dialog_w, self.dialog_h, pyxel.COLOR_WHITE)
        
        # タイトル
        if self.title:
            pyxel.text(self.dialog_x + 4, self.dialog_y + 4, self.title, pyxel.COLOR_WHITE)
        
        # プロンプト
        if self.prompt:
            pyxel.text(self.dialog_x + 10, self.dialog_y + 25, self.prompt, pyxel.COLOR_WHITE)
        
        # テキスト入力フィールド
        pyxel.rect(self.input_x, self.input_y, self.input_w, self.input_h, pyxel.COLOR_BLACK)
        pyxel.rectb(self.input_x, self.input_y, self.input_w, self.input_h, pyxel.COLOR_WHITE)
        
        # 入力テキスト表示
        display_text = self.input_text if self.input_text else self.placeholder
        text_color = pyxel.COLOR_WHITE if self.input_text else pyxel.COLOR_GRAY
        
        # 表示可能文字数制限
        visible_chars = (self.input_w - 6) // 4  # 4ピクセル幅フォント
        visible_text = display_text[:visible_chars]
        pyxel.text(self.input_x + 3, self.input_y + 6, visible_text, text_color)
        
        # カーソル表示（点滅）
        if self.cursor_blink < 30:
            cursor_x = self.input_x + 3 + min(self.cursor_pos, visible_chars) * 4
            cursor_y = self.input_y + 4
            pyxel.line(cursor_x, cursor_y, cursor_x, cursor_y + 12, pyxel.COLOR_WHITE)
        
        # OKボタン
        ok_color = pyxel.COLOR_NAVY
        if self.ok_pressed:
            ok_color = pyxel.COLOR_DARK_BLUE
        elif self.ok_hovered:
            ok_color = pyxel.COLOR_LIGHT_BLUE
        
        pyxel.rect(self.ok_btn_x, self.ok_btn_y, self.ok_btn_w, self.ok_btn_h, ok_color)
        pyxel.rectb(self.ok_btn_x, self.ok_btn_y, self.ok_btn_w, self.ok_btn_h, pyxel.COLOR_WHITE)
        pyxel.text(self.ok_btn_x + 12, self.ok_btn_y + 9, "OK", pyxel.COLOR_WHITE)
        
        # Cancelボタン
        cancel_color = pyxel.COLOR_NAVY
        if self.cancel_pressed:
            cancel_color = pyxel.COLOR_DARK_BLUE
        elif self.cancel_hovered:
            cancel_color = pyxel.COLOR_LIGHT_BLUE
        
        pyxel.rect(self.cancel_btn_x, self.cancel_btn_y, self.cancel_btn_w, self.cancel_btn_h, cancel_color)
        pyxel.rectb(self.cancel_btn_x, self.cancel_btn_y, self.cancel_btn_w, self.cancel_btn_h, pyxel.COLOR_WHITE)
        pyxel.text(self.cancel_btn_x + 8, self.cancel_btn_y + 9, "Cancel", pyxel.COLOR_WHITE)
        
        # 追加ラベル描画
        for label in self.labels:
            label.draw()
        
        # マウスカーソル描画（ダイアログ最前面）
        self._draw_mouse_cursor()
    
    def _draw_mouse_cursor(self):
        """マウスカーソル描画"""
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        
        # 十字カーソル描画
        pyxel.line(mx - 3, my, mx + 3, my, pyxel.COLOR_WHITE)
        pyxel.line(mx, my - 3, mx, my + 3, pyxel.COLOR_WHITE)
        
        # 中央点
        pyxel.pset(mx, my, pyxel.COLOR_YELLOW)
    
    def _close_dialog(self, result: bool):
        """ダイアログを閉じる"""
        self.result = result
        self.active = False
        
        # 結果保存
        if result:
            self.control_values['text'] = self.input_text
    
    def _add_label_from_json(self, control_def: Dict[str, Any]):
        """JSON定義からラベルを追加"""
        x = self.dialog_x + control_def.get('x', 10)
        y = self.dialog_y + control_def.get('y', 20)
        text = control_def.get('text', '')
        color = self._parse_color(control_def.get('color', 'white'))
        
        label = DialogLabel(x, y, text, color)
        self.labels.append(label)
    
    def _setup_textinput_from_json(self, control_def: Dict[str, Any]):
        """JSON定義からテキスト入力を設定"""
        # 入力フィールド位置を JSON定義で上書き
        self.input_x = self.dialog_x + control_def.get('x', 10)
        self.input_y = self.dialog_y + control_def.get('y', 50)
        self.input_w = control_def.get('width', self.dialog_w - 20)
        self.input_h = control_def.get('height', 20)
        
        # 入力タイプ設定
        input_type_str = control_def.get('input_type', 'text')
        if input_type_str == 'number':
            self.input_type = InputType.NUMBER
        elif input_type_str == 'device_address':
            self.input_type = InputType.DEVICE_ADDRESS
        else:
            self.input_type = InputType.TEXT
        
        # 初期値とプレースホルダー
        self.input_text = control_def.get('value', '')
        self.placeholder = control_def.get('placeholder', '')
        self.cursor_pos = len(self.input_text)
    
    def _recalculate_button_positions(self):
        """ダイアログサイズに基づいてボタン位置を再計算"""
        self.ok_btn_x = self.dialog_x + self.dialog_w // 2 - 50
        self.ok_btn_y = self.dialog_y + self.dialog_h - 35
        
        self.cancel_btn_x = self.dialog_x + self.dialog_w // 2 + 10
        self.cancel_btn_y = self.dialog_y + self.dialog_h - 35
    
    def _parse_color(self, color_name: str) -> int:
        """色名からPyxel色定数に変換"""
        color_map = {
            'black': pyxel.COLOR_BLACK,
            'white': pyxel.COLOR_WHITE,
            'red': pyxel.COLOR_RED,
            'green': pyxel.COLOR_GREEN,
            'blue': pyxel.COLOR_LIGHT_BLUE,
            'yellow': pyxel.COLOR_YELLOW,
            'cyan': pyxel.COLOR_CYAN,
            'pink': pyxel.COLOR_PINK,
            'gray': pyxel.COLOR_GRAY,
            'grey': pyxel.COLOR_GRAY,
            'orange': pyxel.COLOR_ORANGE,
            'brown': pyxel.COLOR_BROWN,
            'purple': pyxel.COLOR_PURPLE,
            'navy': pyxel.COLOR_NAVY,
            'dark_blue': pyxel.COLOR_DARK_BLUE,
            'lime': pyxel.COLOR_LIME,
            'peach': pyxel.COLOR_PEACH
        }
        return color_map.get(color_name.lower(), pyxel.COLOR_WHITE)
    
    def show_modal(self) -> bool:
        """モーダル表示（JSON用）"""
        self.active = True
        
        # モーダルループ
        while self.active:
            self._update()
            self._draw()
            pyxel.flip()
        
        return self.result


# 便利な関数群
def input_device_address(title: str = "Device Settings", current_value: str = "X001") -> Tuple[bool, str]:
    """デバイスアドレス入力ダイアログ"""
    dialog = PyxDialog()
    return dialog.input_text_dialog(title, "Device Address:", current_value, InputType.DEVICE_ADDRESS)


def input_number(title: str = "Number Input", prompt: str = "Enter number:", current_value: str = "0") -> Tuple[bool, str]:
    """数値入力ダイアログ"""
    dialog = PyxDialog()
    return dialog.input_text_dialog(title, prompt, current_value, InputType.NUMBER)


def input_text(title: str = "Text Input", prompt: str = "Enter text:", current_value: str = "") -> Tuple[bool, str]:
    """テキスト入力ダイアログ"""
    dialog = PyxDialog()
    return dialog.input_text_dialog(title, prompt, current_value, InputType.TEXT)


# テスト用メイン関数
def main():
    """pyxdlg.py単体テスト"""
    pyxel.init(256, 256, title="PyxDialog Test")
    
    def update():
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        
        # 従来のAPI
        if pyxel.btnp(pyxel.KEY_1):
            # デバイスアドレス入力テスト
            result, text = input_device_address("Device Settings", "X001")
            print(f"Device Address: OK={result}, Text='{text}'")
        
        if pyxel.btnp(pyxel.KEY_2):
            # 数値入力テスト
            result, text = input_number("Timer Settings", "Timer preset (sec):", "3")
            print(f"Number: OK={result}, Text='{text}'")
        
        if pyxel.btnp(pyxel.KEY_3):
            # テキスト入力テスト
            result, text = input_text("Text Input", "Enter your name:", "PyPlc")
            print(f"Text: OK={result}, Text='{text}'")
        
        # JSONダイアログテスト
        if pyxel.btnp(pyxel.KEY_4):
            try:
                result, values = JsonDialogBuilder.show_json_dialog("dialogs/device_settings.json")
                print(f"JSON Device Dialog: OK={result}, Values={values}")
            except FileNotFoundError as e:
                print(f"JSON file not found: {e}")
        
        if pyxel.btnp(pyxel.KEY_5):
            try:
                result, values = JsonDialogBuilder.show_json_dialog("dialogs/timer_settings.json", preset_value="5")
                print(f"JSON Timer Dialog: OK={result}, Values={values}")
            except FileNotFoundError as e:
                print(f"JSON file not found: {e}")
        
        if pyxel.btnp(pyxel.KEY_6):
            try:
                result, values = JsonDialogBuilder.show_json_dialog("dialogs/text_input.json")
                print(f"JSON Text Dialog: OK={result}, Values={values}")
            except FileNotFoundError as e:
                print(f"JSON file not found: {e}")
    
    def draw():
        pyxel.cls(pyxel.COLOR_BLACK)
        pyxel.text(10, 10, "PyxDialog Test", pyxel.COLOR_WHITE)
        pyxel.text(10, 30, "Classic API:", pyxel.COLOR_YELLOW)
        pyxel.text(10, 40, "1: Device Address Dialog", pyxel.COLOR_WHITE)
        pyxel.text(10, 50, "2: Number Input Dialog", pyxel.COLOR_WHITE)
        pyxel.text(10, 60, "3: Text Input Dialog", pyxel.COLOR_WHITE)
        
        pyxel.text(10, 80, "JSON Resource API:", pyxel.COLOR_CYAN)
        pyxel.text(10, 90, "4: JSON Device Settings", pyxel.COLOR_WHITE)
        pyxel.text(10, 100, "5: JSON Timer Settings", pyxel.COLOR_WHITE)
        pyxel.text(10, 110, "6: JSON Text Input", pyxel.COLOR_WHITE)
        
        pyxel.text(10, 130, "Q: Quit", pyxel.COLOR_PINK)
    
    pyxel.run(update, draw)


if __name__ == "__main__":
    main()
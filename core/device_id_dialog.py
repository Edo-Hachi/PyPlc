# PyPlc Ver3 - Device ID編集ダイアログシステム
# 作成日: 2025-08-06
# 目的: エディットモードでのデバイスID入力・編集機能

import pyxel
import re
from enum import Enum
from typing import Tuple, Optional
from config import DeviceType, DisplayConfig

class DialogState(Enum):
    """ダイアログ状態管理"""
    INACTIVE = "inactive"    # ダイアログ非表示
    EDITING = "editing"      # テキスト入力中
    WAITING = "waiting"      # OK/Cancel待ち

class DeviceIDDialog:
    """Ver3専用デバイスID編集ダイアログ"""
    
    def __init__(self, device_type: DeviceType, current_id: str = ""):
        """ダイアログ初期化"""
        self.device_type = device_type
        self.current_id = current_id
        self.input_text = current_id
        self.is_active = False
        self.dialog_result: Optional[bool] = None  # True: OK, False: Cancel
        self.state = DialogState.INACTIVE
        
        # UI設定
        self.dialog_width = 220
        self.dialog_height = 140
        self.dialog_x = (DisplayConfig.WINDOW_WIDTH - self.dialog_width) // 2
        self.dialog_y = (DisplayConfig.WINDOW_HEIGHT - self.dialog_height) // 2
        
        # ボタン設定
        self.ok_button_rect = (self.dialog_x + 20, self.dialog_y + 100, 60, 20)
        self.cancel_button_rect = (self.dialog_x + 140, self.dialog_y + 100, 60, 20)
        self.mouse_over_ok = False
        self.mouse_over_cancel = False
        
        # 入力フィールド設定
        self.input_field_rect = (self.dialog_x + 20, self.dialog_y + 60, 180, 20)
        self.cursor_pos = len(self.input_text)
        self.cursor_blink_timer = 0
        
        # エラーメッセージ
        self.error_message = ""
        
    def show_modal(self, background_draw_func=None) -> Tuple[bool, str]:
        """モーダル表示・入力処理（Pyxelループ統合）"""
        self.is_active = True
        self.state = DialogState.EDITING
        self.dialog_result = None
        self.input_text = self.current_id
        self.cursor_pos = len(self.input_text)
        self.error_message = ""
        
        # モーダルループ（Pyxelの描画・更新を利用）
        while self.is_active:
            # バックグラウンド描画（呼び出し側から提供）
            if background_draw_func:
                background_draw_func()
            else:
                pyxel.cls(pyxel.COLOR_BLACK)
            
            self.update()
            self.draw()
            
            pyxel.flip()
            
            # 結果確定時はループ終了
            if self.dialog_result is not None:
                self.is_active = False
                break
        
        # 結果を返す
        if self.dialog_result is True:
            return True, self.input_text
        else:
            return False, self.current_id
    
    def update(self):
        """キーボード・マウス入力処理"""
        if not self.is_active:
            return
            
        # カーソル点滅タイマー更新
        self.cursor_blink_timer += 1
        
        # マウス位置取得・ホバー判定
        mouse_x, mouse_y = pyxel.mouse_x, pyxel.mouse_y
        self.mouse_over_ok = self._point_in_rect(mouse_x, mouse_y, self.ok_button_rect)
        self.mouse_over_cancel = self._point_in_rect(mouse_x, mouse_y, self.cancel_button_rect)
        
        # マウスクリック処理
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.mouse_over_ok:
                self._handle_ok_click()
            elif self.mouse_over_cancel:
                self._handle_cancel_click()
        
        # キーボード入力処理
        self._handle_keyboard_input()
    
    def _handle_keyboard_input(self):
        """キーボード入力処理"""
        # ESCキー: キャンセル
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self._handle_cancel_click()
            return
            
        # ENTERキー: OK
        if pyxel.btnp(pyxel.KEY_RETURN):
            self._handle_ok_click()
            return
        
        # バックスペース: 文字削除
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            if self.cursor_pos > 0:
                self.input_text = self.input_text[:self.cursor_pos-1] + self.input_text[self.cursor_pos:]
                self.cursor_pos -= 1
                self.error_message = ""  # エラーメッセージクリア
        
        # 文字入力（英数字のみ）
        self._handle_text_input()
    
    def _handle_text_input(self):
        """テキスト入力処理（英数字のみ）"""
        # 文字数制限
        if len(self.input_text) >= 8:  # デバイスID最大長
            return
            
        # A-Z文字入力
        for i in range(26):
            if pyxel.btnp(pyxel.KEY_A + i):
                char = chr(ord('A') + i)  # 常に大文字
                self.input_text = self.input_text[:self.cursor_pos] + char + self.input_text[self.cursor_pos:]
                self.cursor_pos += 1
                self.error_message = ""  # エラーメッセージクリア
                break
        
        # 0-9数字入力
        for i in range(10):
            if pyxel.btnp(pyxel.KEY_0 + i):
                char = str(i)
                self.input_text = self.input_text[:self.cursor_pos] + char + self.input_text[self.cursor_pos:]
                self.cursor_pos += 1
                self.error_message = ""  # エラーメッセージクリア
                break
    
    def _handle_ok_click(self):
        """OK ボタンクリック処理"""
        # バリデーション実行
        if self._validate_device_id(self.input_text):
            self.dialog_result = True
        else:
            # バリデーション失敗時はエラーメッセージ表示
            pass  # エラーメッセージは_validate_device_idで設定済み
    
    def _handle_cancel_click(self):
        """Cancel ボタンクリック処理"""
        self.dialog_result = False
    
    def draw(self):
        """ダイアログUI描画"""
        if not self.is_active:
            return
            
        # 背景暗転効果（50%透明度風）
        for y in range(0, DisplayConfig.WINDOW_HEIGHT, 2):
            for x in range(0, DisplayConfig.WINDOW_WIDTH, 2):
                pyxel.pset(x, y, pyxel.COLOR_BLACK)
        
        # ダイアログウィンドウ背景
        pyxel.rect(self.dialog_x, self.dialog_y, self.dialog_width, self.dialog_height, pyxel.COLOR_DARK_BLUE)
        pyxel.rectb(self.dialog_x, self.dialog_y, self.dialog_width, self.dialog_height, pyxel.COLOR_WHITE)
        
        # タイトル
        title = "Device ID Editor"
        title_x = self.dialog_x + (self.dialog_width - len(title) * 4) // 2
        pyxel.text(title_x, self.dialog_y + 8, title, pyxel.COLOR_WHITE)
        
        # デバイスタイプ表示
        device_type_text = f"Device Type: {self.device_type.value}"
        pyxel.text(self.dialog_x + 10, self.dialog_y + 25, device_type_text, pyxel.COLOR_CYAN)
        
        # 入力フィールド
        self._draw_input_field()
        
        # バリデーション情報
        self._draw_validation_info()
        
        # エラーメッセージ
        if self.error_message:
            pyxel.text(self.dialog_x + 10, self.dialog_y + 85, self.error_message, pyxel.COLOR_RED)
        
        # ボタン
        self._draw_buttons()
    
    def _draw_input_field(self):
        """入力フィールド描画"""
        # 入力フィールド背景
        field_color = pyxel.COLOR_WHITE
        pyxel.rect(self.input_field_rect[0], self.input_field_rect[1], 
                  self.input_field_rect[2], self.input_field_rect[3], field_color)
        pyxel.rectb(self.input_field_rect[0], self.input_field_rect[1], 
                   self.input_field_rect[2], self.input_field_rect[3], pyxel.COLOR_BLACK)
        
        # 入力テキスト
        text_x = self.input_field_rect[0] + 4
        text_y = self.input_field_rect[1] + 6
        pyxel.text(text_x, text_y, self.input_text, pyxel.COLOR_BLACK)
        
        # カーソル描画（点滅）
        if (self.cursor_blink_timer // 30) % 2 == 0:  # 30フレームごとに点滅
            cursor_x = text_x + self.cursor_pos * 4
            pyxel.line(cursor_x, text_y, cursor_x, text_y + 6, pyxel.COLOR_BLACK)
    
    def _draw_validation_info(self):
        """バリデーション情報表示"""
        format_info = self._get_format_info()
        info_lines = format_info.split('\n')
        
        y_offset = 0
        for line in info_lines:
            pyxel.text(self.dialog_x + 10, self.dialog_y + 45 + y_offset, line, pyxel.COLOR_GRAY)
            y_offset += 8
    
    def _draw_buttons(self):
        """ボタン描画"""
        # OKボタン
        ok_color = pyxel.COLOR_GREEN if self.mouse_over_ok else pyxel.COLOR_DARK_BLUE
        pyxel.rect(self.ok_button_rect[0], self.ok_button_rect[1], 
                  self.ok_button_rect[2], self.ok_button_rect[3], ok_color)
        pyxel.rectb(self.ok_button_rect[0], self.ok_button_rect[1], 
                   self.ok_button_rect[2], self.ok_button_rect[3], pyxel.COLOR_WHITE)
        
        ok_text_x = self.ok_button_rect[0] + (self.ok_button_rect[2] - 8) // 2
        ok_text_y = self.ok_button_rect[1] + 6
        pyxel.text(ok_text_x, ok_text_y, "OK", pyxel.COLOR_WHITE)
        
        # Cancelボタン
        cancel_color = pyxel.COLOR_RED if self.mouse_over_cancel else pyxel.COLOR_DARK_BLUE
        pyxel.rect(self.cancel_button_rect[0], self.cancel_button_rect[1], 
                  self.cancel_button_rect[2], self.cancel_button_rect[3], cancel_color)
        pyxel.rectb(self.cancel_button_rect[0], self.cancel_button_rect[1], 
                   self.cancel_button_rect[2], self.cancel_button_rect[3], pyxel.COLOR_WHITE)
        
        cancel_text_x = self.cancel_button_rect[0] + (self.cancel_button_rect[2] - 24) // 2
        cancel_text_y = self.cancel_button_rect[1] + 6
        pyxel.text(cancel_text_x, cancel_text_y, "Cancel", pyxel.COLOR_WHITE)
    
    def _get_format_info(self) -> str:
        """デバイスタイプ別フォーマット情報取得"""
        format_info = {
            DeviceType.CONTACT_A: "Format: X000-X377\nExample: X001, X010",
            DeviceType.CONTACT_B: "Format: X000-X377\nExample: X001, X010", 
            DeviceType.COIL_STD: "Format: Y000-Y377, M0-M7999\nExample: Y001, M100",
            DeviceType.COIL_REV: "Format: Y000-Y377, M0-M7999\nExample: Y001, M100",
            DeviceType.TIMER: "Format: T000-T255\nExample: T001, T050",
            DeviceType.COUNTER: "Format: C000-C255\nExample: C001, C020"
        }
        
        return format_info.get(self.device_type, "Format: Not specified")
    
    def _validate_device_id(self, device_id: str) -> bool:
        """PLC標準準拠デバイスIDバリデーション"""
        if not device_id:
            self.error_message = "Device ID cannot be empty"
            return False
            
        # デバイスタイプ別バリデーション
        if self.device_type in [DeviceType.CONTACT_A, DeviceType.CONTACT_B]:
            return self._validate_x_device(device_id)
        elif self.device_type in [DeviceType.COIL_STD, DeviceType.COIL_REV]:
            return self._validate_y_m_device(device_id)
        elif self.device_type == DeviceType.TIMER:
            return self._validate_timer_device(device_id)
        elif self.device_type == DeviceType.COUNTER:
            return self._validate_counter_device(device_id)
        elif self.device_type in [DeviceType.LINK_HORZ, DeviceType.LINK_BRANCH, DeviceType.LINK_VIRT]:
            # LINK系デバイスはID不要
            self.error_message = "Link devices do not require ID"
            return False
        else:
            self.error_message = "Unknown device type"
            return False
    
    def _validate_x_device(self, device_id: str) -> bool:
        """X接点デバイスバリデーション (X000-X377, 8進数)"""
        pattern = r'^X[0-3][0-7][0-7]$'
        if re.match(pattern, device_id):
            return True
        else:
            self.error_message = "Format: X000-X377 (octal)"
            return False
    
    def _validate_y_m_device(self, device_id: str) -> bool:
        """Y出力・M内部リレーバリデーション"""
        # Y000-Y377 (8進数)
        y_pattern = r'^Y[0-3][0-7][0-7]$'
        if re.match(y_pattern, device_id):
            return True
            
        # M0-M7999 (10進数) - 3桁または4桁に対応
        m_pattern = r'^M([0-9]{1,3}|[0-7][0-9]{3})$'
        if re.match(m_pattern, device_id):
            # 数値範囲チェック (0-7999)
            num = int(device_id[1:])
            if 0 <= num <= 7999:
                return True
            
        self.error_message = "Format: Y000-Y377 or M0-M7999"
        return False
    
    def _validate_timer_device(self, device_id: str) -> bool:
        """タイマーデバイスバリデーション (T000-T255)"""
        pattern = r'^T([0-1][0-9]{2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2})$'
        if re.match(pattern, device_id):
            # 数値範囲チェック
            num = int(device_id[1:])
            if 0 <= num <= 255:
                return True
                
        self.error_message = "Format: T000-T255"
        return False
    
    def _validate_counter_device(self, device_id: str) -> bool:
        """カウンターデバイスバリデーション (C000-C255)"""
        pattern = r'^C([0-1][0-9]{2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2})$'
        if re.match(pattern, device_id):
            # 数値範囲チェック
            num = int(device_id[1:])
            if 0 <= num <= 255:
                return True
                
        self.error_message = "Format: C000-C255"
        return False
    
    def _point_in_rect(self, x: int, y: int, rect: Tuple[int, int, int, int]) -> bool:
        """点が矩形内にあるかチェック"""
        rx, ry, rw, rh = rect
        return rx <= x <= rx + rw and ry <= y <= ry + rh
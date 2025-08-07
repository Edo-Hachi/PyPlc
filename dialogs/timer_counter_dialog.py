# PyPlc Ver3 Timer Counter Preset Dialog System
# 作成日: 2025-08-07
# 目標: タイマー・カウンタープリセット値編集ダイアログ

import pyxel
from typing import Tuple, Optional
from config import DeviceType, TimerConfig, CounterConfig

class TimerCounterPresetDialog:
    """
    タイマー・カウンタープリセット値編集専用ダイアログ
    PLC標準準拠のプリセット値入力・バリデーション機能
    """
    
    def __init__(self):
        self.dialog_w = 260
        self.dialog_h = 140
        self.dialog_x = (384 - self.dialog_w) // 2  # Ver3画面サイズ対応
        self.dialog_y = (384 - self.dialog_h) // 2
        
        self.input_text = ""
        self.cursor_pos = 0
        self.is_visible = False
        self.result_ready = False
        self.edit_success = False
        self.new_preset_value = 0
        self.error_message = ""
        self.device_type = DeviceType.TIMER_TON
        
    def show(self, device_type: DeviceType, current_preset: int) -> Tuple[bool, int]:
        """
        プリセット値編集ダイアログ表示・実行
        
        Args:
            device_type: デバイス種別（TIMER_TON/COUNTER_CTU）
            current_preset: 現在のプリセット値
            
        Returns:
            Tuple[bool, int]: (success, new_preset_value)
        """
        self.device_type = device_type
        self.input_text = str(current_preset)
        self.cursor_pos = len(self.input_text)
        self.is_visible = True
        self.result_ready = False
        self.edit_success = False
        self.error_message = ""
        
        # モーダルループ
        while self.is_visible and not self.result_ready:
            self._handle_input()
            self._draw()
            pyxel.flip()
            
        return self.edit_success, self.new_preset_value
    
    def _handle_input(self) -> None:
        """キーボード入力処理（数値入力専用）"""
        
        # ESCキー: キャンセル
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.is_visible = False
            self.result_ready = True
            self.edit_success = False
            return
            
        # Enterキー: プリセット値更新実行
        if pyxel.btnp(pyxel.KEY_RETURN):
            self._execute_preset_update()
            return
            
        # バックスペース: 文字削除
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            if self.cursor_pos > 0:
                self.input_text = (self.input_text[:self.cursor_pos-1] + 
                                 self.input_text[self.cursor_pos:])
                self.cursor_pos -= 1
                self.error_message = ""
                
        # Delete: 右文字削除
        if pyxel.btnp(pyxel.KEY_DELETE):
            if self.cursor_pos < len(self.input_text):
                self.input_text = (self.input_text[:self.cursor_pos] + 
                                 self.input_text[self.cursor_pos+1:])
                self.error_message = ""
                
        # カーソル移動
        if pyxel.btnp(pyxel.KEY_LEFT) and self.cursor_pos > 0:
            self.cursor_pos -= 1
        if pyxel.btnp(pyxel.KEY_RIGHT) and self.cursor_pos < len(self.input_text):
            self.cursor_pos += 1
        if pyxel.btnp(pyxel.KEY_HOME):
            self.cursor_pos = 0
        if pyxel.btnp(pyxel.KEY_END):
            self.cursor_pos = len(self.input_text)
            
        # 数値入力のみ許可
        self._handle_numeric_input()
    
    def _handle_numeric_input(self) -> None:
        """数値入力処理（0-9のみ許可）"""
        new_char = ""
        
        # 数字入力（0-9）
        for i in range(10):
            if pyxel.btnp(pyxel.KEY_0 + i):
                new_char = str(i)
                break
                
        # 数字が入力された場合
        if new_char:
            # 最大桁数制限（タイマー: 5桁、カウンター: 5桁）
            max_length = 5
            if len(self.input_text) < max_length:
                self.input_text = (self.input_text[:self.cursor_pos] + 
                                 new_char + 
                                 self.input_text[self.cursor_pos:])
                self.cursor_pos += 1
                self.error_message = ""
    
    def _execute_preset_update(self) -> None:
        """プリセット値更新実行処理"""
        # 空文字チェック
        if not self.input_text:
            self.error_message = "Value cannot be empty"
            return
            
        # 数値変換
        try:
            preset_value = int(self.input_text)
        except ValueError:
            self.error_message = "Invalid number format"
            return
            
        # デバイス種別に応じたバリデーション
        if self.device_type == DeviceType.TIMER_TON:
            if not self._validate_timer_preset(preset_value):
                return
            # タイマー: PLC標準準拠（1ms単位、そのまま保存）
            self.new_preset_value = preset_value
            print(f"[TIMER PRESET DEBUG] User input: {preset_value}ms -> Internal value: {preset_value}ms")
            
        elif self.device_type == DeviceType.COUNTER_CTU:
            if not self._validate_counter_preset(preset_value):
                return
            # カウンター: そのまま（回数）
            self.new_preset_value = preset_value
            
        else:
            self.error_message = "Unsupported device type"
            return
        self.edit_success = True
        self.result_ready = True
        self.is_visible = False
    
    def _validate_timer_preset(self, value: int) -> bool:
        """タイマープリセット値バリデーション"""
        if value < TimerConfig.MIN_PRESET:
            self.error_message = f"Min value: {TimerConfig.MIN_PRESET}"
            return False
        if value > TimerConfig.MAX_PRESET:
            self.error_message = f"Max value: {TimerConfig.MAX_PRESET}"
            return False
        return True
    
    def _validate_counter_preset(self, value: int) -> bool:
        """カウンタープリセット値バリデーション"""
        if value < CounterConfig.MIN_PRESET:
            self.error_message = f"Min value: {CounterConfig.MIN_PRESET}"
            return False
        if value > CounterConfig.MAX_PRESET:
            self.error_message = f"Max value: {CounterConfig.MAX_PRESET}"
            return False
        return True
    
    def _draw(self) -> None:
        """ダイアログ描画"""
        # 背景暗転効果
        for y in range(0, 384, 4):
            pyxel.line(0, y, 384, y, pyxel.COLOR_BLACK)
        for x in range(0, 384, 4):
            pyxel.line(x, 0, x, 384, pyxel.COLOR_BLACK)
            
        # ダイアログ本体
        pyxel.rect(self.dialog_x, self.dialog_y, self.dialog_w, self.dialog_h, pyxel.COLOR_DARK_BLUE)
        pyxel.rectb(self.dialog_x, self.dialog_y, self.dialog_w, self.dialog_h, pyxel.COLOR_WHITE)
        
        # タイトル（デバイス種別に応じて変更）
        if self.device_type == DeviceType.TIMER_TON:
            title = "Timer Preset Value"
        elif self.device_type == DeviceType.COUNTER_CTU:
            title = "Counter Preset Value"
        else:
            title = "Preset Value"
            
        title_x = self.dialog_x + (self.dialog_w - len(title) * 4) // 2
        pyxel.text(title_x, self.dialog_y + 10, title, pyxel.COLOR_WHITE)
        
        # プリセット値入力ラベル
        pyxel.text(self.dialog_x + 20, self.dialog_y + 35, "Enter preset value:", pyxel.COLOR_WHITE)
        
        # テキスト入力ボックス
        input_x = self.dialog_x + 20
        input_y = self.dialog_y + 55
        input_w = self.dialog_w - 40
        input_h = 20
        
        pyxel.rect(input_x, input_y, input_w, input_h, pyxel.COLOR_WHITE)
        pyxel.rectb(input_x, input_y, input_w, input_h, pyxel.COLOR_BLACK)
        
        # 入力テキスト表示
        if self.input_text:
            pyxel.text(input_x + 4, input_y + 6, self.input_text, pyxel.COLOR_BLACK)
            
        # カーソル描画（点滅効果）
        if pyxel.frame_count % 60 < 30:  # 0.5秒間隔で点滅
            cursor_x = input_x + 4 + self.cursor_pos * 4
            pyxel.line(cursor_x, input_y + 2, cursor_x, input_y + 16, pyxel.COLOR_RED)
            
        # 単位・範囲表示
        self._draw_unit_and_range()
        
        # エラーメッセージ表示
        if self.error_message:
            pyxel.text(self.dialog_x + 20, self.dialog_y + 95, self.error_message, pyxel.COLOR_RED)
            
        # ボタン・操作ヒント
        self._draw_buttons()
        
    def _draw_unit_and_range(self) -> None:
        """単位・範囲情報表示"""
        if self.device_type == DeviceType.TIMER_TON:
            unit_text = "Unit: 1ms"
            range_text = f"Range: {TimerConfig.MIN_PRESET}-{TimerConfig.MAX_PRESET}ms"
        elif self.device_type == DeviceType.COUNTER_CTU:
            unit_text = "Unit: count"
            range_text = f"Range: {CounterConfig.MIN_PRESET}-{CounterConfig.MAX_PRESET}"
        else:
            unit_text = "Unit: unknown"
            range_text = "Range: unknown"
            
        pyxel.text(self.dialog_x + 20, self.dialog_y + 80, unit_text, pyxel.COLOR_GRAY)
        pyxel.text(self.dialog_x + 120, self.dialog_y + 80, range_text, pyxel.COLOR_GRAY)
        
    def _draw_buttons(self) -> None:
        """OK/Cancelボタン・操作ヒント描画"""
        # OKボタン
        ok_x = self.dialog_x + 60
        ok_y = self.dialog_y + self.dialog_h - 30
        ok_w = 50
        ok_h = 20
        
        pyxel.rect(ok_x, ok_y, ok_w, ok_h, pyxel.COLOR_GREEN)
        pyxel.rectb(ok_x, ok_y, ok_w, ok_h, pyxel.COLOR_WHITE)
        pyxel.text(ok_x + 18, ok_y + 6, "OK", pyxel.COLOR_WHITE)
        
        # Cancelボタン
        cancel_x = self.dialog_x + 150
        
        pyxel.rect(cancel_x, ok_y, ok_w, ok_h, pyxel.COLOR_RED)
        pyxel.rectb(cancel_x, ok_y, ok_w, ok_h, pyxel.COLOR_WHITE)
        pyxel.text(cancel_x + 10, ok_y + 6, "Cancel", pyxel.COLOR_WHITE)
        
        # 操作ヒント
        hint_y = self.dialog_y + self.dialog_h - 10
        pyxel.text(self.dialog_x + 20, hint_y, "Enter:Set  ESC:Cancel", pyxel.COLOR_GRAY)
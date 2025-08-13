# PyPlc Ver3 Dialog System - TimerCounterDialog (JSON版)
# Phase B3: JSON定義によるタイマー・カウンタープリセット値編集ダイアログ
# 作成日: 2025-08-08

import pyxel
import re
from typing import Optional, Tuple
from .base_dialog import BaseDialog
from .json_dialog_loader import JSONDialogLoader
from .control_factory import ControlFactory
from config import DeviceType, TimerConfig, CounterConfig


class TimerCounterDialogJSON(BaseDialog):
    """
    JSON定義によるタイマー・カウンタープリセット値編集ダイアログ
    既存TimerCounterPresetDialogと同等機能をJSON駆動で実現
    """
    
    def __init__(self, device_type: DeviceType, current_preset: int = 0):
        """
        TimerCounterDialogJSON初期化
        
        Args:
            device_type: デバイスタイプ（TIMER_TON or COUNTER_CTU）
            current_preset: 現在のプリセット値
        """
        super().__init__()
        
        self.device_type = device_type
        self.current_preset = current_preset
        self.input_text = str(current_preset)
        self.dialog_result = None
        self.error_message = ""
        self.new_preset_value = current_preset
        
        # デバイス種別に応じてJSON定義を選択
        if device_type == DeviceType.TIMER_TON:
            json_filename = "timer_settings.json"
        elif device_type == DeviceType.COUNTER_CTU:
            json_filename = "counter_settings.json"
        else:
            raise ValueError(f"Unsupported device type: {device_type}")
        
        # JSON定義からダイアログを構築
        self.loader = JSONDialogLoader()
        self.factory = ControlFactory()
        
        # ダイアログ定義を読み込み
        dialog_definition = self.loader.load_dialog_definition(json_filename)
        
        if dialog_definition:
            # ダイアログ基本設定
            self.title = dialog_definition.get("title", "Timer/Counter Settings")
            self.width = dialog_definition.get("width", 260)
            self.height = dialog_definition.get("height", 160)
            
            # 位置を再計算
            self.x = (384 - self.width) // 2  # Ver3画面サイズ対応
            self.y = (384 - self.height) // 2
            
            # コントロールを生成・追加
            self._create_controls(dialog_definition.get("controls", []))
            
            # イベント登録
            self._setup_events()
        else:
            # フォールバック: 基本設定
            print(f"Warning: Could not load {json_filename}")
            self.title = f"{device_type.value} Settings"
            self.width = 260
            self.height = 160
            self.x = (384 - self.width) // 2
            self.y = (384 - self.height) // 2
        
        print(f"TimerCounterDialogJSON initialized: {self.title} (preset: {current_preset})")
    
    def _draw_custom(self) -> None:
        """
        カスタム描画処理（BaseDialogの抽象メソッド実装）
        """
        # TimerCounterDialogJSONは標準描画のみ使用
        pass
    
    def _create_controls(self, control_definitions: list) -> None:
        """
        JSON定義からコントロールを作成・追加
        
        Args:
            control_definitions: コントロール定義リスト
        """
        for control_def in control_definitions:
            try:
                control = self.factory.create_control(control_def)
                if control:
                    self.add_control(control_def["id"], control)
                    print(f"Control added: {control_def['id']}")
            except Exception as e:
                print(f"Failed to create control {control_def.get('id', 'unknown')}: {e}")
        
        # 現在のプリセット値を入力フィールドに設定
        preset_input = self.get_control("preset_input")
        if preset_input and hasattr(preset_input, 'set_text'):
            preset_input.set_text(str(self.current_preset))
            self.input_text = str(self.current_preset)
    
    def _setup_events(self) -> None:
        """イベント処理を設定"""
        # プリセット値入力の変更イベント
        preset_input = self.get_control("preset_input")
        if preset_input:
            preset_input.on("change", self._on_preset_changed)
            preset_input.on("enter", self._on_ok_pressed)
        
        # ボタンクリックイベント
        ok_button = self.get_control("ok_button")
        if ok_button:
            ok_button.on("click", self._on_ok_pressed)
        
        cancel_button = self.get_control("cancel_button")
        if cancel_button:
            cancel_button.on("click", self._on_cancel_pressed)
    
    def _on_preset_changed(self, control, old_text: str, new_text: str) -> None:
        """
        プリセット値入力変更時の処理
        
        Args:
            control: 入力コントロール
            old_text: 変更前のテキスト
            new_text: 変更後のテキスト
        """
        self.input_text = new_text
        
        # エラーメッセージをクリア
        self._clear_error_message()
        
        print(f"Preset value changed: '{old_text}' -> '{new_text}'")
    
    def _on_ok_pressed(self, *args) -> None:
        """OKボタン押下時の処理"""
        if self._validate_preset_value():
            self.dialog_result = True
            self.close(True)  # BaseDialogのresultにもTrueを設定
            print(f"Timer/Counter dialog: OK pressed with preset '{self.new_preset_value}'")
        else:
            print("Timer/Counter dialog: Invalid preset value")
    
    def _on_cancel_pressed(self, *args) -> None:
        """キャンセルボタン押下時の処理"""
        self.dialog_result = False
        self.close(False)  # BaseDialogのresultにもFalseを設定
        print("Timer/Counter dialog: Cancel pressed")
    
    def _validate_preset_value(self) -> bool:
        """
        プリセット値バリデーション
        
        Returns:
            有効なプリセット値の場合True
        """
        text = self.input_text.strip()
        
        if not text:
            self._show_error_message("Preset value cannot be empty")
            return False
        
        # 数値チェック
        if not re.match(r'^\d+$', text):
            self._show_error_message("Preset value must be numeric")
            return False
        
        try:
            value = int(text)
        except ValueError:
            self._show_error_message("Invalid numeric value")
            return False
        
        # 範囲チェック（デバイス種別に応じて）
        if self.device_type == DeviceType.TIMER_TON:
            min_val, max_val = TimerConfig.MIN_PRESET, TimerConfig.MAX_PRESET
            if value < min_val or value > max_val:
                self._show_error_message(f"Timer range: {min_val} - {max_val}")
                return False
        elif self.device_type == DeviceType.COUNTER_CTU:
            min_val, max_val = CounterConfig.MIN_PRESET, CounterConfig.MAX_PRESET
            if value < min_val or value > max_val:
                self._show_error_message(f"Counter range: {min_val} - {max_val}")
                return False
        
        # バリデーション成功
        self.new_preset_value = value
        return True
    
    def _show_error_message(self, message: str) -> None:
        """
        エラーメッセージを表示
        
        Args:
            message: エラーメッセージ
        """
        self.error_message = message
        error_label = self.get_control("error_label")
        if error_label:
            error_label.text = message
            error_label.visible = True
    
    def _clear_error_message(self) -> None:
        """エラーメッセージをクリア"""
        self.error_message = ""
        error_label = self.get_control("error_label")
        if error_label:
            error_label.text = ""
            error_label.visible = False
    
    def show_timer_counter_dialog(self) -> Tuple[bool, int]:
        """
        タイマー・カウンターダイアログを表示
        
        Returns:
            (success: bool, preset_value: int)
        """
        try:
            result = self.show()
            if result and self.dialog_result:
                return True, self.new_preset_value
            else:
                return False, self.current_preset
        except Exception as e:
            print(f"TimerCounterDialogJSON error: {e}")
            return False, self.current_preset


def show_timer_counter_preset_dialog(device_type: DeviceType, current_preset: int = 0) -> Tuple[bool, int]:
    """
    タイマー・カウンタープリセット値編集ダイアログを表示する便利関数
    
    Args:
        device_type: デバイスタイプ（TIMER_TON or COUNTER_CTU）
        current_preset: 現在のプリセット値
        
    Returns:
        (success: bool, preset_value: int)
    """
    try:
        dialog = TimerCounterDialogJSON(device_type, current_preset)
        return dialog.show_timer_counter_dialog()
    except Exception as e:
        print(f"show_timer_counter_preset_dialog error: {e}")
        return False, current_preset
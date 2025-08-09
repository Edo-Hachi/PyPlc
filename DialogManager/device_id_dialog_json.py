"""
DeviceIDDialogJSON - JSON定義によるDeviceIDDialog

PyPlc Ver3 Dialog System - Phase 2 Implementation
既存DeviceIDDialogと同等の機能をJSON定義で実現
"""

from DialogManager.base_dialog import BaseDialog
from DialogManager.json_dialog_loader import JSONDialogLoader
from DialogManager.control_factory import ControlFactory
from DialogManager.events.event_system import get_dialog_event_system
from DialogManager.validation.validator import create_validator_from_config
from config import DeviceType
from typing import Tuple, Optional
import re


class DeviceIDDialogJSON(BaseDialog):
    """
    JSON定義によるDeviceIDDialog
    
    機能:
    - 既存DeviceIDDialogと同等の機能
    - JSON定義による完全な宣言的UI
    - バリデーションシステム統合
    - 疎結合イベントシステム活用
    """
    
    def __init__(self, device_type: DeviceType, current_id: str = ""):
        """
        DeviceIDDialogJSON初期化
        
        Args:
            device_type: デバイスタイプ
            current_id: 現在のデバイスID
        """
        self.device_type = device_type
        self.current_id = current_id
        self.input_text = current_id
        self.validation_error = ""
        self.is_valid = True
        
        # JSON定義を読み込み
        self.loader = JSONDialogLoader()
        self.definition = self.loader.load_dialog_definition("device_settings.json")
        
        if self.definition is None:
            raise ValueError("Failed to load device_settings.json")
        
        # BaseDialogを初期化
        super().__init__(
            title=self.definition["title"],
            width=self.definition["width"],
            height=self.definition["height"]
        )
        
        # ControlFactoryでコントロールを生成
        self.factory = ControlFactory()
        self._create_controls()
        
        # イベントシステムを取得
        self.event_system = get_dialog_event_system()
        
        # バリデーションシステムを設定
        self._setup_validation()
        
        # 初期値設定
        self._setup_initial_values()
        
        print(f"DeviceIDDialogJSON initialized for {device_type}")
    
    def _create_controls(self) -> None:
        """
        JSON定義からコントロールを生成・追加
        """
        for control_def in self.definition["controls"]:
            # ControlFactoryでコントロールを生成
            control = self.factory.create_control(control_def)
            
            if control is not None:
                # ダイアログにコントロールを追加
                self.add_control(control.id, control)
                
                # イベントハンドラーを設定
                self._setup_control_events(control, control_def)
    
    def _setup_control_events(self, control, control_def: dict) -> None:
        """
        コントロールのイベントハンドラーを設定
        
        Args:
            control: コントロールオブジェクト
            control_def: コントロール定義
        """
        control_id = control.id
        
        if control_id == "device_id_input":
            # テキスト入力フィールドのイベント
            control.on("change", self._on_input_changed)
            control.on("focus", self._on_input_focused)
            control.on("blur", self._on_input_blurred)
            control.on("enter", self._on_enter_pressed)
            control.on("validate", self._on_validation_result)
        elif control_id == "ok_button":
            control.on("click", self._on_ok_clicked)
        elif control_id == "cancel_button":
            control.on("click", self._on_cancel_clicked)
    
    def _setup_validation(self) -> None:
        """
        バリデーションシステムを設定
        """
        # デバイスID入力フィールドにバリデーターを設定
        device_input = self.get_control("device_id_input")
        if device_input and hasattr(device_input, 'set_validator'):
            # JSON定義からバリデーション設定を取得
            for control_def in self.definition["controls"]:
                if control_def["id"] == "device_id_input":
                    validation_config = control_def.get("validation", {})
                    base_validator = create_validator_from_config(validation_config)
                    # RSTのみ、対象アドレスをT/Cかつ0-255に制限
                    if self.device_type == DeviceType.RST:
                        device_input.set_validator(lambda text: self._validate_rst_address(text, base_validator))
                    else:
                        device_input.set_validator(lambda text: self._validate_device_id(text, base_validator))
                    break
    
    def _validate_device_id(self, text: str, validator) -> Tuple[bool, str]:
        """
        デバイスIDバリデーション
        
        Args:
            text: 入力テキスト
            validator: バリデーター
            
        Returns:
            (is_valid, error_message)
        """
        try:
            result = validator.validate(text)
            return result.is_valid, result.error_message
        except Exception as e:
            return False, f"Validation error: {e}"

    def _validate_rst_address(self, text: str, base_validator) -> Tuple[bool, str]:
        """
        RST用のターゲットアドレスバリデーション
        - 形式検証は既存のPLCアドレス検証を使用
        - 追加制約: TまたはCのみ、数値は0-255
        """
        try:
            result = base_validator.validate(text)
            if not result.is_valid:
                return result.is_valid, result.error_message
            value = text.strip().upper()
            match = re.match(r'^(T|C)(\d+)$', value)
            if not match:
                return False, "Use T0-255 or C0-255"
            addr_num = int(match.group(2))
            if not (0 <= addr_num <= 255):
                return False, "T/C address must be 0-255"
            return True, ""
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def _setup_initial_values(self) -> None:
        """
        初期値を設定
        """
        # デバイスタイプラベルを更新
        device_type_label = self.get_control("device_type_label")
        if device_type_label and hasattr(device_type_label, 'text'):
            device_type_name = self.device_type.name if hasattr(self.device_type, 'name') else str(self.device_type)
            device_type_label.text = f"デバイスタイプ: {device_type_name}"
        
        # 入力フィールドに現在の値を設定
        device_input = self.get_control("device_id_input")
        if device_input and hasattr(device_input, 'set_text'):
            device_input.set_text(self.current_id)
            self.input_text = self.current_id
    
    def _on_input_changed(self, control, old_text: str, new_text: str) -> None:
        """
        入力テキスト変更時の処理
        
        Args:
            control: 入力コントロール
            old_text: 変更前のテキスト
            new_text: 変更後のテキスト
        """
        self.input_text = new_text
        
        # エラーメッセージをクリア
        self._clear_error_message()
        
        print(f"Device ID input changed: '{old_text}' -> '{new_text}'")
    
    def _on_input_focused(self, control) -> None:
        """
        入力フィールドフォーカス時の処理
        
        Args:
            control: 入力コントロール
        """
        print("Device ID input focused")
    
    def _on_input_blurred(self, control) -> None:
        """
        入力フィールドフォーカス解除時の処理
        
        Args:
            control: 入力コントロール
        """
        print("Device ID input blurred")
    
    def _on_enter_pressed(self, control) -> None:
        """
        Enterキー押下時の処理（OK処理）
        
        Args:
            control: 入力コントロール
        """
        print("Enter key pressed in device ID input")
        self._handle_ok_action()
    
    def _on_validation_result(self, control, is_valid: bool, error_message: str) -> None:
        """
        バリデーション結果処理
        
        Args:
            control: 入力コントロール
            is_valid: バリデーション結果
            error_message: エラーメッセージ
        """
        self.is_valid = is_valid
        self.validation_error = error_message
        
        if not is_valid:
            self._show_error_message(error_message)
        else:
            self._clear_error_message()
        
        print(f"Validation result: {is_valid}, Error: {error_message}")
    
    def _on_ok_clicked(self, control) -> None:
        """
        OKボタンクリック時の処理
        
        Args:
            control: OKボタンコントロール
        """
        print("OK button clicked!")
        self._handle_ok_action()
    
    def _on_cancel_clicked(self, control) -> None:
        """
        Cancelボタンクリック時の処理
        
        Args:
            control: Cancelボタンコントロール
        """
        print("Cancel button clicked!")
        self.close((False, self.current_id))
    
    def _handle_ok_action(self) -> None:
        """
        OK処理の実行
        """
        # 最終バリデーション実行
        device_input = self.get_control("device_id_input")
        if device_input and hasattr(device_input, 'validate'):
            if not device_input.validate():
                print("Validation failed, cannot proceed")
                return
        
        if self.is_valid and self.input_text.strip():
            print(f"Device ID dialog OK: '{self.input_text}'")
            self.close((True, self.input_text.strip().upper()))
        else:
            error_msg = self.validation_error or "有効なデバイスIDを入力してください"
            self._show_error_message(error_msg)
            print(f"OK action failed: {error_msg}")
    
    def _show_error_message(self, message: str) -> None:
        """
        エラーメッセージを表示
        
        Args:
            message: エラーメッセージ
        """
        error_label = self.get_control("error_label")
        if error_label:
            if hasattr(error_label, 'text'):
                error_label.text = message
            if hasattr(error_label, 'visible'):
                error_label.visible = True
    
    def _clear_error_message(self) -> None:
        """
        エラーメッセージをクリア
        """
        error_label = self.get_control("error_label")
        if error_label:
            if hasattr(error_label, 'text'):
                error_label.text = ""
            if hasattr(error_label, 'visible'):
                error_label.visible = False
    
    def _handle_custom_input(self) -> None:
        """
        カスタム入力処理（ボタンのホバー状態更新）
        """
        import pyxel
        
        # 各ボタンコントロールのホバー状態を更新
        for control_id in ["ok_button", "cancel_button"]:
            control = self.get_control(control_id)
            if control is not None and hasattr(control, 'is_hovered'):
                # ホバー状態を更新
                abs_x, abs_y, w, h = control.get_absolute_rect(self.x, self.y)
                control.is_hovered = (abs_x <= self.mouse_x <= abs_x + w and 
                                    abs_y <= self.mouse_y <= abs_y + h)
                
                # マウスクリック処理
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and control.is_hovered:
                    control.emit("click")
    
    def _draw_custom(self) -> None:
        """
        カスタム描画処理
        """
        # Phase 2では基本描画のみ
        pass
    
    def show_modal(self, background_draw_func=None) -> Tuple[bool, str]:
        """
        モーダル表示（既存DeviceIDDialogとの互換性のため）
        
        Args:
            background_draw_func: 背景描画関数（未使用）
            
        Returns:
            (success: bool, device_id: str)
        """
        result = self.show()
        
        if isinstance(result, tuple):
            return result
        else:
            # フォールバック
            return (False, self.current_id)


def show_device_id_dialog(device_type: DeviceType, current_id: str = "") -> Tuple[bool, str]:
    """
    DeviceIDDialogを表示する便利関数
    
    Args:
        device_type: デバイスタイプ
        current_id: 現在のデバイスID
        
    Returns:
        (success: bool, device_id: str)
    """
    try:
        dialog = DeviceIDDialogJSON(device_type, current_id)
        return dialog.show_modal()
        
    except Exception as e:
        print(f"DeviceIDDialog error: {e}")
        return (False, current_id)

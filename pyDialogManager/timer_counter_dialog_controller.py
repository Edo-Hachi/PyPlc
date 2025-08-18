"""
タイマー・カウンターの設定編集ダイアログのコントローラー
"""
import re
import pyxel
from .dialog_manager import DialogManager
from config import DeviceType, TimerConfig, CounterConfig

class TimerCounterDialogController:
    """タイマー・カウンターの設定編集ダイアログのロジックを管理する"""

    def __init__(self, dialog_manager: DialogManager):
        self.dialog_manager = dialog_manager
        self.active_dialog = None
        self.result = None
        self.device_type = None
        self.last_device_id_text = ""
        self.last_preset_text = ""

    def show_dialog(self, device_type: DeviceType, initial_preset_value: int = 0, initial_device_id: str = ""):
        """ダイアログを表示する"""
        self.result = None
        self.device_type = device_type
        self.last_device_id_text = initial_device_id
        self.last_preset_text = str(initial_preset_value)
        
        self.dialog_manager.show("IDD_TIMER_COUNTER_EDIT")
        self.active_dialog = self.dialog_manager.active_dialog

        if self.active_dialog:
            self.active_dialog.title = f"Edit {device_type.name} Settings"
            
            # デバイスタイプ表示を更新
            type_widget = self._find_widget("IDC_LABEL_TYPE")
            if type_widget:
                type_widget.text = f"Type: {device_type.name}"
            
            # デバイスID初期値を設定
            device_id_widget = self._find_widget("IDC_DEVICE_ID_INPUT")
            if device_id_widget:
                device_id_widget.text = initial_device_id
            
            # プリセット値初期値を設定
            preset_widget = self._find_widget("IDC_PRESET_INPUT")
            if preset_widget:
                preset_widget.text = str(initial_preset_value)
            
            # エラーメッセージをクリア
            self._clear_error_message()

    def get_result(self):
        """結果を取得し、クリアする"""
        result = self.result
        self.result = None
        return result

    def update(self):
        """フレームごとの更新処理"""
        # マネージャーと自身のアクティブダイアログが一致しない場合、自身を非アクティブ化
        if self.active_dialog and self.active_dialog != self.dialog_manager.active_dialog:
            self.active_dialog = None

        if not self.active_dialog:
            return

        # リアルタイムバリデーション
        self._check_input_validation()

        # ボタンイベント処理
        ok_button = self._find_widget("IDOK")
        if ok_button and ok_button.is_pressed:
            self._handle_ok()

        cancel_button = self._find_widget("IDCANCEL")
        if cancel_button and cancel_button.is_pressed:
            self._handle_cancel()

    def _check_input_validation(self):
        """入力内容のリアルタイムバリデーション"""
        device_id_widget = self._find_widget("IDC_DEVICE_ID_INPUT")
        preset_widget = self._find_widget("IDC_PRESET_INPUT")
        
        if not device_id_widget or not preset_widget:
            return
        
        device_id_text = device_id_widget.text
        preset_text = preset_widget.text
        
        # デバイスIDまたはプリセット値が変更された場合
        if device_id_text != self.last_device_id_text or preset_text != self.last_preset_text:
            self.last_device_id_text = device_id_text
            self.last_preset_text = preset_text
            
            # デバイスIDバリデーション
            if device_id_text.strip():
                is_device_id_valid, device_id_error = self._validate_device_id(device_id_text.strip().upper())
                if not is_device_id_valid:
                    self._show_error_message(device_id_error)
                    return
            
            # プリセット値バリデーション
            if preset_text.strip():
                is_preset_valid, preset_error = self._validate_preset_value(preset_text.strip())
                if not is_preset_valid:
                    self._show_error_message(preset_error)
                    return
            
            # 両方とも有効な場合、エラーメッセージをクリア
            self._clear_error_message()

    def _show_error_message(self, message: str):
        """エラーメッセージを表示"""
        error_widget = self._find_widget("IDC_ERROR_MESSAGE")
        if error_widget:
            error_widget.text = message
            error_widget.color = pyxel.COLOR_RED

    def _clear_error_message(self):
        """エラーメッセージをクリア"""
        error_widget = self._find_widget("IDC_ERROR_MESSAGE")
        if error_widget:
            error_widget.text = ""
            error_widget.color = pyxel.COLOR_BLACK

    def _handle_ok(self):
        """OKボタンが押されたときの処理"""
        device_id_widget = self._find_widget("IDC_DEVICE_ID_INPUT")
        preset_widget = self._find_widget("IDC_PRESET_INPUT")
        
        if device_id_widget and preset_widget:
            device_id = device_id_widget.text.strip().upper()
            preset_text = preset_widget.text.strip()
            
            # デバイスIDバリデーション
            is_device_id_valid, device_id_error = self._validate_device_id(device_id)
            if not is_device_id_valid:
                self._show_error_message(device_id_error)
                return
            
            # プリセット値バリデーション
            is_preset_valid, preset_error = self._validate_preset_value(preset_text)
            if not is_preset_valid:
                self._show_error_message(preset_error)
                return
            
            # 両方とも有効な場合、結果を返す
            try:
                preset_value = int(preset_text)
                self.result = (True, device_id, preset_value)
                self.dialog_manager.close()
            except ValueError:
                self._show_error_message("Preset value must be an integer")

    def _handle_cancel(self):
        """Cancelボタンが押されたときの処理"""
        self.result = (False, None, None)
        self.dialog_manager.close()

    def _validate_device_id(self, device_id: str) -> tuple[bool, str]:
        """デバイスIDの妥当性を検証"""
        if not device_id:
            return False, "Device ID cannot be empty."
        
        if self.device_type == DeviceType.TIMER_TON:
            match = re.match(r'^T(\d+)$', device_id)
            if not match:
                return False, "Timer ID must be T followed by number (e.g., T1)."
            number = int(match.group(1))
            if not (0 <= number <= 255):
                return False, "Timer number must be 0-255."
        
        elif self.device_type == DeviceType.COUNTER_CTU:
            match = re.match(r'^C(\d+)$', device_id)
            if not match:
                return False, "Counter ID must be C followed by number (e.g., C1)."
            number = int(match.group(1))
            if not (0 <= number <= 255):
                return False, "Counter number must be 0-255."
        
        else:
            return False, f"Invalid device type: {self.device_type.name}"
        
        return True, ""

    def _validate_preset_value(self, preset_text: str) -> tuple[bool, str]:
        """プリセット値の妥当性を検証"""
        if not preset_text:
            return False, "Preset value cannot be empty."
        
        try:
            value = int(preset_text)
        except ValueError:
            return False, "Preset value must be an integer."
        
        if self.device_type == DeviceType.TIMER_TON:
            if not (TimerConfig.MIN_PRESET <= value <= TimerConfig.MAX_PRESET):
                return False, f"Timer preset must be {TimerConfig.MIN_PRESET}-{TimerConfig.MAX_PRESET}."
        
        elif self.device_type == DeviceType.COUNTER_CTU:
            if not (CounterConfig.MIN_PRESET <= value <= CounterConfig.MAX_PRESET):
                return False, f"Counter preset must be {CounterConfig.MIN_PRESET}-{CounterConfig.MAX_PRESET}."
        
        else:
            return False, f"Invalid device type: {self.device_type.name}"
        
        return True, ""

    def _is_valid_preset(self, value: int) -> bool:
        """後方互換性のためのプリセット値検証（簡易版）"""
        if self.device_type == DeviceType.TIMER_TON:
            return TimerConfig.MIN_PRESET <= value <= TimerConfig.MAX_PRESET
        elif self.device_type == DeviceType.COUNTER_CTU:
            return CounterConfig.MIN_PRESET <= value <= CounterConfig.MAX_PRESET
        return False

    def _find_widget(self, widget_id: str):
        """ウィジェットIDでウィジェットを検索"""
        if not self.active_dialog:
            return None
        for widget in self.active_dialog.widgets:
            if hasattr(widget, 'id') and widget.id == widget_id:
                return widget
        return None

    def is_active(self) -> bool:
        """ダイアログがアクティブかどうかを返す"""
        return self.dialog_manager.active_dialog is not None and self.active_dialog is not None

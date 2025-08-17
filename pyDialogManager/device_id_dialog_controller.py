"""
デバイスID編集ダイアログのコントローラー
"""
import re
from .dialog_manager import DialogManager
from config import DeviceType, TimerConfig, CounterConfig

class DeviceIdDialogController:
    """デバイスID編集ダイアログのロジックを管理する"""

    def __init__(self, dialog_manager: DialogManager):
        self.dialog_manager = dialog_manager
        self.active_dialog = None
        self.result = None
        self.device_type = None

    def show_dialog(self, device_type: DeviceType, initial_value: str = ""):
        """ダイアログを表示する"""
        self.result = None
        self.device_type = device_type
        self.dialog_manager.show("IDD_DEVICE_ID_EDIT")
        self.active_dialog = self.dialog_manager.active_dialog

        if self.active_dialog:
            self.active_dialog.title = f"Edit {device_type.name} ID"
            input_widget = self._find_widget("IDC_ID_INPUT")
            if input_widget:
                input_widget.text = initial_value

    def get_result(self):
        """結果を取得し、クリアする"""
        result = self.result
        self.result = None
        return result

    def update(self):
        """フレームごとの更新処理"""
        if not self.active_dialog:
            return

        ok_button = self._find_widget("IDOK")
        if ok_button and ok_button.is_pressed:
            self._handle_ok()

        cancel_button = self._find_widget("IDCANCEL")
        if cancel_button and cancel_button.is_pressed:
            self._handle_cancel()

    def _handle_ok(self):
        """OKボタンが押されたときの処理"""
        input_widget = self._find_widget("IDC_ID_INPUT")
        if input_widget:
            new_id = input_widget.text.upper()
            if self._is_valid_address(new_id):
                self.result = (True, new_id)
                self.dialog_manager.close()
            else:
                # TODO: Add visual feedback for invalid input
                print(f"Invalid address format for {self.device_type.name}: {new_id}")
                self.result = (False, None)

    def _handle_cancel(self):
        """Cancelボタンが押されたときの処理"""
        self.result = (False, None)
        self.dialog_manager.close()

    def _is_valid_address(self, address: str) -> bool:
        """PLC標準仕様に基づきアドレスを検証する"""
        if self.device_type in [DeviceType.CONTACT_A, DeviceType.CONTACT_B, DeviceType.COIL_STD, DeviceType.COIL_REV]:
            if not re.fullmatch(r"[XYM]\d{1,4}", address):
                return False
            if address.startswith('X') or address.startswith('Y'):
                try:
                    int(address[1:], 8)
                    return True
                except ValueError:
                    return False
            return True # M address

        elif self.device_type == DeviceType.TIMER_TON:
            if not re.fullmatch(r"T\d{1,3}", address):
                return False
            return TimerConfig.PRESET_MIN <= int(address[1:]) <= TimerConfig.PRESET_MAX

        elif self.device_type == DeviceType.COUNTER_CTU:
            if not re.fullmatch(r"C\d{1,3}", address):
                return False
            return CounterConfig.PRESET_MIN <= int(address[1:]) <= CounterConfig.PRESET_MAX

        elif self.device_type == DeviceType.RST:
            if not re.fullmatch(r"[TC]\d{1,3}", address):
                return False
            num = int(address[1:])
            if address.startswith('T'):
                return TimerConfig.PRESET_MIN <= num <= TimerConfig.PRESET_MAX
            else: # C
                return CounterConfig.PRESET_MIN <= num <= CounterConfig.PRESET_MAX

        elif self.device_type == DeviceType.ZRST:
            return self._is_valid_zrst_address(address)

        return False

    def _is_valid_zrst_address(self, address: str) -> bool:
        """ZRST命令の複雑なアドレス指定を検証する"""
        parts = address.split(',')
        if not parts:
            return False

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Range check (e.g., T0-T10)
            if '-' in part:
                match = re.fullmatch(r"([TC])(\d{1,3})-(\d{1,3})", part)
                if not match:
                    return False
                prefix, start_str, end_str = match.groups()
                start, end = int(start_str), int(end_str)
                if start >= end:
                    return False
                # Validate range for T/C
                if prefix == 'T':
                    if not (TimerConfig.PRESET_MIN <= start <= TimerConfig.PRESET_MAX and TimerConfig.PRESET_MIN <= end <= TimerConfig.PRESET_MAX):
                        return False
                else: # C
                    if not (CounterConfig.PRESET_MIN <= start <= CounterConfig.PRESET_MAX and CounterConfig.PRESET_MIN <= end <= CounterConfig.PRESET_MAX):
                        return False
            # Single address check (e.g., C20)
            else:
                match = re.fullmatch(r"([TC])(\d{1,3})", part)
                if not match:
                    return False
                prefix, num_str = match.groups()
                num = int(num_str)
                if prefix == 'T':
                    if not (TimerConfig.PRESET_MIN <= num <= TimerConfig.PRESET_MAX):
                        return False
                else: # C
                    if not (CounterConfig.PRESET_MIN <= num <= CounterConfig.PRESET_MAX):
                        return False
        return True

    def _find_widget(self, widget_id: str):
        """ウィジェットIDでウィジェットを検索"""
        if not self.active_dialog:
            return None
        for widget in self.active_dialog.widgets:
            if hasattr(widget, 'id') and widget.id == widget_id:
                return widget
        return None
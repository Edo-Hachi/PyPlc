"""
タイマー・カウンターのプリセット値編集ダイアログのコントローラー
"""
from .dialog_manager import DialogManager
from config import DeviceType, TimerConfig, CounterConfig

class TimerCounterDialogController:
    """タイマー・カウンターのプリセット値編集ダイアログのロジックを管理する"""

    def __init__(self, dialog_manager: DialogManager):
        self.dialog_manager = dialog_manager
        self.active_dialog = None
        self.result = None
        self.device_type = None

    def show_dialog(self, device_type: DeviceType, initial_value: int = 0):
        """ダイアログを表示する"""
        self.result = None
        self.device_type = device_type
        self.dialog_manager.show("IDD_TIMER_COUNTER_EDIT")
        self.active_dialog = self.dialog_manager.active_dialog

        if self.active_dialog:
            self.active_dialog.title = f"Edit {device_type.name} Preset"
            
            input_widget = self._find_widget("IDC_PRESET_INPUT")
            if input_widget:
                input_widget.text = str(initial_value)

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

        ok_button = self._find_widget("IDOK")
        if ok_button and ok_button.is_pressed:
            self._handle_ok()

        cancel_button = self._find_widget("IDCANCEL")
        if cancel_button and cancel_button.is_pressed:
            self._handle_cancel()

    def _handle_ok(self):
        """OKボタンが押されたときの処理"""
        input_widget = self._find_widget("IDC_PRESET_INPUT")
        if input_widget:
            try:
                value = int(input_widget.text)
                if self._is_valid_preset(value):
                    self.result = (True, value)
                    self.dialog_manager.close()
                else:
                    # TODO: Add visual feedback for invalid input
                    print(f"Invalid preset value for {self.device_type.name}: {value}")
                    self.result = (False, None)
            except ValueError:
                print(f"Invalid input: not an integer")
                self.result = (False, None)

    def _handle_cancel(self):
        """Cancelボタンが押されたときの処理"""
        self.result = (False, None)
        self.dialog_manager.close()

    def _is_valid_preset(self, value: int) -> bool:
        """プリセット値が有効な範囲にあるか検証する"""
        if self.device_type == DeviceType.TIMER_TON:
            return TimerConfig.PRESET_MIN <= value <= TimerConfig.PRESET_MAX
        elif self.device_type == DeviceType.COUNTER_CTU:
            return CounterConfig.PRESET_MIN <= value <= CounterConfig.PRESET_MAX
        return False

    def _find_widget(self, widget_id: str):
        """ウィジェットIDでウィジェットを検索"""
        if not self.active_dialog:
            return None
        for widget in self.active_dialog.widgets:
            if hasattr(widget, 'id') and widget.id == widget_id:
                return widget
        return None

"""
デバイスID編集ダイアログのコントローラー
"""
import re
import pyxel
from .dialog_manager import DialogManager
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DeviceType, TimerConfig, CounterConfig

class DeviceIdDialogController:
    """デバイスID編集ダイアログのロジックを管理する"""

    def __init__(self, dialog_manager: DialogManager):
        self.dialog_manager = dialog_manager
        self.active_dialog = None
        self.result = None
        self.device_type = None
        self.last_input_text = ""

    def show_dialog(self, device_type: DeviceType, initial_value: str = ""):
        """ダイアログを表示する"""
        print(f"[DEBUG] DeviceIdDialogController.show_dialog called: type={device_type}, initial={initial_value}")
        self.result = None
        self.device_type = device_type
        self.last_input_text = initial_value
        self.dialog_manager.show("IDD_DEVICE_ID_EDIT")
        self.active_dialog = self.dialog_manager.active_dialog
        print(f"[DEBUG] Dialog manager active_dialog: {self.active_dialog}")

        if self.active_dialog:
            print(f"[DEBUG] Dialog successfully created and assigned")
            self.active_dialog.title = f"Edit {device_type.name} ID"
            
            # デバイスタイプ表示を更新
            type_widget = self._find_widget("IDC_LABEL_TYPE")
            if type_widget:
                type_widget.text = f"Type: {device_type.name}"
            
            # 初期値を設定
            input_widget = self._find_widget("IDC_ID_INPUT")
            if input_widget:
                input_widget.text = initial_value
            
            # エラーメッセージをクリア
            self._clear_error_message()
        else:
            print(f"[DEBUG] ERROR: Failed to create dialog 'IDD_DEVICE_ID_EDIT'")

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
        input_widget = self._find_widget("IDC_ID_INPUT")
        if not input_widget:
            return
        
        current_text = input_widget.text
        if current_text != self.last_input_text:
            self.last_input_text = current_text
            if current_text.strip():  # 空でない場合のみバリデーション
                is_valid, error_message = self._validate_address(current_text.strip().upper())
                if not is_valid:
                    self._show_error_message(error_message)
                else:
                    self._clear_error_message()
            else:
                self._clear_error_message()

    def _show_error_message(self, message: str):
        """エラーメッセージを表示"""
        error_widget = self._find_widget("IDC_ERROR_MESSAGE")
        if error_widget:
            error_widget.text = message
            error_widget.color = pyxel.COLOR_RED  # エラーメッセージを赤色で表示

    def _clear_error_message(self):
        """エラーメッセージをクリア"""
        error_widget = self._find_widget("IDC_ERROR_MESSAGE")
        if error_widget:
            error_widget.text = ""
            error_widget.color = pyxel.COLOR_BLACK  # 色もデフォルトに戻す

    def _handle_ok(self):
        """OKボタンが押されたときの処理"""
        input_widget = self._find_widget("IDC_ID_INPUT")
        if input_widget:
            new_id = input_widget.text.strip().upper()
            is_valid, error_message = self._validate_address(new_id)
            if is_valid:
                self.result = (True, new_id)
                self.dialog_manager.close()
            else:
                self._show_error_message(error_message)
                self.result = (False, None)

    def _handle_cancel(self):
        """Cancelボタンが押されたときの処理"""
        self.result = (False, None)
        self.dialog_manager.close()

    def _validate_address(self, address: str) -> tuple[bool, str]:
        """
        PLC標準仕様に基づきアドレスを検証する（旧システムと同等の詳細バリデーション）
        
        Returns:
            tuple[bool, str]: (バリデーション結果, エラーメッセージ)
        """
        address = address.strip().upper()
        if not address:
            return False, "ID cannot be empty."

        # RST専用バリデーション
        if self.device_type == DeviceType.RST:
            return self._validate_rst_address(address)

        # ZRST専用バリデーション  
        if self.device_type == DeviceType.ZRST:
            return self._validate_zrst_address(address)

        # 標準的なデバイスアドレスのバリデーション
        match = re.match(r'^([XYMLTCD])(\d+)$', address)
        if not match:
            return False, "Format error. Use e.g., X0, M100."

        prefix = match.group(1)
        number = int(match.group(2))

        # デバイスタイプに応じた有効プレフィックスチェック
        valid_prefixes = {
            DeviceType.CONTACT_A: "XYMLTC",
            DeviceType.CONTACT_B: "XYMLTC", 
            DeviceType.COIL_STD: "YM",
            DeviceType.COIL_REV: "YM",
            DeviceType.TIMER_TON: "T",
            DeviceType.COUNTER_CTU: "C",
        }.get(self.device_type)

        if valid_prefixes and prefix not in valid_prefixes:
            return False, f"'{prefix}' is not valid for {self.device_type.name}."

        # X,Y接点の8進数チェック
        if prefix in "XY":
            try:
                # 8進数として解釈できるかチェック
                int(str(number), 8)
                if number > 377:  # 8進数で377が最大
                    return False, f"{prefix} number must be 0-377 (octal)."
            except ValueError:
                return False, f"{prefix} must use octal digits (0-7)."

        # T,Cの範囲チェック
        if prefix == "T" and not (0 <= number <= 255):
            return False, "Timer number must be 0-255."
        if prefix == "C" and not (0 <= number <= 255): 
            return False, "Counter number must be 0-255."

        # M接点の範囲チェック
        if prefix == "M" and not (0 <= number <= 7999):
            return False, "M number must be 0-7999."

        return True, ""

    def _validate_rst_address(self, address: str) -> tuple[bool, str]:
        """RST命令対象アドレスのバリデーション"""
        match = re.match(r'^(T|C)(\d+)$', address)
        if not match:
            return False, "RST target must be T or C (e.g., T5)."
        
        number = int(match.group(2))
        if not (0 <= number <= 255):
            return False, "RST target number must be 0-255."
            
        return True, ""

    def _validate_zrst_address(self, address: str) -> tuple[bool, str]:
        """ZRST命令の複雑なアドレス指定を検証"""
        if not re.match(r'^[TC0-9,\s-]*$', address):
            return False, "Invalid chars for ZRST. Use T,C,0-9,-,,"
        
        parts = address.split(',')
        if not parts:
            return False, "ZRST address cannot be empty."

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # 範囲指定チェック (例: T0-10)
            if '-' in part:
                match = re.match(r'^([TC])(\d+)-(\d+)$', part)
                if not match:
                    return False, f"Invalid range format: {part}"
                prefix, start_str, end_str = match.groups()
                start, end = int(start_str), int(end_str)
                if start >= end:
                    return False, f"Invalid range {part}: start >= end"
                if not (0 <= start <= 255 and 0 <= end <= 255):
                    return False, f"Range {part}: numbers must be 0-255"
            # 単一指定チェック (例: C20)
            else:
                match = re.match(r'^([TC])(\d+)$', part)
                if not match:
                    return False, f"Invalid address format: {part}"
                prefix, num_str = match.groups()
                num = int(num_str)
                if not (0 <= num <= 255):
                    return False, f"Address {part}: number must be 0-255"

        return True, ""

    def _is_valid_address(self, address: str) -> bool:
        """後方互換性のための簡易バリデーション"""
        is_valid, _ = self._validate_address(address)
        return is_valid


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
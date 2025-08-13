"""
データレジスタ設定ダイアログ（JSON定義ベース）
PyPlc Ver3 データレジスタ機能統合モジュール
"""

import os
from typing import Optional, Dict, Any
from DialogManager.core.json_dialog_loader import JSONDialogLoader
from DialogManager.core.base_dialog import BaseDialog
from DialogManager.core.control_factory import ControlFactory

class DataRegisterDialog(BaseDialog):
    """データレジスタ設定ダイアログクラス"""
    
    def __init__(self, address: str = "", value: int = 0):
        """
        データレジスタ設定ダイアログの初期化
        
        Args:
            address: 初期アドレス
            value: 初期値
        """
        self.address = address
        self.value = value
        self.input_address = address
        self.input_value = str(value)
        self.validation_error = ""
        self.is_valid = True
        
        # JSON定義を読み込み
        self.loader = JSONDialogLoader()
        self.definition = self.loader.load_dialog_definition("data_register_settings.json")
        
        if self.definition is None:
            raise ValueError("Failed to load data_register_settings.json")
        
        # BaseDialogを初期化
        super().__init__(
            title=self.definition.get("title", "データレジスタ設定"),
            width=self.definition.get("width", 250),
            height=self.definition.get("height", 180)
        )
        
        # ControlFactoryでコントロールを生成
        self.factory = ControlFactory()
        self._create_controls()
        
        # 初期値をコントロールに設定
        self.set_initial_values(address, value)
        
        # 結果格納用
        self.result: Optional[Dict[str, Any]] = None
        self.confirmed = False
        self.active = False
    
    def set_initial_values(self, address: str = "", value: int = 0):
        """
        初期値を設定する
        
        Args:
            address: データレジスタアドレス
            value: データレジスタ値
        """
        # デフォルト値の設定
        if not address:
            address = "D1"  # デフォルトアドレス
        
        print(f"[DataRegisterDialog] Setting initial values: address='{address}', value={value}")
        if "address_input" in self.controls:
            self.controls["address_input"].set_text(address)
            print(f"[DataRegisterDialog] Address input set to: '{address}'")
        if "value_input" in self.controls:
            self.controls["value_input"].set_text(str(value))
            print(f"[DataRegisterDialog] Value input set to: '{value}'")
    
    def handle_event(self, event_type: str, control_id: str, data: Any = None) -> bool:
        """
        イベント処理
        
        Args:
            event_type: イベントの種類
            control_id: イベントを発生させたコントロールのID
            data: イベントデータ
            
        Returns:
            bool: イベントが処理された場合True
        """
        if event_type == "click":
            if control_id == "ok_button":
                return self._handle_ok_click()
            elif control_id == "cancel_button":
                return self._handle_cancel_click()
        
        elif event_type == "enter":
            if control_id in ["address_input", "value_input"]:
                return self._handle_ok_click()
        
        elif event_type == "validate":
            return self._handle_validation(control_id, data)
        
        return False
    
    def _handle_ok_click(self) -> bool:
        """OKボタンクリック処理"""
        print("[DataRegisterDialog] _handle_ok_click called")
        # バリデーション実行
        if not self._validate_all_inputs():
            print("[DataRegisterDialog] Validation failed")
            return False
        
        # 結果を構築
        address = self.controls["address_input"].get_text().strip().upper()
        value_text = self.controls["value_input"].get_text().strip()
        
        try:
            value = int(value_text) if value_text else 0
        except ValueError:
            self._show_error("値は数値で入力してください")
            return False
        
        # データレジスタアドレスの正規化（D番号）
        if not address.startswith('D'):
            address = f"D{address}"
        
        self.result = {
            "address": address,
            "value": value
        }
        self.confirmed = True
        self.active = False
        self.result_ready = True  # モーダルループ終了フラグ
        print(f"[DataRegisterDialog] OK result: {self.result}")
        return True
    
    def _handle_cancel_click(self) -> bool:
        """キャンセルボタンクリック処理"""
        print("[DataRegisterDialog] _handle_cancel_click called")
        self.result = None
        self.confirmed = False
        self.active = False
        self.result_ready = True  # モーダルループ終了フラグ
        print("[DataRegisterDialog] Cancel result: None")
        return True
    
    def _handle_validation(self, control_id: str, data: Any) -> bool:
        """入力値バリデーション処理"""
        if control_id == "address_input":
            address = data.strip().upper()
            if not address:
                self._show_error("アドレスを入力してください")
                return False
            
            # D番号の形式チェック
            if address.startswith('D'):
                number_part = address[1:]
            else:
                number_part = address
            
            if not number_part.isdigit():
                self._show_error("アドレスはD番号で入力してください（例: D1, D100）")
                return False
            
            number = int(number_part)
            if not (0 <= number <= 255):
                self._show_error("D番号は0-255の範囲で入力してください")
                return False
        
        elif control_id == "value_input":
            try:
                value = int(data) if data else 0
                if not (0 <= value <= 32767):
                    self._show_error("値は0-32767の範囲で入力してください")
                    return False
            except ValueError:
                self._show_error("値は数値で入力してください")
                return False
        
        # バリデーション成功時はエラーメッセージをクリア
        self._hide_error()
        return True
    
    def _validate_all_inputs(self) -> bool:
        """全入力値の総合バリデーション"""
        address = self.controls["address_input"].get_text().strip()
        value_text = self.controls["value_input"].get_text().strip()
        
        print(f"[DataRegisterDialog] Validating address: '{address}', value: '{value_text}'")
        
        # アドレスバリデーション
        if not self._handle_validation("address_input", address):
            print("[DataRegisterDialog] Address validation failed")
            return False
        
        # 値バリデーション
        if not self._handle_validation("value_input", value_text):
            print("[DataRegisterDialog] Value validation failed")
            return False
        
        print("[DataRegisterDialog] All validation passed")
        return True
    
    def _show_error(self, message: str):
        """エラーメッセージを表示"""
        if "error_label" in self.controls:
            self.controls["error_label"].text = message
            self.controls["error_label"].visible = True
    
    def _hide_error(self):
        """エラーメッセージを非表示"""
        if "error_label" in self.controls:
            self.controls["error_label"].text = ""
            self.controls["error_label"].visible = False
    
    def _draw_custom(self) -> None:
        """カスタム描画処理（BaseDialog抽象メソッド実装）"""
        # 基本的なダイアログ描画はBaseDialogで処理されるため、
        # 特別なカスタム描画が必要な場合のみここに実装
        pass
    
    def get_result(self) -> Optional[Dict[str, Any]]:
        """
        ダイアログの結果を取得
        
        Returns:
            Dict[str, Any]: 確定された場合は{"address": str, "value": int}、
                          キャンセルされた場合はNone
        """
        return self.result if self.confirmed else None
    
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
            control_def: コントロール定義辞書
        """
        events = control_def.get("events", [])
        
        if "click" in events:
            control.on("click", lambda c=control: self._on_control_clicked(c))
        
        if "change" in events:
            control.on("change", lambda c=control, old="", new="": self._on_input_changed(c, old, new))
        
        if "enter" in events:
            control.on("enter", lambda c=control: self._on_enter_pressed(c))
    
    def _on_control_clicked(self, control):
        """コントロールクリック処理"""
        print(f"[DataRegisterDialog] Control clicked: {control.id}")
        if control.id == "ok_button":
            print("[DataRegisterDialog] OK button processing...")
            self._handle_ok_click()
        elif control.id == "cancel_button":
            print("[DataRegisterDialog] Cancel button processing...")
            self._handle_cancel_click()
    
    def _on_input_changed(self, control, old_text: str, new_text: str):
        """入力変更処理"""
        # バリデーションを実行
        self._handle_validation(control.id, new_text)
    
    def _on_enter_pressed(self, control):
        """Enterキー処理"""
        if control.id in ["address_input", "value_input"]:
            self._handle_ok_click()
    
    def show(self):
        """ダイアログを表示"""
        self.active = True
        return super().show()
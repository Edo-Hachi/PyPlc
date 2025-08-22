"""
データレジスタダイアログの制御機能

PLC式のデータレジスタ設定ダイアログを提供し、
操作種類（MOV, ADD, SUB, MUL, DIV）とオペランド値の編集機能を実装
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.base_dialog_controller import PyPlcDialogController
from .dialog_manager import DialogManager


class DataRegisterDialogController(PyPlcDialogController):
    """データレジスタダイアログのコントローラークラス"""
    
    def __init__(self, dialog_manager: DialogManager):
        super().__init__(dialog_manager)
        
    def show_data_register_dialog(self, current_device_id="", current_operation="MOV", current_operand=""):
        """データレジスタダイアログを表示"""
        if self._safe_show_dialog("IDD_DATA_REGISTER_EDIT"):
            # 初期化処理
            self._initialize_dialog(current_device_id, current_operation, current_operand)
            self._setup_event_handlers()

    # get_result()は基底クラスから継承
    
    def _initialize_dialog(self, current_device_id, current_operation, current_operand):
        """ダイアログの初期化"""
        if not self.active_dialog:
            return
            
        # デバイスID入力ボックスの初期値設定
        device_id_widget = self._find_widget("IDC_DEVICE_ID_INPUT")
        if device_id_widget:
            device_id_widget.text = str(current_device_id) if current_device_id else ""
            
        # 操作種類ドロップダウンの初期値設定
        operation_widget = self._find_widget("IDC_OPERATION_DROPDOWN")
        if operation_widget:
            # 現在の操作に対応するインデックスを設定
            operations = ["MOV", "ADD", "SUB", "MUL", "DIV"]
            try:
                index = operations.index(current_operation)
                operation_widget.selected_index = index
            except ValueError:
                operation_widget.selected_index = 0  # デフォルトはMOV
                
        # オペランド値入力ボックスの初期値設定
        operand_widget = self._find_widget("IDC_OPERAND_INPUT")
        if operand_widget:
            operand_widget.text = str(current_operand) if current_operand else ""
            
        # エラーメッセージをクリア
        error_widget = self._find_widget("IDC_ERROR_MESSAGE")
        if error_widget:
            error_widget.text = ""
    
    def _find_widget(self, widget_id: str):
        """ウィジェットIDでウィジェットを検索"""
        if not self.active_dialog:
            return None
            
        for widget in self.active_dialog.widgets:
            if hasattr(widget, 'id') and widget.id == widget_id:
                return widget
        return None
    
    def _validate_mitsubishi_data_register_id(self, device_id: str) -> bool:
        """
        三菱PLC標準データレジスタIDのバリデーション
        
        Args:
            device_id: 検証するデバイスID文字列
            
        Returns:
            bool: 有効なフォーマットの場合True
            
        仕様:
            - フォーマット: D + 数値 (例: D0, D100, D12000)
            - 範囲: D0 から D12000
            - 大文字小文字: D は大文字のみ
        """
        # 空文字列は無効
        if not device_id:
            return False
            
        # 最低2文字 (D + 数値) 必要
        if len(device_id) < 2:
            return False
            
        # 最初の文字が 'D' でない場合は無効
        if device_id[0] != 'D':
            return False
            
        # 'D' の後の部分を取得
        number_part = device_id[1:]
        
        # 数値部分が空の場合は無効
        if not number_part:
            return False
            
        # 数値部分が数字のみで構成されているかチェック
        if not number_part.isdigit():
            return False
            
        # 数値に変換して範囲チェック (0 <= number <= 12000)
        try:
            number = int(number_part)
            if 0 <= number <= 12000:
                return True
            else:
                return False
        except ValueError:
            return False
    
    def _setup_event_handlers(self):
        """イベントハンドラーを設定"""
        # ドロップダウンの選択変更イベント
        operation_widget = self._find_widget("IDC_OPERATION_DROPDOWN")
        if operation_widget:
            print(f"[DEBUG] Setting up operation dropdown event handler for widget: {operation_widget}")
            operation_widget.on_selection_changed = self.handle_operation_changed
            print(f"[DEBUG] Operation dropdown event handler set successfully")
        else:
            print(f"[DEBUG] Operation dropdown widget 'IDC_OPERATION_DROPDOWN' not found!")

    def handle_operation_changed(self, selected_index: int, selected_value: str):
        """操作種類ドロップダウンの選択が変更された時の処理"""
        print(f"[DEBUG] Operation changed to: {selected_value} (index: {selected_index})")
        
        # オペランド値入力欄にヒントを表示（任意）
        operand_widget = self._find_widget("IDC_OPERAND_INPUT")
        if operand_widget and not operand_widget.text:
            # 操作に応じたヒント値を設定
            hint_values = {
                "MOV": "100",    # データ転送
                "ADD": "10",     # 加算演算
                "SUB": "5",      # 減算演算
                "MUL": "2",      # 乗算演算
                "DIV": "2"       # 除算演算
            }
            hint = hint_values.get(selected_value, "")
            if hint:
                operand_widget.text = hint
                print(f"[DEBUG] Set hint value: {hint} for operation: {selected_value}")
    
    def handle_ok_button(self):
        """OKボタンが押された時の処理"""
        device_id_widget = self._find_widget("IDC_DEVICE_ID_INPUT")
        operation_widget = self._find_widget("IDC_OPERATION_DROPDOWN")
        operand_widget = self._find_widget("IDC_OPERAND_INPUT")
        error_widget = self._find_widget("IDC_ERROR_MESSAGE")
        
        if not device_id_widget or not operation_widget or not operand_widget:
            return None
            
        # デバイスIDを取得してバリデーション
        device_id = device_id_widget.text.strip()
        
        # バリデーション: デバイスID空値チェック
        if not device_id:
            if error_widget:
                error_widget.text = "Error: Device ID required"
            print("Error: Device ID is required")
            return None
            
        # バリデーション: 三菱PLC標準 D0-D12000 形式チェック
        if not self._validate_mitsubishi_data_register_id(device_id):
            if error_widget:
                error_widget.text = "Error: Use D0-D12000 format (Mitsubishi PLC)"
            print(f"Error: Invalid Device ID format: {device_id}")
            return None
            
        # 選択された操作を取得
        selected_operation = operation_widget.get_selected_value()
        if not selected_operation:
            selected_operation = "MOV"  # デフォルト
            
        # オペランド値を取得してバリデーション
        operand_value = operand_widget.text.strip()
        
        # バリデーション: オペランド値空値チェック
        if not operand_value:
            if error_widget:
                error_widget.text = "Error: Operand value required"
            print("Error: Operand value is required")
            return None
            
        # バリデーション: オペランド値の数値チェック（整数型のみ対応）
        try:
            # 整数として解析を試みる（データレジスタは整数型前提）
            operand_int = int(operand_value)
            
            # DIV演算の場合、ゼロ値チェックを実行
            if selected_operation == 'DIV' and operand_int == 0:
                if error_widget:
                    error_widget.text = "Error: Division by zero not allowed"
                print(f"Error: DIV operation with zero operand not allowed: {operand_value}")
                return None
                
        except ValueError:
            if error_widget:
                error_widget.text = "Error: Enter integer value only"
            print(f"Error: Invalid integer format: {operand_value}")
            return None
        
        # バリデーション成功
        if error_widget:
            error_widget.text = ""
            
        result = {
            'device_id': device_id,
            'operation': selected_operation,
            'operand': operand_value
        }
        
        print(f"Data register configured: {result}")
        return result
    
    def handle_cancel_button(self):
        """Cancelボタンが押された時の処理"""
        print("Data register dialog cancelled")
        self.result = None
        self.dialog_manager.close()
        return None
    
    def update(self):
        """フレームごとの更新処理"""
        # マネージャーと自身のアクティブダイアログが一致しない場合、自身を非アクティブ化
        if self.active_dialog and self.active_dialog != self.dialog_manager.active_dialog:
            self.active_dialog = None

        if not self.active_dialog:
            return
            
        # ボタンクリックのチェック
        self._check_button_clicks()
    
    def _check_button_clicks(self):
        """ボタンクリックをチェックして対応する処理を実行"""
        if not self.active_dialog:
            return
            
        # 各ボタンのクリック状態をチェック
        for widget in self.active_dialog.widgets:
            if hasattr(widget, 'id') and hasattr(widget, 'is_pressed') and widget.is_pressed:
                if widget.id == "IDOK":
                    result = self.handle_ok_button()
                    if result:
                        print(f"Data register settings: {result}")
                        self.result = result
                        self.dialog_manager.close()
                elif widget.id == "IDCANCEL":
                    self.handle_cancel_button()

    # is_active()は基底クラスから継承（Stale参照検出機能付き）
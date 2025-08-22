"""
Compare Device Dialog Controller
比較デバイス設定ダイアログの制御機能

PLC式の比較接点設定ダイアログを提供し、
左辺値、演算子、右辺値の編集機能を実装（MVP版）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.base_dialog_controller import PyPlcDialogController
from .dialog_manager import DialogManager


class CompareDialogController(PyPlcDialogController):
    """比較デバイスダイアログのコントローラークラス"""
    
    def __init__(self, dialog_manager: DialogManager):
        super().__init__(dialog_manager)
        
    def show_compare_dialog(self, current_left="", current_operator="=", current_right=""):
        """比較デバイスダイアログを表示"""
        if self._safe_show_dialog("IDD_COMPARE_DEVICE_EDIT"):
            # 現在の値をダイアログに設定
            left_widget = self._find_widget("IDC_LEFT_VALUE_INPUT")
            if left_widget:
                left_widget.text = current_left
            
            right_widget = self._find_widget("IDC_RIGHT_VALUE_INPUT")
            if right_widget:
                right_widget.text = current_right
            
            # 演算子の選択インデックスを設定
            operator_widget = self._find_widget("IDC_OPERATOR_DROPDOWN")
            if operator_widget:
                operator_map = {"=": 0, "<": 1, ">": 2}
                selected_index = operator_map.get(current_operator, 0)
                operator_widget.selected_index = selected_index
            
            # プレビューを更新
            self._update_preview()

    def _validate_compare_inputs(self, left: str, operator: str, right: str) -> bool:
        """比較入力値のバリデーション（MVP版）"""
        
        # 左辺値バリデーション
        if not self._validate_device_name(left):
            return False
            
        # 演算子バリデーション（MVP: =, <, > のみ）
        mvp_operators = ["=", "<", ">"]
        if operator not in mvp_operators:
            return False
            
        # 右辺値バリデーション
        if not self._validate_right_value(right):
            return False
        
        return True
    
    def _validate_device_name(self, device_name: str) -> bool:
        """デバイス名のバリデーション"""
        if not device_name:
            return False
            
        # デバイス名の基本パターンチェック
        # D0-D7999, T000-T255, C000-C255
        device_name = device_name.upper()
        
        if device_name.startswith('D'):
            # データレジスタ: D0-D7999
            try:
                num = int(device_name[1:])
                return 0 <= num <= 7999
            except ValueError:
                return False
                
        elif device_name.startswith('T'):
            # タイマー: T000-T255
            try:
                num = int(device_name[1:])
                return 0 <= num <= 255
            except ValueError:
                return False
                
        elif device_name.startswith('C'):
            # カウンター: C000-C255
            try:
                num = int(device_name[1:])
                return 0 <= num <= 255
            except ValueError:
                return False
                
        return False
    
    def _validate_right_value(self, right_value: str) -> bool:
        """右辺値のバリデーション"""
        if not right_value:
            return False
            
        # 定数値チェック
        try:
            value = int(right_value)
            return -32768 <= value <= 32767
        except ValueError:
            # デバイス名として再チェック
            return self._validate_device_name(right_value)
    
    # get_result()は基底クラスから継承
    
    def update(self):
        """フレームごとの更新処理"""
        # マネージャーと自身のアクティブダイアログが一致しない場合、自身を非アクティブ化
        if self.active_dialog and self.active_dialog != self.dialog_manager.active_dialog:
            self.active_dialog = None

        if not self.active_dialog:
            return

        # プレビューの更新（入力が変更された場合）
        self._update_preview()

        # ボタンイベント処理
        ok_button = self._find_widget("IDOK")
        if ok_button and ok_button.is_pressed:
            self._handle_ok()

        cancel_button = self._find_widget("IDCANCEL")
        if cancel_button and cancel_button.is_pressed:
            self._handle_cancel()

    def _handle_ok(self):
        """OKボタンが押された時の処理"""
        try:
            left_widget = self._find_widget("IDC_LEFT_VALUE_INPUT")
            right_widget = self._find_widget("IDC_RIGHT_VALUE_INPUT")
            operator_widget = self._find_widget("IDC_OPERATOR_DROPDOWN")
            
            left_value = left_widget.text if left_widget else ""
            right_value = right_widget.text if right_widget else ""
            operator_index = operator_widget.selected_index if operator_widget else 0
            
            operator_list = ["=", "<", ">"]
            operator = operator_list[operator_index] if 0 <= operator_index < len(operator_list) else "="
            
            # バリデーション
            if self._validate_compare_inputs(left_value, operator, right_value):
                self.result = {
                    'compare_left': left_value,
                    'compare_operator': operator,
                    'compare_right': right_value
                }
                # ダイアログを閉じる
                self.dialog_manager.close()
                self.active_dialog = None
            # バリデーションエラーの場合はダイアログを閉じない
        except Exception:
            pass

    def _handle_cancel(self):
        """キャンセルボタンが押された時の処理"""
        self.result = None
        self.dialog_manager.close()
        self.active_dialog = None
    
    # is_active()は基底クラスから継承（Stale参照検出機能付き）
    
    # _find_widget()は基底クラスから継承

    def _update_preview(self):
        """プレビューテキストを更新"""
        if not self.active_dialog:
            return
        
        try:
            left_widget = self._find_widget("IDC_LEFT_VALUE_INPUT")
            right_widget = self._find_widget("IDC_RIGHT_VALUE_INPUT")
            operator_widget = self._find_widget("IDC_OPERATOR_DROPDOWN")
            
            left_value = left_widget.text if left_widget else ""
            right_value = right_widget.text if right_widget else ""
            operator_index = operator_widget.selected_index if operator_widget else 0
            
            operator_list = ["=", "<", ">"]
            operator = operator_list[operator_index] if 0 <= operator_index < len(operator_list) else "="
            
            # プレビューテキスト生成
            preview_text = f"{left_value or 'D0'} {operator} {right_value or '10'}"
            
            preview_widget = self._find_widget("IDC_PREVIEW_TEXT")
            if preview_widget:
                preview_widget.text = preview_text
            
            # エラーメッセージのクリア
            error_widget = self._find_widget("IDC_ERROR_MESSAGE")
            if error_widget:
                error_widget.text = ""
            
        except Exception:
            pass
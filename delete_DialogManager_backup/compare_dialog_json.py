"""
比較命令設定ダイアログ（JSON定義ベース）
PyPlc Ver3 比較命令機能統合モジュール
"""

import os
import re
from typing import Optional, Dict, Any
from .json_dialog_loader import JSONDialogLoader
from .base_dialog import BaseDialog

class CompareDialog(BaseDialog):
    """比較命令設定ダイアログクラス"""
    
    def __init__(self, x: int = 50, y: int = 50):
        """
        比較命令設定ダイアログの初期化
        
        Args:
            x: ダイアログのX座標
            y: ダイアログのY座標
        """
        # JSON定義ファイルのパス
        definition_path = os.path.join(
            os.path.dirname(__file__), 
            "definitions", 
            "compare_settings.json"
        )
        
        # JSONからダイアログ定義を読み込み
        loader = JSONDialogLoader()
        dialog_definition = loader.load_definition(definition_path)
        
        # 基底クラスを初期化
        super().__init__(
            title=dialog_definition.get("title", "比較命令設定"),
            width=dialog_definition.get("width", 280),
            height=dialog_definition.get("height", 200)
        )
        
        # ダイアログ位置を調整
        self.x = x
        self.y = y
        
        # JSON定義からコントロールを構築
        self._build_controls_from_definition(dialog_definition)
        
        # 結果格納用
        self.result: Optional[str] = None
        self.confirmed = False
    
    def set_initial_condition(self, condition: str = ""):
        """
        初期条件を設定する
        
        Args:
            condition: 比較条件式
        """
        if "condition_input" in self.controls:
            self.controls["condition_input"].set_text(condition)
    
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
            if control_id == "condition_input":
                return self._handle_ok_click()
        
        elif event_type == "validate":
            return self._handle_validation(control_id, data)
        
        return False
    
    def _handle_ok_click(self) -> bool:
        """OKボタンクリック処理"""
        # バリデーション実行
        condition = self.controls["condition_input"].get_text().strip()
        if not self._validate_compare_expression(condition):
            return False
        
        # 結果を設定
        self.result = condition
        self.confirmed = True
        self.active = False
        return True
    
    def _handle_cancel_click(self) -> bool:
        """キャンセルボタンクリック処理"""
        self.result = None
        self.confirmed = False
        self.active = False
        return True
    
    def _handle_validation(self, control_id: str, data: Any) -> bool:
        """入力値バリデーション処理"""
        if control_id == "condition_input":
            return self._validate_compare_expression(data)
        return True
    
    def _validate_compare_expression(self, expression: str) -> bool:
        """
        比較式のバリデーション
        
        Args:
            expression: 比較式文字列
            
        Returns:
            bool: 有効な比較式の場合True
        """
        if not expression.strip():
            self._show_error("比較条件を入力してください")
            return False
        
        # サポートする演算子
        operators = ['>=', '<=', '<>', '=', '>', '<']
        
        # 演算子が含まれているかチェック
        has_operator = False
        for op in operators:
            if op in expression:
                has_operator = True
                parts = expression.split(op, 1)
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()
                    
                    # 左辺と右辺のバリデーション
                    if not self._validate_operand(left):
                        self._show_error(f"左辺が無効です: {left}")
                        return False
                    
                    if not self._validate_operand(right):
                        self._show_error(f"右辺が無効です: {right}")
                        return False
                    
                    self._hide_error()
                    return True
                break
        
        if not has_operator:
            self._show_error("演算子が必要です (=, <>, >, <, >=, <=)")
            return False
        
        self._show_error("比較式の形式が正しくありません")
        return False
    
    def _validate_operand(self, operand: str) -> bool:
        """
        オペランド（左辺・右辺）のバリデーション
        
        Args:
            operand: オペランド文字列
            
        Returns:
            bool: 有効なオペランドの場合True
        """
        operand = operand.strip().upper()
        
        # データレジスタ（D番号）の場合
        if operand.startswith('D'):
            number_part = operand[1:]
            if number_part.isdigit():
                number = int(number_part)
                return 0 <= number <= 255
            return False
        
        # 定数値の場合
        try:
            value = int(operand)
            return 0 <= value <= 32767  # PLC標準範囲
        except ValueError:
            return False
    
    def _show_error(self, message: str):
        """エラーメッセージを表示"""
        if "error_label" in self.controls:
            self.controls["error_label"].set_text(message)
            self.controls["error_label"].visible = True
    
    def _hide_error(self):
        """エラーメッセージを非表示"""
        if "error_label" in self.controls:
            self.controls["error_label"].set_text("")
            self.controls["error_label"].visible = False
    
    def _draw_custom(self) -> None:
        """カスタム描画処理（BaseDialog抽象メソッド実装）"""
        # 基本的なダイアログ描画はBaseDialogで処理されるため、
        # 特別なカスタム描画が必要な場合のみここに実装
        pass
    
    def get_result(self) -> Optional[str]:
        """
        ダイアログの結果を取得
        
        Returns:
            str: 確定された場合は比較条件式、キャンセルされた場合はNone
        """
        return self.result if self.confirmed else None
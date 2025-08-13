"""
Data Register Dialog - 既存パターン準拠版
PyPlc Ver3 DialogManager - シンプル関数ベースAPI

既存のshow_device_id_dialog等と同じパターンで実装
独自イベントループを使わず、Pyxelメインループと統合
"""

import pyxel
import logging
from typing import Dict, Any, Optional, Tuple
from DialogManager.core.json_dialog_loader import JSONDialogLoader
from DialogManager.core.control_factory import ControlFactory
from config import DataOperationConfig, DeviceAddressRanges

logger = logging.getLogger(__name__)


class SimpleDataRegisterDialog:
    """シンプルなデータレジスタダイアログ（関数ベースAPI用）"""
    
    def __init__(self, address: str, operation: str, operand: int, execution: bool):
        """
        初期化
        
        Args:
            address: 現在のアドレス
            operation: 演算種別
            operand: オペランド値
            execution: 実行許可状態
        """
        self.address = address
        self.operation_type = operation
        self.operand_value = operand
        self.execution_enabled = execution
        
        # ダイアログ状態
        self.is_active = False
        self.result = None
        
        # JSON定義読み込み
        self._load_dialog_definition()
        self._initialize_controls()
    
    def _load_dialog_definition(self) -> None:
        """JSON定義読み込み"""
        try:
            loader = JSONDialogLoader()
            self.dialog_definition = loader.load_dialog_definition('data_register_settings.json')
            
            if not self.dialog_definition:
                raise RuntimeError("Failed to load data_register_settings.json")
            
            # ダイアログプロパティ設定
            self.title = self.dialog_definition.get('title', 'Data Register')
            self.width = self.dialog_definition.get('width', 350)
            self.height = self.dialog_definition.get('height', 280)
            
            # 画面中央に配置
            self.x = (384 - self.width) // 2
            self.y = (384 - self.height) // 2
            
        except Exception as e:
            logger.error(f"Failed to load dialog definition: {e}")
            raise
    
    def _initialize_controls(self) -> None:
        """コントロール初期化"""
        try:
            factory = ControlFactory()
            self.controls = {}
            
            for control_def in self.dialog_definition.get('controls', []):
                control = factory.create_control(control_def)
                if control:
                    self.controls[control.id] = control
                    # 初期値設定
                    self._set_control_initial_value(control, control_def)
                    
        except Exception as e:
            logger.error(f"Control initialization failed: {e}")
            raise
    
    def _set_control_initial_value(self, control, control_def: Dict) -> None:
        """コントロール初期値設定"""
        control_id = control_def.get('id', '')
        
        try:
            if control_id == 'address_input':
                control.value = self.address
            elif control_id == 'operation_dropdown':
                if hasattr(control, 'set_selected_value'):
                    control.set_selected_value(self.operation_type)
            elif control_id == 'operand_input':
                control.value = str(self.operand_value)
            elif control_id == 'execution_button':
                control.text = "ENABLED" if self.execution_enabled else "DISABLED"
                control.bg_color = 11 if self.execution_enabled else 2
        except Exception as e:
            logger.warning(f"Failed to set initial value for {control_id}: {e}")
    
    def update(self) -> None:
        """更新処理（メインループから呼ばれる）"""
        if not self.is_active:
            return
            
        # 入力処理
        mouse_x = pyxel.mouse_x
        mouse_y = pyxel.mouse_y
        mouse_clicked = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
        
        # ESCキーで終了
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.is_active = False
            self.result = {'success': False}
            return
        
        # 各コントロールの入力処理
        for control in self.controls.values():
            if hasattr(control, 'handle_input'):
                try:
                    # 相対座標で入力処理
                    rel_x = mouse_x - self.x
                    rel_y = mouse_y - self.y
                    control.handle_input(rel_x, rel_y, mouse_clicked)
                except Exception as e:
                    logger.warning(f"Control input error {control.id}: {e}")
        
        # ボタンクリック処理
        self._handle_button_clicks(mouse_x, mouse_y, mouse_clicked)
    
    def _handle_button_clicks(self, mouse_x: int, mouse_y: int, mouse_clicked: bool) -> None:
        """ボタンクリック処理"""
        if not mouse_clicked:
            return
        
        # OKボタン
        ok_button = self.controls.get('ok_button')
        if ok_button and ok_button.point_in_control(mouse_x, mouse_y, self.x, self.y):
            self._handle_ok_button()
            return
        
        # Cancelボタン
        cancel_button = self.controls.get('cancel_button')
        if cancel_button and cancel_button.point_in_control(mouse_x, mouse_y, self.x, self.y):
            self._handle_cancel_button()
            return
        
        # Execution toggleボタン
        exec_button = self.controls.get('execution_button')
        if exec_button and exec_button.point_in_control(mouse_x, mouse_y, self.x, self.y):
            self._handle_execution_toggle()
    
    def _handle_ok_button(self) -> None:
        """OKボタン処理"""
        try:
            # 値収集
            address = self.controls.get('address_input', {}).value or self.address
            operation = self._get_selected_operation()
            operand = self._get_operand_value()
            execution = self.execution_enabled
            
            # バリデーション
            errors = self._validate_inputs(address, operand)
            if errors:
                self._show_validation_errors(errors)
                return
            
            # 結果設定
            self.result = {
                'success': True,
                'address': address,
                'operation_type': operation,
                'operand_value': operand,
                'execution_enabled': execution
            }
            
            self.is_active = False
            
        except Exception as e:
            logger.error(f"OK button error: {e}")
    
    def _handle_cancel_button(self) -> None:
        """Cancelボタン処理"""
        self.result = {'success': False}
        self.is_active = False
    
    def _handle_execution_toggle(self) -> None:
        """実行許可トグル処理"""
        try:
            exec_button = self.controls.get('execution_button')
            if exec_button:
                self.execution_enabled = not self.execution_enabled
                exec_button.text = "ENABLED" if self.execution_enabled else "DISABLED"
                exec_button.bg_color = 11 if self.execution_enabled else 2
        except Exception as e:
            logger.warning(f"Execution toggle error: {e}")
    
    def _get_selected_operation(self) -> str:
        """選択された演算種別取得"""
        try:
            dropdown = self.controls.get('operation_dropdown')
            if dropdown and hasattr(dropdown, 'get_selected_value'):
                return dropdown.get_selected_value()
            return self.operation_type
        except Exception:
            return 'MOV'
    
    def _get_operand_value(self) -> int:
        """オペランド値取得"""
        try:
            operand_input = self.controls.get('operand_input')
            if operand_input and operand_input.value:
                return int(operand_input.value)
            return self.operand_value
        except ValueError:
            return 0
    
    def _validate_inputs(self, address: str, operand: int) -> list:
        """入力バリデーション"""
        errors = []
        
        # アドレス検証
        if not address or not address.startswith('D'):
            errors.append("Address must start with 'D'")
        else:
            try:
                addr_num = int(address[1:])
                if not DeviceAddressRanges.validate_address('D', addr_num):
                    errors.append(f"Address out of range: {address}")
            except ValueError:
                errors.append(f"Invalid address format: {address}")
        
        # オペランド検証
        if not (-32768 <= operand <= 32767):
            errors.append(f"Operand out of range: {operand}")
        
        return errors
    
    def _show_validation_errors(self, errors: list) -> None:
        """バリデーションエラー表示"""
        try:
            error_label = self.controls.get('error_label')
            if error_label:
                error_label.text = "; ".join(errors[:2])
                error_label.visible = True
                error_label.color = 8
        except Exception as e:
            logger.error(f"Error display error: {e}")
    
    def draw(self) -> None:
        """描画処理"""
        if not self.is_active:
            return
        
        try:
            # 背景暗転
            for y in range(0, 384, 2):
                pyxel.line(0, y, 384, y, pyxel.COLOR_NAVY)
            
            # ダイアログ背景
            pyxel.rect(self.x, self.y, self.width, self.height, pyxel.COLOR_BLACK)
            pyxel.rectb(self.x, self.y, self.width, self.height, pyxel.COLOR_WHITE)
            
            # タイトル
            pyxel.text(self.x + 10, self.y + 5, self.title, pyxel.COLOR_WHITE)
            
            # コントロール描画
            for control in self.controls.values():
                if hasattr(control, 'draw') and control.visible:
                    try:
                        control.draw(self.x, self.y)
                    except Exception as e:
                        logger.warning(f"Control draw error {control.id}: {e}")
        
        except Exception as e:
            logger.error(f"Draw error: {e}")


# グローバルダイアログインスタンス（既存パターン準拠）
_current_dialog: Optional[SimpleDataRegisterDialog] = None


def show_data_register_dialog(address: str, operation: str, operand: int, execution: bool) -> Tuple[bool, Dict[str, Any]]:
    """
    データレジスタダイアログを表示する関数（修正版）
    
    既存のshow_device_id_dialogと同じ即座実行パターンに修正
    Pyxelメインループとのコンフリクトを回避
    
    Args:
        address: 現在のアドレス
        operation: 演算種別
        operand: オペランド値
        execution: 実行許可状態
        
    Returns:
        (success: bool, result: Dict)
    """
    # NOTE: この関数は現在は使用されない
    # DialogManagerから直接SimpleDataRegisterDialogを管理する方式に変更
    logger.warning("show_data_register_dialog called - this function is deprecated")
    return False, {}
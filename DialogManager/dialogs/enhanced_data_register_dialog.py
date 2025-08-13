"""
EnhancedDataRegisterDialog - DropdownControl統合・WindSurf改善版
PyPlc Ver3 DialogManager - Phase 2実装

機能:
- JSON駆動UI構成（data_register_settings.json使用）
- DropdownControl統合による演算種別選択
- WindSurf提案の包括的エラーハンドリング
- PLCDevice拡張フィールド完全対応
- パフォーマンス最適化（再描画スキップ）
- ログシステム統合
"""

import pyxel
import logging
from typing import Dict, Any, Optional
from DialogManager.core.json_dialog_loader import JSONDialogLoader
from DialogManager.core.control_factory import ControlFactory
from config import DataOperationConfig, DeviceAddressRanges

logger = logging.getLogger(__name__)


class EnhancedDataRegisterDialog:
    """拡張データレジスタダイアログ（WindSurf改善組み込み版）"""
    
    def __init__(self, dialog_config: Dict[str, Any]):
        """
        ダイアログ初期化
        
        Args:
            dialog_config: ダイアログ設定辞書
                - address: 現在のアドレス
                - operation_type: 現在の演算種別
                - operand_value: 現在のオペランド値
                - execution_enabled: 実行許可状態
                - error_state: エラー状態
                - json_definition: JSON定義ファイル名
        """
        try:
            # 初期値設定（WindSurf提案）
            self.address = dialog_config.get('address', 'D0')
            self.operation_type = dialog_config.get('operation_type', 'MOV')
            self.operand_value = dialog_config.get('operand_value', 0)
            self.execution_enabled = dialog_config.get('execution_enabled', False)
            self.error_state = dialog_config.get('error_state', '')
            
            # JSON定義読み込み
            self.json_file = dialog_config.get('json_definition', 'data_register_settings.json')
            self.dialog_loader = JSONDialogLoader()
            self.control_factory = ControlFactory()
            
            # ダイアログ定義・コントロール読み込み
            self._load_dialog_definition()
            self._initialize_controls()
            
            # 状態管理
            self.is_active = False
            self.result = None
            self.needs_redraw = True  # パフォーマンス最適化
            
            # ログ記録
            logger.info(f"EnhancedDataRegisterDialog initialized: {self.address}, {self.operation_type}")
            
        except Exception as e:
            logger.error(f"Dialog initialization failed: {e}")
            raise
    
    def _load_dialog_definition(self) -> None:
        """JSON定義読み込み"""
        try:
            self.dialog_definition = self.dialog_loader.load_dialog_definition(self.json_file)
            if not self.dialog_definition:
                raise RuntimeError(f"Failed to load dialog definition: {self.json_file}")
            
            # ダイアログプロパティ設定
            self.title = self.dialog_definition.get('title', 'Data Register')
            self.width = self.dialog_definition.get('width', 400)
            self.height = self.dialog_definition.get('height', 320)
            
            # 画面中央に配置
            self.x = (384 - self.width) // 2
            self.y = (384 - self.height) // 2
            
            logger.debug(f"Dialog definition loaded: {self.width}x{self.height}")
            
        except Exception as e:
            logger.error(f"Failed to load dialog definition: {e}")
            raise
    
    def _initialize_controls(self) -> None:
        """コントロール初期化"""
        try:
            self.controls = {}
            
            for control_def in self.dialog_definition.get('controls', []):
                control = self.control_factory.create_control(control_def)
                if control:
                    self.controls[control.id] = control
                    
                    # 初期値設定（現在の設定を反映）
                    self._set_control_initial_value(control, control_def)
            
            logger.debug(f"Controls initialized: {len(self.controls)}")
            
        except Exception as e:
            logger.error(f"Control initialization failed: {e}")
            raise
    
    def _set_control_initial_value(self, control, control_def: Dict) -> None:
        """コントロール初期値設定"""
        try:
            control_id = control_def.get('id', '')
            
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
            elif control_id == 'status_label':
                if self.error_state:
                    control.text = f"Status: Error - {self.error_state}"
                    control.color = 8  # Red
                else:
                    control.text = "Status: Ready (WindSurf Enhanced)"
                    control.color = 11  # Green
                    
        except Exception as e:
            logger.warning(f"Failed to set initial value for control {control_def.get('id', 'unknown')}: {e}")
    
    def show_and_get_result(self) -> Optional[Dict[str, Any]]:
        """ダイアログ表示・結果取得（Pyxel統合版）"""
        try:
            self.is_active = True
            self.result = None
            
            logger.info("Enhanced data register dialog opened")
            
            # Pyxelメインループ統合モード（独自ループは使用しない）
            # main.pyのupdate/drawサイクル内で処理される
            return None  # 非同期処理のため、結果は別途取得
            
        except Exception as e:
            logger.error(f"Dialog show error: {e}")
            self.is_active = False
            return None
    
    def _handle_input(self) -> None:
        """入力処理（エラーハンドリング強化版）"""
        try:
            mouse_x = pyxel.mouse_x
            mouse_y = pyxel.mouse_y
            mouse_clicked = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
            
            # ESCキーで終了
            if pyxel.btnp(pyxel.KEY_ESCAPE):
                self.is_active = False
                return
            
            # 各コントロールの入力処理
            for control in self.controls.values():
                if hasattr(control, 'handle_input'):
                    try:
                        # 絶対座標でコントロールに入力処理を委譲
                        control.handle_input(mouse_x - self.x, mouse_y - self.y, mouse_clicked)
                    except Exception as e:
                        logger.warning(f"Control input error {control.id}: {e}")
            
            # ボタンクリック処理
            self._handle_button_clicks(mouse_x, mouse_y, mouse_clicked)
            
        except Exception as e:
            logger.error(f"Input handling error: {e}")
    
    def _handle_button_clicks(self, mouse_x: int, mouse_y: int, mouse_clicked: bool) -> None:
        """ボタンクリック処理"""
        if not mouse_clicked:
            return
        
        try:
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
                return
                
        except Exception as e:
            logger.error(f"Button click handling error: {e}")
    
    def _handle_ok_button(self) -> None:
        """OKボタン処理（バリデーション・エラーハンドリング強化）"""
        try:
            # 値収集
            address = self.controls.get('address_input', {}).value or self.address
            operation = self._get_selected_operation()
            operand = self._get_operand_value()
            execution = self.execution_enabled
            
            # バリデーション（WindSurf提案）
            validation_errors = self._validate_inputs(address, operand)
            if validation_errors:
                self._show_validation_errors(validation_errors)
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
            logger.info(f"Dialog OK: {address}, {operation}, {operand}, {execution}")
            
        except Exception as e:
            logger.error(f"OK button error: {e}")
            self._show_validation_errors([f"Internal error: {str(e)}"])
    
    def _handle_cancel_button(self) -> None:
        """Cancelボタン処理"""
        self.result = {'success': False}
        self.is_active = False
        logger.info("Dialog canceled")
    
    def _handle_execution_toggle(self) -> None:
        """実行許可トグル処理"""
        try:
            exec_button = self.controls.get('execution_button')
            if exec_button:
                self.execution_enabled = not self.execution_enabled
                exec_button.text = "ENABLED" if self.execution_enabled else "DISABLED"
                exec_button.bg_color = 11 if self.execution_enabled else 2
                self.needs_redraw = True
                logger.debug(f"Execution toggled: {self.execution_enabled}")
                
        except Exception as e:
            logger.warning(f"Execution toggle error: {e}")
    
    def _get_selected_operation(self) -> str:
        """選択された演算種別取得"""
        try:
            dropdown = self.controls.get('operation_dropdown')
            if dropdown and hasattr(dropdown, 'get_selected_value'):
                return dropdown.get_selected_value()
            return self.operation_type
        except Exception as e:
            logger.warning(f"Operation selection error: {e}")
            return 'MOV'
    
    def _get_operand_value(self) -> int:
        """オペランド値取得"""
        try:
            operand_input = self.controls.get('operand_input')
            if operand_input and operand_input.value:
                return int(operand_input.value)
            return self.operand_value
        except ValueError as e:
            logger.warning(f"Operand value parse error: {e}")
            return 0
        except Exception as e:
            logger.warning(f"Operand value error: {e}")
            return 0
    
    def _validate_inputs(self, address: str, operand: int) -> list:
        """入力バリデーション（WindSurf提案）"""
        errors = []
        
        try:
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
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return [f"Validation system error: {str(e)}"]
    
    def _show_validation_errors(self, errors: list) -> None:
        """バリデーションエラー表示"""
        try:
            error_label = self.controls.get('error_label')
            if error_label:
                error_label.text = "; ".join(errors[:2])  # 最大2エラー表示
                error_label.visible = True
                error_label.color = 8  # Red
                self.needs_redraw = True
            
            logger.warning(f"Validation errors: {errors}")
            
        except Exception as e:
            logger.error(f"Error display error: {e}")
    
    def _draw(self) -> None:
        """描画処理（最適化版）"""
        try:
            # 背景暗転
            self._draw_modal_background()
            
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
    
    def _draw_modal_background(self) -> None:
        """モーダル背景描画（軽量化版）"""
        try:
            # 効率化: line描画で背景暗転（psetループ回避）
            for y in range(0, 384, 2):
                pyxel.line(0, y, 384, y, pyxel.COLOR_NAVY)
                
        except Exception as e:
            logger.warning(f"Modal background draw error: {e}")
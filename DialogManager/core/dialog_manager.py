"""
PyPlc Ver3 - DialogManager統合管理システム v2
統合された、クリーンなDialogManagerの実装

作成日: 2025-08-13
目的: DialogManagerシステムの統合・整理版
"""

from typing import Callable, Optional
from config import DeviceType
from DialogManager.dialogs.data_register_dialog import DataRegisterDialog
from DialogManager.dialogs.device_id_dialog import show_device_id_dialog
# 全ダイアログクラス統合完了


class DialogManager:
    """
    DialogManagerシステム統合管理クラス v2
    
    目的:
    - すべてのダイアログの統合管理
    - JSON駆動による柔軟なUI構成
    - デバイス種別に応じた適切なダイアログ表示
    - 保守性・拡張性の向上
    """
    
    def __init__(self):
        """DialogManager初期化"""
        # DialogManagerは現在状態を持たないためpassのまま
    
    def show_device_edit_dialog(
        self,
        device,
        row: int,
        col: int,
        background_draw_func: Callable[[], None],
        grid_system
    ) -> None:
        """
        デバイス編集ダイアログ統合処理
        
        Args:
            device: 編集対象デバイス  
            row: グリッド行座標
            col: グリッド列座標
            background_draw_func: バックグラウンド描画関数（互換性のため保持）
            grid_system: グリッドシステムインスタンス
        """
        if device.device_type in [DeviceType.TIMER_TON, DeviceType.COUNTER_CTU]:
            # タイマー・カウンターはプリセット値編集
            self._show_timer_counter_dialog(device, row, col, grid_system)
        elif device.device_type == DeviceType.DATA_REGISTER:
            # データレジスタはアドレス・値編集
            self._show_data_register_dialog(device, row, col, grid_system)
        elif device.device_type == DeviceType.COMPARE_DEVICE:
            # Compare命令は条件式編集
            self._show_compare_dialog(device, row, col, grid_system)
        else:
            # その他はデバイスID編集
            self._show_device_id_dialog(device, row, col, grid_system)
    
    def _show_device_id_dialog(self, device, row: int, col: int, grid_system) -> None:
        """デバイスID編集ダイアログ表示"""
        from DialogManager.dialogs.device_id_dialog import show_device_id_dialog
        
        # デバイスID編集ダイアログを表示
        success, new_address = show_device_id_dialog(device.device_type, device.address)
        
        if success and new_address:
            # アドレスを更新
            device.address = new_address
            print(f"[DialogManager] Device address updated: {device.device_type.value} = {new_address}")
    
    def _show_timer_counter_dialog(self, device, row: int, col: int, grid_system) -> None:
        """タイマー・カウンタープリセット値編集ダイアログ表示"""
        from DialogManager.dialogs.timer_counter_dialog import show_timer_counter_preset_dialog
        
        # タイマー・カウンタープリセット値編集ダイアログを表示
        success, new_preset = show_timer_counter_preset_dialog(device.device_type, device.preset_value)
        
        if success and new_preset is not None:
            # プリセット値を更新
            device.preset_value = new_preset
            print(f"[DialogManager] Timer/Counter preset updated: {device.device_type.value} = {new_preset}")
    
    def _show_data_register_dialog(self, device, row: int, col: int, grid_system) -> None:
        """データレジスタ編集ダイアログ表示（WindSurf改善版）"""
        try:
            # 事前バリデーション（WindSurf提案）
            if device.device_type != DeviceType.DATA_REGISTER:
                raise ValueError(f"Invalid device type for data register dialog: {device.device_type}")
            
            if not hasattr(device, 'address'):
                raise ValueError("Device missing required 'address' attribute")
            
            # 現在値を安全に取得（PLCDevice拡張フィールド使用）
            current_address = device.address if device.address else f"D{row}"
            current_operation = getattr(device, 'operation_type', 'MOV')
            current_operand = getattr(device, 'operand_value', 0)  
            current_execution = getattr(device, 'execution_enabled', False)
            current_error = getattr(device, 'error_state', '')
            
            # ログ記録（WindSurf提案）
            print(f"[DialogManager] Opening enhanced data register dialog:")
            print(f"  Address: {current_address}")
            print(f"  Operation: {current_operation}")
            print(f"  Operand: {current_operand}")
            print(f"  Execution: {current_execution}")
            print(f"  Error State: '{current_error}'")
            
            # シンプルダイアログ作成・実行（既存パターン準拠）
            result = self._create_enhanced_data_register_dialog(
                current_address, current_operation, current_operand, current_execution, current_error
            )
            
            if result:
                # WindSurf提案: 包括的エラーハンドリング付きデバイス更新
                self._update_device_with_validation(device, result, row, col)
            else:
                print("[DialogManager] Data register edit canceled or failed")
                
        except ValueError as e:
            print(f"[DialogManager] Data register dialog validation error: {e}")
            self._show_error_message("Validation Error", str(e))
        except Exception as e:
            print(f"[DialogManager] Data register dialog error: {e}")
            self._show_error_message("Dialog Error", "Failed to open data register dialog")
            import traceback
            traceback.print_exc()
    
    def _create_enhanced_data_register_dialog(self, address: str, operation: str, operand: int, 
                                            execution: bool, error_state: str):
        """既存のDataRegisterDialogを使用（最も確実な解決策）"""
        try:
            # 既存の動作確認済みDataRegisterDialogを使用
            from DialogManager.dialogs.data_register_dialog import DataRegisterDialog
            
            print(f"[DialogManager] Using existing DataRegisterDialog for {address}")
            
            # 既存のダイアログで基本値設定を実行（操作種別も渡す）
            dialog = DataRegisterDialog(address, operand, operation)
            dialog.show()
            
            result = dialog.get_result()
            if result:
                # 結果を新形式に変換（操作種別も正しく取得）
                selected_operation = result.get('operation_type', operation)  # ダイアログからの選択値を使用
                return {
                    'success': True,
                    'address': result.get('address', address),
                    'operation_type': selected_operation,  # ダイアログで選択された操作種別
                    'operand_value': result.get('value', operand),  # 'value' → 'operand_value' 変換
                    'execution_enabled': execution  # 維持
                }
            else:
                return {'success': False}
                
        except ImportError:
            print("[DialogManager] DataRegisterDialog not available, using fallback")
            return self._create_fallback_data_register_dialog(address, operand)
        except Exception as e:
            print(f"[DialogManager] Error with DataRegisterDialog: {e}")
            return self._create_fallback_data_register_dialog(address, operand)
    
    def _update_device_with_validation(self, device, result: dict, row: int, col: int) -> None:
        """WindSurf提案: バリデーション付きデバイス更新"""
        try:
            # アドレス更新
            new_address = result.get('address', device.address)
            if new_address != device.address:
                device.address = new_address
                print(f"[DialogManager] Address updated: {new_address}")
            
            # 演算設定更新（PLCDevice拡張フィールド使用）
            new_operation = result.get('operation_type', 'MOV')
            new_operand = result.get('operand_value', 0)
            new_execution = result.get('execution_enabled', False)
            
            # 範囲チェック（WindSurf提案）
            if not (-32768 <= new_operand <= 32767):
                raise ValueError(f"Operand value out of range: {new_operand}")
            
            device.operation_type = new_operation
            device.operand_value = new_operand
            device.execution_enabled = new_execution
            device.error_state = ""  # 正常更新時はエラー状態クリア
            
            print(f"[DialogManager] Data register fully updated:")
            print(f"  Address: {device.address}")
            print(f"  Operation: {device.operation_type}")
            print(f"  Operand: {device.operand_value}")
            print(f"  Execution: {device.execution_enabled}")
            
        except Exception as e:
            print(f"[DialogManager] Device update validation failed: {e}")
            device.error_state = "UPDATE_FAILED"
            raise
    
    def _show_error_message(self, title: str, message: str) -> None:
        """エラーメッセージ表示（WindSurf提案）"""
        print(f"[DialogManager] ERROR - {title}: {message}")
        # 将来的にはエラーダイアログ表示を実装
    
    def _create_fallback_data_register_dialog(self, address: str, value: int):
        """フォールバック用シンプルダイアログ"""
        # 既存のDataRegisterDialogを使用
        try:
            dialog = DataRegisterDialog(address, value)
            return dialog
        except Exception as e:
            print(f"[DialogManager] Fallback dialog creation failed: {e}")
            return None
    
    def _show_compare_dialog(self, device, row: int, col: int, grid_system) -> None:
        """比較命令編集ダイアログ表示"""
        from DialogManager.dialogs.compare_dialog import show_compare_dialog
        
        # 現在の条件式を取得（未設定時はデフォルト値）
        current_condition = getattr(device, 'condition', "")
        
        # 比較命令編集ダイアログを表示
        success, new_condition = show_compare_dialog(current_condition)
        
        if success and new_condition:
            # 条件式を更新
            device.condition = new_condition
            print(f"[DialogManager] Compare condition updated: {new_condition}")
    
    def validate_device_for_id_edit(self, device) -> bool:
        """
        デバイスがID編集対象かどうかを検証
        
        Args:
            device: 検証対象デバイス
            
        Returns:
            bool: ID編集可能な場合True
        """
        # LINK系デバイスはID編集対象外
        link_types = [
            DeviceType.LINK_HORZ,
            DeviceType.LINK_BRANCH,
            DeviceType.LINK_VIRT,
            DeviceType.L_SIDE,
            DeviceType.R_SIDE
        ]
        return device.device_type not in link_types
    
    def generate_default_device_id(self, device_type: DeviceType, row: int, col: int) -> str:
        """
        デバイスタイプに応じたデフォルトIDを生成
        
        Args:
            device_type: デバイスタイプ
            row: グリッド行座標
            col: グリッド列座標
            
        Returns:
            str: デフォルトID
        """
        if device_type == DeviceType.CONTACT_A:
            return f"X{row:03d}"
        elif device_type == DeviceType.CONTACT_B:
            return f"X{row:03d}"
        elif device_type == DeviceType.COIL:
            return f"Y{row:03d}"
        elif device_type == DeviceType.COIL_REV:
            return f"Y{row:03d}"
        elif device_type == DeviceType.TIMER_TON:
            return f"T{row:03d}"
        elif device_type == DeviceType.COUNTER_CTU:
            return f"C{row:03d}"
        elif device_type == DeviceType.DATA_REGISTER:
            return f"D{row}"
        elif device_type == DeviceType.RST:
            return f"T{row:03d}"
        elif device_type == DeviceType.ZRST:
            return f"T{row:03d}-{col:03d}"
        else:
            return f"DEV{row}{col}"
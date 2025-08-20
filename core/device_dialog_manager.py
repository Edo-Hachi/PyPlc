"""
PyPlc Ver3 デバイスダイアログ統合マネージャー

Gemini提案準拠：main.pyからダイアログ振り分けロジックを移譲し、
responsibility separation（責務分離）を実現
"""

from typing import Optional
from config import DeviceType

class DeviceDialogManager:
    """
    デバイス右クリック時のダイアログ表示を統合管理するクラス
    Gemini提案：DialogManagerへのロジック移譲により責務分離を実現
    """
    
    def __init__(self, controllers_dict: dict):
        """
        初期化：既存の各ダイアログコントローラーを受け取る
        
        Args:
            controllers_dict: 既存コントローラーの辞書
            {
                'device_id': DeviceIdDialogController,
                'timer_counter': TimerCounterDialogController,
                'data_register': DataRegisterDialogController, 
                'compare': CompareDialogController
            }
        """
        self.controllers = controllers_dict
    
    def show_for_device(self, device) -> bool:
        """
        Gemini提案統合版：デバイスオブジェクトを受け取り、適切なダイアログを起動
        
        main.pyから分岐ロジックを完全移譲し、責務分離を実現
        新規ダイアログ追加時はこのメソッドのみ修正すれば済む
        
        Args:
            device: PLCDevice インスタンス
            
        Returns:
            bool: ダイアログ表示成功時True、対象外デバイス時False
        """
        if not device:
            return False
        
        # デバイスタイプから文字列値を取得
        device_type_str = device.device_type.value if hasattr(device.device_type, 'value') else str(device.device_type)
        
        # ダイアログ種別判定・表示（Gemini提案準拠の責務統合）
        if device_type_str in ['TIMER_TON', 'COUNTER_CTU']:
            # タイマー・カウンタープリセット値編集ダイアログ
            self.controllers['timer_counter'].show_dialog(
                device.device_type, 
                device.preset_value, 
                device.address
            )
            return True
            
        elif device_type_str in ['CONTACT_A', 'CONTACT_B', 'COIL_STD', 'COIL_REV', 'RST', 'ZRST']:
            # デバイスID編集ダイアログ
            self.controllers['device_id'].show_dialog(
                device.device_type, 
                device.address
            )
            return True
            
        elif device_type_str == 'DATA_REGISTER':
            # データレジスタ操作・オペランド編集ダイアログ
            current_device_id = getattr(device, 'address', '')
            current_operation = getattr(device, 'operation', 'MOV')
            current_preset_value = getattr(device, 'preset_value', 0)
            current_operand = str(current_preset_value) if current_preset_value != 0 else ''
            
            self.controllers['data_register'].show_data_register_dialog(
                current_device_id, 
                current_operation, 
                current_operand
            )
            return True
            
        elif device_type_str == 'COMPARE_DEVICE':
            # 比較条件編集ダイアログ
            current_left = getattr(device, 'compare_left', '')
            current_operator = getattr(device, 'compare_operator', '=')
            current_right = getattr(device, 'compare_right', '')
            
            self.controllers['compare'].show_compare_dialog(
                current_left, 
                current_operator, 
                current_right
            )
            return True
        
        # 対象外デバイス（バスバー等）
        return False
    
    def get_supported_device_types(self) -> list:
        """
        サポート対象デバイスタイプ一覧を取得
        デバッグ・テスト用途
        
        Returns:
            list: サポート対象デバイスタイプの文字列リスト
        """
        return [
            'TIMER_TON', 'COUNTER_CTU',
            'CONTACT_A', 'CONTACT_B', 'COIL_STD', 'COIL_REV', 'RST', 'ZRST',
            'DATA_REGISTER', 'COMPARE_DEVICE'
        ]
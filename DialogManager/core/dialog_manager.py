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
        """データレジスタ編集ダイアログ表示"""
        if device.device_type != DeviceType.DATA_REGISTER:
            return
        
        # 現在のアドレスと値を取得
        current_address = device.address if device.address else f"D{row}"
        current_value = getattr(device, 'data_value', 0)
        
        # データレジスタダイアログを作成・表示
        dialog = DataRegisterDialog(current_address, current_value)
        dialog.show()
        
        # 結果を取得してデバイスに反映
        result = dialog.get_result()
        if result:
            device.address = result["address"]
            device.data_value = result["value"]
            print(f"[DialogManager] Data register updated: {result['address']} = {result['value']}")
        else:
            print("[DialogManager] Data register edit canceled")
    
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
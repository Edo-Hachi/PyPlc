# PyPlc Ver3 - ダイアログシステム統合管理
# 作成日: 2025-08-06
# 目的: main.pyからダイアログ処理を分離し、責任を明確化

from typing import Callable, Optional
from config import DeviceType
from .device_id_dialog import DeviceIDDialog

class DialogManager:
    """
    ダイアログシステム統合管理クラス
    main.pyからダイアログ関連処理を完全分離し、
    保守性・拡張性・可読性を向上させる
    """
    
    def show_device_id_dialog(
        self, 
        device, 
        row: int, 
        col: int, 
        background_draw_func: Callable[[], None],
        grid_system
    ) -> None:
        """
        デバイスID編集ダイアログ統合処理
        EDITモードでの右クリック時に呼び出される
        
        Args:
            device: 編集対象デバイス
            row: グリッド行座標
            col: グリッド列座標
            background_draw_func: バックグラウンド描画関数
            grid_system: グリッドシステムインスタンス
        """
        # LINK系デバイスはID編集対象外
        if not self.validate_device_for_id_edit(device):
            return
            
        # 現在のデバイスIDを取得（未設定の場合はデフォルト値を生成）
        current_id = device.address if device.address else self.generate_default_device_id(device.device_type, row, col)
        
        # ダイアログ作成・表示
        dialog = DeviceIDDialog(device.device_type, current_id)
        
        # モーダルダイアログ表示（バックグラウンド描画関数を渡す）
        result, new_id = dialog.show_modal(background_draw_func)
        
        # OK が押された場合、デバイスIDを更新
        if result:
            grid_system.update_device_address(row, col, new_id)
    
    def generate_default_device_id(self, device_type: DeviceType, row: int, col: int) -> str:
        """
        デバイスタイプに基づくデフォルトID生成
        PLC標準に準拠した適切なデフォルト値を生成
        
        Args:
            device_type: デバイスタイプ
            row: グリッド行座標
            col: グリッド列座標
            
        Returns:
            str: 生成されたデフォルトデバイスID
        """
        if device_type in [DeviceType.CONTACT_A, DeviceType.CONTACT_B]:
            # X接点は8進数系 (001, 010, 100等)
            return f"X{row+1:03o}"  # X001, X002等（8進数）
        elif device_type in [DeviceType.COIL_STD, DeviceType.COIL_REV]:
            # Y出力は8進数系、Mは10進数系のどちらでも（ここではY系を選択）
            return f"Y{row+1:03o}"  # Y001, Y002等（8進数）
        elif device_type == DeviceType.TIMER:
            # タイマーは10進数系 (001, 002, 003等)
            return f"T{row+1:03d}"  # T001, T002等（10進数）
        elif device_type == DeviceType.COUNTER:
            # カウンターは10進数系 (001, 002, 003等)
            return f"C{row+1:03d}"  # C001, C002等（10進数）
        else:
            return ""
    
    def validate_device_for_id_edit(self, device) -> bool:
        """
        ID編集可能デバイス判定
        LINK系デバイスはID編集対象外
        
        Args:
            device: 検証対象デバイス
            
        Returns:
            bool: True=編集可能, False=編集不可
        """
        if not device:
            return False
            
        # LINK系デバイスはID編集対象外
        if device.device_type in [DeviceType.LINK_HORZ, DeviceType.LINK_BRANCH, DeviceType.LINK_VIRT]:
            return False
            
        return True
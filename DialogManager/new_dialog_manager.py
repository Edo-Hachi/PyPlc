# PyPlc Ver3 - 新DialogManager統合管理システム
# 作成日: 2025-08-08
# 目的: 古いdialogs/DialogManagerと同等機能をJSON駆動で実現

from typing import Callable, Optional
from config import DeviceType
from DialogManager.device_id_dialog_json import show_device_id_dialog
from DialogManager.file_load_dialog_json import FileLoadDialogJSON
from DialogManager.timer_counter_dialog_json import show_timer_counter_preset_dialog


class NewDialogManager:
    """
    新DialogManagerシステム統合管理クラス
    
    目的:
    - 古いdialogs/DialogManagerと同等の機能をJSON駆動で実現
    - 段階的移行をサポート
    - 既存のインターフェースとの互換性確保
    """
    
    def __init__(self):
        """NewDialogManager初期化"""
        pass
    
    def show_device_edit_dialog(
        self,
        device,
        row: int,
        col: int,
        background_draw_func: Callable[[], None],
        grid_system
    ) -> None:
        """
        デバイス編集ダイアログ統合処理（新システム版）
        
        Args:
            device: 編集対象デバイス  
            row: グリッド行座標
            col: グリッド列座標
            background_draw_func: バックグラウンド描画関数（互換性のため保持）
            grid_system: グリッドシステムインスタンス
        """
        if device.device_type in [DeviceType.TIMER_TON, DeviceType.COUNTER_CTU]:
            # タイマー・カウンターはプリセット値編集（新TimerCounterDialogJSON使用）
            self.show_timer_counter_preset_dialog_json(device, row, col, grid_system)
        else:
            # その他はデバイスID編集（新DeviceIDDialogJSON使用）
            self.show_device_id_dialog_json(device, row, col, grid_system)
    
    def show_device_id_dialog_json(
        self, 
        device,
        row: int,
        col: int, 
        grid_system
    ) -> None:
        """
        新DeviceIDDialogJSON使用のデバイスID編集処理
        
        Args:
            device: 編集対象デバイス
            row: グリッド行座標
            col: グリッド列座標
            grid_system: グリッドシステムインスタンス
        """
        # LINK系デバイスはID編集対象外
        if not self.validate_device_for_id_edit(device):
            return
            
        # 現在のデバイスIDを取得（未設定の場合はデフォルト値を生成）
        current_id = device.address if device.address else self.generate_default_device_id(device.device_type, row, col)
        
        # 新DeviceIDDialogJSONを使用してダイアログ表示
        success, new_id = show_device_id_dialog(device.device_type, current_id)
        
        # OK が押された場合、デバイスIDを更新
        if success and new_id:
            device.address = new_id
            print(f"[NewDialogManager] Device ID updated: {device.device_type.value} -> {new_id}")
    
    def show_timer_counter_preset_dialog_json(
        self,
        device,
        row: int,
        col: int,
        grid_system
    ) -> None:
        """
        新TimerCounterDialogJSON使用のプリセット値編集処理
        
        Args:
            device: 編集対象デバイス
            row: グリッド行座標
            col: グリッド列座標
            grid_system: グリッドシステムインスタンス
        """
        # タイマー・カウンター以外は対象外
        if device.device_type not in [DeviceType.TIMER_TON, DeviceType.COUNTER_CTU]:
            return
            
        # 新TimerCounterDialogJSONを使用してダイアログ表示
        success, new_preset = show_timer_counter_preset_dialog(device.device_type, device.preset_value)
        
        # OK が押された場合、プリセット値を更新
        if success:
            device.preset_value = new_preset
            print(f"[NewDialogManager] Preset value updated: {device.device_type.value} -> {new_preset}")
        else:
            print("[NewDialogManager] Timer/Counter preset edit canceled")
    
    def validate_device_for_id_edit(self, device) -> bool:
        """
        デバイスがID編集対象かどうかを判定
        
        Args:
            device: チェック対象デバイス
            
        Returns:
            ID編集可能な場合True
        """
        # LINK系・バスバー系デバイスはID編集対象外
        excluded_types = [
            DeviceType.L_SIDE, DeviceType.R_SIDE,
            DeviceType.LINK_HORZ, DeviceType.LINK_VIRT, 
            DeviceType.LINK_BRANCH
        ]
        
        return device.device_type not in excluded_types
    
    def generate_default_device_id(self, device_type: DeviceType, row: int, col: int) -> str:
        """
        デバイス種別と位置に基づくデフォルトID生成
        
        Args:
            device_type: デバイス種別
            row: 行座標
            col: 列座標
            
        Returns:
            デフォルトデバイスID
        """
        # 古いDialogManagerと同等のロジック
        if device_type == DeviceType.CONTACT_A:
            return f"X{col:03d}"  # X000, X001, ...
        elif device_type == DeviceType.CONTACT_B:
            return f"X{col:03d}"  # X000, X001, ...
        elif device_type == DeviceType.COIL:
            return f"Y{col:03d}"  # Y000, Y001, ...
        elif device_type == DeviceType.COIL_REV:
            return f"Y{col:03d}"  # Y000, Y001, ...
        elif device_type == DeviceType.TIMER_TON:
            return f"T{row * 10 + col:03d}"  # T000, T001, ...
        elif device_type == DeviceType.COUNTER_CTU:
            return f"C{row * 10 + col:03d}"  # C000, C001, ...
        else:
            return f"M{row * 10 + col:03d}"  # M000, M001, ...
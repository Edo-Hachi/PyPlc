"""
PyPlc Device Utilities Module

デバイスタイプの判定や分類を行うユーティリティ関数を提供するモジュール。
コード重複を削減し、デバイス関連の処理を一元化する。
"""

from typing import List, Set
from config import DeviceType


class DeviceTypeUtils:
    """デバイスタイプに関するユーティリティクラス"""
    
    # デバイスタイプのグループ定義
    CONTACT_TYPES: Set[DeviceType] = {DeviceType.TYPE_A, DeviceType.TYPE_B}
    
    COIL_TYPES: Set[DeviceType] = {
        DeviceType.COIL, 
        DeviceType.INCOIL, 
        DeviceType.OUTCOIL_REV
    }
    
    LOAD_TYPES: Set[DeviceType] = {
        DeviceType.COIL,
        DeviceType.INCOIL, 
        DeviceType.OUTCOIL_REV,
        DeviceType.TIMER,
        DeviceType.COUNTER
    }
    
    WIRE_TYPES: Set[DeviceType] = {DeviceType.WIRE_H, DeviceType.WIRE_V}
    
    LINK_TYPES: Set[DeviceType] = {DeviceType.LINK_UP, DeviceType.LINK_DOWN}
    
    ELECTRICAL_TYPES: Set[DeviceType] = CONTACT_TYPES | COIL_TYPES | WIRE_TYPES | LINK_TYPES
    
    @classmethod
    def is_contact(cls, device_type: DeviceType) -> bool:
        """接点デバイス（A接点、B接点）かどうかを判定"""
        return device_type in cls.CONTACT_TYPES
    
    @classmethod
    def is_coil(cls, device_type: DeviceType) -> bool:
        """コイルデバイスかどうかを判定"""
        return device_type in cls.COIL_TYPES
    
    @classmethod
    def is_load_device(cls, device_type: DeviceType) -> bool:
        """負荷デバイス（コイル、タイマー、カウンター）かどうかを判定"""
        return device_type in cls.LOAD_TYPES
    
    @classmethod
    def is_wire(cls, device_type: DeviceType) -> bool:
        """配線デバイスかどうかを判定"""
        return device_type in cls.WIRE_TYPES
    
    @classmethod
    def is_link(cls, device_type: DeviceType) -> bool:
        """縦方向結線デバイスかどうかを判定"""
        return device_type in cls.LINK_TYPES
    
    @classmethod
    def is_electrical_device(cls, device_type: DeviceType) -> bool:
        """電気的な処理が必要なデバイスかどうかを判定"""
        return device_type in cls.ELECTRICAL_TYPES
    
    @classmethod
    def can_conduct_power(cls, device_type: DeviceType) -> bool:
        """電力を伝導できるデバイスかどうかを判定"""
        return device_type in (cls.WIRE_TYPES | cls.LINK_TYPES | cls.LOAD_TYPES)
    
    @classmethod
    def requires_address(cls, device_type: DeviceType) -> bool:
        """デバイスアドレスが必要なデバイスかどうかを判定"""
        return device_type in (cls.CONTACT_TYPES | cls.COIL_TYPES | {DeviceType.TIMER, DeviceType.COUNTER})


class DeviceAddressGenerator:
    """デバイスアドレス生成ユーティリティクラス"""
    
    @staticmethod
    def generate_address(device_type: DeviceType, grid_x: int, grid_y: int) -> str:
        """デバイスタイプとグリッド座標からアドレスを生成"""
        if device_type in {DeviceType.TYPE_A, DeviceType.TYPE_B}:
            return f"X{grid_x:03d}"
        elif device_type == DeviceType.COIL:
            return f"Y{grid_x:03d}"
        elif device_type == DeviceType.TIMER:
            return f"T{grid_y:03d}"
        elif device_type == DeviceType.COUNTER:
            return f"C{grid_y:03d}"
        elif device_type in {DeviceType.INCOIL, DeviceType.OUTCOIL_REV}:
            return f"M{grid_x:03d}"
        else:
            return ""
    
    @staticmethod
    def get_address_prefix(device_type: DeviceType) -> str:
        """デバイスタイプからアドレスプレフィックスを取得"""
        if device_type in {DeviceType.TYPE_A, DeviceType.TYPE_B}:
            return "X"
        elif device_type == DeviceType.COIL:
            return "Y"
        elif device_type == DeviceType.TIMER:
            return "T"
        elif device_type == DeviceType.COUNTER:
            return "C"
        elif device_type in {DeviceType.INCOIL, DeviceType.OUTCOIL_REV}:
            return "M"
        else:
            return ""


class DeviceStateUtils:
    """デバイス状態管理ユーティリティクラス"""
    
    @staticmethod
    def reset_device_electrical_state(device):
        """デバイスの電気的状態をリセット"""
        device.active = False
        if hasattr(device, 'coil_energized'):
            device.coil_energized = False
        if hasattr(device, 'wire_energized'):
            device.wire_energized = False
    
    @staticmethod
    def has_electrical_state(device) -> bool:
        """デバイスが電気的状態を持つかどうかを判定"""
        return hasattr(device, 'active') or hasattr(device, 'coil_energized') or hasattr(device, 'wire_energized')
    
    @staticmethod
    def get_device_display_state(device) -> str:
        """デバイスの表示用状態文字列を取得"""
        if hasattr(device, 'active') and device.active:
            return "ON"
        elif hasattr(device, 'coil_energized') and device.coil_energized:
            return "ENERGIZED"
        elif hasattr(device, 'wire_energized') and device.wire_energized:
            return "POWERED"
        else:
            return "OFF"

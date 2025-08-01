"""
PyPlc PLC Logic Module

従来のPLCロジックシステムを管理するモジュール。
- PLCDevice: PLCデバイス（X, Y, M, T, C等）の表現
- DeviceManager: PLCデバイス管理システム
- LogicElement: 論理素子基底クラスと実装群
- LadderLine, LadderProgram: 従来のラダー図管理
"""

import time
from typing import List
from abc import ABC, abstractmethod


class PLCDevice:
    """PLCデバイス（X, Y, M, T, C等）を表現するクラス"""
    def __init__(self, address: str, device_type: str):
        self.address = address
        self.device_type = device_type
        if device_type in ['X', 'Y', 'M']:
            self.value = False
        elif device_type in ['T', 'C']:
            self.value = 0
            self.preset_value = 0
            self.current_value = 0
            self.coil_state = False
        else:
            self.value = 0


class DeviceManager:
    """PLCデバイスを管理するクラス"""
    def __init__(self):
        self.devices = {}
        
    def get_device(self, address: str) -> PLCDevice:
        """デバイスを取得（存在しない場合は作成）"""
        if address not in self.devices:
            device_type = address[0]
            self.devices[address] = PLCDevice(address, device_type)
        return self.devices[address]
    
    def set_device_value(self, address: str, value):
        """デバイス値を設定"""
        device = self.get_device(address)
        device.value = value
    
    def reset_all_devices(self):
        """全デバイスを初期状態にリセット"""
        for device in self.devices.values():
            if device.device_type in ['X', 'Y', 'M']:
                # 接点・コイル系デバイスはFalseに初期化
                device.value = False
            elif device.device_type in ['T', 'C']:
                # タイマー・カウンター系デバイスは0に初期化
                device.value = 0
                device.preset_value = 0
                device.current_value = 0
                device.coil_state = False
            else:
                # その他のデバイスは0に初期化
                device.value = 0


class LogicElement(ABC):
    """論理素子の基底クラス"""
    def __init__(self, device_address: str = None):
        self.inputs: List[LogicElement] = []
        self.device_address = device_address
        self.device = None
        self.last_result = False
        
    def add_input(self, element: 'LogicElement'):
        """入力素子を追加"""
        self.inputs.append(element)
        
    @abstractmethod
    def evaluate(self, device_manager: DeviceManager) -> bool:
        """論理演算を実行"""
        pass


class ContactA(LogicElement):
    """A接点（ノーマルオープン）"""
    def __init__(self, device_address: str):
        super().__init__(device_address)
        
    def evaluate(self, device_manager: DeviceManager) -> bool:
        device = device_manager.get_device(self.device_address)
        self.last_result = bool(device.value)
        return self.last_result


class ContactB(LogicElement):
    """B接点（ノーマルクローズ）"""
    def __init__(self, device_address: str):
        super().__init__(device_address)
        
    def evaluate(self, device_manager: DeviceManager) -> bool:
        device = device_manager.get_device(self.device_address)
        self.last_result = not bool(device.value)
        return self.last_result


class Coil(LogicElement):
    """出力コイル"""
    def __init__(self, device_address: str):
        super().__init__(device_address)
        
    def evaluate(self, device_manager: DeviceManager) -> bool:
        result = self.inputs[0].evaluate(device_manager) if self.inputs else False
        device_manager.set_device_value(self.device_address, result)
        self.last_result = result
        return result


class Timer(LogicElement):
    """タイマー（TON: タイマーオン）"""
    def __init__(self, device_address: str, preset_time: float = 5.0):
        super().__init__(device_address)
        self.preset_time = preset_time
        self.start_time = None
        self.is_timing = False
        
    def evaluate(self, device_manager: DeviceManager) -> bool:
        input_state = self.inputs[0].evaluate(device_manager) if self.inputs else False
        device = device_manager.get_device(self.device_address)
        
        current_time = time.time()
        
        if input_state and not self.is_timing:
            self.start_time = current_time
            self.is_timing = True
            device.current_value = 0
            device.coil_state = False
            
        elif not input_state:
            self.is_timing = False
            self.start_time = None
            device.current_value = 0
            device.coil_state = False
            
        if self.is_timing:
            elapsed = current_time - self.start_time
            device.current_value = elapsed
            
            if elapsed >= self.preset_time:
                device.coil_state = True
            else:
                device.coil_state = False
        
        device.preset_value = self.preset_time
        self.last_result = device.coil_state
        return device.coil_state


class Counter(LogicElement):
    """カウンター（CTU: カウントアップ）"""
    def __init__(self, device_address: str, preset_count: int = 5):
        super().__init__(device_address)
        self.preset_count = preset_count
        self.last_input_state = False
        
    def evaluate(self, device_manager: DeviceManager) -> bool:
        input_state = self.inputs[0].evaluate(device_manager) if self.inputs else False
        device = device_manager.get_device(self.device_address)
        
        if input_state and not self.last_input_state:
            device.current_value += 1
            
        if device.current_value >= self.preset_count:
            device.coil_state = True
        else:
            device.coil_state = False
            
        device.preset_value = self.preset_count
        self.last_input_state = input_state
        self.last_result = device.coil_state
        return device.coil_state


class LadderLine:
    """ラダー図の1行を表現するクラス"""
    def __init__(self):
        self.elements: List[LogicElement] = []
        self.power_flow = False
        
    def add_element(self, element: LogicElement):
        """素子を追加（左から右の順序）"""
        if self.elements:
            element.add_input(self.elements[-1])
        self.elements.append(element)
        
    def scan(self, device_manager: DeviceManager):
        """ライン実行（左から右へ）"""
        if self.elements:
            self.power_flow = self.elements[-1].evaluate(device_manager)


class LadderProgram:
    """ラダープログラム全体を管理するクラス"""
    def __init__(self):
        self.lines: List[LadderLine] = []
        self.current_line = 0
        
    def add_line(self, line: LadderLine):
        """ラインを追加"""
        self.lines.append(line)
        
    def scan_cycle(self, device_manager: DeviceManager):
        """スキャンサイクル実行（上から下へ）"""
        for i, line in enumerate(self.lines):
            self.current_line = i
            line.scan(device_manager)
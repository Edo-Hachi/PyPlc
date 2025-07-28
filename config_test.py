#!/usr/bin/env python3
"""
Configuration Test
設定値確認テスト
"""

from config import PyPlcConfig, DeviceType, Colors
from core.grid_manager import GridDeviceManager

def test_config():
    print("=== Configuration Test ===")
    
    # 設定読み込み
    config = PyPlcConfig.load_from_file()
    print(f"Grid size: {config.grid_rows}x{config.grid_cols}")
    print(f"Grid origin: ({config.grid_origin_x}, {config.grid_origin_y})")
    print(f"Cell size: {config.grid_cell_size}")
    print(f"Window size: {config.window_width}x{config.window_height}")
    
    # GridManager作成
    manager = GridDeviceManager(config)
    print(f"Initial devices: {len(manager.get_all_devices())}")
    
    # (1,0)配置テスト
    result = manager.place_device(1, 0, DeviceType.CONTACT_A, "X001")
    print(f"Device placement at (1,0): {result}")
    
    device = manager.get_device(1, 0)
    if device:
        print(f"Device found: {device}")
        print(f"Device position: ({device.grid_row}, {device.grid_col})")
        print(f"Device type: {device.device_type}")
        print(f"Device active: {device.active}")
    else:
        print("No device found at (1,0)")
    
    # 全デバイス確認
    print(f"Total devices after placement: {len(manager.get_all_devices())}")
    for device in manager.get_all_devices():
        if not device.is_bus_device():
            print(f"  Non-bus device: {device.name} at ({device.grid_row}, {device.grid_col})")

if __name__ == "__main__":
    test_config()
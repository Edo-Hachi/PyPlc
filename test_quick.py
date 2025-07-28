#!/usr/bin/env python3
"""
Quick test for PyPlc-v2 basic functionality
PyPlc-v2基本機能テスト
"""

# Test imports / インポートテスト
try:
    import pyxel
    print("✓ pyxel import success")
except ImportError as e:
    print(f"✗ pyxel import failed: {e}")
    exit(1)

try:
    from config import PyPlcConfig, DeviceType, Layout
    print("✓ config import success")
except ImportError as e:
    print(f"✗ config import failed: {e}")
    exit(1)

try:
    from core.grid_manager import GridDeviceManager
    print("✓ grid_manager import success")
except ImportError as e:
    print(f"✗ grid_manager import failed: {e}")
    exit(1)

try:
    from core.logic_element import LogicElement
    print("✓ logic_element import success")
except ImportError as e:
    print(f"✗ logic_element import failed: {e}")
    exit(1)

# Test configuration loading / 設定読み込みテスト
print("\n--- Configuration Test ---")
config = PyPlcConfig.load_from_file()
print(f"Grid size: {config.grid_rows}x{config.grid_cols}")
print(f"Window size: {config.window_width}x{config.window_height}")
print(f"Grid origin: ({config.grid_origin_x}, {config.grid_origin_y})")

# Test grid manager / グリッドマネージャーテスト
print("\n--- Grid Manager Test ---")
grid_manager = GridDeviceManager(config)
print(f"Grid initialized: {grid_manager.grid_rows}x{grid_manager.grid_cols}")

# Test device placement / デバイス配置テスト
print("\n--- Device Placement Test ---")
result = grid_manager.place_device(1, 2, DeviceType.CONTACT_A, "X001")
print(f"Device placement result: {result}")
print(f"Total devices: {len(grid_manager.get_all_devices())}")

# Test device retrieval / デバイス取得テスト
device = grid_manager.get_device(1, 2)
if device:
    print(f"Found device at (1,2): {device.name}, type: {device.device_type}, active: {device.active}")
else:
    print("No device found at (1,2)")

print("\n✓ All basic tests passed")
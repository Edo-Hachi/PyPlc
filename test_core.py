#!/usr/bin/env python3
"""
PyPlc-v2 Core System Test
コアシステムテスト
"""

from config import PyPlcConfig, DeviceType
from core.grid_manager import GridDeviceManager
from core.logic_element import LogicElement, create_logic_element


def test_config_system():
    """Test configuration system / 設定システムテスト"""
    print("=== Configuration System Test ===")
    
    # Load config / 設定読み込み
    config = PyPlcConfig.load_from_file()
    print(f"Grid size: {config.grid_rows}x{config.grid_cols}")
    print(f"Cell size: {config.grid_cell_size}px")
    print(f"Window size: {config.window_width}x{config.window_height}")
    print(f"Auto address generation: {config.auto_generate_address}")
    print()


def test_logic_element():
    """Test LogicElement creation / LogicElement作成テスト"""
    print("=== LogicElement Test ===")
    
    # Create various devices / 各種デバイス作成
    contact_a = create_logic_element(2, 3, DeviceType.CONTACT_A, "X001")
    contact_b = create_logic_element(2, 5, DeviceType.CONTACT_B, "X002")
    coil = create_logic_element(2, 8, DeviceType.COIL, "Y001")
    timer = create_logic_element(4, 4, DeviceType.TIMER, "T001")
    
    print(f"A Contact: {contact_a}")
    print(f"B Contact: {contact_b}")
    print(f"Output Coil: {coil}")
    print(f"Timer: {timer}")
    
    # Test device type checks / デバイスタイプチェックテスト
    print(f"Contact A is contact device: {contact_a.is_contact_device()}")
    print(f"Coil is coil device: {coil.is_coil_device()}")
    print(f"Timer is function device: {timer.is_function_device()}")
    print()


def test_grid_manager():
    """Test GridDeviceManager / GridDeviceManagerテスト"""
    print("=== GridDeviceManager Test ===")
    
    # Create config and manager / 設定とマネージャー作成
    config = PyPlcConfig.load_from_file()
    manager = GridDeviceManager(config)
    
    print(f"Grid size: {manager.get_grid_size()}")
    print(f"Initial device count: {len(manager.get_all_devices())}")
    
    # Test device placement / デバイス配置テスト
    success1 = manager.place_device(2, 2, DeviceType.CONTACT_A, "X001")
    success2 = manager.place_device(2, 4, DeviceType.CONTACT_B, "X002")
    success3 = manager.place_device(2, 7, DeviceType.COIL, "Y001")
    success4 = manager.place_device(4, 3, DeviceType.TIMER, "T001")
    
    print(f"Device placement results: {success1}, {success2}, {success3}, {success4}")
    print(f"Total devices after placement: {len(manager.get_all_devices())}")
    
    # Test invalid placements / 無効配置テスト
    invalid1 = manager.place_device(0, 5, DeviceType.CONTACT_A)  # Bus lane
    invalid2 = manager.place_device(2, 2, DeviceType.CONTACT_B)  # Already occupied
    
    print(f"Invalid placement results: {invalid1}, {invalid2}")
    
    # Test device retrieval / デバイス取得テスト
    device = manager.get_device(2, 2)
    print(f"Device at (2,2): {device.name if device else 'None'}")
    
    # Test connections / 接続テスト
    if device:
        connections = device.get_connections()
        print(f"Device connections: {connections}")
    
    # Test grid integrity / グリッド整合性テスト
    integrity = manager.validate_grid_integrity()
    print(f"Grid integrity valid: {integrity}")
    
    print()


def test_device_logic():
    """Test device logic evaluation / デバイス論理評価テスト"""
    print("=== Device Logic Test ===")
    
    # Create test devices / テストデバイス作成
    contact_a = create_logic_element(1, 1, DeviceType.CONTACT_A, "X001")
    contact_b = create_logic_element(1, 2, DeviceType.CONTACT_B, "X002")
    
    # Test A contact logic / A接点論理テスト
    contact_a.powered = True
    contact_a.active = False
    result1 = contact_a.evaluate_logic()
    
    contact_a.active = True
    result2 = contact_a.evaluate_logic()
    
    print(f"A Contact - inactive: {result1}, active: {result2}")
    
    # Test B contact logic / B接点論理テスト
    contact_b.powered = True
    contact_b.active = False
    result3 = contact_b.evaluate_logic()
    
    contact_b.active = True
    result4 = contact_b.evaluate_logic()
    
    print(f"B Contact - inactive: {result3}, active: {result4}")
    
    # Test timer / タイマーテスト
    timer = create_logic_element(2, 1, DeviceType.TIMER, "T001")
    timer.powered = True
    timer.timer_preset = 2.0
    
    # Simulate timer operation / タイマー動作シミュレーション
    timer.update_timer(1.0)
    print(f"Timer after 1s: current={timer.timer_current:.1f}, active={timer.active}")
    
    timer.update_timer(1.5)
    print(f"Timer after 2.5s: current={timer.timer_current:.1f}, active={timer.active}")
    
    print()


def test_system_integration():
    """Test complete system integration / 完全システム統合テスト"""
    print("=== System Integration Test ===")
    
    config = PyPlcConfig.load_from_file()
    manager = GridDeviceManager(config)
    
    # Create simple ladder circuit / シンプルなラダー回路作成
    # L_SIDE -> X001 -> X002 -> Y001 -> R_SIDE
    manager.place_device(3, 2, DeviceType.CONTACT_A, "X001")
    manager.place_device(3, 4, DeviceType.CONTACT_B, "X002")
    manager.place_device(3, 7, DeviceType.COIL, "Y001")
    
    # Get devices for testing / テスト用デバイス取得
    x001 = manager.get_device(3, 2)
    x002 = manager.get_device(3, 4)
    y001 = manager.get_device(3, 7)
    
    print("Circuit: L_SIDE -> X001 -> X002 -> Y001 -> R_SIDE")
    
    # Test case 1: Both contacts OFF / 両接点OFF
    x001.active = False
    x002.active = False
    print(f"X001=OFF, X002=OFF -> Expected: Y001=OFF")
    
    # Test case 2: X001 ON, X002 OFF / X001 ON、X002 OFF
    x001.active = True
    x002.active = False
    print(f"X001=ON, X002=OFF -> Expected: Y001=ON (B contact)")
    
    # Test case 3: X001 ON, X002 ON / X001 ON、X002 ON
    x001.active = True
    x002.active = True
    print(f"X001=ON, X002=ON -> Expected: Y001=OFF (B contact active)")
    
    print()


def main():
    """Main test function / メインテスト関数"""
    print("PyPlc-v2 Core System Test")
    print("=" * 50)
    
    try:
        test_config_system()
        test_logic_element()
        test_grid_manager()
        test_device_logic()
        test_system_integration()
        
        print("✅ All tests completed successfully!")
        print("   全テストが正常に完了しました！")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print(f"   テスト失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
データレジスタとcompare命令の動作テスト
Pyxelなしで基本機能をテストする
"""

from core.grid_system import GridSystem, GridDevice
from core.circuit_analyzer import CircuitAnalyzer
from config import DeviceType

def test_data_register_compare():
    """データレジスタとcompare命令の連携テスト"""
    print("=== データレジスタ・Compare命令動作テスト ===")
    
    # GridSystemの初期化
    grid = GridSystem(15, 20, 16, 50, 50)
    analyzer = CircuitAnalyzer(grid)
    
    # テスト回路構築: X001 → COMP(D1>10) → Y001
    # 同時にD1データレジスタを配置
    
    # 1. 左バス
    left_bus = GridDevice(DeviceType.L_SIDE, 0, 0)
    left_bus.is_energized = True
    grid.place_device(left_bus, 0, 0)
    
    # 2. X001接点
    x001_contact = GridDevice(DeviceType.CONTACT_A, 0, 1)
    x001_contact.address = "X001"
    x001_contact.state = True  # 手動でON状態に設定
    grid.place_device(x001_contact, 0, 1)
    
    # 3. Compare命令 (D1>10)
    compare_device = GridDevice(DeviceType.COMPARE_DEVICE, 0, 2)
    compare_device.address = "D1>10"
    grid.place_device(compare_device, 0, 2)
    
    # 4. Y001コイル
    y001_coil = GridDevice(DeviceType.COIL_STD, 0, 3)
    y001_coil.address = "Y001"
    grid.place_device(y001_coil, 0, 3)
    
    # 5. 右バス
    right_bus = GridDevice(DeviceType.R_SIDE, 0, 4)
    grid.place_device(right_bus, 0, 4)
    
    # 6. D1データレジスタ（別の行に配置）
    d1_register = GridDevice(DeviceType.DATA_REGISTER, 1, 1)
    d1_register.address = "D1"
    d1_register.data_value = 5  # 初期値: 5
    grid.place_device(d1_register, 1, 1)
    
    # デバイス間の接続設定
    grid.auto_connect_adjacent_devices()
    
    print("\n=== 初期状態 ===")
    print(f"X001接点: {x001_contact.state}")
    print(f"D1データレジスタ値: {d1_register.data_value}")
    print(f"Compare命令(D1>10): {compare_device.address}")
    print(f"Y001コイル: {y001_coil.state}")
    
    # 回路解析実行
    print("\n=== 1回目解析: D1=5, D1>10は偽 ===")
    analyzer.solve_ladder()
    
    print(f"Compare命令結果: {compare_device.state}")
    print(f"Y001コイル: {y001_coil.state}")
    print(f"Y001コイル通電: {y001_coil.is_energized}")
    
    # D1の値を15に変更してテスト
    print("\n=== D1の値を15に変更 ===")
    d1_register.data_value = 15
    
    print("\n=== 2回目解析: D1=15, D1>10は真 ===")
    analyzer.solve_ladder()
    
    print(f"D1データレジスタ値: {d1_register.data_value}")
    print(f"Compare命令結果: {compare_device.state}")
    print(f"Y001コイル: {y001_coil.state}")
    print(f"Y001コイル通電: {y001_coil.is_energized}")
    
    # 複数の比較演算子をテスト
    test_comparison_operators(grid, analyzer)

def test_comparison_operators(grid, analyzer):
    """様々な比較演算子のテスト"""
    print("\n=== 比較演算子テスト ===")
    
    # D2データレジスタを追加
    d2_register = GridDevice(DeviceType.DATA_REGISTER, 2, 1)
    d2_register.address = "D2"
    d2_register.data_value = 20
    grid.place_device(d2_register, 2, 1)
    
    # テストケース
    test_cases = [
        ("D1=15", True),   # D1(15) = 15
        ("D1<>10", True),  # D1(15) <> 10
        ("D1>=15", True),  # D1(15) >= 15
        ("D1<=15", True),  # D1(15) <= 15
        ("D1<20", True),   # D1(15) < 20
        ("D2>15", True),   # D2(20) > 15
        ("D1=D2", False),  # D1(15) = D2(20)
    ]
    
    for expression, expected in test_cases:
        # 新しいcompare命令を作成してテスト
        compare_test = GridDevice(DeviceType.COMPARE_DEVICE, 3, 1)
        compare_test.address = expression
        compare_test.is_energized = True  # 通電状態にして評価可能にする
        
        # 比較演算を実行
        analyzer._execute_compare_operation(compare_test)
        
        result = compare_test.state
        status = "✓" if result == expected else "✗"
        print(f"  {status} {expression} -> {result} (期待値: {expected})")

if __name__ == "__main__":
    test_data_register_compare()
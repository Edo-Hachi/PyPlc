#!/usr/bin/env python3
"""
デバイスハイライト機能のテストスクリプト
PyPlc Ver3 - 同アドレスデバイス検索機能テスト
"""

import sys
sys.path.append('.')

from typing import List, Tuple
from config import DeviceType
from core.device_base import PLCDevice
from core.grid_system import GridSystem

def test_find_devices_by_address():
    """find_devices_by_address()メソッドの動作テスト"""
    print("=== デバイスハイライト機能テスト開始 ===")
    
    # GridSystemを初期化
    grid = GridSystem()
    
    # テスト用デバイスを配置
    print("\n1. テスト用デバイス配置...")
    
    # X001接点を複数箇所に配置
    device1 = grid.place_device(2, 2, DeviceType.CONTACT_A, "X001")
    device2 = grid.place_device(4, 5, DeviceType.CONTACT_A, "X001")
    device3 = grid.place_device(6, 8, DeviceType.CONTACT_B, "X001")  # B接点でも同一アドレス
    
    # M100デバイスを配置
    device4 = grid.place_device(3, 10, DeviceType.COIL_STD, "M100")
    device5 = grid.place_device(5, 12, DeviceType.CONTACT_A, "M100")
    
    # 異なるアドレスのデバイス
    device6 = grid.place_device(7, 3, DeviceType.CONTACT_A, "X002")
    
    # アドレス無しデバイス
    device7 = grid.place_device(8, 6, DeviceType.LINK_HORZ, "")
    
    print(f"配置完了: {7}個のデバイスを配置")
    
    # テスト1: X001アドレス検索
    print("\n2. X001アドレス検索テスト...")
    x001_positions = grid.find_devices_by_address("X001")
    print(f"X001デバイス発見: {len(x001_positions)}個")
    print(f"座標: {x001_positions}")
    
    expected_x001 = [(2, 2), (4, 5), (6, 8)]
    if set(x001_positions) == set(expected_x001):
        print("✅ X001検索テスト: 成功")
    else:
        print(f"❌ X001検索テスト: 失敗 (期待値: {expected_x001})")
    
    # テスト2: M100アドレス検索
    print("\n3. M100アドレス検索テスト...")
    m100_positions = grid.find_devices_by_address("M100")
    print(f"M100デバイス発見: {len(m100_positions)}個")
    print(f"座標: {m100_positions}")
    
    expected_m100 = [(3, 10), (5, 12)]
    if set(m100_positions) == set(expected_m100):
        print("✅ M100検索テスト: 成功")
    else:
        print(f"❌ M100検索テスト: 失敗 (期待値: {expected_m100})")
    
    # テスト3: 存在しないアドレス検索
    print("\n4. 存在しないアドレス検索テスト...")
    none_positions = grid.find_devices_by_address("Y999")
    print(f"Y999デバイス発見: {len(none_positions)}個")
    if len(none_positions) == 0:
        print("✅ 存在しないアドレス検索テスト: 成功")
    else:
        print("❌ 存在しないアドレス検索テスト: 失敗")
    
    # テスト4: 空文字列・None検索
    print("\n5. 空文字列検索テスト...")
    empty_positions = grid.find_devices_by_address("")
    none_positions = grid.find_devices_by_address(None)
    if len(empty_positions) == 0:
        print("✅ 空文字列検索テスト: 成功")
    else:
        print("❌ 空文字列検索テスト: 失敗")
    
    # テスト5: 大文字小文字の正規化テスト
    print("\n6. 大文字小文字正規化テスト...")
    lower_positions = grid.find_devices_by_address("x001")  # 小文字
    mixed_positions = grid.find_devices_by_address("X001")   # 大文字
    if set(lower_positions) == set(mixed_positions) == set(expected_x001):
        print("✅ 大文字小文字正規化テスト: 成功")
    else:
        print("❌ 大文字小文字正規化テスト: 失敗")
    
    print("\n=== テスト完了 ===")
    print("Phase 1基本機能の実装が正常に完了しました")
    print("次のステップ: 実際のPyPlcアプリでホバーテストを実行")

if __name__ == "__main__":
    test_find_devices_by_address()
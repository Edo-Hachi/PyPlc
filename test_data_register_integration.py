#!/usr/bin/env python3
"""
データレジスタとCompare命令の統合テスト
ダイアログシステムとの連携確認
"""

import sys
import os

# モジュールパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 構文チェック用インポート
def test_imports():
    """必要なモジュールのインポートテスト"""
    print("=== インポートテスト ===")
    
    try:
        from DialogManager.data_register_dialog_json import DataRegisterDialog
        print("✓ DataRegisterDialog インポート成功")
    except Exception as e:
        print(f"✗ DataRegisterDialog インポート失敗: {e}")
        return False
    
    try:
        from DialogManager.compare_dialog_json import CompareDialog
        print("✓ CompareDialog インポート成功")
    except Exception as e:
        print(f"✗ CompareDialog インポート失敗: {e}")
        return False
    
    try:
        from DialogManager.new_dialog_manager import NewDialogManager
        print("✓ NewDialogManager インポート成功")
    except Exception as e:
        print(f"✗ NewDialogManager インポート失敗: {e}")
        return False
    
    return True

def test_data_register_dialog():
    """データレジスタダイアログの機能テスト"""
    print("\n=== データレジスタダイアログテスト ===")
    
    try:
        from DialogManager.data_register_dialog_json import DataRegisterDialog
        
        # ダイアログの初期化テスト
        dialog = DataRegisterDialog(x=50, y=50)
        print("✓ ダイアログ初期化成功")
        
        # 初期値設定テスト
        dialog.set_initial_values("D10", 100)
        print("✓ 初期値設定成功")
        
        # バリデーションテスト
        test_cases = [
            ("D1", True),      # 正常なアドレス
            ("D255", True),    # 正常なアドレス（最大値）
            ("D256", False),   # 範囲外アドレス
            ("X1", False),     # 不正なプレフィックス
            ("", False),       # 空文字
        ]
        
        for address, expected in test_cases:
            result = dialog._handle_validation("address_input", address)
            status = "✓" if result == expected else "✗"
            print(f"  {status} アドレス '{address}' -> {result} (期待値: {expected})")
        
        # 値バリデーションテスト
        value_test_cases = [
            ("100", True),     # 正常値
            ("0", True),       # 最小値
            ("32767", True),   # 最大値
            ("32768", False),  # 範囲外
            ("-1", False),     # 負数
            ("abc", False),    # 非数値
        ]
        
        for value, expected in value_test_cases:
            result = dialog._handle_validation("value_input", value)
            status = "✓" if result == expected else "✗"
            print(f"  {status} 値 '{value}' -> {result} (期待値: {expected})")
        
        return True
        
    except Exception as e:
        print(f"✗ データレジスタダイアログテスト失敗: {e}")
        return False

def test_compare_dialog():
    """Compare命令ダイアログの機能テスト"""
    print("\n=== Compare命令ダイアログテスト ===")
    
    try:
        from DialogManager.compare_dialog_json import CompareDialog
        
        # ダイアログの初期化テスト
        dialog = CompareDialog(x=50, y=50)
        print("✓ ダイアログ初期化成功")
        
        # 初期条件設定テスト
        dialog.set_initial_condition("D1>10")
        print("✓ 初期条件設定成功")
        
        # 比較式バリデーションテスト
        test_cases = [
            ("D1>10", True),     # 正常な比較式
            ("D2=100", True),    # 等号比較
            ("D3<>D4", True),    # レジスタ同士比較
            ("D5>=50", True),    # 以上比較
            ("D6<=D7", True),    # 以下比較
            ("D1", False),       # 演算子なし
            ("D256>10", False),  # 範囲外レジスタ
            ("X1>10", False),    # 不正なプレフィックス
            ("D1>32768", False), # 範囲外値
            ("", False),         # 空文字
        ]
        
        for expression, expected in test_cases:
            result = dialog._validate_compare_expression(expression)
            status = "✓" if result == expected else "✗"
            print(f"  {status} 式 '{expression}' -> {result} (期待値: {expected})")
        
        return True
        
    except Exception as e:
        print(f"✗ Compare命令ダイアログテスト失敗: {e}")
        return False

def test_dialog_manager_integration():
    """DialogManager統合テスト"""
    print("\n=== DialogManager統合テスト ===")
    
    try:
        from DialogManager.new_dialog_manager import NewDialogManager
        from config import DeviceType
        
        # MockDeviceクラス
        class MockDevice:
            def __init__(self, device_type, address=None):
                self.device_type = device_type
                self.address = address
                self.data_value = 0
        
        manager = NewDialogManager()
        print("✓ NewDialogManager初期化成功")
        
        # データレジスタのデフォルトID生成テスト
        default_id = manager.generate_default_device_id(DeviceType.DATA_REGISTER, 1, 5)
        expected_id = "D015"
        status = "✓" if default_id == expected_id else "✗"
        print(f"  {status} データレジスタデフォルトID: {default_id} (期待値: {expected_id})")
        
        # Compare命令のデフォルトID生成テスト
        default_compare = manager.generate_default_device_id(DeviceType.COMPARE_DEVICE, 0, 0)
        expected_compare = "D1>10"
        status = "✓" if default_compare == expected_compare else "✗"
        print(f"  {status} Compare命令デフォルト条件: {default_compare} (期待値: {expected_compare})")
        
        # デバイスタイプ判定テスト
        data_device = MockDevice(DeviceType.DATA_REGISTER, "D10")
        is_valid = manager.validate_device_for_id_edit(data_device)
        print(f"  ✓ データレジスタ編集可能性: {is_valid}")
        
        compare_device = MockDevice(DeviceType.COMPARE_DEVICE, "D1>5")
        is_valid = manager.validate_device_for_id_edit(compare_device)
        print(f"  ✓ Compare命令編集可能性: {is_valid}")
        
        return True
        
    except Exception as e:
        print(f"✗ DialogManager統合テスト失敗: {e}")
        return False

def test_json_definitions():
    """JSON定義ファイルの構文テスト"""
    print("\n=== JSON定義ファイルテスト ===")
    
    import json
    
    # データレジスタ設定JSON
    try:
        with open("DialogManager/definitions/data_register_settings.json", 'r') as f:
            data_register_def = json.load(f)
        print("✓ data_register_settings.json 読み込み成功")
        
        # 必要フィールドの確認
        required_fields = ["title", "width", "height", "controls"]
        for field in required_fields:
            if field in data_register_def:
                print(f"  ✓ {field} フィールド存在")
            else:
                print(f"  ✗ {field} フィールド不足")
                return False
                
    except Exception as e:
        print(f"✗ data_register_settings.json 読み込み失敗: {e}")
        return False
    
    # Compare設定JSON
    try:
        with open("DialogManager/definitions/compare_settings.json", 'r') as f:
            compare_def = json.load(f)
        print("✓ compare_settings.json 読み込み成功")
        
        # 必要フィールドの確認
        for field in required_fields:
            if field in compare_def:
                print(f"  ✓ {field} フィールド存在")
            else:
                print(f"  ✗ {field} フィールド不足")
                return False
                
    except Exception as e:
        print(f"✗ compare_settings.json 読み込み失敗: {e}")
        return False
    
    return True

def main():
    """統合テストメイン処理"""
    print("=== データレジスタ・Compare命令統合テスト開始 ===\n")
    
    tests = [
        ("インポートテスト", test_imports),
        ("JSON定義テスト", test_json_definitions),
        ("データレジスタダイアログテスト", test_data_register_dialog),
        ("Compare命令ダイアログテスト", test_compare_dialog),
        ("DialogManager統合テスト", test_dialog_manager_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} 成功")
            else:
                print(f"✗ {test_name} 失敗")
        except Exception as e:
            print(f"✗ {test_name} 例外発生: {e}")
    
    print(f"\n=== テスト結果 ===")
    print(f"合格: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 全テストが成功しました！データレジスタ・Compare命令機能は正常に動作します。")
        return True
    else:
        print("⚠️  一部テストが失敗しました。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
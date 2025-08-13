"""
Phase2IntegrationTest - Phase 2統合テスト

PyPlc Ver3 Dialog System - Phase 2 Integration Test
TextInputControl + ValidationSystem + DeviceIDDialogJSON の統合動作確認
"""

from DialogManager.device_id_dialog_json import show_device_id_dialog
from config import DeviceType


def test_device_id_dialog_json():
    """
    DeviceIDDialogJSONの動作テスト
    """
    print("🚀 Phase 2 Integration Test: DeviceIDDialogJSON")
    print("=" * 60)
    
    # テストケース1: 新規デバイスID入力
    print("\n📋 Test Case 1: New Device ID Input")
    try:
        result = show_device_id_dialog(DeviceType.CONTACT_A, "")
        print(f"Result: {result}")
        print("✅ Test Case 1 completed")
    except Exception as e:
        print(f"❌ Test Case 1 failed: {e}")
    
    # テストケース2: 既存デバイスID編集
    print("\n📋 Test Case 2: Edit Existing Device ID")
    try:
        result = show_device_id_dialog(DeviceType.COIL_STD, "Y100")
        print(f"Result: {result}")
        print("✅ Test Case 2 completed")
    except Exception as e:
        print(f"❌ Test Case 2 failed: {e}")
    
    print("\n🎉 Phase 2 Integration Test completed!")
    print("Note: Actual dialog interaction requires Pyxel environment")


def show_phase2_integration_test_dialog():
    """
    Phase 2統合テストダイアログを表示する便利関数
    main.pyから呼び出し可能
    
    Returns:
        テスト結果
    """
    try:
        print("🚀 Phase 2 Integration Test: Starting DeviceIDDialogJSON test...")
        
        # CONTACT_Aデバイスの新規作成テスト
        result = show_device_id_dialog(DeviceType.CONTACT_A, "")
        
        print(f"📋 Phase 2 Integration Test Result: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Phase 2 Integration Test error: {e}")
        return (False, "")


if __name__ == "__main__":
    test_device_id_dialog_json()

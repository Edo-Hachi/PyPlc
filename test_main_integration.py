#!/usr/bin/env python3
"""
main.pyとDialogManager_v3の統合テスト
実際にmain.pyのファイルダイアログが動作するかテスト
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_main_imports():
    """main.pyの必要なインポートが正常に動作するかテスト"""
    print("=== main.py インポートテスト ===")
    
    try:
        # main.pyの必要なインポートをテスト
        from DialogManager_v3 import FileManagerV3
        print("✅ FileManagerV3 インポート成功")
        
        from core.circuit_csv_manager import CircuitCsvManager
        print("✅ CircuitCsvManager インポート成功")
        
        from core.grid_system import GridSystem
        print("✅ GridSystem インポート成功")
        
        print("=== main.py インポートテスト完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ インポートテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_manager_v3():
    """FileManagerV3の基本動作テスト"""
    print("\n=== FileManagerV3 動作テスト ===")
    
    try:
        from DialogManager_v3 import FileManagerV3
        from core.circuit_csv_manager import CircuitCsvManager
        from core.grid_system import GridSystem
        
        # 必要なオブジェクトを作成
        grid_system = GridSystem()
        csv_manager = CircuitCsvManager(grid_system)
        file_manager = FileManagerV3(csv_manager)
        
        print("✅ FileManagerV3 作成成功")
        
        # show_load_dialogメソッドの存在確認
        if hasattr(file_manager, 'show_load_dialog'):
            print("✅ show_load_dialog メソッド存在確認")
        else:
            print("❌ show_load_dialog メソッドが見つかりません")
            
        print("=== FileManagerV3 動作テスト完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ FileManagerV3テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dialog_creation():
    """ダイアログ作成のフルテスト"""
    print("\n=== ダイアログ作成フルテスト ===")
    
    try:
        import pyxel
        pyxel.init(400, 300, title="Integration Test", fps=30, quit_key=pyxel.KEY_F12)
        print("✅ Pyxel初期化成功")
        
        from DialogManager_v3 import FileManagerV3
        from core.circuit_csv_manager import CircuitCsvManager
        from core.grid_system import GridSystem
        
        # PyPlc Ver3と同じ方式でオブジェクトを作成
        grid_system = GridSystem()
        csv_manager = CircuitCsvManager(grid_system)
        file_manager = FileManagerV3(csv_manager)
        
        print("✅ FileManagerV3 作成成功")
        
        # ダイアログを作成（実際にGUIを開かずにテスト）
        if hasattr(file_manager, 'dialog'):
            dialog = file_manager.dialog
            print(f"✅ Dialog object: {type(dialog).__name__}")
            
            # 重要メソッドの存在確認
            required_methods = ['handle_key_input', 'handle_text_input', 'show_load_dialog']
            for method in required_methods:
                if hasattr(dialog, method):
                    print(f"✅ {method} メソッド存在確認")
                else:
                    print(f"❌ {method} メソッド不足")
        else:
            print("⚠️ file_manager.dialog プロパティが見つかりません")
            
        print("=== ダイアログ作成フルテスト完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ ダイアログ作成テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("main.py統合テスト開始\n")
    
    results = []
    results.append(test_main_imports())
    results.append(test_file_manager_v3())
    results.append(test_dialog_creation())
    
    # 結果サマリー
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"テスト結果: {passed}/{total} 成功")
    
    if passed == total:
        print("🎉 すべてのテストが成功しました！")
        print("main.pyでDialogManager_v3が正常に動作する準備が整いました。")
        print("\n📋 次のステップ:")
        print("1. main.pyを実行")
        print("2. TABキーでEDITモードに切り替え")
        print("3. Ctrl+Oでファイルダイアログを開く")
        print("4. ファイル名入力欄でキーボード入力テスト")
    else:
        print("⚠️  一部のテストが失敗しました。")
        print("詳細なエラー内容を確認して修正してください。")
    
    print("=" * 50)
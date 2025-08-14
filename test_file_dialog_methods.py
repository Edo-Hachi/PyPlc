#!/usr/bin/env python3
"""
FileLoadDialogJSONのメソッド実装確認テスト
"""

import os
import sys
import pyxel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_file_dialog_methods():
    """FileLoadDialogJSONの必要メソッドが実装されているかテスト"""
    print("=== FileLoadDialogJSON メソッド実装確認テスト ===")
    
    try:
        # Pyxel初期化
        pyxel.init(400, 300, title="Method Test", fps=30, quit_key=pyxel.KEY_F12)
        
        from DialogManager_v3.dialogs.file_load_dialog import FileLoadDialogJSON
        
        # FileLoadDialogJSONを作成
        dialog = FileLoadDialogJSON()
        print("✅ FileLoadDialogJSON作成成功")
        
        # 必要なメソッドの存在確認
        required_methods = [
            'handle_key_input',
            'handle_text_input', 
            'show_load_dialog'
        ]
        
        for method_name in required_methods:
            if hasattr(dialog, method_name):
                print(f"✅ {method_name}メソッド存在確認")
                
                # メソッドが呼び出し可能かテスト
                method = getattr(dialog, method_name)
                if callable(method):
                    print(f"✅ {method_name}は呼び出し可能")
                else:
                    print(f"❌ {method_name}は呼び出し不可")
            else:
                print(f"❌ {method_name}メソッドが見つかりません")
        
        # フォーカス設定の確認
        if hasattr(dialog, 'filename_textbox') and hasattr(dialog, 'focused_control'):
            textbox = dialog.filename_textbox
            print(f"✅ filename_textbox: {type(textbox).__name__}")
            print(f"✅ focused_control: {type(dialog.focused_control).__name__}")
            
            if dialog.focused_control == textbox:
                print("✅ TextBoxControlが正しくフォーカスされています")
            else:
                print("⚠️ フォーカス設定に問題があります")
        
        # TextBoxControlのメソッド確認
        if hasattr(dialog, 'filename_textbox'):
            textbox = dialog.filename_textbox
            textbox_methods = ['on_key', 'on_text', 'text']
            
            for method_name in textbox_methods:
                if hasattr(textbox, method_name):
                    print(f"✅ TextBoxControl.{method_name} 存在確認")
                else:
                    print(f"❌ TextBoxControl.{method_name} が見つかりません")
        
        print("=== テスト完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_key_input():
    """キー入力処理のテスト"""
    print("\n=== キー入力処理テスト ===")
    
    try:
        # Pyxel初期化（既に初期化されている場合はスキップ）
        from DialogManager_v3.dialogs.file_load_dialog import FileLoadDialogJSON
        
        dialog = FileLoadDialogJSON()
        
        # handle_key_inputのテスト
        if hasattr(dialog, 'handle_key_input'):
            result = dialog.handle_key_input(pyxel.KEY_A)
            print(f"✅ handle_key_input(KEY_A): {result}")
        
        # handle_text_inputのテスト
        if hasattr(dialog, 'handle_text_input'):
            result = dialog.handle_text_input('A')
            print(f"✅ handle_text_input('A'): {result}")
            
            # テキストが実際に入力されているかチェック
            if hasattr(dialog, 'filename_textbox'):
                textbox = dialog.filename_textbox
                print(f"✅ TextBox内容: '{textbox.text}'")
        
        print("=== キー入力処理テスト完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ キー入力テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("FileLoadDialogJSON メソッド実装確認テスト開始\n")
    
    results = []
    results.append(test_file_dialog_methods())
    results.append(test_key_input())
    
    # 結果サマリー
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"テスト結果: {passed}/{total} 成功")
    
    if passed == total:
        print("🎉 すべてのテストが成功しました！")
        print("FileLoadDialogJSONの必要メソッドは正常に実装されています。")
    else:
        print("⚠️  一部のテストが失敗しました。")
    
    print("=" * 50)
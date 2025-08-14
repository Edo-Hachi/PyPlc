#!/usr/bin/env python3
"""
TextBoxControl入力フィルター統合テスト
normal, filename_safe, numeric_only各モードの動作確認
"""

import os
import sys
import pyxel
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_normal_mode():
    """normalモードのテスト"""
    print("=== Normal Mode テスト ===")
    
    try:
        # Pyxel初期化
        pyxel.init(400, 300, title="Normal Mode Test", fps=30, quit_key=pyxel.KEY_F12)
        
        from DialogManager_v3.controls.textbox_control import TextBoxControl
        
        # Normal モードでTextBoxControl作成
        textbox = TextBoxControl(x=10, y=10, width=200, input_filter="normal")
        
        print(f"✅ Normal TextBoxControl作成: {textbox.input_filter}")
        print(f"✅ 許可文字: {textbox.get_allowed_characters()}")
        
        # すべての印字可能文字をテスト
        test_chars = [
            'a', 'A', '1', '!', '@', '#', '$', '%', '^', '&', '*', 
            '(', ')', '-', '_', '=', '+', '[', '{', ']', '}', 
            '\\', '|', ';', ':', "'", '"', ',', '<', '.', '>', 
            '/', '?', '`', '~', ' ', '\t'
        ]
        
        results = []
        for char in test_chars:
            textbox.text = ""
            result = textbox.on_text(char)
            if result and textbox.text == char:
                print(f"✅ '{char}' 入力許可")
                results.append(True)
            else:
                print(f"❌ '{char}' 入力拒否")
                results.append(False)
        
        passed = sum(results)
        total = len(results)
        
        print(f"Normal Mode結果: {passed}/{total} ({passed/total*100:.1f}%)")
        return passed == total
        
    except Exception as e:
        print(f"❌ Normal Mode テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_filename_safe_mode():
    """filename_safeモードのテスト"""
    print("\n=== Filename Safe Mode テスト ===")
    
    try:
        from DialogManager_v3.controls.textbox_control import TextBoxControl
        
        # Filename Safe モードでTextBoxControl作成
        textbox = TextBoxControl(x=10, y=10, width=200, input_filter="filename_safe")
        
        print(f"✅ Filename Safe TextBoxControl作成: {textbox.input_filter}")
        print(f"✅ 許可文字: {textbox.get_allowed_characters()}")
        
        # 許可される文字
        allowed_chars = [
            'a', 'A', '1', '!', '@', '#', '$', '%', '^', '&', '*', 
            '(', ')', '-', '_', '[', '{', ']', '}', 
            '\\', '|', ';', ':', "'", '"', ',', '.', 
            '/', '?', '`', '~', ' '
        ]
        
        # 拒否される文字
        rejected_chars = ['=', '+', '<', '>']
        
        print("\n--- 許可文字テスト ---")
        allowed_results = []
        for char in allowed_chars:
            textbox.text = ""
            result = textbox.on_text(char)
            if result and textbox.text == char:
                print(f"✅ '{char}' 正しく許可")
                allowed_results.append(True)
            else:
                print(f"❌ '{char}' 誤って拒否")
                allowed_results.append(False)
        
        print("\n--- 拒否文字テスト ---")
        rejected_results = []
        for char in rejected_chars:
            textbox.text = ""
            result = textbox.on_text(char)
            if not result and textbox.text == "":
                print(f"✅ '{char}' 正しく拒否")
                rejected_results.append(True)
            else:
                print(f"❌ '{char}' 誤って許可")
                rejected_results.append(False)
        
        allowed_passed = sum(allowed_results)
        allowed_total = len(allowed_results)
        rejected_passed = sum(rejected_results)
        rejected_total = len(rejected_results)
        
        print(f"\n許可文字: {allowed_passed}/{allowed_total} ({allowed_passed/allowed_total*100:.1f}%)")
        print(f"拒否文字: {rejected_passed}/{rejected_total} ({rejected_passed/rejected_total*100:.1f}%)")
        
        return allowed_passed == allowed_total and rejected_passed == rejected_total
        
    except Exception as e:
        print(f"❌ Filename Safe Mode テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_numeric_only_mode():
    """numeric_onlyモードのテスト"""
    print("\n=== Numeric Only Mode テスト ===")
    
    try:
        from DialogManager_v3.controls.textbox_control import TextBoxControl
        
        # Numeric Only モードでTextBoxControl作成
        textbox = TextBoxControl(x=10, y=10, width=200, input_filter="numeric_only")
        
        print(f"✅ Numeric Only TextBoxControl作成: {textbox.input_filter}")
        print(f"✅ 許可文字: {textbox.get_allowed_characters()}")
        
        # 許可される文字（数値関連）
        allowed_chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '-', '+']
        
        # 拒否される文字
        rejected_chars = ['a', 'A', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '=', ' ', '/']
        
        print("\n--- 数値文字テスト ---")
        allowed_results = []
        for char in allowed_chars:
            textbox.text = ""
            result = textbox.on_text(char)
            if result and textbox.text == char:
                print(f"✅ '{char}' 正しく許可")
                allowed_results.append(True)
            else:
                print(f"❌ '{char}' 誤って拒否")
                allowed_results.append(False)
        
        print("\n--- 非数値文字テスト ---")
        rejected_results = []
        for char in rejected_chars:
            textbox.text = ""
            result = textbox.on_text(char)
            if not result and textbox.text == "":
                print(f"✅ '{char}' 正しく拒否")
                rejected_results.append(True)
            else:
                print(f"❌ '{char}' 誤って許可")
                rejected_results.append(False)
        
        allowed_passed = sum(allowed_results)
        allowed_total = len(allowed_results)
        rejected_passed = sum(rejected_results)
        rejected_total = len(rejected_results)
        
        print(f"\n数値文字: {allowed_passed}/{allowed_total} ({allowed_passed/allowed_total*100:.1f}%)")
        print(f"非数値文字: {rejected_passed}/{rejected_total} ({rejected_passed/rejected_total*100:.1f}%)")
        
        return allowed_passed == allowed_total and rejected_passed == rejected_total
        
    except Exception as e:
        print(f"❌ Numeric Only Mode テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_filter_switching():
    """フィルター動的切り替えテスト"""
    print("\n=== フィルター動的切り替えテスト ===")
    
    try:
        from DialogManager_v3.controls.textbox_control import TextBoxControl
        
        # 初期設定：normal
        textbox = TextBoxControl(x=10, y=10, width=200, input_filter="normal")
        print(f"✅ 初期フィルター: {textbox.input_filter}")
        
        # normalで'='を入力（成功するはず）
        textbox.text = ""
        result1 = textbox.on_text('=')
        print(f"✅ normal + '=': {result1} ('{textbox.text}')")
        
        # filename_safeに切り替え
        textbox.input_filter = "filename_safe"
        print(f"✅ フィルター切り替え: {textbox.input_filter}")
        
        # filename_safeで'='を入力（失敗するはず）
        textbox.text = ""
        result2 = textbox.on_text('=')
        print(f"✅ filename_safe + '=': {result2} ('{textbox.text}')")
        
        # filename_safeで'a'を入力（成功するはず）
        textbox.text = ""
        result3 = textbox.on_text('a')
        print(f"✅ filename_safe + 'a': {result3} ('{textbox.text}')")
        
        # numeric_onlyに切り替え
        textbox.input_filter = "numeric_only"
        print(f"✅ フィルター切り替え: {textbox.input_filter}")
        
        # numeric_onlyで'1'を入力（成功するはず）
        textbox.text = ""
        result4 = textbox.on_text('1')
        print(f"✅ numeric_only + '1': {result4} ('{textbox.text}')")
        
        # numeric_onlyで'a'を入力（失敗するはず）
        textbox.text = ""
        result5 = textbox.on_text('a')
        print(f"✅ numeric_only + 'a': {result5} ('{textbox.text}')")
        
        # 期待する結果
        expected = [True, False, True, True, False]
        actual = [result1, result2, result3, result4, result5]
        
        success = expected == actual
        print(f"\nフィルター切り替え結果: {'成功' if success else '失敗'}")
        print(f"期待値: {expected}")
        print(f"実際値: {actual}")
        
        return success
        
    except Exception as e:
        print(f"❌ フィルター切り替えテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_dialog_integration():
    """ファイルダイアログ統合テスト"""
    print("\n=== ファイルダイアログ統合テスト ===")
    
    try:
        from DialogManager_v3.dialogs.file_load_dialog import FileLoadDialogJSON
        
        # FileLoadDialogJSON作成
        dialog = FileLoadDialogJSON()
        textbox = dialog.filename_textbox
        
        print(f"✅ FileDialog TextBox作成: {textbox.input_filter}")
        
        # filename_safeモードの確認
        if textbox.input_filter == "filename_safe":
            print("✅ FileDialogは正しくfilename_safeモードを使用")
        else:
            print(f"❌ FileDialogのフィルターが間違っています: {textbox.input_filter}")
            return False
        
        # 危険文字の拒否テスト
        dangerous_chars = ['=', '+', '<', '>']
        test_results = []
        
        for char in dangerous_chars:
            textbox.text = ""
            result = textbox.on_text(char)
            success = (not result and textbox.text == "")
            test_results.append(success)
            print(f"✅ FileDialog '{char}': {'正しく拒否' if success else '誤って許可'}")
        
        # 安全文字の許可テスト
        safe_chars = ['a', '1', '.', '-', '_']
        for char in safe_chars:
            textbox.text = ""
            result = textbox.on_text(char)
            success = (result and textbox.text == char)
            test_results.append(success)
            print(f"✅ FileDialog '{char}': {'正しく許可' if success else '誤って拒否'}")
        
        passed = sum(test_results)
        total = len(test_results)
        
        print(f"\nファイルダイアログ統合: {passed}/{total} ({passed/total*100:.1f}%)")
        return passed == total
        
    except Exception as e:
        print(f"❌ ファイルダイアログ統合テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("TextBoxControl入力フィルター統合テスト開始\n")
    
    results = []
    results.append(test_normal_mode())
    results.append(test_filename_safe_mode())
    results.append(test_numeric_only_mode())
    results.append(test_filter_switching())
    results.append(test_file_dialog_integration())
    
    # 結果サマリー
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 70)
    print(f"📊 総合テスト結果: {passed}/{total} ({passed/total*100:.1f}%) 成功")
    
    if passed == total:
        print("🎉 すべての入力フィルターテストが成功しました！")
        print("\n📋 実装完了機能:")
        print("  ✅ Normal Mode: すべての印字可能文字入力")
        print("  ✅ Filename Safe Mode: ファイル名安全文字のみ")
        print("  ✅ Numeric Only Mode: 数値文字のみ") 
        print("  ✅ 動的フィルター切り替え")
        print("  ✅ FileLoadDialog統合")
        
        print("\n🚀 TextBoxControlは3つの入力モードを完全サポートします！")
        print("   - パラメータ1つでモード切り替え可能")
        print("   - 既存コードへの影響最小")
        print("   - 将来拡張が容易")
        
    else:
        print("⚠️  一部のテストが失敗しました。")
        print("詳細なエラー内容を確認して修正してください。")
    
    print("=" * 70)
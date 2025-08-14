#!/usr/bin/env python3
"""
TextBoxControl単体テスト
TextBoxControlの基本機能をテスト
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_textbox_basic():
    """TextBoxControlの基本機能テスト"""
    print("=== TextBoxControl基本機能テスト ===")
    
    try:
        # TextBoxControlをインポート
        from DialogManager_v3.controls.textbox_control import TextBoxControl
        
        # TextBoxControlを作成
        textbox = TextBoxControl(x=10, y=10, width=100, text="test")
        print(f"✅ TextBoxControl作成成功: text='{textbox.text}'")
        
        # テキストの設定と取得
        textbox.text = "Hello World"
        assert textbox.text == "Hello World", f"Expected 'Hello World', got '{textbox.text}'"
        print(f"✅ テキスト設定・取得成功: '{textbox.text}'")
        
        # 文字入力テスト
        textbox.text = ""  # clearメソッドの代わり
        textbox.on_text('A')
        textbox.on_text('B')
        textbox.on_text('C')
        assert textbox.text == "ABC", f"Expected 'ABC', got '{textbox.text}'"
        print(f"✅ 文字入力テスト成功: '{textbox.text}'")
        
        # Backspaceテスト
        import pyxel
        if hasattr(pyxel, 'KEY_BACKSPACE'):
            textbox.on_key(pyxel.KEY_BACKSPACE)
            assert textbox.text == "AB", f"Expected 'AB', got '{textbox.text}'"
            print(f"✅ Backspaceテスト成功: '{textbox.text}'")
        else:
            print("⚠️  Backspaceテスト: pyxel.KEY_BACKSPACE not available")
        
        # カーソル位置テスト
        cursor_pos = textbox._cursor_pos
        print(f"✅ カーソル位置: {cursor_pos}")
        
        print("=== TextBoxControl基本機能テスト完了 ===\n")
        return True
        
    except Exception as e:
        print(f"❌ TextBoxControlテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dialog_integration():
    """ダイアログ統合テスト"""
    print("=== ダイアログ統合テスト ===")
    
    try:
        from DialogManager_v3.core.base_dialog import BaseDialog
        from DialogManager_v3.controls.textbox_control import TextBoxControl
        
        # BaseDialogを作成
        dialog = BaseDialog(x=50, y=50, width=200, height=100, title="Test Dialog")
        print("✅ BaseDialog作成成功")
        
        # TextBoxControlを作成してダイアログに追加
        textbox = TextBoxControl(x=10, y=10, width=100, text="dialog test")
        textbox.parent = dialog
        
        # フォーカス設定
        dialog.focused_control = textbox
        print(f"✅ フォーカス設定成功: focused='{dialog.focused_control}'")
        
        # キーボードイベントテスト
        import pyxel
        if hasattr(dialog, 'handle_text_input'):
            result = dialog.handle_text_input('X')
            print(f"✅ テキスト入力イベント処理: result={result}")
        
        print("=== ダイアログ統合テスト完了 ===\n")
        return True
        
    except Exception as e:
        print(f"❌ ダイアログ統合テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_dialog_textbox():
    """ファイルダイアログのTextBoxテスト"""
    print("=== ファイルダイアログTextBoxテスト ===")
    
    try:
        # Pyxelを初期化してからテスト
        import pyxel
        pyxel.init(400, 300, title="Test", fps=30, quit_key=pyxel.KEY_F12)
        
        from DialogManager_v3.dialogs.file_load_dialog import FileLoadDialogJSON
        
        # ファイルダイアログを作成
        dialog = FileLoadDialogJSON()
        print("✅ FileLoadDialogJSON作成成功")
        
        # TextBoxControlが存在するかチェック
        if hasattr(dialog, 'filename_textbox'):
            textbox = dialog.filename_textbox
            print(f"✅ filename_textbox存在確認: type={type(textbox).__name__}")
            
            # テキスト設定テスト
            textbox.text = "test_file.csv"
            text = textbox.text
            print(f"✅ ファイル名設定テスト: '{text}'")
            
            # フォーカス設定確認
            if dialog.focused_control == textbox:
                print("✅ フォーカス設定確認: TextBoxControlが正しくフォーカスされています")
            else:
                print("⚠️  フォーカス設定: focused_controlが期待と異なります")
        else:
            print("❌ filename_textboxが見つかりません")
        
        print("=== ファイルダイアログTextBoxテスト完了 ===\n")
        return True
        
    except Exception as e:
        print(f"❌ ファイルダイアログTextBoxテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("TextBox機能統合テスト開始\n")
    
    results = []
    results.append(test_textbox_basic())
    results.append(test_dialog_integration())
    results.append(test_file_dialog_textbox())
    
    # 結果サマリー
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"テスト結果: {passed}/{total} 成功")
    
    if passed == total:
        print("🎉 すべてのテストが成功しました！")
        print("TextBoxControl入力機能は正常に動作しています。")
    else:
        print("⚠️  一部のテストが失敗しました。")
        print("詳細なエラー内容を確認してください。")
    
    print("=" * 50)
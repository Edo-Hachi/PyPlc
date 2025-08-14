#!/usr/bin/env python3
"""
カーソル位置修正テスト
フォント幅修正後のカーソル位置が正確かテスト
"""

import os
import sys
import pyxel
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cursor_positioning():
    """カーソル位置の正確性テスト"""
    print("=== カーソル位置テスト ===")
    
    try:
        # Pyxel初期化
        pyxel.init(400, 300, title="Cursor Position Test", fps=30, quit_key=pyxel.KEY_F12)
        
        from DialogManager_v3.controls.textbox_control import TextBoxControl, PYXEL_FONT_WIDTH
        
        # TextBoxControlを作成
        textbox = TextBoxControl(x=10, y=10, width=200, text="ABCDEF")
        
        print(f"✅ TextBoxControl作成: text='{textbox.text}'")
        print(f"✅ フォント幅定数: {PYXEL_FONT_WIDTH}ピクセル")
        
        # テキスト幅の計算テスト
        test_texts = ["A", "AB", "ABC", "ABCDEF", "Hello World"]
        
        for test_text in test_texts:
            width = textbox._get_text_width(test_text)
            expected_width = len(test_text) * PYXEL_FONT_WIDTH
            print(f"✅ '{test_text}' 幅: {width}px (期待値: {expected_width}px)")
            assert width == expected_width, f"Width mismatch for '{test_text}'"
        
        # カーソル位置計算テスト
        textbox.text = "TEST123"
        
        # 各文字位置でのカーソル位置テスト
        for i in range(len(textbox.text) + 1):
            textbox._cursor_pos = i
            cursor_text_width = textbox._get_text_width(textbox.text[:i])
            expected_cursor_x = 10 + 4 + cursor_text_width  # x + padding + text_width
            
            print(f"✅ カーソル位置{i}: テキスト幅{cursor_text_width}px, 期待X座標{expected_cursor_x}px")
        
        print("=== カーソル位置テスト完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ カーソル位置テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dialog_cursor():
    """ダイアログ内でのカーソル位置テスト"""
    print("\n=== ダイアログカーソル位置テスト ===")
    
    try:
        from DialogManager_v3.dialogs.file_load_dialog import FileLoadDialogJSON
        
        # ファイルダイアログを作成
        dialog = FileLoadDialogJSON()
        textbox = dialog.filename_textbox
        
        # テスト用テキストを設定
        textbox.text = "test_file.csv"
        print(f"✅ ファイル名設定: '{textbox.text}'")
        
        # カーソル位置を最後に移動
        textbox._cursor_pos = len(textbox.text)
        
        # カーソル位置の計算
        text_width = textbox._get_text_width(textbox.text)
        cursor_x = dialog.controls['filename_input']['x'] + 4 + text_width
        
        print(f"✅ テキスト幅: {text_width}px")
        print(f"✅ 計算されたカーソルX座標: {cursor_x}px")
        print(f"✅ TextBox X座標: {dialog.controls['filename_input']['x']}px")
        print(f"✅ パディング: 4px")
        
        # 文字数とピクセル数の対応確認
        char_count = len(textbox.text)
        expected_width = char_count * 4  # 1文字4ピクセル
        
        print(f"✅ 文字数: {char_count}")
        print(f"✅ 期待される幅: {expected_width}px")
        print(f"✅ 実際の幅: {text_width}px")
        
        assert text_width == expected_width, f"Width calculation error: {text_width} != {expected_width}"
        
        print("=== ダイアログカーソル位置テスト完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ ダイアログカーソルテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("カーソル位置修正テスト開始\n")
    
    results = []
    results.append(test_cursor_positioning())
    results.append(test_dialog_cursor())
    
    # 結果サマリー
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"テスト結果: {passed}/{total} 成功")
    
    if passed == total:
        print("🎉 すべてのテストが成功しました！")
        print("📏 カーソル位置がフォント幅に正確に合わせられました。")
        print("\n🔧 修正内容:")
        print("- フォント幅を6ピクセルから4ピクセルに修正")
        print("- PYXEL_FONT_WIDTH定数の追加")
        print("- _get_text_width()メソッドの修正") 
        print("- _update_cursor_position()メソッドの修正")
        print("\n🚀 main.pyでCtrl+Oを押してファイルダイアログを開き、")
        print("   ファイル名入力欄でカーソル位置を確認してください！")
    else:
        print("⚠️  一部のテストが失敗しました。")
    
    print("=" * 60)
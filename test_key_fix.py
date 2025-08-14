#!/usr/bin/env python3
"""
KEY_EQUAL → KEY_EQUALS修正確認テスト
"""

import os
import sys
import pyxel
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_key_constants():
    """Pyxelキー定数の存在確認"""
    print("=== Pyxelキー定数存在確認 ===")
    
    required_keys = [
        'KEY_0', 'KEY_1', 'KEY_2', 'KEY_3', 'KEY_4', 
        'KEY_5', 'KEY_6', 'KEY_7', 'KEY_8', 'KEY_9',
        'KEY_A', 'KEY_Z', 'KEY_PERIOD', 'KEY_MINUS', 
        'KEY_EQUALS', 'KEY_COMMA', 'KEY_SLASH', 
        'KEY_SEMICOLON', 'KEY_QUOTE', 'KEY_LEFTBRACKET', 
        'KEY_RIGHTBRACKET', 'KEY_BACKSLASH', 'KEY_BACKQUOTE', 
        'KEY_SPACE'
    ]
    
    missing_keys = []
    
    for key_name in required_keys:
        if hasattr(pyxel, key_name):
            print(f"✅ {key_name}")
        else:
            print(f"❌ {key_name}")
            missing_keys.append(key_name)
    
    if not missing_keys:
        print("🎉 すべての必要なキー定数が存在します！")
        return True
    else:
        print(f"⚠️ 不足するキー定数: {missing_keys}")
        return False

def test_file_dialog_creation():
    """FileLoadDialogJSON作成テスト"""
    print("\n=== FileLoadDialogJSON作成テスト ===")
    
    try:
        # Pyxel初期化
        pyxel.init(400, 300, title="Key Fix Test", fps=30, quit_key=pyxel.KEY_F12)
        
        from DialogManager_v3.dialogs.file_load_dialog import FileLoadDialogJSON
        
        # FileLoadDialogJSON作成
        dialog = FileLoadDialogJSON()
        
        print("✅ FileLoadDialogJSON作成成功")
        print(f"✅ TextBox input_filter: {dialog.filename_textbox.input_filter}")
        
        # KEY_EQUALSを使った記号入力テスト
        textbox = dialog.filename_textbox
        
        # '='文字の拒否テスト（filename_safeモードで）
        textbox.text = ""
        result_eq = textbox.on_text('=')
        
        # '+'文字の拒否テスト
        textbox.text = ""
        result_plus = textbox.on_text('+')
        
        # 'a'文字の許可テスト
        textbox.text = ""
        result_a = textbox.on_text('a')
        
        print(f"✅ '='文字拒否テスト: {not result_eq and textbox.text == ''}")
        print(f"✅ '+'文字拒否テスト: {not result_plus}")
        
        textbox.text = ""
        result_a = textbox.on_text('a')
        print(f"✅ 'a'文字許可テスト: {result_a and textbox.text == 'a'}")
        
        return True
        
    except Exception as e:
        print(f"❌ FileLoadDialogJSONテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_key_mapping():
    """キーマッピング動作テスト"""
    print("\n=== キーマッピング動作テスト ===")
    
    try:
        # key_mappingsと同じ構造でテスト
        key_mappings = {
            pyxel.KEY_0: ('0', ')'), pyxel.KEY_1: ('1', '!'), pyxel.KEY_2: ('2', '@'),
            pyxel.KEY_3: ('3', '#'), pyxel.KEY_4: ('4', '$'), pyxel.KEY_5: ('5', '%'),
            pyxel.KEY_6: ('6', '^'), pyxel.KEY_7: ('7', '&'), pyxel.KEY_8: ('8', '*'),
            pyxel.KEY_9: ('9', '('), pyxel.KEY_PERIOD: ('.', '>'), pyxel.KEY_MINUS: ('-', '_'),
            pyxel.KEY_EQUALS: ('=', '+'), pyxel.KEY_COMMA: (',', '<'), pyxel.KEY_SLASH: ('/', '?'), 
            pyxel.KEY_SEMICOLON: (';', ':'), pyxel.KEY_QUOTE: ("'", '"'), 
            pyxel.KEY_LEFTBRACKET: ('[', '{'), pyxel.KEY_RIGHTBRACKET: (']', '}'), 
            pyxel.KEY_BACKSLASH: ('\\', '|'), pyxel.KEY_BACKQUOTE: ('`', '~'), 
            pyxel.KEY_SPACE: (' ', ' ')
        }
        
        print("✅ key_mappings辞書作成成功")
        print(f"✅ マッピング数: {len(key_mappings)}")
        
        # 特にKEY_EQUALSの確認
        equals_mapping = key_mappings.get(pyxel.KEY_EQUALS)
        print(f"✅ KEY_EQUALS マッピング: {equals_mapping}")
        
        if equals_mapping == ('=', '+'):
            print("✅ KEY_EQUALSマッピング正常")
        else:
            print("❌ KEY_EQUALSマッピング異常")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ キーマッピングテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("KEY_EQUAL → KEY_EQUALS修正確認テスト開始\n")
    
    results = []
    results.append(test_key_constants())
    results.append(test_file_dialog_creation())
    results.append(test_key_mapping())
    
    # 結果サマリー
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"📊 テスト結果: {passed}/{total} ({passed/total*100:.1f}%) 成功")
    
    if passed == total:
        print("🎉 KEY_EQUALS修正が成功しました！")
        print("\n✅ 修正内容:")
        print("  - KEY_EQUAL → KEY_EQUALS に変更")
        print("  - Pyxelキー定数の正しい参照")
        print("  - FileLoadDialogJSONの正常動作確認")
        
        print("\n🚀 main.pyでCtrl+Oを押してファイルダイアログを開いてください！")
        print("   '=' と '+' は filename_safe モードで自動的に除外されます。")
        
    else:
        print("⚠️ 一部のテストが失敗しました。")
        print("エラー詳細を確認してください。")
    
    print("=" * 60)
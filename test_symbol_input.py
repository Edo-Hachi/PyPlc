#!/usr/bin/env python3
"""
拡張記号入力テスト
追加された記号入力機能のテスト
"""

import os
import sys
import pyxel
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_symbol_input():
    """拡張記号入力のテスト"""
    print("=== 拡張記号入力テスト ===")
    
    try:
        # Pyxel初期化
        pyxel.init(400, 300, title="Symbol Input Test", fps=30, quit_key=pyxel.KEY_F12)
        
        from DialogManager_v3.dialogs.file_load_dialog import FileLoadDialogJSON
        
        # ファイルダイアログを作成
        dialog = FileLoadDialogJSON()
        textbox = dialog.filename_textbox
        
        print(f"✅ FileLoadDialogJSON作成: TextBox初期化完了")
        
        # テスト用の記号とキーのマッピング
        symbol_tests = [
            # 基本記号（既存）
            ('a', 'a'),
            ('A', 'A'),  # Shift+A
            ('1', '1'),
            ('!', '!'),  # Shift+1
            ('.', '.'),
            ('>', '>'),  # Shift+.
            ('-', '-'),
            ('_', '_'),  # Shift+-
            (' ', ' '),  # スペース
            (',', ','),
            ('<', '<'),  # Shift+,
            ('=', '='),
            ('+', '+'),  # Shift+=
            
            # 新追加記号
            ('/', '/'),
            ('?', '?'),  # Shift+/
            (';', ';'),
            (':', ':'),  # Shift+;
            ("'", "'"),
            ('"', '"'),  # Shift+'
            ('[', '['),
            ('{', '{'),  # Shift+[
            (']', ']'),
            ('}', '}'),  # Shift+]
            ('\\', '\\'),
            ('|', '|'),  # Shift+\
            ('`', '`'),
            ('~', '~'),  # Shift+`
        ]
        
        # 各記号の入力テスト（シミュレーション）
        test_results = []
        
        for symbol, expected in symbol_tests:
            # TextBoxControlに直接文字を入力してテスト
            textbox.text = ""  # リセット
            
            # on_textメソッドを直接呼び出してテスト
            if hasattr(textbox, 'on_text'):
                result = textbox.on_text(symbol)
                if result and textbox.text == expected:
                    print(f"✅ '{symbol}' -> '{expected}' 入力成功")
                    test_results.append(True)
                else:
                    print(f"❌ '{symbol}' -> '{expected}' 入力失敗 (実際: '{textbox.text}')")
                    test_results.append(False)
            else:
                print(f"❌ on_textメソッドが見つかりません")
                test_results.append(False)
        
        # ファイル名例のテスト
        filename_examples = [
            "test_file.csv",
            "data-2024.txt", 
            "config_backup.json",
            "report[v1.0].doc",
            "script{final}.py",
            "path/to/file.dat",
            "query?param=value",
            "list:items;data",
            'text"with"quotes.txt',
            "mixed~symbols@#$.log"
        ]
        
        print("\n=== ファイル名入力例テスト ===")
        for filename in filename_examples:
            textbox.text = ""
            
            # 1文字ずつ入力テスト
            success = True
            for char in filename:
                if hasattr(textbox, 'on_text'):
                    if not textbox.on_text(char):
                        success = False
                        break
                else:
                    success = False
                    break
            
            if success and textbox.text == filename:
                print(f"✅ '{filename}' 入力成功")
                test_results.append(True)
            else:
                print(f"❌ '{filename}' 入力失敗 (実際: '{textbox.text}')")
                test_results.append(False)
        
        # 結果サマリー
        passed = sum(test_results)
        total = len(test_results)
        
        print(f"\n=== テスト結果 ===")
        print(f"成功: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 すべての記号入力テストが成功しました！")
            return True
        else:
            print("⚠️ 一部の記号入力テストが失敗しました")
            return False
        
    except Exception as e:
        print(f"❌ 記号入力テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keyboard_coverage():
    """キーボードカバレッジテスト"""
    print("\n=== キーボードカバレッジ確認 ===")
    
    try:
        # Pyxelのキー定数の存在確認
        key_constants = [
            'KEY_SLASH',       # /
            'KEY_SEMICOLON',   # ;
            'KEY_QUOTE',       # '
            'KEY_LEFTBRACKET',  # [
            'KEY_RIGHTBRACKET', # ]
            'KEY_BACKSLASH',   # \
            'KEY_BACKQUOTE'    # `
        ]
        
        coverage_results = []
        
        for key_name in key_constants:
            if hasattr(pyxel, key_name):
                print(f"✅ {key_name} 定数存在確認")
                coverage_results.append(True)
            else:
                print(f"❌ {key_name} 定数が見つかりません")
                coverage_results.append(False)
        
        passed = sum(coverage_results)
        total = len(coverage_results)
        
        print(f"\nキーボードカバレッジ: {passed}/{total} ({passed/total*100:.1f}%)")
        
        return passed == total
        
    except Exception as e:
        print(f"❌ カバレッジテストエラー: {e}")
        return False

if __name__ == "__main__":
    print("拡張記号入力テスト開始\n")
    
    results = []
    results.append(test_symbol_input())
    results.append(test_keyboard_coverage())
    
    # 結果サマリー
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"総合テスト結果: {passed}/{total} 成功")
    
    if passed == total:
        print("🎉 すべての拡張記号入力テストが成功しました！")
        print("\n📝 対応記号一覧:")
        print("基本: A-Z, a-z, 0-9, スペース")
        print("記号: . - _ , = + / ? ; : ' \" [ { ] } \\ | ` ~")
        print("Shift記号: ! @ # $ % ^ & * ( ) < > + ? : \" { } | ~")
        print("\n🚀 ファイル名入力で豊富な記号が使用可能になりました！")
    else:
        print("⚠️ 一部のテストが失敗しました。")
        print("Pyxelのキー定数が不足している可能性があります。")
    
    print("=" * 60)
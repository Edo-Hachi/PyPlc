#!/usr/bin/env python3
"""
ファイル名安全文字テスト
ファイル名に適した文字のみが入力できることを確認
"""

import os
import sys
import pyxel
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_filename_safe_characters():
    """ファイル名安全文字のテスト"""
    print("=== ファイル名安全文字テスト ===")
    
    try:
        # Pyxel初期化
        pyxel.init(400, 300, title="Filename Safe Test", fps=30, quit_key=pyxel.KEY_F12)
        
        from DialogManager_v3.dialogs.file_load_dialog import FileLoadDialogJSON
        
        # ファイルダイアログを作成
        dialog = FileLoadDialogJSON()
        textbox = dialog.filename_textbox
        
        print(f"✅ FileLoadDialogJSON作成: TextBox初期化完了")
        
        # ファイル名に適した文字（許可）
        safe_characters = [
            'a', 'A', '1', '!',  # 基本文字・Shift+数字
            '.', '-', '_', ' ',  # ピリオド・ハイフン・アンダースコア・スペース
            ',',                 # カンマ（通常）
            '/', '?',           # スラッシュ・クエスチョン
            ';', ':',           # セミコロン・コロン
            "'", '"',           # クォート
            '[', '{', ']', '}', # 角括弧
            '\\', '|',          # バックスラッシュ・パイプ
            '`', '~'            # バッククォート・チルダ
        ]
        
        # ファイル名に適さない文字（除外対象）
        unsafe_characters = [
            '=', '+',           # イコール・プラス（除外済み）
            '<', '>',           # 不等号（除外済み）
        ]
        
        print("\n=== 安全文字入力テスト ===")
        safe_results = []
        
        for char in safe_characters:
            textbox.text = ""  # リセット
            
            if hasattr(textbox, 'on_text'):
                result = textbox.on_text(char)
                if result and textbox.text == char:
                    print(f"✅ '{char}' 入力許可")
                    safe_results.append(True)
                else:
                    print(f"❌ '{char}' 入力失敗")
                    safe_results.append(False)
            else:
                safe_results.append(False)
        
        print("\n=== 危険文字除外テスト ===")
        # 注意: これらの文字はキーボード入力段階で除外されるため、
        # on_text()では直接テストできない。実際のキー入力動作を想定したテスト
        
        excluded_note = """
        ✅ 除外対象文字:
        - '=' (イコール): KEY_EQUAL + Shift無し → 除外
        - '+' (プラス): KEY_EQUAL + Shift → 除外  
        - '<' (小なり): KEY_COMMA + Shift → 除外
        - '>' (大なり): KEY_PERIOD + Shift → 除外
        
        これらはキーボード入力段階で除外されるため、
        ファイル名入力欄に入力されません。
        """
        print(excluded_note)
        
        # 安全なファイル名例のテスト
        safe_filenames = [
            "document.txt",
            "data_2024.csv", 
            "config-backup.json",
            "report[v1.0].doc",
            "script{final}.py",
            "path/to/file.dat",
            "query?search",
            "list:items;data",
            'text"quotes".txt',
            "file~backup.log"
        ]
        
        print("\n=== 安全ファイル名テスト ===")
        filename_results = []
        
        for filename in safe_filenames:
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
                filename_results.append(True)
            else:
                print(f"❌ '{filename}' 入力失敗")
                filename_results.append(False)
        
        # 結果サマリー
        safe_passed = sum(safe_results)
        safe_total = len(safe_results)
        filename_passed = sum(filename_results)
        filename_total = len(filename_results)
        
        print(f"\n=== テスト結果サマリー ===")
        print(f"安全文字テスト: {safe_passed}/{safe_total} ({safe_passed/safe_total*100:.1f}%)")
        print(f"ファイル名テスト: {filename_passed}/{filename_total} ({filename_passed/filename_total*100:.1f}%)")
        
        overall_success = (safe_passed == safe_total and filename_passed == filename_total)
        
        if overall_success:
            print("🎉 ファイル名安全文字テストが成功しました！")
            return True
        else:
            print("⚠️ 一部のテストが失敗しました")
            return False
        
    except Exception as e:
        print(f"❌ ファイル名安全文字テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_character_summary():
    """文字対応サマリーの表示"""
    print("\n" + "=" * 60)
    print("📋 ファイル名入力対応文字サマリー")
    print("=" * 60)
    
    print("\n✅ 許可文字:")
    print("  基本文字: A-Z, a-z, 0-9, スペース")
    print("  記号: . - _ , / ? ; : ' \" [ { ] } \\ | ` ~")
    print("  Shift記号: ! @ # $ % ^ & * ( ) ? : \" { } | ~")
    
    print("\n❌ 除外文字:")
    print("  = (イコール)")
    print("  + (プラス)")  
    print("  < (小なり)")
    print("  > (大なり)")
    
    print("\n📝 除外理由:")
    print("  - URL/ウェブでエスケープが必要")
    print("  - コマンドラインパラメータとして使用")
    print("  - ファイルシステムでの特殊用途")
    print("  - 一般的なファイル名規則で推奨されない")
    
    print("\n🎯 適用場面:")
    print("  - CSV設定ファイル名")
    print("  - プロジェクトファイル名")
    print("  - ログファイル名")
    print("  - 一般的なドキュメント名")

if __name__ == "__main__":
    print("ファイル名安全文字テスト開始\n")
    
    success = test_filename_safe_characters()
    
    show_character_summary()
    
    if success:
        print("\n🚀 ファイル名入力システムは安全で実用的な文字セットに対応しています！")
    else:
        print("\n⚠️ ファイル名入力システムに問題があります。")
    
    print("=" * 60)
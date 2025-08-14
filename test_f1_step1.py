#!/usr/bin/env python3
"""
Phase F1 Step 1: キーマッピング追加テスト
TextBoxControlにキーマッピング辞書が正しく追加されたか確認
"""

import os
import sys
import pyxel
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_key_mappings_creation():
    """キーマッピング作成テスト"""
    print("=== Step 1: キーマッピング作成テスト ===")
    
    try:
        # Pyxel初期化
        pyxel.init(400, 300, title="F1 Step1 Test", fps=30, quit_key=pyxel.KEY_F12)
        
        from DialogManager_v3.controls.textbox_control import TextBoxControl
        
        # TextBoxControl作成
        textbox = TextBoxControl(x=10, y=10, width=200)
        
        print("✅ TextBoxControl作成成功")
        
        # キーマッピング辞書の存在確認
        if hasattr(textbox, '_key_mappings'):
            print("✅ _key_mappings属性存在")
            mappings = textbox._key_mappings
            print(f"✅ キーマッピング数: {len(mappings)}")
            
            # 主要キーのマッピング確認
            test_keys = [
                (pyxel.KEY_0, ('0', ')')),
                (pyxel.KEY_1, ('1', '!')),
                (pyxel.KEY_A, None),  # 英字は含まれないはず
                (pyxel.KEY_EQUALS, ('=', '+')),
                (pyxel.KEY_SPACE, (' ', ' '))
            ]
            
            mapping_results = []
            for key, expected in test_keys:
                if key in mappings:
                    actual = mappings[key]
                    if expected is None:
                        print(f"❌ {key}: 予期しない存在 {actual}")
                        mapping_results.append(False)
                    elif actual == expected:
                        print(f"✅ {key}: 正しいマッピング {actual}")
                        mapping_results.append(True)
                    else:
                        print(f"❌ {key}: 間違ったマッピング {actual} (期待: {expected})")
                        mapping_results.append(False)
                else:
                    if expected is None:
                        print(f"✅ {key}: 正しく除外")
                        mapping_results.append(True)
                    else:
                        print(f"❌ {key}: 見つからない (期待: {expected})")
                        mapping_results.append(False)
            
            # 期待されるキー数のチェック
            expected_count = 22  # FileLoadDialogから移植した数
            actual_count = len(mappings)
            
            if actual_count == expected_count:
                print(f"✅ キー数正確: {actual_count}")
                mapping_results.append(True)
            else:
                print(f"❌ キー数不正確: {actual_count} (期待: {expected_count})")
                mapping_results.append(False)
            
            passed = sum(mapping_results)
            total = len(mapping_results)
            
            print(f"\nキーマッピングテスト: {passed}/{total} ({passed/total*100:.1f}%)")
            return passed == total
            
        else:
            print("❌ _key_mappings属性が見つかりません")
            return False
        
    except Exception as e:
        print(f"❌ Step 1 テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_key_mappings_content():
    """キーマッピング内容詳細テスト"""
    print("\n=== キーマッピング内容詳細確認 ===")
    
    try:
        from DialogManager_v3.controls.textbox_control import TextBoxControl
        
        textbox = TextBoxControl(x=10, y=10, width=200)
        mappings = textbox._key_mappings
        
        # 全マッピングの表示
        print("📋 全キーマッピング:")
        for key, (normal, shift) in mappings.items():
            key_name = [attr for attr in dir(pyxel) if attr.startswith('KEY_') and getattr(pyxel, attr) == key]
            key_display = key_name[0] if key_name else f"KEY_{key}"
            print(f"  {key_display}: '{normal}' / '{shift}'")
        
        # 必須キーの確認
        required_keys = [
            pyxel.KEY_0, pyxel.KEY_1, pyxel.KEY_2, pyxel.KEY_3, pyxel.KEY_4,
            pyxel.KEY_5, pyxel.KEY_6, pyxel.KEY_7, pyxel.KEY_8, pyxel.KEY_9,
            pyxel.KEY_SPACE, pyxel.KEY_PERIOD, pyxel.KEY_MINUS, pyxel.KEY_EQUALS
        ]
        
        missing_keys = []
        for key in required_keys:
            if key not in mappings:
                missing_keys.append(key)
        
        if not missing_keys:
            print("✅ 必須キーすべて存在")
            return True
        else:
            print(f"❌ 不足キー: {missing_keys}")
            return False
        
    except Exception as e:
        print(f"❌ 内容確認テストエラー: {e}")
        return False

if __name__ == "__main__":
    print("Phase F1 Step 1: キーマッピング追加テスト開始\n")
    
    results = []
    results.append(test_key_mappings_creation())
    results.append(test_key_mappings_content())
    
    # 結果サマリー
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"📊 Step 1 テスト結果: {passed}/{total} ({passed/total*100:.1f}%) 成功")
    
    if passed == total:
        print("🎉 Step 1完了: キーマッピング辞書が正常に追加されました！")
        print("\n✅ 完了内容:")
        print("  - _key_mappings属性追加")
        print("  - 22個のキーマッピング作成")
        print("  - 数字・記号・特殊文字の対応")
        print("  - Shift文字変換対応")
        
        print("\n🚀 次のステップ: on_keyメソッドで文字変換処理統合")
        
    else:
        print("⚠️ Step 1で問題が発生しました。")
        print("修正が必要です。")
    
    print("=" * 60)
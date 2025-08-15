"""
DialogManager v4 - JSON定義検証テスト

JSON定義ファイルの妥当性・スキーマ準拠性テスト
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


def test_json_file_validity(json_file_path):
    """JSON ファイルの基本妥当性テスト"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ {os.path.basename(json_file_path)}: JSON構文正常")
        return True, data
    except json.JSONDecodeError as e:
        print(f"❌ {os.path.basename(json_file_path)}: JSON構文エラー - {e}")
        return False, None
    except FileNotFoundError:
        print(f"❌ {os.path.basename(json_file_path)}: ファイルが見つかりません")
        return False, None


def test_dialog_structure(dialog_data, filename):
    """ダイアログ構造の基本検証"""
    print(f"\n--- {filename} 構造検証 ---")
    
    # 必須フィールドチェック
    required_fields = ["dialog", "controls"]
    for field in required_fields:
        if field not in dialog_data:
            print(f"❌ 必須フィールド '{field}' が不足")
            return False
        print(f"✅ 必須フィールド '{field}' 存在")
    
    # ダイアログプロパティチェック
    dialog = dialog_data["dialog"]
    dialog_required = ["title", "width", "height"]
    for field in dialog_required:
        if field not in dialog:
            print(f"❌ ダイアログの必須プロパティ '{field}' が不足")
            return False
        print(f"✅ ダイアログプロパティ '{field}': {dialog[field]}")
    
    # コントロール基本チェック
    controls = dialog_data["controls"]
    print(f"✅ コントロール数: {len(controls)}")
    
    for i, control in enumerate(controls):
        control_required = ["type", "id", "x", "y"]
        for field in control_required:
            if field not in control:
                print(f"❌ コントロール{i}の必須プロパティ '{field}' が不足")
                return False
        print(f"✅ コントロール{i}: {control['type']} '{control['id']}'")
    
    return True


def test_csv_default_setting():
    """CSVデフォルト設定テスト（重要なユースケース）"""
    print("\n=== CSVデフォルト設定テスト ===")
    
    # file_load.json読み込み
    file_path = "dialogs/file_load.json"
    valid, data = test_json_file_validity(file_path)
    
    if not valid:
        return False
    
    # filter_dropdownのselected_indexチェック
    for control in data["controls"]:
        if control.get("id") == "filter_dropdown":
            if "selected_index" in control:
                selected_index = control["selected_index"]
                items = control.get("items", [])
                
                print(f"✅ filter_dropdown selected_index: {selected_index}")
                if selected_index < len(items):
                    selected_item = items[selected_index]
                    print(f"✅ 選択されるアイテム: '{selected_item}'")
                    
                    if "CSV" in selected_item:
                        print("🎯 CSVデフォルト設定: 正常動作")
                        return True
                    else:
                        print("❌ CSVがデフォルト選択されていません")
                        return False
                else:
                    print("❌ selected_indexが範囲外です")
                    return False
            else:
                print("❌ selected_indexが設定されていません")
                return False
    
    print("❌ filter_dropdownが見つかりません")
    return False


def test_event_action_consistency():
    """イベント・アクション整合性テスト"""
    print("\n=== イベント・アクション整合性テスト ===")
    
    file_path = "dialogs/file_load.json"
    valid, data = test_json_file_validity(file_path)
    
    if not valid:
        return False
    
    events = data.get("events", {})
    actions = data.get("actions", {})
    
    print(f"✅ イベント定義数: {len(events)}")
    print(f"✅ アクション定義数: {len(actions)}")
    
    # イベントに対応するアクションが存在するかチェック
    for event_key, action_name in events.items():
        if action_name in actions:
            print(f"✅ {event_key} → {action_name} (対応アクション存在)")
        else:
            print(f"❌ {event_key} → {action_name} (対応アクションなし)")
            return False
    
    # 未使用アクションのチェック
    used_actions = set(events.values())
    all_actions = set(actions.keys())
    unused_actions = all_actions - used_actions
    
    if unused_actions:
        print(f"⚠️ 未使用アクション: {unused_actions}")
    else:
        print("✅ 全アクションが使用されています")
    
    return True


def run_all_json_tests():
    """全JSON検証テスト実行"""
    print("🧪 DialogManager v4 JSON定義検証テスト開始\n")
    
    # テスト対象JSONファイル
    json_files = [
        "dialogs/simple_test.json",
        "dialogs/file_load.json",
        "schema/dialog_schema.json"
    ]
    
    all_success = True
    
    # 基本妥当性テスト
    print("=== JSON基本妥当性テスト ===")
    for json_file in json_files:
        valid, data = test_json_file_validity(json_file)
        if not valid:
            all_success = False
    
    # ダイアログ構造テスト
    dialog_files = ["dialogs/simple_test.json", "dialogs/file_load.json"]
    for dialog_file in dialog_files:
        valid, data = test_json_file_validity(dialog_file)
        if valid:
            if not test_dialog_structure(data, os.path.basename(dialog_file)):
                all_success = False
        else:
            all_success = False
    
    # 専用テスト
    if not test_csv_default_setting():
        all_success = False
    
    if not test_event_action_consistency():
        all_success = False
    
    # 結果出力
    if all_success:
        print("\n🎉 全JSON検証テスト完了: すべて正常")
        print("\n📋 検証完了項目:")
        print("  ✅ JSON構文妥当性")
        print("  ✅ ダイアログ構造妥当性")
        print("  ✅ CSVデフォルト設定")
        print("  ✅ イベント・アクション整合性")
    else:
        print("\n❌ JSON検証テストで問題が発見されました")
    
    return all_success


if __name__ == "__main__":
    success = run_all_json_tests()
    sys.exit(0 if success else 1)
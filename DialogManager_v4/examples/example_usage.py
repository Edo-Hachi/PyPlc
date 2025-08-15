"""
DialogManager v4 使用例

JSON完全定義主義に基づくダイアログの使用方法
DESIGN.md準拠の理想的な実装例
"""

from ..core.dialog_engine import DialogEngine


def example_simple_dialog():
    """シンプルダイアログの例"""
    
    # ✅ DESIGN.md準拠の理想的な使用方法
    dialog_engine = DialogEngine(debug=True)
    
    try:
        # JSON定義からダイアログを完全構築
        dialog = dialog_engine.create_dialog_from_json("../dialogs/simple_test.json")
        
        # 全ロジックがJSON定義済みなので、showのみで完結
        success, result = dialog.show_modal()
        
        if success:
            print(f"ダイアログ成功: {result}")
        else:
            print("ダイアログキャンセル")
            
    except Exception as e:
        print(f"エラー: {e}")


def example_file_dialog():
    """ファイルダイアログの例"""
    
    dialog_engine = DialogEngine(debug=True)
    
    try:
        # ファイルダイアログをJSON定義から構築
        dialog = dialog_engine.create_dialog_from_json("../dialogs/file_load.json")
        
        success, result = dialog.show_modal()
        
        if success and "selected_file" in result:
            file_path = result["selected_file"]
            print(f"選択されたファイル: {file_path}")
            
            # ファイル処理（ビジネスロジック）
            process_file(file_path)
        else:
            print("ファイル選択キャンセル")
            
    except Exception as e:
        print(f"エラー: {e}")


def process_file(file_path: str):
    """ファイル処理のビジネスロジック（JSON定義外）"""
    print(f"ファイル処理中: {file_path}")
    # 実際のファイル読み込み・処理ロジック


if __name__ == "__main__":
    print("=== DialogManager v4 使用例 ===")
    print("1. シンプルダイアログテスト")
    example_simple_dialog()
    
    print("\n2. ファイルダイアログテスト") 
    example_file_dialog()
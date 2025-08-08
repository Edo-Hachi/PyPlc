# PyPlc Ver3 - 新FileDialogManager統合管理システム
# 作成日: 2025-08-08
# 目的: 古いdialogs/FileDialogManagerと同等機能をJSON駆動で実現

from typing import Optional
from core.circuit_csv_manager import CircuitCsvManager
from DialogManager.file_save_dialog_json import show_file_save_dialog
from DialogManager.file_load_dialog_json import FileLoadDialogJSON


class NewFileDialogManager:
    """
    新FileDialogManagerシステム統合管理クラス
    
    目的:
    - 古いdialogs/FileDialogManagerと同等の機能をJSON駆動で実現
    - FileSaveDialogJSON、FileLoadDialogJSONを使用
    - CircuitCsvManagerとの完全統合
    """
    
    def __init__(self, csv_manager: CircuitCsvManager):
        """
        NewFileDialogManager初期化
        
        Args:
            csv_manager: CSV管理システムインスタンス
        """
        self.csv_manager = csv_manager
    
    def show_save_dialog(self, default_name: str = "my_circuit") -> bool:
        """
        新保存ダイアログ表示→CSV保存実行
        
        Args:
            default_name: デフォルトファイル名
            
        Returns:
            保存成功時True
        """
        print(f"[NewFileDialogManager] Showing save dialog (default: {default_name})")
        
        # 新FileSaveDialogJSONを使用
        success, filename = show_file_save_dialog(default_name)
        
        if success and filename:
            # CSVManager経由で保存実行（正しいメソッド名を使用）
            saved = self.csv_manager.save_circuit_to_csv(filename)
            if saved:
                print(f"[NewFileDialogManager] File saved successfully: {filename}")
                return True
            else:
                print("[NewFileDialogManager] Save failed: CSV manager error")
                return False
        else:
            print("[NewFileDialogManager] Save canceled by user")
            return False
    
    def show_load_dialog(self) -> bool:
        """
        新読み込みダイアログ表示→CSV読み込み実行
        
        Returns:
            読み込み成功時True
        """
        print("[NewFileDialogManager] Showing load dialog")
        
        # 新FileLoadDialogJSONを使用
        try:
            dialog = FileLoadDialogJSON()
            success, file_path = dialog.show_load_dialog()
            
            if success and file_path:
                # CSVManager経由で読み込み実行（正しいメソッド名を使用）
                loaded = self.csv_manager.load_circuit_from_csv(file_path)
                if loaded:
                    print(f"[NewFileDialogManager] File loaded successfully: {file_path}")
                    return True
                else:
                    print(f"[NewFileDialogManager] Load failed: CSV manager error")
                    return False
            else:
                print("[NewFileDialogManager] Load canceled by user")
                return False
                
        except Exception as e:
            print(f"[NewFileDialogManager] Load dialog error: {e}")
            return False
    
    def get_recent_files(self) -> list:
        """
        最近のファイル一覧を取得（将来拡張用）
        
        Returns:
            最近のファイルパスリスト
        """
        # Phase B2では基本実装、将来的に履歴管理機能を追加予定
        return []
    
    def is_file_dialog_active(self) -> bool:
        """
        ファイルダイアログがアクティブかどうかを確認
        
        Returns:
            ダイアログ表示中の場合True
        """
        # Phase B2では基本実装、将来的にダイアログ状態管理を追加予定
        return False
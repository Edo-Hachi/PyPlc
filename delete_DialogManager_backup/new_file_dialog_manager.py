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
        self.current_filename: Optional[str] = None  # 現在編集中のファイル名
    
    def show_save_dialog(self, default_name: Optional[str] = None) -> bool:
        """
        新保存ダイアログ表示→CSV保存実行
        現在編集中のファイル名を優先的にデフォルト値として使用
        
        Args:
            default_name: デフォルトファイル名（指定がない場合は現在のファイル名または"untitled.csv"）
            
        Returns:
            保存成功時True
        """
        # デフォルトファイル名の決定ロジック
        if default_name:
            effective_default = default_name
        elif self.current_filename:
            # 現在編集中のファイル名からパス部分を除去してファイル名のみ抽出
            import os
            filename_only = os.path.basename(self.current_filename)
            # 拡張子を除去
            effective_default = filename_only.replace('.csv', '') if filename_only.endswith('.csv') else filename_only
        else:
            # 新規エディット時
            effective_default = "untitled"
        
        print(f"[NewFileDialogManager] Showing save dialog (default: {effective_default})")
        
        # 新FileSaveDialogJSONを使用
        success, filename = show_file_save_dialog(effective_default)
        
        if success and filename:
            # CSVManager経由で保存実行（正しいメソッド名を使用）
            saved = self.csv_manager.save_circuit_to_csv(filename)
            if saved:
                # 保存成功時に現在のファイル名として記憶
                self.current_filename = filename if filename.endswith('.csv') else f"{filename}.csv"
                print(f"[NewFileDialogManager] File saved successfully: {self.current_filename}")
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
        読み込み成功時に現在のファイル名として記憶
        
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
                    # 読み込み成功時に現在のファイル名として記憶
                    self.current_filename = file_path
                    print(f"[NewFileDialogManager] File loaded successfully: {self.current_filename}")
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
    
    def get_current_filename(self) -> str:
        """
        現在編集中のファイル名を取得
        
        Returns:
            現在のファイル名、または新規時は"untitled.csv"
        """
        return self.current_filename if self.current_filename else "untitled.csv"
    
    def reset_current_filename(self) -> None:
        """
        現在のファイル名をリセット（新規作成時用）
        """
        self.current_filename = None
    
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
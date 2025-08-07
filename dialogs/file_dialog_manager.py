# PyPlc Ver3 File Dialog Manager
# 作成日: 2025-08-07
# 目標: ファイルダイアログ統合管理・CSV機能連携

from typing import Optional
from .file_dialogs import FileSaveDialog, FileLoadDialog
from core.circuit_csv_manager import CircuitCsvManager

class FileDialogManager:
    """
    ファイルダイアログ統合管理クラス
    保存・読み込みダイアログとCSV機能の橋渡し
    """
    
    def __init__(self, csv_manager: CircuitCsvManager):
        """
        Args:
            csv_manager: CSV管理システムインスタンス
        """
        self.csv_manager = csv_manager
        self.save_dialog = FileSaveDialog()
        self.load_dialog = FileLoadDialog()
        
    def show_save_dialog(self, default_name: str = "my_circuit") -> bool:
        """
        保存ダイアログ表示→CSV保存実行
        
        Args:
            default_name: デフォルトファイル名
            
        Returns:
            bool: 保存成功時True
        """
        try:
            # 保存ダイアログ表示
            success, filename = self.save_dialog.show(default_name)
            
            if success and filename:
                # CSV保存実行
                save_result = self.csv_manager.save_circuit_to_csv(filename)
                
                if save_result:
                    print(f"Circuit saved successfully: {filename}")
                else:
                    print(f"Failed to save circuit: {filename}")
                    
                return save_result
            else:
                print("Save operation cancelled by user")
                return False
                
        except Exception as e:
            print(f"Error in save dialog: {e}")
            return False
            
    def show_load_dialog(self) -> bool:
        """
        読み込みダイアログ表示→CSV読み込み実行
        
        Returns:
            bool: 読み込み成功時True
        """
        try:
            # 読み込みダイアログ表示
            success, filename = self.load_dialog.show()
            
            if success and filename:
                # CSV読み込み実行
                load_result = self.csv_manager.load_circuit_from_csv(filename)
                
                if load_result:
                    print(f"Circuit loaded successfully: {filename}")
                else:
                    print(f"Failed to load circuit: {filename}")
                    
                return load_result
            else:
                print("Load operation cancelled by user")
                return False
                
        except Exception as e:
            print(f"Error in load dialog: {e}")
            return False
            
    def get_recent_files(self, count: int = 5) -> list[str]:
        """
        最近使用したファイル一覧取得
        
        Args:
            count: 取得件数
            
        Returns:
            list[str]: ファイル名リスト（新しい順）
        """
        return self.csv_manager.get_available_csv_files()[:count]
        
    def delete_file(self, filename: str) -> bool:
        """
        指定ファイル削除
        
        Args:
            filename: 削除対象ファイル名
            
        Returns:
            bool: 削除成功時True
        """
        return self.csv_manager.delete_csv_file(filename)
        
    def get_file_count(self) -> int:
        """
        利用可能CSVファイル数取得
        
        Returns:
            int: ファイル数
        """
        return len(self.csv_manager.get_available_csv_files())
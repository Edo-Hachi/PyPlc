"""
PyPlc Ver3 - ファイル管理システム
CSV形式でのファイル保存・読み込み機能を提供

作成日: 2025-08-13
目的: ファイルダイアログとCSV管理の統合
"""

import os
from typing import Optional, Tuple
from DialogManager.dialogs.file_save_dialog import FileSaveDialogJSON
from DialogManager.dialogs.file_load_dialog import FileLoadDialogJSON


class FileManager:
    """
    ファイル保存・読み込み管理クラス
    
    機能:
    - CSV ファイルの保存・読み込み
    - ファイルダイアログとの統合
    - ファイル名の管理
    """
    
    def __init__(self, csv_manager):
        """
        FileManager初期化
        
        Args:
            csv_manager: CSV管理システム（CircuitCsvManager）
        """
        self.csv_manager = csv_manager
        self.current_filename = None
        self.base_directory = "."  # カレントディレクトリ
    
    def show_save_dialog(self) -> bool:
        """
        ファイル保存ダイアログを表示
        
        Returns:
            bool: 保存が成功した場合True
        """
        try:
            # デフォルトファイル名を生成
            default_name = self.current_filename or "my_circuit"
            if default_name.endswith('.csv'):
                default_name = default_name[:-4]  # .csv拡張子を除去
            
            # ファイル保存ダイアログを表示
            dialog = FileSaveDialogJSON(default_name)
            success, filename = dialog.show_save_dialog()
            
            if success and filename:
                # .csv拡張子を付加
                if not filename.endswith('.csv'):
                    filename = f"{filename}.csv"
                
                # CircuitCsvManagerを使用してファイル保存
                filepath = os.path.join(self.base_directory, filename)
                success = self.csv_manager.save_circuit_to_csv(filepath)
                
                if success:
                    self.current_filename = filename
                    print(f"[FileManager] File saved: {filepath}")
                    return True
                else:
                    print(f"[FileManager] Save failed: {filepath}")
                    return False
            
            return False
            
        except Exception as e:
            print(f"[FileManager] Save error: {e}")
            return False
    
    def show_load_dialog(self) -> bool:
        """
        ファイル読み込みダイアログを表示
        
        Returns:
            bool: 読み込みが成功した場合True
        """
        try:
            # ファイル読み込みダイアログを表示
            dialog = FileLoadDialogJSON()
            success, filepath = dialog.show_load_dialog()
            
            if success and filepath:
                # ファイルの存在確認
                if not os.path.exists(filepath):
                    print(f"[FileManager] File not found: {filepath}")
                    return False
                
                # CircuitCsvManagerを使用してファイル読み込み
                success = self.csv_manager.load_circuit_from_csv(filepath)
                
                if success:
                    self.current_filename = os.path.basename(filepath)
                    print(f"[FileManager] File loaded: {filepath}")
                    return True
                else:
                    print(f"[FileManager] Failed to load CSV: {filepath}")
                    return False
            
            return False
            
        except Exception as e:
            print(f"[FileManager] Load error: {e}")
            return False
    
    def get_current_filename(self) -> str:
        """
        現在のファイル名を取得
        
        Returns:
            str: 現在のファイル名、未設定の場合は"[Untitled]"
        """
        return self.current_filename or "[Untitled]"
    
    def set_current_filename(self, filename: str) -> None:
        """
        現在のファイル名を設定
        
        Args:
            filename: ファイル名
        """
        self.current_filename = filename
    
    def has_file(self) -> bool:
        """
        ファイルが設定されているかチェック
        
        Returns:
            bool: ファイルが設定されている場合True
        """
        return self.current_filename is not None
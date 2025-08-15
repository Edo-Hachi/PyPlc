"""
PyPlc Ver3 - DialogManager_v3用ファイル管理システム
既存FileManagerとの互換性を保ちつつ、DialogManager_v3の機能を活用

作成日: 2025-08-14
目的: 既存システムからDialogManager_v3への段階的移行
"""

import os
from typing import Optional, Tuple
from ..dialogs.file_load_dialog import FileLoadDialogJSON
from ..dialogs.file_save_dialog import FileSaveDialogJSON


class FileManagerV3:
    """
    DialogManager_v3用ファイル管理クラス
    既存FileManagerとの互換性を保持
    
    機能:
    - CSV ファイルの保存・読み込み
    - DialogManager_v3ファイルダイアログとの統合
    - ファイル名の管理
    """
    
    def __init__(self, csv_manager):
        """
        FileManagerV3初期化
        
        Args:
            csv_manager: CSV管理システム（CircuitCsvManager）
        """
        self.csv_manager = csv_manager
        self.current_filename = None
        self.base_directory = "."  # カレントディレクトリ
    
    def show_load_dialog(self) -> bool:
        """
        ファイル読み込みダイアログを表示
        既存FileManagerと同じインターフェース
        
        Returns:
            bool: 読み込みが成功した場合True
        """
        try:
            # DialogManager_v3のFileLoadDialogJSONを使用
            # PyPlc Ver3ウィンドウサイズ（384x384）に適したサイズで作成
            dialog = FileLoadDialogJSON(
                initial_dir=self.base_directory,
                file_pattern="*.csv",  # CSVファイルのみ表示
                title="Load Circuit File",
                width=340,   # PyPlc Ver3に適したサイズ
                height=280   # PyPlc Ver3に適したサイズ
            )
            
            # ダイアログ表示
            success, filepath = dialog.show_load_dialog()
            
            if success and filepath:
                # ファイルの存在確認
                if not os.path.exists(filepath):
                    print(f"[FileManagerV3] File not found: {filepath}")
                    return False
                
                # CircuitCsvManagerを使用してファイル読み込み
                success = self.csv_manager.load_circuit_from_csv(filepath)
                
                if success:
                    self.current_filename = os.path.basename(filepath)
                    print(f"[FileManagerV3] File loaded: {filepath}")
                    return True
                else:
                    print(f"[FileManagerV3] Failed to load CSV: {filepath}")
                    return False
            
            return False
            
        except Exception as e:
            print(f"[FileManagerV3] Load error: {e}")
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
    
    def show_save_dialog(self) -> bool:
        """
        ファイル保存ダイアログを表示
        既存FileManagerと同じインターフェース
        
        Returns:
            bool: 保存が成功した場合True
        """
        try:
            # デフォルトファイル名を生成
            default_name = self.current_filename or "my_circuit"
            if default_name.endswith('.csv'):
                default_name = default_name[:-4]  # .csv拡張子を除去
            
            # DialogManager_v3のFileSaveDialogJSONを使用
            # PyPlc Ver3ウィンドウサイズ（384x384）に適したサイズで作成
            dialog = FileSaveDialogJSON(
                default_filename=default_name,
                title="Save Circuit File",
                width=340,   # LoadDialogと同じサイズ
                height=280   # LoadDialogと同じサイズ
            )
            
            # ダイアログ表示
            success, filename = dialog.show_save_dialog()
            
            if success and filename:
                # .csv拡張子を付加
                if not filename.endswith('.csv'):
                    filename = f"{filename}.csv"
                
                # フルパス生成
                filepath = os.path.join(self.base_directory, filename)
                
                # CircuitCsvManagerを使用してファイル保存
                success = self.csv_manager.save_circuit_to_csv(filepath)
                
                if success:
                    self.current_filename = filename
                    print(f"[FileManagerV3] File saved: {filepath}")
                    return True
                else:
                    print(f"[FileManagerV3] Failed to save CSV: {filepath}")
                    return False
            
            return False
            
        except Exception as e:
            print(f"[FileManagerV3] Save error: {e}")
            return False
# PyPlc Ver3 Circuit CSV Management System
# 作成日: 2025-08-07
# 目標: Save/Load機能の責任分離・保守性向上

import csv
import os
import glob
from datetime import datetime
from typing import Optional
from config import DeviceType
from core.grid_system import GridSystem

class CircuitCsvManager:
    """
    回路のCSV保存・読み込み機能を管理するクラス
    main.pyからの責任分離により、保守性と拡張性を向上
    """
    
    def __init__(self, grid_system: GridSystem):
        """
        Args:
            grid_system: 対象のGridSystemインスタンス
        """
        self.grid_system = grid_system
        
    def save_circuit_to_csv(self, filename: Optional[str] = None) -> bool:
        """
        CSV形式で回路情報を保存
        
        Args:
            filename: 保存ファイル名（未指定時はタイムスタンプ付き自動生成）
            
        Returns:
            bool: 保存成功時True、失敗時False
        """
        try:
            # ファイル名生成
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"circuit_{timestamp}.csv"
            else:
                # .csv拡張子を自動追加（既に拡張子がある場合は追加しない）
                if not filename.lower().endswith('.csv'):
                    filename = f"{filename}.csv"
            
            # grid_system.to_csv()を使用して拡張フォーマットで保存
            csv_data = self.grid_system.to_csv()
            # print(f"[DEBUG] Saving {len(csv_data)} characters to {filename}")  # デバッグログ
            
            with open(filename, 'w', encoding='utf-8') as csvfile:
                csvfile.write(csv_data)
                
            return True
                
        except Exception as e:
            print(f"Save error: {e}")
            return False

    def load_circuit_from_csv(self, filename: Optional[str] = None) -> bool:
        """
        CSV形式で回路情報を読み込み
        
        Args:
            filename: 読み込みファイル名（未指定時は最新ファイル自動選択）
            
        Returns:
            bool: 読み込み成功時True、失敗時False
        """
        try:
            # ファイル選択
            if filename is None:
                # *.csvファイルを検索
                csv_files = glob.glob("*.csv")
                if not csv_files:
                    return False
                    
                # 最新ファイルを選択
                filename = max(csv_files, key=os.path.getctime)
                
            print(f"Loading from: {filename}")
            
            # CSVファイル読み込み
            with open(filename, 'r', encoding='utf-8') as csvfile:
                csv_data = csvfile.read()
            
            # print(f"[DEBUG] CSV data length: {len(csv_data)} characters")  # デバッグログ
            # grid_system.from_csv()を使用して読み込み
            result = self.grid_system.from_csv(csv_data)
            # print(f"[DEBUG] from_csv result: {result}")  # デバッグログ
            return result
            
        except Exception as e:
            print(f"Load error: {e}")
            return False
                    
    def get_available_csv_files(self) -> list[str]:
        """
        利用可能なCSVファイル一覧を取得
        
        Returns:
            list[str]: CSVファイル名のリスト（作成日時順）
        """
        csv_files = glob.glob("circuit_*.csv")
        # 作成日時順でソート（新しい順）
        csv_files.sort(key=os.path.getctime, reverse=True)
        return csv_files
        
    def delete_csv_file(self, filename: str) -> bool:
        """
        指定したCSVファイルを削除
        
        Args:
            filename: 削除対象ファイル名
            
        Returns:
            bool: 削除成功時True、失敗時False
        """
        try:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"CSV file deleted: {filename}")
                return True
            else:
                print(f"File not found: {filename}")
                return False
        except Exception as e:
            print(f"Delete error: {e}")
            return False
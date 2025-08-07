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
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # ヘッダー行
                writer.writerow(['Row', 'Col', 'DeviceType', 'DeviceID', 'IsEnergized', 'State'])
                
                # 全デバイス情報を書き出し（バスバー除外）
                saved_count = 0
                total_devices = 0
                for row in range(self.grid_system.rows):
                    for col in range(self.grid_system.cols):
                        device = self.grid_system.get_device(row, col)
                        if device:
                            total_devices += 1
                            print(f"Debug: Found device at ({row},{col}): {device.device_type.value} - {device.address}")
                            # バスバーとEMPTYデバイス以外を保存対象とする
                            if device.device_type not in [DeviceType.L_SIDE, DeviceType.R_SIDE, DeviceType.EMPTY]:
                                writer.writerow([
                                    row, col, 
                                    device.device_type.value,
                                    device.address,
                                    device.is_energized,
                                    getattr(device, 'state', False)
                                ])
                                saved_count += 1
                                print(f"Debug: Saved device: {device.device_type.value}")
                
                print(f"Debug: Total devices found: {total_devices}, Saved: {saved_count}")
                print(f"Circuit saved to: {filename}")
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
                # circuit_*.csvファイルを検索
                csv_files = glob.glob("circuit_*.csv")
                if not csv_files:
                    print("No circuit CSV files found")
                    return False
                    
                # 最新ファイルを選択
                filename = max(csv_files, key=os.path.getctime)
                
            print(f"Loading from: {filename}")
            
            # 現在の回路をクリア（バスバー以外のデバイスを削除）
            self._clear_user_devices()
            
            loaded_count = 0
            with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for line_num, row_data in enumerate(reader, start=2):
                    try:
                        row = int(row_data['Row'])
                        col = int(row_data['Col'])
                        device_type_str = row_data['DeviceType']
                        device_address = row_data['DeviceID']  # CSVのカラム名はDeviceIDだがaddressとして使用
                        is_energized = row_data['IsEnergized'].lower() == 'true'
                        state = row_data['State'].lower() == 'true'
                        
                        print(f"Debug Load: Processing ({row},{col}) {device_type_str} - {device_address}")
                        
                        # DeviceType変換
                        device_type = DeviceType(device_type_str)
                        
                        # デバイス配置
                        place_result = self.grid_system.place_device(row, col, device_type, device_address)
                        print(f"Debug Load: place_device result: {place_result is not None}")
                        
                        if place_result:
                            device = self.grid_system.get_device(row, col)
                            if device:
                                device.is_energized = is_energized
                                if hasattr(device, 'state'):
                                    device.state = state
                                loaded_count += 1
                                print(f"Debug Load: Successfully loaded {device_type_str}")
                            else:
                                print("Debug Load: Failed to get device after placement")
                        else:
                            print(f"Debug Load: Failed to place device {device_type_str}")
                                
                    except (ValueError, KeyError) as e:
                        print(f"Warning: CSV line {line_num} skipped: {e}")
                        continue
            
            print(f"Circuit loaded: {loaded_count} devices from {filename}")
            return True
            
        except Exception as e:
            print(f"Load error: {e}")
            return False
            
    def _clear_user_devices(self) -> None:
        """
        ユーザー配置デバイスをクリア（バスバー以外のデバイスを削除）
        """
        for row in range(self.grid_system.rows):
            for col in range(self.grid_system.cols):
                device = self.grid_system.get_device(row, col)
                if device and device.device_type not in [DeviceType.L_SIDE, DeviceType.R_SIDE]:
                    self.grid_system.remove_device(row, col)
                    
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
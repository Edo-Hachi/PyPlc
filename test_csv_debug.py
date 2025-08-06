#!/usr/bin/env python3
"""
CSV読み込み機能のデバッグテスト
画面反映問題の特定用
"""

from core.grid_system import GridSystem
from config import DeviceType

def test_csv_import():
    """CSV読み込み機能の単体テスト"""
    
    print("🧪 CSV読み込み単体テスト開始")
    
    # GridSystemインスタンス作成
    grid = GridSystem()
    
    # 既存CSVファイルから読み込み
    try:
        with open('circuit_20250803_210756.csv', 'r', encoding='utf-8') as f:
            csv_data = f.read()
        
        print(f"📄 CSVファイル読み込み完了: {len(csv_data)} chars")
        print("--- CSV内容 ---")
        print(csv_data)
        print("--- CSV内容終了 ---")
        
        # from_csv()実行
        result = grid.from_csv(csv_data)
        print(f"from_csv() result: {result}")
        
        # Grid status check
        print("\nGrid status check:")
        device_count = 0
        for row in range(grid.rows):
            for col in range(grid.cols):
                device = grid.get_device(row, col)
                if device and device.device_type.value not in ['L_SIDE', 'R_SIDE']:
                    device_count += 1
                    print(f"  Device found: [{row}][{col}] = {device.device_type.value} (state={device.state})")
        
        print(f"\nResult: {device_count} user devices confirmed")
        
        if device_count == 0:
            print("ERROR: No devices loaded")
        else:
            print("SUCCESS: Device loading is normal")
            
    except Exception as e:
        print(f"ERROR: Test failed: {e}")

if __name__ == "__main__":
    test_csv_import()
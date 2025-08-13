#!/usr/bin/env python3
"""
Compare命令の論理演算部分のみをテスト（Pyxel非依存）
"""

import sys
import os

# モジュールパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 直接circuit_analyzerから比較ロジックをテスト
class MockCircuitAnalyzer:
    """Circuit Analyzerの比較ロジック部分をテストするためのモッククラス"""
    
    def __init__(self):
        # モックデータレジスタ
        self.mock_data_registers = {
            "D1": 15,
            "D2": 20,
            "D3": 10,
            "D0": 0
        }
    
    def _evaluate_comparison(self, comparison_text: str) -> bool:
        """比較演算式を評価する（circuit_analyzer.pyから移植）"""
        # 演算子の優先順位（長い演算子から先にチェック）
        operators = ['>=', '<=', '<>', '=', '>', '<']
        
        for op in operators:
            if op in comparison_text:
                parts = comparison_text.split(op, 1)
                if len(parts) == 2:
                    left_str = parts[0].strip()
                    right_str = parts[1].strip()
                    
                    # 左辺と右辺の値を取得
                    left_value = self._get_value_from_operand(left_str)
                    right_value = self._get_value_from_operand(right_str)
                    
                    if left_value is None or right_value is None:
                        return False
                    
                    # 比較演算の実行
                    if op == '=':
                        return left_value == right_value
                    elif op == '<>':
                        return left_value != right_value
                    elif op == '>':
                        return left_value > right_value
                    elif op == '<':
                        return left_value < right_value
                    elif op == '>=':
                        return left_value >= right_value
                    elif op == '<=':
                        return left_value <= right_value
                break
        
        return False

    def _get_value_from_operand(self, operand: str):
        """オペランドから値を取得する（circuit_analyzer.pyから移植・簡略化）"""
        operand = operand.strip().upper()
        
        # データレジスタの場合（D番号）
        if operand.startswith('D') and operand[1:].isdigit():
            return self.mock_data_registers.get(operand, 0)
        
        # 定数値の場合
        try:
            return int(operand)
        except ValueError:
            return None

def test_compare_logic():
    """Compare命令の論理演算をテスト"""
    print("=== Compare命令論理演算テスト ===")
    
    analyzer = MockCircuitAnalyzer()
    
    print("\n=== データレジスタ値 ===")
    for reg, value in analyzer.mock_data_registers.items():
        print(f"{reg}: {value}")
    
    # テストケース
    test_cases = [
        # 基本的な比較演算
        ("D1>10", True),    # 15 > 10
        ("D1<20", True),    # 15 < 20
        ("D1=15", True),    # 15 = 15
        ("D1<>10", True),   # 15 <> 10
        ("D1>=15", True),   # 15 >= 15
        ("D1<=15", True),   # 15 <= 15
        
        # 偽となるケース
        ("D1>20", False),   # 15 > 20
        ("D1<10", False),   # 15 < 10
        ("D1=10", False),   # 15 = 10
        ("D1<>15", False),  # 15 <> 15
        ("D1>=20", False),  # 15 >= 20
        ("D1<=10", False),  # 15 <= 10
        
        # データレジスタ同士の比較
        ("D1=D2", False),   # 15 = 20
        ("D1<D2", True),    # 15 < 20
        ("D1>D3", True),    # 15 > 10
        ("D2>D3", True),    # 20 > 10
        
        # 存在しないレジスタ（デフォルト値0）
        ("D99=0", True),    # 存在しないD99は0
        ("D99>5", False),   # 0 > 5
        
        # 定数値との比較
        ("D0=0", True),     # 0 = 0
        ("100>50", True),   # 100 > 50
        ("25<=30", True),   # 25 <= 30
    ]
    
    print("\n=== テスト実行 ===")
    passed = 0
    total = len(test_cases)
    
    for expression, expected in test_cases:
        result = analyzer._evaluate_comparison(expression)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {expression:<10} -> {result:<5} (期待値: {expected})")
        if result == expected:
            passed += 1
    
    print(f"\n=== 結果 ===")
    print(f"合格: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("✓ 全テストケースが正常に動作しています！")
        return True
    else:
        print("✗ 一部テストケースが失敗しました。")
        return False

if __name__ == "__main__":
    success = test_compare_logic()
    sys.exit(0 if success else 1)
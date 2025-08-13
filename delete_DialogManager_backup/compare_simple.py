"""
比較命令設定ダイアログ（簡単実装）
PyPlc Ver3 比較命令機能統合モジュール
"""

from typing import Optional, Tuple

def show_compare_dialog(condition: str = "") -> Tuple[bool, Optional[str]]:
    """
    比較命令設定ダイアログを表示（簡単実装）
    
    Args:
        condition: 初期条件式
        
    Returns:
        Tuple[bool, Optional[str]]: (成功フラグ, 条件式)
    """
    # 簡単な実装として、常に成功を返す
    # 実際のUI実装は将来的に追加
    
    # デフォルト値処理
    if not condition:
        condition = "D1>10"
    
    # バリデーション
    if not _validate_compare_expression(condition):
        return False, None
    
    return True, condition

def _validate_compare_expression(expression: str) -> bool:
    """比較式のバリデーション"""
    if not expression.strip():
        return False
    
    # サポートする演算子
    operators = ['>=', '<=', '<>', '=', '>', '<']
    
    # 演算子が含まれているかチェック
    for op in operators:
        if op in expression:
            parts = expression.split(op, 1)
            if len(parts) == 2:
                left = parts[0].strip()
                right = parts[1].strip()
                
                # 左辺と右辺のバリデーション
                if _validate_operand(left) and _validate_operand(right):
                    return True
            break
    
    return False

def _validate_operand(operand: str) -> bool:
    """オペランドのバリデーション"""
    operand = operand.strip().upper()
    
    # データレジスタ（D番号）の場合
    if operand.startswith('D'):
        number_part = operand[1:]
        if number_part.isdigit():
            number = int(number_part)
            return 0 <= number <= 255
        return False
    
    # 定数値の場合
    try:
        value = int(operand)
        return 0 <= value <= 32767  # PLC標準範囲
    except ValueError:
        return False
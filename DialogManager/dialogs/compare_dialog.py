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

def _validate_compare_expression(condition: str) -> bool:
    """
    比較式の妥当性を検証
    
    Args:
        condition: 検証対象の条件式
        
    Returns:
        bool: 妥当な場合True
    """
    if not condition or len(condition.strip()) == 0:
        return False
    
    # 基本的な比較演算子の存在チェック
    operators = ['>', '<', '>=', '<=', '==', '!=']
    has_operator = any(op in condition for op in operators)
    
    return has_operator
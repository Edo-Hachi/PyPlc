"""
データレジスタ設定ダイアログ（簡単実装）
PyPlc Ver3 データレジスタ機能統合モジュール
"""

from typing import Optional, Tuple, Dict, Any

def show_data_register_dialog(address: str = "", value: int = 0) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    データレジスタ設定ダイアログを表示（簡単実装）
    
    Args:
        address: 初期アドレス
        value: 初期値
        
    Returns:
        Tuple[bool, Optional[Dict]]: (成功フラグ, 結果辞書)
    """
    # 簡単な実装として、常に成功を返す
    # 実際のUI実装は将来的に追加
    
    # デフォルト値処理
    if not address:
        address = "D1"
    
    # バリデーション
    if not _validate_address(address):
        return False, None
    
    if not _validate_value(value):
        return False, None
    
    # 正規化されたアドレス
    normalized_address = _normalize_address(address)
    
    result = {
        "address": normalized_address,
        "value": value
    }
    
    return True, result

def _validate_address(address: str) -> bool:
    """アドレスのバリデーション"""
    if not address:
        return False
    
    address = address.upper().strip()
    
    # D番号の形式チェック
    if address.startswith('D'):
        number_part = address[1:]
    else:
        # Dプレフィックスがない場合も許可
        number_part = address
    
    if not number_part.isdigit():
        return False
    
    number = int(number_part)
    return 0 <= number <= 255

def _validate_value(value: int) -> bool:
    """値のバリデーション"""
    return 0 <= value <= 32767

def _normalize_address(address: str) -> str:
    """アドレスの正規化"""
    address = address.upper().strip()
    
    if not address.startswith('D'):
        address = f"D{address}"
    
    return address
# PyPlc Ver3 File Name Validation System
# 作成日: 2025-08-07
# 目標: ファイル名検証・サニタイズ機能

import re
from typing import Tuple

class FileNameValidator:
    """
    ファイル名検証・サニタイズクラス
    PLC標準準拠の安全なファイル名管理
    """
    
    # 不正文字リスト（Windows/Linux/macOS共通）
    INVALID_CHARS = ['<', '>', ':', '"', '|', '?', '*', '/', '\\']
    
    # 予約語リスト（Windows準拠）
    RESERVED_NAMES = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    
    # 長さ制限
    MAX_LENGTH = 50
    MIN_LENGTH = 1
    
    @staticmethod
    def validate(filename: str) -> Tuple[bool, str]:
        """
        ファイル名バリデーション実行
        
        Args:
            filename: 検証対象ファイル名
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not filename:
            return False, "Filename cannot be empty"
            
        # 長さチェック
        if len(filename) < FileNameValidator.MIN_LENGTH:
            return False, "Filename too short"
        if len(filename) > FileNameValidator.MAX_LENGTH:
            return False, f"Filename too long (max {FileNameValidator.MAX_LENGTH} chars)"
            
        # 不正文字チェック
        for char in FileNameValidator.INVALID_CHARS:
            if char in filename:
                return False, f"Invalid character: '{char}'"
                
        # 先頭・末尾スペース/ピリオドチェック
        if filename.startswith(' ') or filename.endswith(' '):
            return False, "Filename cannot start/end with space"
        if filename.startswith('.') or filename.endswith('.'):
            return False, "Filename cannot start/end with period"
            
        # 予約語チェック（大文字小文字無視）
        name_upper = filename.upper()
        base_name = name_upper.split('.')[0]  # 拡張子を除去
        if base_name in FileNameValidator.RESERVED_NAMES:
            return False, f"Reserved name: '{filename}'"
            
        # 制御文字チェック
        if any(ord(c) < 32 for c in filename):
            return False, "Control characters not allowed"
            
        return True, ""
    
    @staticmethod
    def sanitize(filename: str) -> str:
        """
        ファイル名サニタイズ実行
        
        Args:
            filename: サニタイズ対象ファイル名
            
        Returns:
            str: サニタイズ後ファイル名
        """
        if not filename:
            return "untitled"
            
        # 不正文字を_に置換
        sanitized = filename
        for char in FileNameValidator.INVALID_CHARS:
            sanitized = sanitized.replace(char, '_')
            
        # 制御文字を_に置換
        sanitized = ''.join(c if ord(c) >= 32 else '_' for c in sanitized)
        
        # 先頭・末尾スペース/ピリオド削除
        sanitized = sanitized.strip(' .')
        
        # 予約語チェック・修正
        name_upper = sanitized.upper()
        base_name = name_upper.split('.')[0]
        if base_name in FileNameValidator.RESERVED_NAMES:
            sanitized = f"file_{sanitized}"
            
        # 長さ制限
        if len(sanitized) > FileNameValidator.MAX_LENGTH:
            sanitized = sanitized[:FileNameValidator.MAX_LENGTH]
            
        # 空文字チェック
        if not sanitized:
            sanitized = "untitled"
            
        return sanitized
    
    @staticmethod
    def add_csv_extension(filename: str) -> str:
        """
        .csv拡張子自動付加
        
        Args:
            filename: 元ファイル名
            
        Returns:
            str: .csv拡張子付きファイル名
        """
        if not filename.lower().endswith('.csv'):
            return f"{filename}.csv"
        return filename
    
    @staticmethod
    def get_display_name(full_path: str) -> str:
        """
        表示用ファイル名取得（拡張子除去）
        
        Args:
            full_path: フルパスファイル名
            
        Returns:
            str: 表示用ファイル名（拡張子なし）
        """
        import os
        base_name = os.path.basename(full_path)
        if base_name.lower().endswith('.csv'):
            return base_name[:-4]  # .csv削除
        return base_name
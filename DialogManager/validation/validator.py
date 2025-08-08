"""
Validator - バリデーションシステム

PyPlc Ver3 Dialog System - Phase 2 Implementation
入力値検証エンジン・PLC標準準拠バリデーター・エラーメッセージ管理
"""

import re
from typing import Tuple, Dict, List, Callable, Optional
from abc import ABC, abstractmethod


class ValidationResult:
    """
    バリデーション結果を格納するクラス
    """
    
    def __init__(self, is_valid: bool, error_message: str = "", error_code: str = ""):
        """
        ValidationResult初期化
        
        Args:
            is_valid: バリデーション結果
            error_message: エラーメッセージ
            error_code: エラーコード
        """
        self.is_valid = is_valid
        self.error_message = error_message
        self.error_code = error_code
    
    def __bool__(self) -> bool:
        """
        bool変換でis_validを返す
        """
        return self.is_valid


class BaseValidator(ABC):
    """
    バリデーターの基底クラス
    """
    
    def __init__(self, error_message: str = ""):
        """
        BaseValidator初期化
        
        Args:
            error_message: デフォルトエラーメッセージ
        """
        self.error_message = error_message
    
    @abstractmethod
    def validate(self, value: str) -> ValidationResult:
        """
        バリデーション実行（サブクラスで実装）
        
        Args:
            value: 検証する値
            
        Returns:
            バリデーション結果
        """
        pass


class RequiredValidator(BaseValidator):
    """
    必須入力バリデーター
    """
    
    def __init__(self, error_message: str = "This field is required"):
        super().__init__(error_message)
    
    def validate(self, value: str) -> ValidationResult:
        """
        必須入力チェック
        
        Args:
            value: 検証する値
            
        Returns:
            バリデーション結果
        """
        if not value or not value.strip():
            return ValidationResult(False, self.error_message, "REQUIRED")
        return ValidationResult(True)


class LengthValidator(BaseValidator):
    """
    文字列長バリデーター
    """
    
    def __init__(self, min_length: int = 0, max_length: int = 100, 
                 error_message: str = ""):
        """
        LengthValidator初期化
        
        Args:
            min_length: 最小文字数
            max_length: 最大文字数
            error_message: カスタムエラーメッセージ
        """
        self.min_length = min_length
        self.max_length = max_length
        
        if not error_message:
            if min_length > 0 and max_length < 100:
                error_message = f"Enter between {min_length} and {max_length} characters"
            elif min_length > 0:
                error_message = f"Enter at least {min_length} characters"
            else:
                error_message = f"Enter no more than {max_length} characters"
        
        super().__init__(error_message)
    
    def validate(self, value: str) -> ValidationResult:
        """
        文字列長チェック
        
        Args:
            value: 検証する値
            
        Returns:
            バリデーション結果
        """
        length = len(value)
        
        if length < self.min_length:
            return ValidationResult(False, self.error_message, "TOO_SHORT")
        elif length > self.max_length:
            return ValidationResult(False, self.error_message, "TOO_LONG")
        
        return ValidationResult(True)


class RegexValidator(BaseValidator):
    """
    正規表現バリデーター
    """
    
    def __init__(self, pattern: str, error_message: str = "Invalid format"):
        """
        RegexValidator初期化
        
        Args:
            pattern: 正規表現パターン
            error_message: エラーメッセージ
        """
        super().__init__(error_message)
        self.pattern = re.compile(pattern)
    
    def validate(self, value: str) -> ValidationResult:
        """
        正規表現チェック
        
        Args:
            value: 検証する値
            
        Returns:
            バリデーション結果
        """
        if not self.pattern.match(value):
            return ValidationResult(False, self.error_message, "PATTERN_MISMATCH")
        return ValidationResult(True)


class PLCDeviceAddressValidator(BaseValidator):
    """
    PLCデバイスアドレスバリデーター
    PLC標準仕様準拠のデバイスアドレス形式をチェック
    """
    
    def __init__(self, error_message: str = "Enter a valid PLC address format"):
        super().__init__(error_message)
        
        # PLC標準デバイスタイプとアドレス範囲
        self.device_patterns = {
            'X': (0, 1023),    # 入力接点
            'Y': (0, 1023),    # 出力接点
            'M': (0, 8191),    # 内部リレー
            'T': (0, 511),     # タイマー
            'C': (0, 255),     # カウンター
            'D': (0, 8191),    # データレジスタ
            'S': (0, 1023),    # ステップリレー
            'F': (0, 2047),    # 特殊リレー
        }
        
        # デバイスアドレス正規表現パターン
        device_types = '|'.join(self.device_patterns.keys())
        self.address_pattern = re.compile(f'^({device_types})(\\d+)$')
    
    def validate(self, value: str) -> ValidationResult:
        """
        PLCデバイスアドレスチェック
        
        Args:
            value: 検証する値
            
        Returns:
            バリデーション結果
        """
        if not value:
            return ValidationResult(False, "Please enter a device address", "EMPTY")
        
        # 大文字に変換
        value = value.upper().strip()
        
        # 正規表現マッチング
        match = self.address_pattern.match(value)
        if not match:
            return ValidationResult(
                False, 
                "Correct format: X0, Y10, M100, T0, C0, etc.", 
                "INVALID_FORMAT"
            )
        
        device_type = match.group(1)
        address_num = int(match.group(2))
        
        # アドレス範囲チェック
        min_addr, max_addr = self.device_patterns[device_type]
        if not (min_addr <= address_num <= max_addr):
            return ValidationResult(
                False,
                f"{device_type} device address must be between {min_addr} and {max_addr}",
                "OUT_OF_RANGE"
            )
        
        return ValidationResult(True)


class NumericValidator(BaseValidator):
    """
    数値バリデーター
    """
    
    def __init__(self, min_value: float = None, max_value: float = None,
                 allow_decimal: bool = True, error_message: str = ""):
        """
        NumericValidator初期化
        
        Args:
            min_value: 最小値
            max_value: 最大値
            allow_decimal: 小数点を許可するか
            error_message: カスタムエラーメッセージ
        """
        self.min_value = min_value
        self.max_value = max_value
        self.allow_decimal = allow_decimal
        
        if not error_message:
            if min_value is not None and max_value is not None:
                error_message = f"Enter a number between {min_value} and {max_value}"
            elif min_value is not None:
                error_message = f"Enter a number greater than or equal to {min_value}"
            elif max_value is not None:
                error_message = f"Enter a number less than or equal to {max_value}"
            else:
                error_message = "Please enter a number"
        
        super().__init__(error_message)
    
    def validate(self, value: str) -> ValidationResult:
        """
        数値チェック
        
        Args:
            value: 検証する値
            
        Returns:
            バリデーション結果
        """
        if not value.strip():
            return ValidationResult(False, "Please enter a number", "EMPTY")
        
        try:
            if self.allow_decimal:
                num_value = float(value)
            else:
                if '.' in value:
                    return ValidationResult(False, "Please enter an integer", "NOT_INTEGER")
                num_value = int(value)
            
            # 範囲チェック
            if self.min_value is not None and num_value < self.min_value:
                return ValidationResult(False, self.error_message, "TOO_SMALL")
            if self.max_value is not None and num_value > self.max_value:
                return ValidationResult(False, self.error_message, "TOO_LARGE")
            
            return ValidationResult(True)
            
        except ValueError:
            return ValidationResult(False, "Please enter a valid number", "INVALID_NUMBER")


class CompositeValidator(BaseValidator):
    """
    複合バリデーター（複数のバリデーターを組み合わせ）
    """
    
    def __init__(self, validators: List[BaseValidator]):
        """
        CompositeValidator初期化
        
        Args:
            validators: バリデーターのリスト
        """
        super().__init__("")
        self.validators = validators
    
    def validate(self, value: str) -> ValidationResult:
        """
        全バリデーターを順次実行
        
        Args:
            value: 検証する値
            
        Returns:
            最初に失敗したバリデーション結果（全て成功の場合は成功）
        """
        for validator in self.validators:
            result = validator.validate(value)
            if not result.is_valid:
                return result
        
        return ValidationResult(True)


class ValidatorFactory:
    """
    バリデーター生成ファクトリー
    """
    
    @staticmethod
    def create_plc_device_validator() -> PLCDeviceAddressValidator:
        """
        PLCデバイスアドレスバリデーターを作成
        
        Returns:
            PLCデバイスアドレスバリデーター
        """
        return PLCDeviceAddressValidator()
    
    @staticmethod
    def create_required_plc_device_validator() -> CompositeValidator:
        """
        必須PLCデバイスアドレスバリデーターを作成
        
        Returns:
            必須+PLCデバイスアドレスバリデーター
        """
        return CompositeValidator([
            RequiredValidator(),
            PLCDeviceAddressValidator()
        ])
    
    @staticmethod
    def create_timer_preset_validator() -> CompositeValidator:
        """
        タイマープリセット値バリデーターを作成
        
        Returns:
            タイマープリセット値バリデーター
        """
        return CompositeValidator([
            RequiredValidator("Please enter a preset value"),
            NumericValidator(0, 32767, False, "Enter an integer between 0 and 32767")
        ])
    
    @staticmethod
    def create_counter_preset_validator() -> CompositeValidator:
        """
        カウンタープリセット値バリデーターを作成
        
        Returns:
            カウンタープリセット値バリデーター
        """
        return CompositeValidator([
            RequiredValidator("Please enter a preset value"),
            NumericValidator(0, 32767, False, "Enter an integer between 0 and 32767")
        ])
    
    @staticmethod
    def create_text_validator(min_length: int = 0, max_length: int = 100,
                            required: bool = False) -> CompositeValidator:
        """
        テキストバリデーターを作成
        
        Args:
            min_length: 最小文字数
            max_length: 最大文字数
            required: 必須かどうか
            
        Returns:
            テキストバリデーター
        """
        validators = []
        
        if required:
            validators.append(RequiredValidator())
        
        validators.append(LengthValidator(min_length, max_length))
        
        return CompositeValidator(validators)


def create_validator_from_config(config: Dict) -> BaseValidator:
    """
    設定辞書からバリデーターを作成
    
    Args:
        config: バリデーター設定辞書
        
    Returns:
        作成されたバリデーター
    """
    validator_type = config.get("type", "text")
    
    if validator_type == "plc_device":
        return ValidatorFactory.create_plc_device_validator()
    elif validator_type == "required_plc_device":
        return ValidatorFactory.create_required_plc_device_validator()
    elif validator_type == "timer_preset":
        return ValidatorFactory.create_timer_preset_validator()
    elif validator_type == "counter_preset":
        return ValidatorFactory.create_counter_preset_validator()
    elif validator_type == "text":
        return ValidatorFactory.create_text_validator(
            min_length=config.get("min_length", 0),
            max_length=config.get("max_length", 100),
            required=config.get("required", False)
        )
    elif validator_type == "numeric":
        return NumericValidator(
            min_value=config.get("min_value"),
            max_value=config.get("max_value"),
            allow_decimal=config.get("allow_decimal", True)
        )
    else:
        # デフォルトは何もチェックしないバリデーター
        return CompositeValidator([])

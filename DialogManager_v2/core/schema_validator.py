# PyPlc Ver3 JSON Schema Validator
# 作成日: 2025-08-08
# 目的: Dialog定義ファイルのJSON schema検証機能

import json
import os
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class SchemaValidationError(Exception):
    """スキーマ検証エラー"""
    pass


class SchemaValidator:
    """
    JSON Schema検証クラス
    
    機能:
    - 定義ファイルのスキーマ検証
    - エラー詳細レポート生成
    - 一括検証機能
    """
    
    def __init__(self, base_path: str = None):
        """
        SchemaValidator初期化
        
        Args:
            base_path: 基準ディレクトリパス（未指定時は現在ディレクトリ）
        """
        if base_path is None:
            self.base_path = Path(__file__).parent
        else:
            self.base_path = Path(base_path)
        
        self.definitions_path = self.base_path / "definitions"
        self.schemas_path = self.definitions_path / "schemas"
        
        print(f"SchemaValidator initialized:")
        print(f"  Base path: {self.base_path}")
        print(f"  Definitions: {self.definitions_path}")
        print(f"  Schemas: {self.schemas_path}")
    
    def validate_json_syntax(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """
        JSONファイルの構文検証
        
        Args:
            file_path: 検証するJSONファイルのパス
            
        Returns:
            (success: bool, error_message: str|None)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"JSON Syntax Error: {e}"
        except Exception as e:
            return False, f"File Error: {e}"
    
    def load_schema(self, schema_path: Path) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        スキーマファイルを読み込み
        
        Args:
            schema_path: スキーマファイルのパス
            
        Returns:
            (success: bool, schema_data: dict|None, error_message: str|None)
        """
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
            return True, schema_data, None
        except Exception as e:
            return False, None, f"Schema Load Error: {e}"
    
    def validate_definition_file(self, definition_file: Path) -> Tuple[bool, List[str]]:
        """
        定義ファイルの検証
        
        Args:
            definition_file: 検証する定義ファイルのパス
            
        Returns:
            (success: bool, error_messages: List[str])
        """
        errors = []
        
        # 1. JSON構文検証
        json_valid, json_error = self.validate_json_syntax(definition_file)
        if not json_valid:
            errors.append(json_error)
            return False, errors
        
        # 2. 定義ファイル読み込み
        try:
            with open(definition_file, 'r', encoding='utf-8') as f:
                definition_data = json.load(f)
        except Exception as e:
            errors.append(f"Definition Load Error: {e}")
            return False, errors
        
        # 3. $schema参照チェック
        if "$schema" not in definition_data:
            errors.append("Missing $schema reference")
            return False, errors
        
        schema_ref = definition_data["$schema"]
        schema_path = self.definitions_path / schema_ref
        
        # 4. スキーマファイル存在チェック
        if not schema_path.exists():
            errors.append(f"Schema file not found: {schema_path}")
            return False, errors
        
        # 5. スキーマファイル読み込み
        schema_valid, schema_data, schema_error = self.load_schema(schema_path)
        if not schema_valid:
            errors.append(f"Schema validation failed: {schema_error}")
            return False, errors
        
        # 6. 基本構造検証（簡易版）
        basic_valid, basic_errors = self._validate_basic_structure(definition_data)
        if not basic_valid:
            errors.extend(basic_errors)
        
        return len(errors) == 0, errors
    
    def _validate_basic_structure(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        基本構造の検証（簡易版）
        
        Args:
            data: 検証するデータ
            
        Returns:
            (success: bool, error_messages: List[str])
        """
        errors = []
        
        # 必須フィールドチェック
        required_fields = ["title", "width", "height", "controls"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # controlsフィールドの検証
        if "controls" in data:
            if not isinstance(data["controls"], list):
                errors.append("'controls' must be an array")
            else:
                for i, control in enumerate(data["controls"]):
                    if not isinstance(control, dict):
                        errors.append(f"Control[{i}] must be an object")
                        continue
                    
                    # 必須コントロールフィールド
                    required_control_fields = ["id", "type", "x", "y", "width", "height"]
                    for field in required_control_fields:
                        if field not in control:
                            errors.append(f"Control[{i}] missing required field: {field}")
        
        return len(errors) == 0, errors
    
    def validate_all_definitions(self) -> Dict[str, Tuple[bool, List[str]]]:
        """
        全定義ファイルの一括検証
        
        Returns:
            検証結果辞書 {filename: (success, errors)}
        """
        results = {}
        
        # 定義ファイルを検索
        definition_files = list(self.definitions_path.glob("*.json"))
        
        print(f"Found {len(definition_files)} definition files:")
        for file_path in definition_files:
            print(f"  - {file_path.name}")
        
        # 各ファイルを検証
        for file_path in definition_files:
            if file_path.name.startswith('.'):
                continue  # 隠しファイルをスキップ
                
            print(f"\nValidating: {file_path.name}")
            success, errors = self.validate_definition_file(file_path)
            results[file_path.name] = (success, errors)
            
            if success:
                print(f"  ✓ Valid")
            else:
                print(f"  ✗ Invalid ({len(errors)} errors):")
                for error in errors:
                    print(f"    - {error}")
        
        return results
    
    def generate_validation_report(self, results: Dict[str, Tuple[bool, List[str]]]) -> str:
        """
        検証結果レポート生成
        
        Args:
            results: validate_all_definitions()の結果
            
        Returns:
            レポート文字列
        """
        report_lines = []
        report_lines.append("PyPlc Ver3 JSON Schema Validation Report")
        report_lines.append("=" * 50)
        
        total_files = len(results)
        valid_files = sum(1 for success, _ in results.values() if success)
        invalid_files = total_files - valid_files
        
        report_lines.append(f"Total files: {total_files}")
        report_lines.append(f"Valid files: {valid_files}")
        report_lines.append(f"Invalid files: {invalid_files}")
        report_lines.append("")
        
        # 詳細結果
        for filename, (success, errors) in results.items():
            status = "✓ VALID" if success else "✗ INVALID"
            report_lines.append(f"{filename}: {status}")
            
            if not success and errors:
                for error in errors:
                    report_lines.append(f"  - {error}")
                report_lines.append("")
        
        return "\n".join(report_lines)


def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PyPlc Ver3 JSON Schema Validator")
    parser.add_argument("--validate-all", action="store_true", 
                       help="Validate all definition files")
    parser.add_argument("--file", type=str, 
                       help="Validate specific file")
    parser.add_argument("--report", action="store_true",
                       help="Generate validation report")
    
    args = parser.parse_args()
    
    validator = SchemaValidator()
    
    if args.validate_all:
        print("Validating all definition files...")
        results = validator.validate_all_definitions()
        
        if args.report:
            report = validator.generate_validation_report(results)
            print("\n" + report)
            
            # レポートをファイルに保存
            report_file = validator.base_path / "validation_report.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\nReport saved to: {report_file}")
    
    elif args.file:
        print(f"Validating file: {args.file}")
        file_path = validator.definitions_path / args.file
        success, errors = validator.validate_definition_file(file_path)
        
        if success:
            print("✓ File is valid")
        else:
            print("✗ File has errors:")
            for error in errors:
                print(f"  - {error}")
    
    else:
        print("Use --validate-all or --file <filename> to validate")
        print("Add --report to generate detailed report")


if __name__ == "__main__":
    main()
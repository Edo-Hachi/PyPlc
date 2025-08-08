#!/usr/bin/env python3
# PyPlc Ver3 Definition Files Validator
# 作成日: 2025-08-08
# 目的: 開発用JSON定義ファイル一括検証スクリプト

"""
PyPlc Ver3 JSON定義ファイル検証スクリプト

使用方法:
  python validate_definitions.py                    # 全ファイル検証
  python validate_definitions.py --report          # 詳細レポート生成
  python validate_definitions.py --file timer.json # 特定ファイル検証
  python validate_definitions.py --ci              # CI用出力（exit codeあり）
"""

import sys
import argparse
from pathlib import Path
from DialogManager.schema_validator import SchemaValidator


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(
        description="PyPlc Ver3 JSON Definition Files Validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--file", 
        type=str, 
        help="Validate specific file (filename only, e.g., 'timer_settings.json')"
    )
    
    parser.add_argument(
        "--report", 
        action="store_true",
        help="Generate detailed validation report"
    )
    
    parser.add_argument(
        "--ci", 
        action="store_true",
        help="CI mode: exit with error code if validation fails"
    )
    
    parser.add_argument(
        "--quiet", 
        action="store_true",
        help="Quiet mode: only show errors"
    )
    
    args = parser.parse_args()
    
    # バナー表示（quiet mode以外）
    if not args.quiet:
        print("PyPlc Ver3 JSON Schema Validator")
        print("=" * 40)
        print()
    
    try:
        # SchemaValidator初期化
        validator = SchemaValidator()
        
        if args.file:
            # 特定ファイル検証
            success = validate_single_file(validator, args.file, args.quiet)
            exit_code = 0 if success else 1
            
        else:
            # 全ファイル検証
            success, results = validate_all_files(validator, args.quiet)
            exit_code = 0 if success else 1
            
            # レポート生成
            if args.report:
                generate_detailed_report(validator, results)
        
        # CI モードでの終了コード制御
        if args.ci:
            sys.exit(exit_code)
        else:
            # 通常モードでは常に正常終了
            sys.exit(0)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def validate_single_file(validator: SchemaValidator, filename: str, quiet: bool = False) -> bool:
    """
    単一ファイルの検証
    
    Args:
        validator: SchemaValidatorインスタンス
        filename: ファイル名
        quiet: 静粛モード
        
    Returns:
        検証成功時True
    """
    if not quiet:
        print(f"Validating: {filename}")
    
    file_path = validator.definitions_path / filename
    
    if not file_path.exists():
        print(f"Error: File not found: {filename}")
        return False
    
    success, errors = validator.validate_definition_file(file_path)
    
    if success:
        if not quiet:
            print("✓ Validation passed")
    else:
        print(f"✗ Validation failed ({len(errors)} errors):")
        for error in errors:
            print(f"  - {error}")
    
    return success


def validate_all_files(validator: SchemaValidator, quiet: bool = False) -> tuple:
    """
    全ファイルの検証
    
    Args:
        validator: SchemaValidatorインスタンス  
        quiet: 静粛モード
        
    Returns:
        (overall_success: bool, results: dict)
    """
    if not quiet:
        print("Validating all definition files...")
        print()
    
    results = validator.validate_all_definitions()
    
    # 結果サマリー
    total_files = len(results)
    valid_files = sum(1 for success, _ in results.values() if success)
    invalid_files = total_files - valid_files
    
    overall_success = invalid_files == 0
    
    print(f"Validation Summary:")
    print(f"  Total files: {total_files}")
    print(f"  Valid files: {valid_files}")
    print(f"  Invalid files: {invalid_files}")
    print()
    
    # 失敗ファイルの詳細表示
    if invalid_files > 0:
        print("Failed files:")
        for filename, (success, errors) in results.items():
            if not success:
                print(f"  ✗ {filename} ({len(errors)} errors)")
                if not quiet:
                    for error in errors:
                        print(f"      - {error}")
        print()
    
    # 成功メッセージ
    if overall_success:
        print("✓ All files passed validation!")
    else:
        print(f"✗ {invalid_files} file(s) failed validation")
    
    return overall_success, results


def generate_detailed_report(validator: SchemaValidator, results: dict):
    """
    詳細レポートの生成と保存
    
    Args:
        validator: SchemaValidatorインスタンス
        results: 検証結果辞書
    """
    print("\n" + "=" * 50)
    print("DETAILED VALIDATION REPORT")
    print("=" * 50)
    
    report = validator.generate_validation_report(results)
    print(report)
    
    # レポートファイル保存
    report_file = Path("validation_report.txt")
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nDetailed report saved to: {report_file}")
    except Exception as e:
        print(f"Warning: Could not save report file: {e}")


if __name__ == "__main__":
    main()
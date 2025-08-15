#!/usr/bin/env python3
"""
DialogManager v4 統合テストランナー

全テストの実行と結果レポート
"""

import sys
import os
import subprocess
from typing import List, Tuple


def run_test_script(script_path: str) -> Tuple[bool, str]:
    """テストスクリプトを実行して結果を取得"""
    try:
        # テストスクリプトのディレクトリで実行
        script_dir = os.path.dirname(script_path)
        working_dir = os.path.dirname(script_dir)  # DialogManager_v4ディレクトリ
        
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=working_dir  # 作業ディレクトリ指定
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "テストがタイムアウトしました"
    except Exception as e:
        return False, f"テスト実行エラー: {e}"


def print_test_header(test_name: str):
    """テストヘッダー表示"""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print('='*60)


def print_test_result(test_name: str, success: bool, output: str):
    """テスト結果表示"""
    status = "✅ 成功" if success else "❌ 失敗"
    print(f"\n📊 {test_name}: {status}")
    
    if not success:
        print(f"\n📝 エラー詳細:\n{output}")


def main():
    """メインテスト実行"""
    print("🚀 DialogManager v4 統合テスト開始")
    print(f"実行環境: Python {sys.version}")
    print(f"作業ディレクトリ: {os.getcwd()}")
    
    # スクリプトの場所を基準にパスを解決
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"スクリプトディレクトリ: {script_dir}")
    
    # テスト定義（絶対パス使用）
    tests = [
        ("コアクラス単体テスト", os.path.join(script_dir, "tests/test_debug_system.py")),
        ("JSON定義検証テスト", os.path.join(script_dir, "tests/test_json_validation.py"))
    ]
    
    results: List[Tuple[str, bool]] = []
    
    # 各テスト実行
    for test_name, script_path in tests:
        print_test_header(test_name)
        
        if not os.path.exists(script_path):
            print(f"❌ テストファイルが見つかりません: {script_path}")
            results.append((test_name, False))
            continue
        
        success, output = run_test_script(script_path)
        results.append((test_name, success))
        
        # 成功時は要約のみ、失敗時は詳細表示
        if success:
            # 出力から重要な情報を抽出
            lines = output.split('\n')
            summary_lines = [line for line in lines if '✅' in line or '🎉' in line or '🎯' in line]
            if summary_lines:
                print("\n📋 テスト要約:")
                for line in summary_lines[-3:]:  # 最後の3行のみ
                    print(f"  {line}")
        else:
            print(f"\n📝 エラー詳細:\n{output}")
    
    # 最終結果サマリー
    print(f"\n{'='*60}")
    print("📊 テスト結果サマリー")
    print('='*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    failed_tests = total_tests - passed_tests
    
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n📈 統計:")
    print(f"  総テスト数: {total_tests}")
    print(f"  成功: {passed_tests}")
    print(f"  失敗: {failed_tests}")
    print(f"  成功率: {(passed_tests/total_tests)*100:.1f}%")
    
    # 全体評価
    if failed_tests == 0:
        print(f"\n🎉 全テスト成功！DialogManager v4は正常に動作しています")
        print("\n🚀 次のステップ:")
        print("  1. Phase V4-1: 最小限コア実装")
        print("  2. Phase V4-2: JSONダイアログ動作テスト")
        return 0
    else:
        print(f"\n⚠️ {failed_tests}個のテストが失敗しました")
        print("修正後に再度テストを実行してください")
        return 1


if __name__ == "__main__":
    sys.exit(main())
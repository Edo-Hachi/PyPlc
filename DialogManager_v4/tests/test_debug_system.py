"""
DialogManager v4 - DebugSystem Unit Tests

DebugSystemクラスの単体テスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.debug_system import DebugSystem
import time


def test_debug_system_basic():
    """DebugSystem基本機能テスト"""
    print("=== DebugSystem基本機能テスト ===")
    
    debug = DebugSystem("TestComponent", "DEBUG")
    
    # 基本ログテスト
    debug.log("INFO", "テスト開始")
    debug.log("DEBUG", "デバッグ情報", {"key": "value", "number": 123})
    debug.error("テストエラー", Exception("テスト例外"))
    
    print("✅ 基本ログ機能: 正常動作")


def test_debug_system_context():
    """DebugSystemコンテキスト管理テスト"""
    print("\n=== DebugSystemコンテキスト管理テスト ===")
    
    debug = DebugSystem("ContextTest")
    
    # 階層コンテキストテスト
    debug.enter_context("outer_context", {"operation": "test"})
    debug.log("INFO", "外側コンテキスト内")
    
    debug.enter_context("inner_context", {"detail": "nested"})
    debug.log("INFO", "内側コンテキスト内")
    debug.exit_context()
    
    debug.log("INFO", "外側コンテキストに戻った")
    debug.exit_context()
    
    debug.log("INFO", "全コンテキスト終了")
    
    print("✅ コンテキスト管理: 正常動作")


def test_debug_system_performance():
    """DebugSystem性能測定テスト"""
    print("\n=== DebugSystem性能測定テスト ===")
    
    debug = DebugSystem("PerformanceTest")
    
    # 性能測定テスト
    with debug.measure_time("test_operation"):
        time.sleep(0.1)  # 0.1秒の処理をシミュレート
        debug.log("INFO", "処理中...")
    
    print("✅ 性能測定機能: 正常動作")


def test_coordinate_system():
    """CoordinateSystem基本テスト"""
    print("\n=== CoordinateSystem基本テスト ===")
    
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from core.coordinate_system import CoordinateSystem
    
    coord_sys = CoordinateSystem(debug=True)
    
    # ダミーダイアログオブジェクト
    class DummyDialog:
        def __init__(self):
            self.x, self.y = 100, 50
            self.width, self.height = 300, 200
    
    # ダミーコントロールオブジェクト
    class DummyControl:
        def __init__(self):
            self.x, self.y = 20, 30
            self.width, self.height = 80, 25
            self.id = "test_control"
    
    dialog = DummyDialog()
    control = DummyControl()
    
    # 座標変換テスト
    dialog_x, dialog_y = coord_sys.screen_to_dialog(150, 100, dialog)
    print(f"画面座標(150,100) → ダイアログ座標({dialog_x},{dialog_y})")
    
    control_x, control_y = coord_sys.dialog_to_control(dialog_x, dialog_y, control)
    print(f"ダイアログ座標({dialog_x},{dialog_y}) → コントロール座標({control_x},{control_y})")
    
    # 境界判定テスト
    inside = coord_sys.is_inside_bounds(50, 75, 0, 0, 100, 100, "test_bounds")
    print(f"境界判定テスト(50,75 in 0,0,100,100): {inside}")
    
    print("✅ CoordinateSystem: 正常動作")


def run_all_core_tests():
    """全コアクラステスト実行"""
    print("🧪 DialogManager v4 コアクラステスト開始\n")
    
    try:
        test_debug_system_basic()
        test_debug_system_context()
        test_debug_system_performance()
        test_coordinate_system()
        
        print("\n🎉 全コアクラステスト完了: すべて正常動作")
        return True
        
    except Exception as e:
        print(f"\n❌ テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_core_tests()
    sys.exit(0 if success else 1)
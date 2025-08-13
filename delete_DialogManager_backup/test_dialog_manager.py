"""
TestDialogManager - Phase 1 MVP動作確認用統合テストクラス

PyPlc Ver3 Dialog System - Phase 1 MVP Test
全コンポーネントの連携動作を確認するテストマネージャー
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DialogManager.base_dialog import BaseDialog
from DialogManager.json_dialog_loader import JSONDialogLoader
from DialogManager.control_factory import ControlFactory
from DialogManager.events.event_system import get_dialog_event_system


class TestConfirmDialog(BaseDialog):
    """
    JSON定義から生成される確認ダイアログのテスト実装
    """
    
    def __init__(self, json_filename: str = "test_confirm.json"):
        """
        TestConfirmDialog初期化
        
        Args:
            json_filename: JSON定義ファイル名
        """
        # JSON定義を読み込み
        self.loader = JSONDialogLoader()
        self.definition = self.loader.load_dialog_definition(json_filename)
        
        if self.definition is None:
            raise ValueError(f"Failed to load dialog definition: {json_filename}")
        
        # BaseDialogを初期化
        super().__init__(
            title=self.definition["title"],
            width=self.definition["width"],
            height=self.definition["height"]
        )
        
        # ControlFactoryでコントロールを生成
        self.factory = ControlFactory()
        self._create_controls()
        
        # イベントシステムを取得
        self.event_system = get_dialog_event_system()
        
        # ダイアログ結果
        self.dialog_result = None
    
    def _create_controls(self) -> None:
        """
        JSON定義からコントロールを生成・追加
        """
        for control_def in self.definition["controls"]:
            # ControlFactoryでコントロールを生成
            control = self.factory.create_control(control_def)
            
            if control is not None:
                # ダイアログにコントロールを追加
                self.add_control(control.id, control)
                
                # イベントハンドラーを設定
                self._setup_control_events(control, control_def)
    
    def _setup_control_events(self, control, control_def: dict) -> None:
        """
        コントロールのイベントハンドラーを設定
        
        Args:
            control: コントロールオブジェクト
            control_def: コントロール定義
        """
        # ボタンクリックイベントの処理
        if control.id == "ok_button":
            control.on("click", self._on_ok_clicked)
        elif control.id == "cancel_button":
            control.on("click", self._on_cancel_clicked)
    
    def _on_ok_clicked(self, control) -> None:
        """
        OKボタンクリック時の処理
        
        Args:
            control: クリックされたコントロール
        """
        print("OK button clicked!")
        self.dialog_result = True
        self.close(True)
    
    def _on_cancel_clicked(self, control) -> None:
        """
        Cancelボタンクリック時の処理
        
        Args:
            control: クリックされたコントロール
        """
        print("Cancel button clicked!")
        self.dialog_result = False
        self.close(False)
    
    def _handle_custom_input(self) -> None:
        """
        カスタム入力処理（ボタンのホバー状態更新）
        """
        # 各ボタンコントロールのホバー状態を更新
        for control_id in ["ok_button", "cancel_button"]:
            control = self.get_control(control_id)
            if control is not None:
                # ホバー状態を更新（簡易実装）
                abs_x, abs_y, w, h = control.get_absolute_rect(self.x, self.y)
                control.is_hovered = (abs_x <= self.mouse_x <= abs_x + w and 
                                    abs_y <= self.mouse_y <= abs_y + h)
    
    def _draw_custom(self) -> None:
        """
        カスタム描画処理（追加の装飾など）
        """
        # Phase 1では基本描画のみ
        pass


class DialogManagerTester:
    """
    DialogManager全体のテスト実行クラス
    """
    
    @staticmethod
    def test_json_loader():
        """
        JSONDialogLoaderのテスト
        """
        print("=== JSONDialogLoader Test ===")
        
        loader = JSONDialogLoader()
        
        # 定義ファイル一覧取得テスト
        available_files = loader.list_available_definitions()
        print(f"Available definition files: {available_files}")
        
        # JSON定義読み込みテスト
        definition = loader.load_dialog_definition("test_confirm.json")
        if definition:
            print("✅ JSON definition loaded successfully")
            print(f"Title: {definition['title']}")
            print(f"Size: {definition['width']}x{definition['height']}")
            print(f"Controls: {len(definition['controls'])}")
        else:
            print("❌ Failed to load JSON definition")
        
        return definition is not None
    
    @staticmethod
    def test_control_factory():
        """
        ControlFactoryのテスト
        """
        print("\n=== ControlFactory Test ===")
        
        factory = ControlFactory()
        
        # サポートされているコントロールタイプ
        supported_types = factory.get_supported_types()
        print(f"Supported control types: {supported_types}")
        
        # テストコントロール定義
        test_controls = [
            {
                "id": "test_label",
                "type": "label",
                "x": 10, "y": 10, "width": 100, "height": 20,
                "text": "Test Label", "color": 7
            },
            {
                "id": "test_button",
                "type": "button", 
                "x": 10, "y": 40, "width": 80, "height": 25,
                "text": "Test Button", "color": 7
            }
        ]
        
        # コントロール生成テスト
        created_controls = []
        for control_def in test_controls:
            control = factory.create_control(control_def)
            if control:
                created_controls.append(control)
                print(f"✅ Created {control_def['type']} control: {control.id}")
            else:
                print(f"❌ Failed to create {control_def['type']} control")
        
        return len(created_controls) == len(test_controls)
    
    @staticmethod
    def test_event_system():
        """
        EventSystemのテスト
        """
        print("\n=== EventSystem Test ===")
        
        event_system = get_dialog_event_system()
        
        # テストイベントハンドラー
        test_results = []
        
        def test_handler(message):
            test_results.append(message)
            print(f"Event received: {message}")
        
        # イベント登録・発火テスト
        event_system.on("test_event", test_handler)
        event_system.emit("test_event", "Hello from event system!")
        
        # 優先度付きイベントテスト
        event_system.set_event_priority("priority_test", 100)
        event_system.on("priority_test", lambda msg: test_results.append(f"Priority: {msg}"))
        event_system.emit_with_priority("priority_test", "High priority event")
        
        success = len(test_results) >= 2
        if success:
            print("✅ Event system working correctly")
        else:
            print("❌ Event system test failed")
        
        return success
    
    @staticmethod
    def run_all_tests():
        """
        全テストを実行
        """
        print("🚀 Phase 1 MVP Component Tests")
        print("=" * 50)
        
        results = []
        results.append(DialogManagerTester.test_json_loader())
        results.append(DialogManagerTester.test_control_factory())
        results.append(DialogManagerTester.test_event_system())
        
        print("\n" + "=" * 50)
        success_count = sum(results)
        total_count = len(results)
        
        if success_count == total_count:
            print(f"🎉 All tests passed! ({success_count}/{total_count})")
            print("Phase 1 MVP components are ready for integration!")
        else:
            print(f"⚠️  Some tests failed ({success_count}/{total_count})")
        
        return success_count == total_count


def main():
    """
    メイン実行関数
    """
    print("PyPlc Ver3 Dialog System - Phase 1 MVP Test")
    print("=" * 60)
    
    # コンポーネントテスト実行
    if DialogManagerTester.run_all_tests():
        print("\n🚀 Starting integrated dialog test...")
        
        try:
            # 統合ダイアログテスト（実際にはPyxelが必要）
            print("Note: Integrated dialog test requires Pyxel environment")
            print("To test the actual dialog, run this in the main PyPlc application")
            
        except Exception as e:
            print(f"Integration test error: {e}")
    
    print("\nPhase 1 MVP testing completed!")


if __name__ == "__main__":
    main()

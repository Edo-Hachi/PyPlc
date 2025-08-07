"""
IntegrationTestDialog - main.py統合テスト用ダイアログ

PyPlc Ver3 Dialog System - Phase 1 Integration Test
Pyxel環境での実際の動作確認用ダイアログクラス
"""

from DialogManager.base_dialog import BaseDialog
from DialogManager.json_dialog_loader import JSONDialogLoader
from DialogManager.control_factory import ControlFactory
from DialogManager.events.event_system import get_dialog_event_system


class IntegrationTestDialog(BaseDialog):
    """
    Phase 1統合テスト用ダイアログ
    
    機能:
    - JSON定義からの完全なダイアログ生成
    - 実際のPyxel環境での動作確認
    - OK/Cancelボタンの実動作テスト
    """
    
    def __init__(self, json_filename: str = "test_confirm.json"):
        """
        IntegrationTestDialog初期化
        
        Args:
            json_filename: JSON定義ファイル名
        """
        # JSON定義を読み込み
        self.loader = JSONDialogLoader()
        self.definition = self.loader.load_dialog_definition(json_filename)
        
        if self.definition is None:
            # フォールバック: デフォルト定義を使用
            print(f"Warning: Could not load {json_filename}, using default definition")
            self.definition = self._get_default_definition()
        
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
        
        print(f"IntegrationTestDialog initialized: {self.title}")
    
    def _get_default_definition(self) -> dict:
        """
        デフォルトダイアログ定義を取得（JSON読み込み失敗時のフォールバック）
        
        Returns:
            デフォルトダイアログ定義
        """
        return {
            "title": "Phase 1 統合テスト",
            "width": 280,
            "height": 140,
            "controls": [
                {
                    "id": "message_label",
                    "type": "label",
                    "x": 20,
                    "y": 30,
                    "width": 240,
                    "height": 20,
                    "text": "Phase 1 MVP統合テスト成功！",
                    "color": 7
                },
                {
                    "id": "info_label",
                    "type": "label",
                    "x": 20,
                    "y": 50,
                    "width": 240,
                    "height": 20,
                    "text": "JSON定義からダイアログが生成されました",
                    "color": 10
                },
                {
                    "id": "ok_button",
                    "type": "button",
                    "x": 60,
                    "y": 80,
                    "width": 60,
                    "height": 25,
                    "text": "OK",
                    "color": 7,
                    "bg_color": 11,
                    "hover_color": 3,
                    "events": ["click"]
                },
                {
                    "id": "cancel_button",
                    "type": "button",
                    "x": 160,
                    "y": 80,
                    "width": 60,
                    "height": 25,
                    "text": "Cancel",
                    "color": 7,
                    "bg_color": 8,
                    "hover_color": 2,
                    "events": ["click"]
                }
            ]
        }
    
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
                
                print(f"Control created: {control.id} ({control_def['type']})")
    
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
        print("✅ OK button clicked! Integration test successful!")
        self.dialog_result = True
        self.close(True)
    
    def _on_cancel_clicked(self, control) -> None:
        """
        Cancelボタンクリック時の処理
        
        Args:
            control: クリックされたコントロール
        """
        print("❌ Cancel button clicked! Dialog cancelled.")
        self.dialog_result = False
        self.close(False)
    
    def _handle_custom_input(self) -> None:
        """
        カスタム入力処理（ボタンのホバー状態更新）
        """
        import pyxel
        
        # 各ボタンコントロールのホバー状態を更新
        for control_id in ["ok_button", "cancel_button"]:
            control = self.get_control(control_id)
            if control is not None and hasattr(control, 'is_hovered'):
                # ホバー状態を更新
                abs_x, abs_y, w, h = control.get_absolute_rect(self.x, self.y)
                control.is_hovered = (abs_x <= self.mouse_x <= abs_x + w and 
                                    abs_y <= self.mouse_y <= abs_y + h)
                
                # マウスクリック処理
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and control.is_hovered:
                    control.emit("click")
    
    def _draw_custom(self) -> None:
        """
        カスタム描画処理（統合テスト情報の表示）
        """
        import pyxel
        
        # 統合テスト情報をダイアログ下部に表示
        info_y = self.y + self.height + 10
        pyxel.text(self.x, info_y, "Integration Test: T key pressed", pyxel.COLOR_YELLOW)
        pyxel.text(self.x, info_y + 8, f"Components: JSON+Factory+Events", pyxel.COLOR_LIGHT_BLUE)


def show_integration_test_dialog() -> bool:
    """
    統合テストダイアログを表示する便利関数
    
    Returns:
        ダイアログの結果（OK: True, Cancel: False）
    """
    try:
        dialog = IntegrationTestDialog()
        result = dialog.show()
        
        print(f"Integration test dialog result: {result}")
        return result
        
    except Exception as e:
        print(f"Integration test dialog error: {e}")
        return False

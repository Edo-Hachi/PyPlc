"""
ControlFactory - コントロールの動的生成ファクトリー

PyPlc Ver3 Dialog System - Phase 1 MVP Implementation
JSON定義からコントロールを動的生成するファクトリーパターン実装
"""

from typing import Dict, Any, Optional, Type, Callable
from abc import ABC, abstractmethod
from DialogManager.controls.text_input_control import TextInputControl


class BaseControl(ABC):
    """
    すべてのコントロールの基底クラス
    """
    
    def __init__(self, control_id: str, x: int, y: int, width: int, height: int, **kwargs):
        """
        BaseControl初期化
        
        Args:
            control_id: コントロールID
            x, y: 相対座標
            width, height: サイズ
            **kwargs: 追加プロパティ
        """
        self.id = control_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.enabled = True
        
        # イベントコールバック
        self.event_callbacks: Dict[str, list] = {}
        
        # 追加プロパティを設定
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def on(self, event_name: str, callback: Callable) -> None:
        """
        イベントコールバックを登録
        
        Args:
            event_name: イベント名
            callback: コールバック関数
        """
        if event_name not in self.event_callbacks:
            self.event_callbacks[event_name] = []
        self.event_callbacks[event_name].append(callback)
    
    def emit(self, event_name: str, *args, **kwargs) -> None:
        """
        イベントを発火
        
        Args:
            event_name: イベント名
            *args: イベント引数
            **kwargs: イベントキーワード引数
        """
        if event_name in self.event_callbacks:
            for callback in self.event_callbacks[event_name]:
                try:
                    callback(self, *args, **kwargs)
                except Exception as e:
                    print(f"Control event callback error: {e}")
    
    @abstractmethod
    def handle_input(self, mouse_x: int, mouse_y: int, mouse_clicked: bool) -> None:
        """
        入力処理（サブクラスで実装）
        
        Args:
            mouse_x, mouse_y: マウス座標
            mouse_clicked: マウスクリック状態
        """
        pass
    
    @abstractmethod
    def draw(self, dialog_x: int, dialog_y: int) -> None:
        """
        描画処理（サブクラスで実装）
        
        Args:
            dialog_x, dialog_y: ダイアログの絶対座標
        """
        pass
    
    def get_absolute_rect(self, dialog_x: int, dialog_y: int) -> tuple:
        """
        絶対座標での矩形を取得
        
        Args:
            dialog_x, dialog_y: ダイアログの絶対座標
            
        Returns:
            (abs_x, abs_y, width, height)
        """
        return (dialog_x + self.x, dialog_y + self.y, self.width, self.height)
    
    def point_in_control(self, mouse_x: int, mouse_y: int, dialog_x: int, dialog_y: int) -> bool:
        """
        マウス座標がコントロール内にあるかチェック
        
        Args:
            mouse_x, mouse_y: マウス座標
            dialog_x, dialog_y: ダイアログの絶対座標
            
        Returns:
            コントロール内にある場合True
        """
        abs_x, abs_y, w, h = self.get_absolute_rect(dialog_x, dialog_y)
        return (abs_x <= mouse_x <= abs_x + w and 
                abs_y <= mouse_y <= abs_y + h)


class ControlFactory:
    """
    コントロールの動的生成ファクトリー
    
    機能:
    - JSON定義からコントロールを動的生成
    - タイプ別ファクトリーパターン
    - コントロール登録システム
    - 拡張可能な設計
    """
    
    def __init__(self):
        """
        ControlFactory初期化
        """
        # コントロールタイプ別の生成関数を登録
        self.control_creators: Dict[str, Callable] = {}
        
        # Phase 1基本コントロールを登録
        self._register_basic_controls()
    
    def _register_basic_controls(self) -> None:
        """
        Phase 1基本コントロールを登録
        """
        # 後で実装するコントロールクラスをインポート予定
        # 現在は仮実装として関数ベースで登録
        self.control_creators["label"] = self._create_label_control
        self.control_creators["button"] = self._create_button_control
        self.control_creators["textinput"] = self._create_textinput_control
    
    def register_control_type(self, control_type: str, creator_func: Callable) -> None:
        """
        新しいコントロールタイプを登録
        
        Args:
            control_type: コントロールタイプ名
            creator_func: コントロール生成関数
        """
        self.control_creators[control_type] = creator_func
    
    def create_control(self, control_definition: Dict[str, Any]) -> Optional[BaseControl]:
        """
        JSON定義からコントロールを生成
        
        Args:
            control_definition: コントロール定義辞書
            
        Returns:
            生成されたコントロール（エラー時はNone）
        """
        try:
            control_type = control_definition.get("type", "label")
            
            # 対応するコントロール生成関数を取得
            if control_type not in self.control_creators:
                print(f"Unknown control type: {control_type}")
                return None
            
            creator_func = self.control_creators[control_type]
            
            # コントロールを生成
            control = creator_func(control_definition)
            
            # イベント登録（疎結合システム用の準備）
            events = control_definition.get("events", [])
            for event_name in events:
                # 実際のイベント登録は後でダイアログマネージャーが行う
                # ここではイベント対応の準備のみ
                pass
            
            return control
            
        except Exception as e:
            print(f"Error creating control: {e}")
            return None
    
    def _create_label_control(self, definition: Dict[str, Any]) -> BaseControl:
        """
        ラベルコントロールを生成
        
        Args:
            definition: コントロール定義
            
        Returns:
            ラベルコントロール
        """
        # 仮実装：後でLabelControlクラスに置き換え予定
        class LabelControl(BaseControl):
            def __init__(self, control_id: str, x: int, y: int, width: int, height: int, **kwargs):
                super().__init__(control_id, x, y, width, height, **kwargs)
                self.text = kwargs.get("text", "")
                self.color = kwargs.get("color", 7)  # pyxel.COLOR_WHITE
            
            def handle_input(self, mouse_x: int, mouse_y: int, mouse_clicked: bool) -> None:
                # ラベルは入力処理なし
                pass
            
            def draw(self, dialog_x: int, dialog_y: int) -> None:
                import pyxel
                abs_x, abs_y, _, _ = self.get_absolute_rect(dialog_x, dialog_y)
                if self.visible and self.text:
                    pyxel.text(abs_x, abs_y, self.text, self.color)
        
        return LabelControl(
            control_id=definition["id"],
            x=definition["x"],
            y=definition["y"],
            width=definition["width"],
            height=definition["height"],
            text=definition.get("text", ""),
            color=definition.get("color", 7)
        )
    
    def _create_button_control(self, definition: Dict[str, Any]) -> BaseControl:
        """
        ボタンコントロールを生成
        
        Args:
            definition: コントロール定義
            
        Returns:
            ボタンコントロール
        """
        # 仮実装：後でButtonControlクラスに置き換え予定
        class ButtonControl(BaseControl):
            def __init__(self, control_id: str, x: int, y: int, width: int, height: int, **kwargs):
                super().__init__(control_id, x, y, width, height, **kwargs)
                self.text = kwargs.get("text", "Button")
                self.color = kwargs.get("color", 7)
                self.bg_color = kwargs.get("bg_color", 5)  # pyxel.COLOR_GRAY
                self.hover_color = kwargs.get("hover_color", 6)  # pyxel.COLOR_LIGHT_BLUE
                self.is_hovered = False
                self.is_pressed = False
            
            def handle_input(self, mouse_x: int, mouse_y: int, mouse_clicked: bool) -> None:
                import pyxel
                
                # ホバー状態更新
                dialog_x, dialog_y = 0, 0  # 実際の値は描画時に設定される
                # 簡易実装：正確な座標計算は後で改善
                self.is_hovered = True  # 仮実装
                
                # クリック処理
                if mouse_clicked and self.is_hovered:
                    self.is_pressed = True
                    self.emit("click")
                else:
                    self.is_pressed = False
            
            def draw(self, dialog_x: int, dialog_y: int) -> None:
                import pyxel
                abs_x, abs_y, w, h = self.get_absolute_rect(dialog_x, dialog_y)
                
                if self.visible:
                    # ボタン背景
                    bg_color = self.hover_color if self.is_hovered else self.bg_color
                    pyxel.rect(abs_x, abs_y, w, h, bg_color)
                    pyxel.rectb(abs_x, abs_y, w, h, self.color)
                    
                    # ボタンテキスト（中央寄せ）
                    text_x = abs_x + (w - len(self.text) * 4) // 2
                    text_y = abs_y + (h - 6) // 2
                    pyxel.text(text_x, text_y, self.text, self.color)
        
        return ButtonControl(
            control_id=definition["id"],
            x=definition["x"],
            y=definition["y"],
            width=definition["width"],
            height=definition["height"],
            text=definition.get("text", "Button"),
            color=definition.get("color", 7),
            bg_color=definition.get("bg_color", 5),
            hover_color=definition.get("hover_color", 6)
        )
    
    def _create_textinput_control(self, definition: Dict[str, Any]) -> BaseControl:
        """
        テキスト入力コントロールを生成（Phase 2本格実装版）
        
        Args:
            definition: コントロール定義
            
        Returns:
            テキスト入力コントロール
        """
        return TextInputControl(
            control_id=definition["id"],
            x=definition["x"],
            y=definition["y"],
            width=definition["width"],
            height=definition["height"],
            value=definition.get("value", ""),
            placeholder=definition.get("placeholder", ""),
            max_length=definition.get("max_length", 50),
            input_type=definition.get("input_type", "text"),
            color=definition.get("color", 7),
            bg_color=definition.get("bg_color", 0),
            border_color=definition.get("border_color", 7),
            focus_border_color=definition.get("focus_border_color", 10)
        )
    
    def get_supported_types(self) -> list:
        """
        サポートされているコントロールタイプの一覧を取得
        
        Returns:
            サポートされているコントロールタイプのリスト
        """
        return list(self.control_creators.keys())
    
    def is_supported_type(self, control_type: str) -> bool:
        """
        指定されたコントロールタイプがサポートされているかチェック
        
        Args:
            control_type: コントロールタイプ名
            
        Returns:
            サポートされている場合True
        """
        return control_type in self.control_creators

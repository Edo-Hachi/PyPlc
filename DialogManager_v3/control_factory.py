"""
コントロールファクトリモジュール

JSON定義からコントロールを動的に生成するためのファクトリクラスを提供します。
"""
import pyxel
from typing import Dict, Any, Type, Optional, List, TypeVar, Generic
from .controls.control_base import ControlBase
from .controls.label_control import LabelControl
from .controls.button_control import ButtonControl
from .controls.textbox_control import TextBoxControl
from .controls.dropdown_control import DropdownControl
from .controls.listbox_control import ListBoxControl

# ジェネリック型変数
T = TypeVar('T', bound=ControlBase)


class ControlFactory:
    """
    コントロールを動的に生成するためのファクトリクラス
    
    このクラスは、JSON定義に基づいて適切なコントロールのインスタンスを生成します。
    """
    
    # コントロールタイプと対応するクラスのマッピング
    _control_types: Dict[str, Type[ControlBase]] = {
        'label': LabelControl,
        'button': ButtonControl,
        'textbox': TextBoxControl,
        'dropdown': DropdownControl,
        'listbox': ListBoxControl,
    }
    
    @classmethod
    def register_control_type(cls, control_type: str, control_class: Type[T]) -> None:
        """
        カスタムコントロールタイプを登録します。
        
        Args:
            control_type: コントロールのタイプ名（JSONで使用する値）
            control_class: コントロールのクラス（ControlBaseを継承している必要があります）
        """
        if not issubclass(control_class, ControlBase):
            raise ValueError(f"{control_class.__name__} は ControlBase を継承している必要があります")
        cls._control_types[control_type] = control_class
    
    @classmethod
    def create_control(cls, control_def: Dict[str, Any], **kwargs) -> ControlBase:
        """
        JSON定義からコントロールを生成します。
        
        Args:
            control_def: コントロールの定義（JSONオブジェクト）
            **kwargs: 追加の引数（親コントロールなど）
            
        Returns:
            ControlBase: 生成されたコントロールのインスタンス
            
        Raises:
            ValueError: 無効なコントロールタイプが指定された場合
        """
        # 必須フィールドのチェック
        if 'type' not in control_def:
            raise ValueError("コントロール定義に 'type' が指定されていません")
        
        control_type = control_def['type']
        if control_type not in cls._control_types:
            raise ValueError(f"未知のコントロールタイプ: {control_type}")
        
        # コントロールクラスを取得
        control_class = cls._control_types[control_type]
        
        # コントロールのプロパティを抽出
        control_kwargs = cls._extract_control_properties(control_def, control_type)
        
        # 追加の引数をマージ
        control_kwargs.update(kwargs)
        
        # コントロールを生成
        control = control_class(**control_kwargs)
        
        # イベントハンドラを設定
        cls._setup_event_handlers(control, control_def)
        
        return control
    
    @classmethod
    def _extract_control_properties(cls, control_def: Dict[str, Any], control_type: str) -> Dict[str, Any]:
        """
        コントロール定義からプロパティを抽出します。
        
        Args:
            control_def: コントロールの定義
            control_type: コントロールのタイプ
            
        Returns:
            Dict[str, Any]: 抽出されたプロパティの辞書
        """
        # 共通のプロパティ
        properties = {
            'x': control_def.get('x', 0),
            'y': control_def.get('y', 0),
            'width': control_def.get('width', 100),
            'visible': control_def.get('visible', True),
            'enabled': control_def.get('enabled', True),
            'id': control_def.get('id', ''),
            'tooltip': control_def.get('tooltip', ''),
        }
        
        # タイプ固有のプロパティ
        if control_type == 'label':
            properties.update({
                'text': control_def.get('text', ''),
                'color': control_def.get('color', pyxel.COLOR_WHITE),  # デフォルトは白
                'shadow': control_def.get('shadow', False),
                'shadow_color': control_def.get('shadow_color', pyxel.COLOR_BLACK),  # デフォルトは黒
                'align': control_def.get('align', 'left'),  # left, center, right
            })
        
        elif control_type == 'button':
            properties.update({
                'text': control_def.get('text', 'Button'),
                'color': control_def.get('color', pyxel.COLOR_WHITE),  # デフォルトは白
                'bg_color': control_def.get('bg_color', pyxel.COLOR_DARK_BLUE),  # デフォルトは濃青
                'hover_color': control_def.get('hover_color', pyxel.COLOR_GREEN),  # デフォルトは緑
                'pressed_color': control_def.get('pressed_color', pyxel.COLOR_RED),  # デフォルトは赤
                'disabled_color': control_def.get('disabled_color', pyxel.COLOR_GRAY),  # デフォルトは灰色
            })
        
        elif control_type == 'textbox':
            properties.update({
                'text': control_def.get('text', ''),
                'max_length': control_def.get('max_length', 255),
                'placeholder': control_def.get('placeholder', ''),
                'color': control_def.get('color', pyxel.COLOR_WHITE),  # デフォルトは白
                'bg_color': control_def.get('bg_color', pyxel.COLOR_BLACK),  # デフォルトは黒
                'cursor_color': control_def.get('cursor_color', pyxel.COLOR_WHITE),  # デフォルトは白
                'selection_color': control_def.get('selection_color', pyxel.COLOR_BROWN),  # デフォルトは茶
                'readonly': control_def.get('readonly', False),
                'password_char': control_def.get('password_char', ''),  # パスワード表示用の文字
            })
        
        elif control_type == 'dropdown':
            properties.update({
                'items': control_def.get('items', []),
                'selected_index': control_def.get('selected_index', -1),
                'button_text': control_def.get('button_text', 'Select...'),
                'color': control_def.get('color', pyxel.COLOR_WHITE),  # デフォルトは白
                'bg_color': control_def.get('bg_color', pyxel.COLOR_DARK_BLUE),  # デフォルトは濃青
                'hover_color': control_def.get('hover_color', pyxel.COLOR_GREEN),  # デフォルトは緑
                'disabled_color': control_def.get('disabled_color', pyxel.COLOR_GRAY),  # デフォルトは灰色
                'item_height': control_def.get('item_height', 20),
                'max_visible_items': control_def.get('max_visible_items', 5),
            })
        
        elif control_type == 'listbox':
            properties.update({
                'items': control_def.get('items', []),
                'selected_index': control_def.get('selected_index', -1),
                'color': control_def.get('color', pyxel.COLOR_WHITE),  # デフォルトは白
                'bg_color': control_def.get('bg_color', pyxel.COLOR_BLACK),  # デフォルトは黒
                'hover_color': control_def.get('hover_color', pyxel.COLOR_NAVY),  # デフォルトは濃青
                'selection_color': control_def.get('selection_color', pyxel.COLOR_BROWN),  # デフォルトは茶
                'item_height': control_def.get('item_height', 20),
                'multi_select': control_def.get('multi_select', False),
            })
        
        return properties
    
    @classmethod
    def _setup_event_handlers(cls, control: ControlBase, control_def: Dict[str, Any]) -> None:
        """
        コントロールにイベントハンドラを設定します。
        
        Args:
            control: イベントハンドラを設定するコントロール
            control_def: コントロールの定義
        """
        if 'on_click' in control_def and hasattr(control, 'on'):
            # クリックイベントハンドラを設定（例: 関数名を指定）
            # 実際の実装では、この関数名を解決する仕組みが必要です
            pass
        
        # その他のイベントハンドラも同様に設定可能
        # if 'on_change' in control_def:
        #     ...
        # if 'on_focus' in control_def:
        #     ...
        # if 'on_blur' in control_def:
        #     ...
    
    @classmethod
    def create_controls_from_json(cls, controls_def: List[Dict[str, Any]], **kwargs) -> List[ControlBase]:
        """
        JSON定義のリストから複数のコントロールを生成します。
        
        Args:
            controls_def: コントロール定義のリスト
            **kwargs: 追加の引数（親コントロールなど）
            
        Returns:
            List[ControlBase]: 生成されたコントロールのリスト
        """
        return [cls.create_control(control_def, **kwargs) for control_def in controls_def]


# シングルトンインスタンス
factory = ControlFactory()

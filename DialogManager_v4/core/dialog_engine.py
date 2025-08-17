"""
DialogManager v4 - Dialog Engine

JSON定義からダイアログを完全構築するエンジン
DESIGN.md完全準拠のコアエンジン
"""

import json
import os
import pyxel
from typing import Dict, Any, Optional
from .debug_system import DebugSystem
from .action_engine import ActionEngine
from .event_binder import EventBinder
from .coordinate_system import CoordinateSystem
from .base_dialog import BaseDialog
from ..controls import LabelControl, ButtonControl, TextBoxControl, DropdownControl, ListBoxControl


class DialogEngine:
    """JSON定義からダイアログを完全構築するエンジン"""
    
    def __init__(self, schema_validator=None, debug: bool = True):
        self.schema_validator = schema_validator
        self.action_engine = ActionEngine(debug=debug)
        self.event_binder = EventBinder(debug=debug)
        self.coordinate_system = CoordinateSystem(debug=debug)
        self.debug_system = DebugSystem("DialogEngine") if debug else None
    
    def create_dialog_from_json(self, json_file: str):
        """JSON定義からダイアログを完全構築"""
        if self.debug_system:
            self.debug_system.enter_context("create_dialog_from_json", {
                "json_file": json_file
            })
        
        try:
            # Phase 1: JSON読み込み・スキーマバリデーション
            dialog_definition = self._load_and_validate_json(json_file)
            
            # Phase 2: ダイアログ基本構造作成
            dialog = self._create_base_dialog(dialog_definition)
            
            # Phase 3: コントロール作成・配置
            self._create_and_place_controls(dialog, dialog_definition)
            
            # Phase 4: イベントバインディング
            self._bind_events(dialog, dialog_definition)
            
            # Phase 5: アクション設定
            self._setup_actions(dialog, dialog_definition)
            
            # Phase 6: 座標系確立
            self._establish_coordinate_system(dialog)
            
            if self.debug_system:
                self.debug_system.log("SUCCESS", "Dialog creation completed")
            
            return dialog
            
        except Exception as e:
            if self.debug_system:
                self.debug_system.error("Dialog creation failed", e)
            raise
        finally:
            if self.debug_system:
                self.debug_system.exit_context()
    
    def _load_and_validate_json(self, json_file: str) -> Dict[str, Any]:
        """JSON読み込み・バリデーション"""
        if self.debug_system:
            self.debug_system.log("INFO", f"Loading JSON: {json_file}")
        
        try:
            # ファイルパス解決
            if not os.path.isabs(json_file):
                # 相対パスの場合、DialogManager_v4ディレクトリからの相対パス
                script_dir = os.path.dirname(os.path.dirname(__file__))
                json_file = os.path.join(script_dir, json_file)
            
            # JSON読み込み
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if self.debug_system:
                self.debug_system.log("SUCCESS", f"JSON loaded successfully: {len(data)} keys")
            
            # TODO: スキーマバリデーション実装
            return data
            
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {json_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load JSON: {e}")
    
    def _create_base_dialog(self, definition: Dict[str, Any]):
        """ダイアログ基本構造作成"""
        if self.debug_system:
            self.debug_system.log("INFO", "Creating base dialog")
        
        dialog_def = definition.get("dialog", {})
        
        # ダイアログ基本プロパティ
        title = dialog_def.get("title", "")
        width = dialog_def.get("width", 300)
        height = dialog_def.get("height", 200)
        modal = dialog_def.get("modal", True)
        
        # 位置計算
        position = dialog_def.get("position", "center")
        if position == "center":
            try:
                # Pyxelが初期化されている場合のみ中央配置
                x = (pyxel.width - width) // 2
                y = (pyxel.height - height) // 2
            except:
                # Pyxel未初期化の場合はデフォルト位置
                x = (800 - width) // 2  # デフォルト画面サイズを想定
                y = (600 - height) // 2
        else:
            x = dialog_def.get("x", 0)
            y = dialog_def.get("y", 0)
        
        # BaseDialog作成
        dialog = BaseDialog(x, y, width, height, title, modal, debug=True)
        
        if self.debug_system:
            self.debug_system.log("SUCCESS", f"Dialog created: {title} at ({x},{y})")
        
        return dialog
    
    def _create_and_place_controls(self, dialog, definition: Dict[str, Any]):
        """コントロール作成・配置"""
        if self.debug_system:
            self.debug_system.log("INFO", "Creating and placing controls")
        
        controls_def = definition.get("controls", [])
        
        for control_def in controls_def:
            control_type = control_def.get("type")
            control_id = control_def.get("id")
            
            if not control_type or not control_id:
                if self.debug_system:
                    self.debug_system.log("WARNING", "Control missing type or id")
                continue
            
            # コントロール作成
            control = self._create_control(control_type, control_def)
            if control:
                dialog.add_control(control_id, control)
                if self.debug_system:
                    self.debug_system.log("SUCCESS", f"Control created: {control_type} '{control_id}'")
            else:
                if self.debug_system:
                    self.debug_system.log("ERROR", f"Failed to create control: {control_type}")
    
    def _create_control(self, control_type: str, control_def: Dict[str, Any]):
        """個別コントロール作成"""
        x = control_def.get("x", 0)
        y = control_def.get("y", 0)
        width = control_def.get("width", 0)
        height = control_def.get("height", 0)
        visible = control_def.get("visible", True)
        enabled = control_def.get("enabled", True)
        
        if control_type == "label":
            text = control_def.get("text", "")
            color = self._resolve_color(control_def.get("color", pyxel.COLOR_WHITE))
            return LabelControl(x, y, text, color, visible=visible, enabled=enabled)
        
        elif control_type == "button":
            text = control_def.get("text", "")
            color = self._resolve_color(control_def.get("color", pyxel.COLOR_WHITE))
            bg_color = self._resolve_color(control_def.get("bg_color", pyxel.COLOR_GRAY))
            return ButtonControl(x, y, width, height, text, color, bg_color, 
                               visible=visible, enabled=enabled)
        
        elif control_type == "textbox":
            text = control_def.get("text", "")
            color = self._resolve_color(control_def.get("color", pyxel.COLOR_WHITE))
            bg_color = self._resolve_color(control_def.get("bg_color", pyxel.COLOR_LIGHT_BLUE))
            readonly = control_def.get("readonly", False)
            placeholder = control_def.get("placeholder", "")
            return TextBoxControl(x, y, width, height, text, color, bg_color, 
                                readonly, placeholder, visible=visible, enabled=enabled)
        
        elif control_type == "dropdown":
            items = control_def.get("items", [])
            selected_index = control_def.get("selected_index", 0)
            color = self._resolve_color(control_def.get("color", pyxel.COLOR_WHITE))
            bg_color = self._resolve_color(control_def.get("bg_color", pyxel.COLOR_LIGHT_BLUE))
            return DropdownControl(x, y, width, height, items, selected_index, 
                                 color, bg_color, visible=visible, enabled=enabled)
        
        elif control_type == "listbox":
            items = control_def.get("items", [])
            selected_index = control_def.get("selected_index", -1)
            color = self._resolve_color(control_def.get("color", pyxel.COLOR_WHITE))
            bg_color = self._resolve_color(control_def.get("bg_color", pyxel.COLOR_BLACK))
            item_height = control_def.get("item_height", 12)
            return ListBoxControl(x, y, width, height, items, selected_index, 
                                color, bg_color, item_height, visible=visible, enabled=enabled)
        
        else:
            if self.debug_system:
                self.debug_system.log("WARNING", f"Unsupported control type: {control_type}")
            return None
    
    def _resolve_color(self, color_value):
        """色定数解決（JSON互換性とDESIGN.md準拠）"""
        # 既に数値の場合はそのまま返す（後方互換性）
        if isinstance(color_value, int):
            return color_value
        
        # 文字列の場合は色定数に変換
        if isinstance(color_value, str):
            color_map = {
                "COLOR_BLACK": pyxel.COLOR_BLACK,
                "COLOR_NAVY": pyxel.COLOR_NAVY,
                "COLOR_PURPLE": pyxel.COLOR_PURPLE,
                "COLOR_GREEN": pyxel.COLOR_GREEN,
                "COLOR_BROWN": pyxel.COLOR_BROWN,
                "COLOR_DARK_BLUE": pyxel.COLOR_DARK_BLUE,
                "COLOR_BLUE": pyxel.COLOR_DARK_BLUE,  # COLOR_BLUEはCOLOR_DARK_BLUEとして解釈
                "COLOR_LIGHT_BLUE": pyxel.COLOR_LIGHT_BLUE,
                "COLOR_WHITE": pyxel.COLOR_WHITE,
                "COLOR_RED": pyxel.COLOR_RED,
                "COLOR_ORANGE": pyxel.COLOR_ORANGE,
                "COLOR_YELLOW": pyxel.COLOR_YELLOW,
                "COLOR_LIME": pyxel.COLOR_LIME,
                "COLOR_CYAN": pyxel.COLOR_CYAN,
                "COLOR_GRAY": pyxel.COLOR_GRAY,
                "COLOR_PINK": pyxel.COLOR_PINK,
                "COLOR_PEACH": pyxel.COLOR_PEACH
            }
            
            # "pyxel.COLOR_WHITE" 形式も対応
            color_key = color_value.replace("pyxel.", "")
            if color_key in color_map:
                return color_map[color_key]
            
            if self.debug_system:
                self.debug_system.log("WARNING", f"Unknown color constant: {color_value}")
        
        # デフォルト値
        return pyxel.COLOR_WHITE
    
    def _bind_events(self, dialog, definition: Dict[str, Any]):
        """イベントバインディング"""
        if self.debug_system:
            self.debug_system.log("INFO", "Binding events")
        
        events_def = definition.get("events", {})
        
        for event_key, action_name in events_def.items():
            dialog.bind_event(event_key, action_name)
            if self.debug_system:
                self.debug_system.log("SUCCESS", f"Event bound: {event_key} -> {action_name}")
    
    def _setup_actions(self, dialog, definition: Dict[str, Any]):
        """アクション設定"""
        if self.debug_system:
            self.debug_system.log("INFO", "Setting up actions")
        
        actions_def = definition.get("actions", {})
        
        for action_name, action_definition in actions_def.items():
            dialog.add_action(action_name, action_definition)
            if self.debug_system:
                self.debug_system.log("SUCCESS", f"Action added: {action_name}")
    
    def _establish_coordinate_system(self, dialog):
        """座標系確立"""
        if self.debug_system:
            self.debug_system.log("INFO", "Establishing coordinate system")
        
        # 座標系は既にBaseDialogに統合済み
        if self.debug_system:
            self.debug_system.log("SUCCESS", "Coordinate system established")
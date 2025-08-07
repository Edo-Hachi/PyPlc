"""
JSONDialogLoader - JSON定義からダイアログを生成するローダー

PyPlc Ver3 Dialog System - Phase 1 MVP Implementation
JSON定義ファイルの読み込み・パース・バリデーション機能を提供
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path


class JSONDialogLoader:
    """
    JSON定義ファイルからダイアログ構造を生成するローダー
    
    機能:
    - JSON定義ファイルの読み込み
    - 基本的なバリデーション
    - エラーハンドリング
    - デフォルト値の適用
    """
    
    def __init__(self, definitions_path: str = "DialogManager/definitions"):
        """
        JSONDialogLoader初期化
        
        Args:
            definitions_path: JSON定義ファイルのベースパス
        """
        self.definitions_path = Path(definitions_path)
        self.loaded_definitions: Dict[str, Dict[str, Any]] = {}
        
        # デフォルト値定義
        self.default_dialog = {
            "title": "",
            "width": 200,
            "height": 150,
            "controls": []
        }
        
        self.default_control = {
            "id": "",
            "type": "label",
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 20,
            "text": "",
            "color": 7,  # pyxel.COLOR_WHITE
            "events": []
        }
    
    def load_dialog_definition(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        JSON定義ファイルを読み込み
        
        Args:
            filename: JSON定義ファイル名（拡張子含む）
            
        Returns:
            ダイアログ定義辞書（エラー時はNone）
        """
        # キャッシュチェック
        if filename in self.loaded_definitions:
            return self.loaded_definitions[filename]
        
        try:
            file_path = self.definitions_path / filename
            
            # ファイル存在チェック
            if not file_path.exists():
                print(f"Dialog definition file not found: {file_path}")
                return None
            
            # JSON読み込み
            with open(file_path, 'r', encoding='utf-8') as f:
                definition = json.load(f)
            
            # 基本バリデーション
            validated_definition = self._validate_definition(definition, filename)
            if validated_definition is None:
                return None
            
            # キャッシュに保存
            self.loaded_definitions[filename] = validated_definition
            
            return validated_definition
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error in {filename}: {e}")
            return None
        except Exception as e:
            print(f"Error loading dialog definition {filename}: {e}")
            return None
    
    def _validate_definition(self, definition: Dict[str, Any], filename: str) -> Optional[Dict[str, Any]]:
        """
        ダイアログ定義の基本バリデーション
        
        Args:
            definition: 読み込んだダイアログ定義
            filename: ファイル名（エラー表示用）
            
        Returns:
            バリデーション済み定義（エラー時はNone）
        """
        try:
            # 必須フィールドのチェックとデフォルト値適用
            validated = self.default_dialog.copy()
            validated.update(definition)
            
            # タイトルの型チェック
            if not isinstance(validated.get("title", ""), str):
                print(f"Warning: Invalid title type in {filename}, using default")
                validated["title"] = self.default_dialog["title"]
            
            # サイズの型・範囲チェック
            for size_key in ["width", "height"]:
                size_value = validated.get(size_key, self.default_dialog[size_key])
                if not isinstance(size_value, int) or size_value <= 0:
                    print(f"Warning: Invalid {size_key} in {filename}, using default")
                    validated[size_key] = self.default_dialog[size_key]
            
            # コントロール配列のチェック
            controls = validated.get("controls", [])
            if not isinstance(controls, list):
                print(f"Warning: Invalid controls format in {filename}, using empty list")
                validated["controls"] = []
            else:
                # 各コントロールのバリデーション
                validated_controls = []
                for i, control in enumerate(controls):
                    validated_control = self._validate_control(control, filename, i)
                    if validated_control is not None:
                        validated_controls.append(validated_control)
                validated["controls"] = validated_controls
            
            return validated
            
        except Exception as e:
            print(f"Validation error in {filename}: {e}")
            return None
    
    def _validate_control(self, control: Dict[str, Any], filename: str, index: int) -> Optional[Dict[str, Any]]:
        """
        コントロール定義のバリデーション
        
        Args:
            control: コントロール定義
            filename: ファイル名（エラー表示用）
            index: コントロールインデックス（エラー表示用）
            
        Returns:
            バリデーション済みコントロール定義（エラー時はNone）
        """
        try:
            if not isinstance(control, dict):
                print(f"Warning: Invalid control format at index {index} in {filename}")
                return None
            
            # デフォルト値適用
            validated = self.default_control.copy()
            validated.update(control)
            
            # 必須フィールドのチェック
            if not validated.get("id"):
                print(f"Warning: Control at index {index} in {filename} missing required 'id'")
                return None
            
            # 型チェック
            type_checks = {
                "id": str,
                "type": str,
                "x": int,
                "y": int,
                "width": int,
                "height": int,
                "text": str,
                "color": int
            }
            
            for field, expected_type in type_checks.items():
                value = validated.get(field)
                if value is not None and not isinstance(value, expected_type):
                    print(f"Warning: Invalid {field} type in control '{validated['id']}' in {filename}")
                    validated[field] = self.default_control[field]
            
            # イベント配列のチェック
            events = validated.get("events", [])
            if not isinstance(events, list):
                print(f"Warning: Invalid events format in control '{validated['id']}' in {filename}")
                validated["events"] = []
            else:
                # イベント名の文字列チェック
                validated_events = []
                for event in events:
                    if isinstance(event, str):
                        validated_events.append(event)
                    else:
                        print(f"Warning: Invalid event format in control '{validated['id']}' in {filename}")
                validated["events"] = validated_events
            
            return validated
            
        except Exception as e:
            print(f"Control validation error at index {index} in {filename}: {e}")
            return None
    
    def get_supported_control_types(self) -> List[str]:
        """
        サポートされているコントロールタイプの一覧を取得
        
        Returns:
            サポートされているコントロールタイプのリスト
        """
        return ["label", "button", "textinput"]  # Phase 1では基本コントロールのみ
    
    def clear_cache(self) -> None:
        """
        読み込みキャッシュをクリア
        """
        self.loaded_definitions.clear()
    
    def reload_definition(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        定義ファイルを強制再読み込み
        
        Args:
            filename: JSON定義ファイル名
            
        Returns:
            再読み込みされたダイアログ定義
        """
        # キャッシュから削除
        if filename in self.loaded_definitions:
            del self.loaded_definitions[filename]
        
        # 再読み込み
        return self.load_dialog_definition(filename)
    
    def validate_definition_file(self, filename: str) -> bool:
        """
        定義ファイルの妥当性をチェック（読み込まずに）
        
        Args:
            filename: JSON定義ファイル名
            
        Returns:
            ファイルが有効な場合True
        """
        definition = self.load_dialog_definition(filename)
        return definition is not None
    
    def list_available_definitions(self) -> List[str]:
        """
        利用可能な定義ファイルの一覧を取得
        
        Returns:
            定義ファイル名のリスト
        """
        try:
            if not self.definitions_path.exists():
                return []
            
            json_files = []
            for file_path in self.definitions_path.glob("*.json"):
                json_files.append(file_path.name)
            
            return sorted(json_files)
            
        except Exception as e:
            print(f"Error listing definition files: {e}")
            return []

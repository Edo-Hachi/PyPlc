"""
JSONダイアログローダーモジュール

JSONファイルからダイアログとそのコントロールを読み込むためのユーティリティを提供します。
"""
import json
import os
from typing import Dict, Any, List, Optional, Type, TypeVar, cast
from pathlib import Path

from .core.base_dialog import BaseDialog
from .control_factory import ControlFactory, factory

# ジェネリック型変数
T = TypeVar('T', bound=BaseDialog)


class JsonDialogLoader:
    """
    JSONファイルからダイアログを読み込むためのローダークラス
    
    このクラスは、JSON形式で定義されたダイアログを読み込み、
    BaseDialogを継承したダイアログクラスのインスタンスを生成します。
    """
    
    def __init__(self, base_path: str = None):
        """
        JsonDialogLoaderを初期化します。
        
        Args:
            base_path: JSONファイルを検索するベースパス（デフォルト: カレントディレクトリ）
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
    
    def load_dialog_definition(self, dialog_name: str) -> Dict[str, Any]:
        """
        ダイアログ定義をJSONファイルから読み込みます。
        
        Args:
            dialog_name: ダイアログ名（拡張子不要）
            
        Returns:
            Dict[str, Any]: ダイアログ定義の辞書
            
        Raises:
            FileNotFoundError: 指定された名前のダイアログ定義ファイルが見つからない場合
            json.JSONDecodeError: JSONの形式が無効な場合
        """
        # 拡張子が指定されていない場合は .json を追加
        if not dialog_name.lower().endswith('.json'):
            dialog_name += '.json'
        
        # ファイルパスを解決
        definitions_dir = self.base_path / 'definitions'
        file_path = definitions_dir / dialog_name
        
        # ファイルが存在するか確認
        if not file_path.exists():
            # 大文字小文字を区別せずに検索
            if definitions_dir.exists():
                for f in definitions_dir.iterdir():
                    if f.name.lower() == dialog_name.lower():
                        file_path = f
                        break
                else:
                    raise FileNotFoundError(
                        f"ダイアログ定義ファイル '{dialog_name}' が見つかりません。"
                        f"検索パス: {definitions_dir}"
                    )
        
        # JSONファイルを読み込む
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_dialog(self, dialog_def: Dict[str, Any], dialog_class: Type[T] = None, **kwargs) -> T:
        """
        ダイアログ定義からダイアログインスタンスを生成します。
        
        Args:
            dialog_def: ダイアログ定義の辞書
            dialog_class: 使用するダイアログクラス（Noneの場合はBaseDialogを使用）
            **kwargs: ダイアログコンストラクタに渡す追加の引数
            
        Returns:
            T: 生成されたダイアログインスタンス
            
        Raises:
            ValueError: ダイアログ定義が無効な場合
        """
        # 必須フィールドのチェック
        if 'title' not in dialog_def:
            raise ValueError("ダイアログ定義に 'title' が指定されていません")
        if 'width' not in dialog_def or 'height' not in dialog_def:
            raise ValueError("ダイアログ定義に 'width' または 'height' が指定されていません")
        
        # ダイアログクラスが指定されていない場合はBaseDialogを使用
        if dialog_class is None:
            dialog_class = BaseDialog
        
        # ダイアログのプロパティを抽出（BaseDialogが受け付けるパラメータのみ）
        dialog_params = {
            'x': dialog_def.get('x', 0),
            'y': dialog_def.get('y', 0),
            'width': dialog_def['width'],
            'height': dialog_def['height'],
            'title': dialog_def['title'],
            'modal': dialog_def.get('modal', False)
        }
        
        # 追加の引数をマージ
        dialog_params.update(kwargs)
        
        # ダイアログインスタンスを生成
        dialog = dialog_class(**dialog_params)
        
        # コントロールを読み込んで追加
        if 'controls' in dialog_def and isinstance(dialog_def['controls'], list):
            for control_def in dialog_def['controls']:
                try:
                    control = factory.create_control(control_def)
                    dialog.add_control(control)
                except Exception as e:
                    raise ValueError(
                        f"コントロールの作成に失敗しました: {control_def.get('id', 'unknown')}. "
                        f"エラー: {str(e)}"
                    )
        
        # ダイアログのイベントハンドラを設定
        self._setup_dialog_handlers(dialog, dialog_def)
        
        return dialog
    
    def load_dialog(self, dialog_name: str, dialog_class: Type[T] = None, **kwargs) -> T:
        """
        JSONファイルからダイアログを読み込んでインスタンスを生成します。
        
        Args:
            dialog_name: ダイアログ名（拡張子不要）
            dialog_class: 使用するダイアログクラス（Noneの場合はBaseDialogを使用）
            **kwargs: ダイアログコンストラクタに渡す追加の引数
            
        Returns:
            T: 生成されたダイアログインスタンス
        """
        dialog_def = self.load_dialog_definition(dialog_name)
        return self.create_dialog(dialog_def, dialog_class, **kwargs)
    
    def _setup_dialog_handlers(self, dialog: BaseDialog, dialog_def: Dict[str, Any]) -> None:
        """
        ダイアログのイベントハンドラを設定します。
        
        Args:
            dialog: イベントハンドラを設定するダイアログ
            dialog_def: ダイアログ定義の辞書
        """
        # ダイアログレベルのイベントハンドラを設定
        if 'on_show' in dialog_def:
            # 実際の実装では、この関数名を解決する仕組みが必要です
            pass
        
        if 'on_close' in dialog_def:
            # 実際の実装では、この関数名を解決する仕組みが必要です
            pass
        
        # その他のイベントハンドラも同様に設定可能
        # if 'on_resize' in dialog_def:
        #     ...
        # if 'on_move' in dialog_def:
        #     ...


# シングルトンインスタンス
dialog_loader = JsonDialogLoader()

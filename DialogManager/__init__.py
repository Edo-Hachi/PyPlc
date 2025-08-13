"""
PyPlc Ver3 DialogManager v2 - 統合ダイアログシステム

このパッケージは、PyPlc Ver3のすべてのダイアログ機能を統合管理します。
JSON駆動による柔軟なUI構成と、デバイス種別に応じた適切なダイアログ表示を提供します。

主要コンポーネント:
- DialogManager: メイン管理クラス
- BaseDialog: すべてのダイアログの基底クラス
- ControlFactory: UI コントロール生成ファクトリ
- JSONDialogLoader: JSON定義ファイル読み込み
- SchemaValidator: JSON スキーマ検証

作成日: 2025-08-13
バージョン: v2.0
"""

# メインクラスのエクスポート
from .core.dialog_manager import DialogManager
from .core.file_manager import FileManager
from .core.base_dialog import BaseDialog
from .core.control_factory import ControlFactory
from .core.json_dialog_loader import JSONDialogLoader
from .core.schema_validator import SchemaValidator

# ダイアログクラスのエクスポート
from .dialogs.data_register_dialog import DataRegisterDialog
from .dialogs.device_id_dialog import show_device_id_dialog
from .dialogs.timer_counter_dialog import show_timer_counter_preset_dialog
from .dialogs.file_load_dialog import FileLoadDialogJSON
from .dialogs.file_save_dialog import FileSaveDialogJSON

# バージョン情報
__version__ = "2.0.0"
__author__ = "PyPlc Ver3 Development Team"
__description__ = "統合ダイアログシステム - JSON駆動UI構成"

# パッケージレベルの設定
DEFAULT_DEFINITIONS_PATH = "DialogManager/definitions"
DEFAULT_SCHEMAS_PATH = "DialogManager/definitions/schemas"

__all__ = [
    # Core classes
    "DialogManager",
    "FileManager",
    "BaseDialog", 
    "ControlFactory",
    "JSONDialogLoader",
    "SchemaValidator",
    
    # Dialog classes
    "DataRegisterDialog",
    "show_device_id_dialog",
    "show_timer_counter_preset_dialog", 
    "FileLoadDialogJSON",
    "FileSaveDialogJSON",
    
    # Constants
    "DEFAULT_DEFINITIONS_PATH",
    "DEFAULT_SCHEMAS_PATH"
]
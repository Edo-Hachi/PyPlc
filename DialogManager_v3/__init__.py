"""
DialogManager_v3 パッケージ

PyPlc向けのモダンなダイアログ管理システムです。
JSON定義に基づいて動的にダイアログを生成・管理する機能を提供します。
"""

# バージョン情報
__version__ = "0.1.0"

# 主要なクラスと関数を公開
from .core.base_dialog import BaseDialog
from .core.file_manager_v3 import FileManagerV3
from .control_factory import ControlFactory, factory
from .json_dialog_loader import JsonDialogLoader, dialog_loader

# コントロールを直接インポートできるようにする
from .controls.control_base import ControlBase
from .controls.label_control import LabelControl
from .controls.button_control import ButtonControl
from .controls.textbox_control import TextBoxControl
from .controls.dropdown_control import DropdownControl
from .controls.listbox_control import ListBoxControl

# シンプルなエイリアス
Dialog = BaseDialog

__all__ = [
    # コアクラス
    'BaseDialog',
    'Dialog',
    'FileManagerV3',
    'ControlFactory',
    'factory',
    'JsonDialogLoader',
    'dialog_loader',
    
    # コントロール
    'ControlBase',
    'LabelControl',
    'ButtonControl',
    'TextBoxControl',
    'DropdownControl',
    'ListBoxControl',
]

"""
PyPlc Ver3 ダイアログシステム
統合ダイアログ管理とデバイスID編集機能

このモジュールは、main.pyからダイアログ処理を分離し、
保守性・拡張性・可読性を向上させる責任分離アーキテクチャを提供します。
"""

from .device_id_dialog import DeviceIDDialog, DialogState
from .dialog_manager import DialogManager

__all__ = [
    'DialogManager',
    'DeviceIDDialog', 
    'DialogState'
]
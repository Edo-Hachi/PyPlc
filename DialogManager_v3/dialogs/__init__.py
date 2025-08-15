"""
DialogManager_v3 - Dialogs Package

This package contains dialog implementations for the DialogManager_v3 system.
"""

from .file_load_dialog import FileLoadDialogJSON
from .file_save_dialog import FileSaveDialogJSON

__all__ = [
    'FileLoadDialogJSON',
    'FileSaveDialogJSON'
]

"""
DialogManager v4 - JSON Complete Definition Dialog System

JSON完全定義主義に基づくダイアログシステム
DESIGN.md準拠のクリーン実装

Created: 2025-08-15
Author: Claude (Sonnet 4)
"""

from .core.dialog_engine import DialogEngine
from .core.action_engine import ActionEngine
from .core.event_binder import EventBinder
from .core.coordinate_system import CoordinateSystem
from .core.debug_system import DebugSystem

__version__ = "4.0.0"
__author__ = "Claude (Sonnet 4)"
__description__ = "JSON Complete Definition Dialog System"

# メインエクスポート
__all__ = [
    "DialogEngine",
    "ActionEngine", 
    "EventBinder",
    "CoordinateSystem",
    "DebugSystem"
]
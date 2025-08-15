"""
DialogManager v4 - Coordinate System

座標系の明確な定義・変換・検証（v3の教訓活用）
バグ予防重視の座標計算システム
"""

from typing import Tuple, Optional
from .debug_system import DebugSystem


class CoordinateSystem:
    """座標系の明確な定義・変換・検証（バグ予防重視）"""
    
    def __init__(self, debug: bool = True):
        self.debug = DebugSystem("CoordinateSystem") if debug else None
        
    def screen_to_dialog(self, screen_x: int, screen_y: int, dialog) -> Tuple[int, int]:
        """画面座標 → ダイアログ座標（検証付き変換）"""
        if self.debug:
            self.debug.enter_context("screen_to_dialog", {
                "screen": (screen_x, screen_y),
                "dialog_pos": (dialog.x, dialog.y)
            })
            
        try:
            # 基本変換
            dialog_x = screen_x - dialog.x
            dialog_y = screen_y - dialog.y
            
            # 境界チェック
            if not self._is_valid_dialog_coords(dialog_x, dialog_y, dialog):
                if self.debug:
                    self.debug.log("WARNING", f"Coordinates outside dialog bounds: ({dialog_x}, {dialog_y})")
                
            result = (dialog_x, dialog_y)
            if self.debug:
                self.debug.log("SUCCESS", f"Converted to: {result}")
            return result
            
        except Exception as e:
            if self.debug:
                self.debug.error("Conversion failed", e)
            raise
        finally:
            if self.debug:
                self.debug.exit_context()
                
    def dialog_to_control(self, dialog_x: int, dialog_y: int, control) -> Tuple[int, int]:
        """ダイアログ座標 → コントロール座標（検証付き変換）"""
        if self.debug:
            self.debug.enter_context("dialog_to_control", {
                "dialog": (dialog_x, dialog_y),
                "control_pos": (control.x, control.y),
                "control_id": getattr(control, 'id', 'unknown')
            })
            
        try:
            control_x = dialog_x - control.x
            control_y = dialog_y - control.y
            
            # 境界チェック
            if not self._is_valid_control_coords(control_x, control_y, control):
                if self.debug:
                    self.debug.log("WARNING", f"Coordinates outside control bounds: ({control_x}, {control_y})")
                
            result = (control_x, control_y)
            if self.debug:
                self.debug.log("SUCCESS", f"Converted to: {result}")
            return result
            
        except Exception as e:
            if self.debug:
                self.debug.error("Conversion failed", e)
            raise
        finally:
            if self.debug:
                self.debug.exit_context()
                
    def is_inside_bounds(self, x: int, y: int, bounds_x: int, bounds_y: int, 
                        bounds_width: int, bounds_height: int, 
                        component_name: str = "Unknown") -> bool:
        """境界判定（明確なロジック・デバッグ対応）"""
        if self.debug:
            self.debug.enter_context("bounds_check", {
                "point": (x, y),
                "bounds": (bounds_x, bounds_y, bounds_width, bounds_height),
                "component": component_name
            })
            
        try:
            # 明確な境界計算
            inside = (bounds_x <= x < bounds_x + bounds_width and 
                     bounds_y <= y < bounds_y + bounds_height)
                     
            if self.debug:
                self.debug.log("RESULT", f"Inside bounds: {inside}")
            return inside
            
        finally:
            if self.debug:
                self.debug.exit_context()
                
    def _is_valid_dialog_coords(self, x: int, y: int, dialog) -> bool:
        """ダイアログ座標の妥当性チェック"""
        return (0 <= x < dialog.width and 0 <= y < dialog.height)
        
    def _is_valid_control_coords(self, x: int, y: int, control) -> bool:
        """コントロール座標の妥当性チェック"""
        return (0 <= x < control.width and 0 <= y < control.height)
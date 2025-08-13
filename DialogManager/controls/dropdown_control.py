"""
DropdownControl - ドロップダウン風選択コントロール
PyPlc Ver3 DialogManager - WindSurf改善組み込み版

既存ButtonControlをベースとした軽量実装
WindSurfレビュー対応項目:
- エラーハンドリング強化
- パフォーマンス最適化（再描画スキップ）
- 設定外部化
- ログシステム統合
"""

import pyxel
import logging
from typing import List, Dict, Any, Optional, Tuple
from DialogManager.core.control_factory import BaseControl
from config import DropdownControlConfig

logger = logging.getLogger(__name__)


class DropdownControl(BaseControl):
    """ドロップダウン風選択コントロール（WindSurf改善組み込み版）"""
    
    def __init__(self, control_id: str, x: int, y: int, width: int, height: int, 
                 options: List[Dict], **kwargs):
        try:
            super().__init__(control_id, x, y, width, height, **kwargs)
            
            # バリデーション強化（WindSurf提案）
            if not options:
                raise ValueError("Options list cannot be empty")
            
            for option in options:
                if 'value' not in option or 'label' not in option:
                    raise ValueError("Each option must have 'value' and 'label' keys")
            
            # 状態管理
            self.options = options
            self.selected_index = 0
            self.expanded = False
            self.hover_index = -1
            
            # パフォーマンス最適化（WindSurf提案）
            self.needs_redraw = True
            self._cached_display_rect = None
            self._last_mouse_pos = (-1, -1)
            
            # デフォルト値設定
            default_value = kwargs.get('default', options[0]['value'] if options else '')
            self._set_default_selection(default_value)
            
            logger.debug(f"DropdownControl '{control_id}' initialized with {len(options)} options")
            
        except Exception as e:
            logger.error(f"DropdownControl initialization failed: {e}")
            raise
    
    def _set_default_selection(self, default_value: str) -> None:
        """デフォルト選択値設定"""
        for i, option in enumerate(self.options):
            if option['value'] == default_value:
                self.selected_index = i
                break
    
    def handle_input(self, mouse_x: int, mouse_y: int, mouse_clicked: bool) -> None:
        """入力処理（エラーハンドリング強化版）"""
        try:
            if not self.visible or not self.enabled:
                return
                
            # パフォーマンス最適化: マウス位置変更時のみ処理
            if (mouse_x, mouse_y) == self._last_mouse_pos and not mouse_clicked:
                return
            self._last_mouse_pos = (mouse_x, mouse_y)
            
            # メインボタンクリック処理
            if self._is_main_button_clicked(mouse_x, mouse_y, mouse_clicked):
                self.expanded = not self.expanded
                self.hover_index = -1  # ホバー状態リセット
                self.invalidate()
                return
            
            # 展開時の選択肢処理
            if self.expanded:
                selected_index = self._get_clicked_option_index(mouse_x, mouse_y, mouse_clicked)
                if selected_index is not None:
                    self.selected_index = selected_index
                    self.expanded = False
                    self.emit('selection_changed', self.options[selected_index]['value'])
                    self.invalidate()
                    return
                
                # ホバー処理
                new_hover = self._get_hovered_option_index(mouse_x, mouse_y)
                if new_hover != self.hover_index:
                    self.hover_index = new_hover
                    self.invalidate()
            
            # 領域外クリックで折りたたみ
            if mouse_clicked and self.expanded and not self._is_dropdown_area(mouse_x, mouse_y):
                self.expanded = False
                self.hover_index = -1
                self.invalidate()
                
        except Exception as e:
            logger.error(f"Input handling error in {self.id}: {e}")
            # エラー時は安全な状態に復旧
            self.expanded = False
            self.hover_index = -1
    
    def _is_main_button_clicked(self, mouse_x: int, mouse_y: int, mouse_clicked: bool) -> bool:
        """メインボタンクリック判定"""
        if not mouse_clicked:
            return False
        
        # mouse_xとmouse_yはすでにダイアログ相対座標として渡されている
        return (self.x <= mouse_x <= self.x + self.width and 
                self.y <= mouse_y <= self.y + DropdownControlConfig.DEFAULT_HEIGHT)
    
    def _get_clicked_option_index(self, mouse_x: int, mouse_y: int, mouse_clicked: bool) -> Optional[int]:
        """クリックされた選択肢のインデックス取得"""
        if not mouse_clicked:
            return None
            
        list_start_y = self.y + DropdownControlConfig.DEFAULT_HEIGHT + 1
        
        for i, option in enumerate(self.options):
            item_y = list_start_y + i * DropdownControlConfig.DEFAULT_ITEM_HEIGHT
            
            # mouse_xとmouse_yはダイアログ相対座標として渡されている
            if (self.x <= mouse_x <= self.x + self.width and 
                item_y <= mouse_y <= item_y + DropdownControlConfig.DEFAULT_ITEM_HEIGHT):
                return i
        
        return None
    
    def _get_hovered_option_index(self, mouse_x: int, mouse_y: int) -> int:
        """ホバー中の選択肢インデックス取得"""
        list_start_y = self.y + DropdownControlConfig.DEFAULT_HEIGHT + 1
        
        for i, option in enumerate(self.options):
            item_y = list_start_y + i * DropdownControlConfig.DEFAULT_ITEM_HEIGHT
            
            # mouse_xとmouse_yはダイアログ相対座標として渡されている
            if (self.x <= mouse_x <= self.x + self.width and 
                item_y <= mouse_y <= item_y + DropdownControlConfig.DEFAULT_ITEM_HEIGHT):
                return i
        
        return -1
    
    def _is_dropdown_area(self, mouse_x: int, mouse_y: int) -> bool:
        """ドロップダウン全体の領域内判定"""
        if not self.expanded:
            return False
            
        # メインボタン + 展開リスト全体の領域
        total_height = (DropdownControlConfig.DEFAULT_HEIGHT + 
                       len(self.options) * DropdownControlConfig.DEFAULT_ITEM_HEIGHT + 1)
        
        # mouse_xとmouse_yはダイアログ相対座標として渡されている
        return (self.x <= mouse_x <= self.x + self.width and 
                self.y <= mouse_y <= self.y + total_height)
    
    def draw(self, dialog_x: int, dialog_y: int) -> None:
        """最適化された描画処理（WindSurf提案）"""
        try:
            # 初期表示問題修正: 常に描画を行う（パフォーマンス最適化は後で再検討）
            if not self.visible:
                return
                
            abs_x = dialog_x + self.x
            abs_y = dialog_y + self.y
            
            # メインボタン描画
            self._draw_main_button(abs_x, abs_y)
            
            # 展開時のみリスト描画
            if self.expanded:
                self._draw_options_list(abs_x, abs_y)
                
            # 描画完了時のみフラグをクリア
            if self.needs_redraw:
                self.needs_redraw = False
                print(f"[DropdownControl] {self.id} drawn successfully")
            
        except Exception as e:
            logger.error(f"Drawing error in {self.id}: {e}")
            # エラー時は最小限の表示
            self._draw_error_state(dialog_x + self.x, dialog_y + self.y)
    
    def _draw_main_button(self, x: int, y: int) -> None:
        """メインボタン描画"""
        # 背景・枠線
        pyxel.rect(x, y, self.width, DropdownControlConfig.DEFAULT_HEIGHT, 
                  DropdownControlConfig.BACKGROUND_COLOR)
        pyxel.rectb(x, y, self.width, DropdownControlConfig.DEFAULT_HEIGHT, 
                   DropdownControlConfig.BORDER_COLOR)
        
        # 選択中テキスト（長さ制限）
        if 0 <= self.selected_index < len(self.options):
            selected_text = self.options[self.selected_index]['label']
            # 幅に応じてテキストを制限
            max_chars = (self.width - 20) // 4  # 4ピクセル/文字、右側にアイコン用20px確保
            if len(selected_text) > max_chars:
                selected_text = selected_text[:max_chars-3] + "..."
            
            pyxel.text(x + DropdownControlConfig.TEXT_PADDING, 
                      y + (DropdownControlConfig.DEFAULT_HEIGHT - 6) // 2, 
                      selected_text, DropdownControlConfig.TEXT_COLOR)
        
        # ドロップダウンアイコン
        icon = DropdownControlConfig.DROPUP_ICON if self.expanded else DropdownControlConfig.DROPDOWN_ICON
        icon_x = x + self.width - 12
        icon_y = y + (DropdownControlConfig.DEFAULT_HEIGHT - 6) // 2
        pyxel.text(icon_x, icon_y, icon, pyxel.COLOR_YELLOW)
    
    def _draw_options_list(self, x: int, y: int) -> None:
        """選択肢リスト描画"""
        list_y = y + DropdownControlConfig.DEFAULT_HEIGHT + 1
        
        for i, option in enumerate(self.options):
            item_y = list_y + i * DropdownControlConfig.DEFAULT_ITEM_HEIGHT
            
            # 背景色（選択中/ホバー/通常）
            if i == self.selected_index:
                bg_color = DropdownControlConfig.SELECTED_COLOR
            elif i == self.hover_index:
                bg_color = DropdownControlConfig.HOVER_COLOR
            else:
                bg_color = pyxel.COLOR_BLACK
                
            # アイテム描画
            pyxel.rect(x, item_y, self.width, DropdownControlConfig.DEFAULT_ITEM_HEIGHT, bg_color)
            pyxel.rectb(x, item_y, self.width, DropdownControlConfig.DEFAULT_ITEM_HEIGHT, 
                       DropdownControlConfig.BORDER_COLOR)
            
            # テキスト（長さ制限）
            label_text = option['label']
            max_chars = (self.width - 8) // 4  # パディング考慮
            if len(label_text) > max_chars:
                label_text = label_text[:max_chars-3] + "..."
            
            pyxel.text(x + DropdownControlConfig.TEXT_PADDING, 
                      item_y + (DropdownControlConfig.DEFAULT_ITEM_HEIGHT - 6) // 2, 
                      label_text, DropdownControlConfig.TEXT_COLOR)
    
    def _draw_error_state(self, x: int, y: int) -> None:
        """エラー状態表示"""
        pyxel.rect(x, y, self.width, DropdownControlConfig.DEFAULT_HEIGHT, 
                  DropdownControlConfig.ERROR_COLOR)
        pyxel.rectb(x, y, self.width, DropdownControlConfig.DEFAULT_HEIGHT, 
                   pyxel.COLOR_WHITE)
        pyxel.text(x + DropdownControlConfig.TEXT_PADDING, 
                  y + (DropdownControlConfig.DEFAULT_HEIGHT - 6) // 2, 
                  "ERROR", pyxel.COLOR_WHITE)
    
    def invalidate(self) -> None:
        """再描画フラグ設定（WindSurf提案）"""
        self.needs_redraw = True
        self._cached_display_rect = None
    
    def get_selected_value(self) -> str:
        """選択値取得"""
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index]['value']
        return self.options[0]['value'] if self.options else ""
    
    def set_selected_value(self, value: str) -> None:
        """選択値設定"""
        for i, option in enumerate(self.options):
            if option['value'] == value:
                if i != self.selected_index:
                    self.selected_index = i
                    self.invalidate()
                    print(f"[DropdownControl] {self.id} selected value changed to: '{value}' (index {i})")
                else:
                    # 同じ値でも再描画フラグを設定（初期表示問題対策）
                    self.invalidate()
                    print(f"[DropdownControl] {self.id} selected value confirmed: '{value}' (index {i})")
                return
        print(f"[DropdownControl] {self.id} warning: value '{value}' not found in options")
    
    def get_selected_label(self) -> str:
        """選択中のラベル取得"""
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index]['label']
        return ""
    
    def set_options(self, options: List[Dict]) -> None:
        """選択肢更新"""
        try:
            if not options:
                raise ValueError("Options list cannot be empty")
                
            for option in options:
                if 'value' not in option or 'label' not in option:
                    raise ValueError("Each option must have 'value' and 'label' keys")
            
            self.options = options
            
            # 現在の選択が無効になった場合は最初の選択肢に戻す
            if self.selected_index >= len(options):
                self.selected_index = 0
            
            self.invalidate()
            logger.debug(f"DropdownControl '{self.id}' options updated to {len(options)} items")
            
        except Exception as e:
            logger.error(f"Failed to update options for {self.id}: {e}")
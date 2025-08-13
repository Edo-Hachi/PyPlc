# PyPlc Ver3 Dialog System - FileListControl
# Phase 3: ファイルリスト表示・選択コントロール
# 作成日: 2025-08-08

import pyxel
import os
import glob
from datetime import datetime
from typing import List, Optional, Dict, Any
from DialogManager.events.event_system import EventSystem

class FileListControl:
    """
    ファイルリスト表示・選択コントロール
    JSON定義対応、疎結合イベントシステム統合
    """
    
    def __init__(self, config: Dict[str, Any], event_system: EventSystem):
        """
        FileListControl初期化
        
        Args:
            config: JSON定義設定
            event_system: イベントシステム
        """
        self.id = config.get('id', 'file_list')
        self.x = config.get('x', 0)
        self.y = config.get('y', 0)
        self.width = config.get('width', 200)
        self.height = config.get('height', 150)
        self.file_pattern = config.get('file_pattern', '*.csv')
        self.directory = config.get('directory', './')
        self.show_details = config.get('show_details', True)
        
        self.event_system = event_system
        
        # ファイルリスト管理
        self.files: List[Dict[str, Any]] = []
        self.selected_index = -1
        self.scroll_offset = 0
        self.visible_items = (self.height - 20) // 12  # 1行12px想定
        
        # マウス・キーボード状態
        self.is_focused = False
        self.last_click_time = 0
        self.double_click_threshold = 0.5  # 500ms
        
        # 表示設定
        self.item_height = 12
        self.header_height = 15
        
        # ファイルリスト初期読み込み
        self.refresh_file_list()
    
    def refresh_file_list(self) -> None:
        """ファイルリスト更新"""
        try:
            # ディレクトリ存在確認
            if not os.path.exists(self.directory):
                self.files = []
                return
            
            # ファイル検索
            pattern_path = os.path.join(self.directory, self.file_pattern)
            file_paths = glob.glob(pattern_path)
            
            self.files = []
            for file_path in sorted(file_paths):
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    file_info = {
                        'name': os.path.basename(file_path),
                        'path': file_path,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'display_name': os.path.splitext(os.path.basename(file_path))[0]
                    }
                    self.files.append(file_info)
            
            # 選択インデックス調整
            if self.selected_index >= len(self.files):
                self.selected_index = len(self.files) - 1 if self.files else -1
                
        except Exception as e:
            print(f"FileListControl: ファイルリスト更新エラー: {e}")
            self.files = []
    
    def handle_input(self, mouse_x: int, mouse_y: int) -> None:
        """入力処理（マウス・キーボード）"""
        # 相対座標での範囲チェック
        local_x = mouse_x - self.x
        local_y = mouse_y - self.y
        
        # マウスクリック処理
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if 0 <= local_x <= self.width and 0 <= local_y <= self.height:
                self._handle_mouse_click(local_x, local_y)
        
        # キーボード処理（フォーカス時のみ）
        if self.is_focused:
            self._handle_keyboard_input()
    
    def _handle_mouse_click(self, local_x: int, local_y: int) -> None:
        """マウスクリック処理"""
        # フォーカス設定
        if not self.is_focused:
            self.is_focused = True
            self.event_system.emit('focus', {'control_id': self.id})
        
        # ヘッダー領域チェック
        if local_y < self.header_height:
            return
        
        # アイテム選択処理
        item_y = local_y - self.header_height
        clicked_index = (item_y // self.item_height) + self.scroll_offset
        
        if 0 <= clicked_index < len(self.files):
            current_time = pyxel.frame_count / 30.0  # 30FPS想定
            
            # ダブルクリック判定
            if (clicked_index == self.selected_index and 
                current_time - self.last_click_time < self.double_click_threshold):
                # ダブルクリック: 即座に選択確定
                self.event_system.emit('file_double_clicked', {
                    'control_id': self.id,
                    'file_info': self.files[clicked_index]
                })
            else:
                # シングルクリック: 選択変更
                old_selection = self.selected_index
                self.selected_index = clicked_index
                
                if old_selection != self.selected_index:
                    self.event_system.emit('selection_changed', {
                        'control_id': self.id,
                        'selected_index': self.selected_index,
                        'file_info': self.files[self.selected_index] if self.selected_index >= 0 else None
                    })
                
                self.event_system.emit('file_selected', {
                    'control_id': self.id,
                    'file_info': self.files[self.selected_index]
                })
            
            self.last_click_time = current_time
    
    def _handle_keyboard_input(self) -> None:
        """キーボード入力処理"""
        if not self.files:
            return
        
        old_selection = self.selected_index
        
        # 上下キーでの選択移動
        if pyxel.btnp(pyxel.KEY_UP):
            if self.selected_index > 0:
                self.selected_index -= 1
                self._adjust_scroll()
        
        elif pyxel.btnp(pyxel.KEY_DOWN):
            if self.selected_index < len(self.files) - 1:
                self.selected_index += 1
                self._adjust_scroll()
        
        # Home/Endキー
        elif pyxel.btnp(pyxel.KEY_HOME):
            self.selected_index = 0
            self.scroll_offset = 0
        
        elif pyxel.btnp(pyxel.KEY_END):
            self.selected_index = len(self.files) - 1
            self._adjust_scroll()
        
        # Page Up/Down
        elif pyxel.btnp(pyxel.KEY_PAGEUP):
            self.selected_index = max(0, self.selected_index - self.visible_items)
            self._adjust_scroll()
        
        elif pyxel.btnp(pyxel.KEY_PAGEDOWN):
            self.selected_index = min(len(self.files) - 1, 
                                    self.selected_index + self.visible_items)
            self._adjust_scroll()
        
        # Enterキー: 選択確定
        elif pyxel.btnp(pyxel.KEY_RETURN):
            if self.selected_index >= 0:
                self.event_system.emit('file_double_clicked', {
                    'control_id': self.id,
                    'file_info': self.files[self.selected_index]
                })
        
        # 選択変更イベント発火
        if old_selection != self.selected_index and self.selected_index >= 0:
            self.event_system.emit('selection_changed', {
                'control_id': self.id,
                'selected_index': self.selected_index,
                'file_info': self.files[self.selected_index]
            })
    
    def _adjust_scroll(self) -> None:
        """スクロール位置調整"""
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.visible_items:
            self.scroll_offset = self.selected_index - self.visible_items + 1
        
        # 範囲チェック
        max_scroll = max(0, len(self.files) - self.visible_items)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
    
    def draw(self, dialog_x: int, dialog_y: int) -> None:
        """描画処理"""
        abs_x = dialog_x + self.x
        abs_y = dialog_y + self.y
        
        # 背景・枠線
        pyxel.rect(abs_x, abs_y, self.width, self.height, pyxel.COLOR_WHITE)
        pyxel.rectb(abs_x, abs_y, self.width, self.height, 
                   pyxel.COLOR_CYAN if self.is_focused else pyxel.COLOR_GRAY)
        
        # ヘッダー描画
        self._draw_header(abs_x, abs_y)
        
        # ファイルリスト描画
        self._draw_file_list(abs_x, abs_y)
        
        # スクロールバー描画（必要に応じて）
        if len(self.files) > self.visible_items:
            self._draw_scrollbar(abs_x, abs_y)
    
    def _draw_header(self, abs_x: int, abs_y: int) -> None:
        """ヘッダー描画"""
        header_y = abs_y + 2
        
        # ヘッダー背景
        pyxel.rect(abs_x + 1, abs_y + 1, self.width - 2, self.header_height - 1, 
                  pyxel.COLOR_LIGHT_BLUE)
        
        # ヘッダーテキスト
        file_count_text = f"Files: {len(self.files)}"
        pyxel.text(abs_x + 4, header_y + 3, file_count_text, pyxel.COLOR_BLACK)
        
        if self.selected_index >= 0:
            selection_text = f"({self.selected_index + 1}/{len(self.files)})"
            text_x = abs_x + self.width - len(selection_text) * 4 - 4
            pyxel.text(text_x, header_y + 3, selection_text, pyxel.COLOR_BLACK)
    
    def _draw_file_list(self, abs_x: int, abs_y: int) -> None:
        """ファイルリスト描画"""
        list_start_y = abs_y + self.header_height
        
        for i in range(self.visible_items):
            file_index = self.scroll_offset + i
            if file_index >= len(self.files):
                break
            
            file_info = self.files[file_index]
            item_y = list_start_y + i * self.item_height
            
            # 選択ハイライト
            if file_index == self.selected_index:
                pyxel.rect(abs_x + 1, item_y, self.width - 2, self.item_height, 
                          pyxel.COLOR_YELLOW)
            
            # ファイル名表示
            display_name = file_info['display_name']
            max_chars = (self.width - 8) // 4  # 4px per character
            if len(display_name) > max_chars:
                display_name = display_name[:max_chars-3] + "..."
            
            text_color = pyxel.COLOR_BLACK if file_index == self.selected_index else pyxel.COLOR_DARK_BLUE
            pyxel.text(abs_x + 4, item_y + 2, display_name, text_color)
    
    def _draw_scrollbar(self, abs_x: int, abs_y: int) -> None:
        """スクロールバー描画"""
        scrollbar_x = abs_x + self.width - 8
        scrollbar_y = abs_y + self.header_height
        scrollbar_height = self.height - self.header_height
        
        # スクロールバー背景
        pyxel.rect(scrollbar_x, scrollbar_y, 6, scrollbar_height, pyxel.COLOR_GRAY)
        
        # スクロールハンドル
        if len(self.files) > 0:
            handle_height = max(10, (self.visible_items * scrollbar_height) // len(self.files))
            handle_y = scrollbar_y + (self.scroll_offset * (scrollbar_height - handle_height)) // max(1, len(self.files) - self.visible_items)
            
            pyxel.rect(scrollbar_x + 1, handle_y, 4, handle_height, pyxel.COLOR_DARK_BLUE)
    
    def get_selected_file(self) -> Optional[Dict[str, Any]]:
        """選択中のファイル情報取得"""
        if 0 <= self.selected_index < len(self.files):
            return self.files[self.selected_index]
        return None
    
    def set_focus(self, focused: bool) -> None:
        """フォーカス設定"""
        if self.is_focused != focused:
            self.is_focused = focused
            if focused:
                self.event_system.emit('focus', {'control_id': self.id})
            else:
                self.event_system.emit('blur', {'control_id': self.id})

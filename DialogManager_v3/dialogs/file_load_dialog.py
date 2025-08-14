"""
PyPlc Ver3 Dialog System - FileLoadDialog (JSON版)
ファイルシステム抽象化レイヤーを使用したファイル読み込みダイアログ
"""
import os
import pyxel
from typing import Optional, Dict, Any, List, Callable, Tuple
from pathlib import Path

from ..core.base_dialog import BaseDialog
from ..control_factory import ControlFactory
from ..json_dialog_loader import JsonDialogLoader
from ..filesystem import (
    FileSystemError,
    FileType,
    FileInfo,
    fs
)
from ..filesystem.utils import (
    FileOperations,
    FileFilter,
    FileSorter
)

class FileLoadDialogJSON(BaseDialog):
    """
    JSON定義によるファイル読み込みダイアログ
    ファイルシステム抽象化レイヤーを使用した実装
    """
    
    def __init__(self, 
                 initial_dir: Optional[str] = None, 
                 file_pattern: str = "*",
                 title: str = "Open File",
                 width: int = 480,
                 height: int = 320):
        """
        ファイルロードダイアログの初期化
        
        Args:
            initial_dir: 初期ディレクトリパス（Noneの場合はカレントディレクトリ）
            file_pattern: ファイルパターン（例: "*.txt"）
            title: ダイアログタイトル
            width: ダイアログ幅
            height: ダイアログ高さ
        """
        # ダイアログ設定（座標とサイズを最初に設定）
        x = (pyxel.width - width) // 2
        y = (pyxel.height - height) // 2
        super().__init__(x=x, y=y, width=width, height=height, title=title)
        
        # ファイルシステム設定
        self.current_dir = os.path.abspath(initial_dir or ".")
        self.file_pattern = file_pattern
        self.file_list: List[FileInfo] = []
        self.filtered_files: List[FileInfo] = []
        self.selected_index = -1
        self.scroll_offset = 0
        
        # コントロール
        self.controls = {}
        self._setup_controls()
        
        # 初期ファイルリスト読み込み
        self.refresh_file_list()
    
    def _setup_controls(self):
        """ダイアログのコントロールを設定"""
        # ディレクトリパス表示
        self.controls['path_label'] = {
            'type': 'label',
            'x': 10,
            'y': 10,
            'text': 'Folder:',
            'color': 7
        }
        
        self.controls['path_text'] = {
            'type': 'textbox',
            'x': 60,
            'y': 8,
            'width': self.width - 140,
            'height': 18,
            'text': self.current_dir,
            'readonly': True,
            'id': 'path_text'
        }
        
        # 親ディレクトリボタン
        self.controls['up_button'] = {
            'type': 'button',
            'x': self.width - 70,
            'y': 8,
            'width': 60,
            'height': 18,
            'text': 'Up',
            'id': 'up_button'
        }
        
        # ファイルリスト
        self.controls['file_list'] = {
            'type': 'listbox',
            'x': 10,
            'y': 40,
            'width': self.width - 20,
            'height': self.height - 120,
            'items': [],
            'id': 'file_list'
        }
        
        # ファイル名フィルター
        self.controls['filter_label'] = {
            'type': 'label',
            'x': 10,
            'y': self.height - 70,
            'text': 'File Type:',
            'color': 7
        }
        
        self.controls['filter_combo'] = {
            'type': 'dropdown',
            'x': 100,
            'y': self.height - 72,
            'width': 200,
            'height': 20,
            'items': ['All Files (*.*)', 'Text Files (*.txt)', 'CSV Files (*.csv)', 'Image Files (*.png, *.jpg)'],
            'selected_index': 0,
            'id': 'filter_combo'
        }
        
        # ファイル名入力
        self.controls['filename_label'] = {
            'type': 'label',
            'x': 10,
            'y': self.height - 40,
            'text': 'File Name:',
            'color': 7
        }
        
        self.controls['filename_input'] = {
            'type': 'textbox',
            'x': 100,
            'y': self.height - 42,
            'width': self.width - 210,
            'height': 20,
            'text': '',
            'id': 'filename_input'
        }
        
        # ボタン
        self.controls['open_button'] = {
            'type': 'button',
            'x': self.width - 200,
            'y': self.height - 80,
            'width': 90,
            'height': 28,
            'text': 'Open',
            'id': 'open_button'
        }
        
        self.controls['cancel_button'] = {
            'type': 'button',
            'x': self.width - 100,
            'y': self.height - 80,
            'width': 90,
            'height': 28,
            'text': 'Cancel',
            'id': 'cancel_button'
        }
        
        # ダイアログ結果
        self.selected_file = None
        self.cancelled = False
        
        # 初期状態では非表示
        self.visible = False
    
    def refresh_file_list(self):
        """ファイルリストを更新"""
        try:
            # ディレクトリ内のファイルとフォルダを取得
            all_entries = FileOperations.list_directory(
                self.current_dir,
                sort_key=FileSorter.by_type
            )
            
            # フィルタリング（ディレクトリとファイルに分ける）
            self.file_list = all_entries
            self._apply_filters()
            
        except FileSystemError as e:
            print(f"Error listing directory: {e}")
            self.file_list = []
            self.filtered_files = []
    
    def _apply_filters(self):
        """現在のフィルターを適用"""
        try:
            # ディレクトリは常に表示
            dirs = [e for e in self.file_list if e.file_type == FileType.DIRECTORY]
            
            # ファイルはパターンでフィルタリング
            files = [e for e in self.file_list if e.file_type == FileType.FILE]
            
            # ファイル名パターンフィルターを適用
            if self.file_pattern != "*":
                pattern = self.file_pattern.lstrip('*')
                files = [f for f in files if f.name.endswith(pattern)]
            
            # 結合してソート（ディレクトリ→ファイル、名前順）
            self.filtered_files = sorted(
                dirs + files,
                key=lambda x: (x.file_type != FileType.DIRECTORY, x.name.lower())
            )
            
            # リストボックスを更新
            if 'file_list' in self.controls:
                self.controls['file_list']['items'] = [
                    f"[DIR] {f.name}" if f.file_type == FileType.DIRECTORY else f.name 
                    for f in self.filtered_files
                ]
                
        except Exception as e:
            print(f"Error applying filters: {e}")
            self.filtered_files = []
    
    def update(self):
        """ダイアログの状態を更新"""
        # マウスイベント処理
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self._handle_mouse_click(pyxel.mouse_x, pyxel.mouse_y)
        
        # キーボードイベント処理
        if pyxel.btnp(pyxel.KEY_UP):
            self._move_selection(-1)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self._move_selection(1)
        elif pyxel.btnp(pyxel.KEY_RETURN):
            self._on_open_clicked()
        elif pyxel.btnp(pyxel.KEY_ESCAPE):
            self._on_cancel_clicked()
    
    def _handle_mouse_click(self, x: int, y: int):
        """マウスクリックを処理"""
        # ダイアログ外をクリックした場合は無視
        if not (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height):
            return
            
        # リストボックス内のクリックを処理
        listbox = self.controls.get('file_list')
        if listbox and self._is_point_in_rect(x, y, listbox):
            self._on_file_selected(x, y, listbox)
            return
        
        # ボタンクリックを処理
        for ctrl_id, ctrl in self.controls.items():
            if ctrl['type'] == 'button' and self._is_point_in_rect(x, y, ctrl):
                if ctrl_id == 'up_button':
                    self._on_up_clicked()
                elif ctrl_id == 'open_button':
                    self._on_open_clicked()
                elif ctrl_id == 'cancel_button':
                    self._on_cancel_clicked()
                return
    
    def _on_file_selected(self, x: int, y: int, listbox: Dict):
        """ファイル/フォルダが選択されたときの処理"""
        # クリック位置から選択されたアイテムのインデックスを計算
        item_height = 12  # 1行の高さ
        relative_y = y - (self.y + listbox['y'])
        clicked_index = (relative_y // item_height) + self.scroll_offset
        
        if 0 <= clicked_index < len(self.filtered_files):
            self.selected_index = clicked_index
            selected = self.filtered_files[clicked_index]
            
            # ダブルクリックのチェック（簡易実装）
            if hasattr(self, '_last_click_time') and (pyxel.frame_count - self._last_click_time) < 10:
                if selected.file_type == FileType.DIRECTORY:
                    self._change_directory(selected.path)
                else:
                    self._on_open_clicked()
            
            self._last_click_time = pyxel.frame_count
            
            # ファイル名を入力フィールドに設定
            if 'filename_input' in self.controls and selected.file_type == FileType.FILE:
                self.controls['filename_input']['text'] = selected.name
    
    def _on_up_clicked(self):
        """「上へ」ボタンがクリックされたときの処理"""
        parent_dir = os.path.dirname(self.current_dir)
        if parent_dir != self.current_dir:  # ルートディレクトリでない場合
            self._change_directory(parent_dir)
    
    def _on_open_clicked(self):
        """「開く」ボタンがクリックされたときの処理"""
        if 0 <= self.selected_index < len(self.filtered_files):
            selected = self.filtered_files[self.selected_index]
            if selected.file_type == FileType.DIRECTORY:
                self._change_directory(selected.path)
            else:
                self.selected_file = selected.path
                self.visible = False
        else:
            # 入力フィールドからファイル名を取得
            filename = self.controls.get('filename_input', {}).get('text', '').strip()
            if filename:
                file_path = os.path.join(self.current_dir, filename)
                if os.path.exists(file_path):
                    self.selected_file = file_path
                    self.visible = False
    
    def _on_cancel_clicked(self):
        """「キャンセル」ボタンがクリックされたときの処理"""
        self.cancelled = True
        self.visible = False
    
    def _change_directory(self, new_dir: str):
        """ディレクトリを変更"""
        try:
            if os.path.isdir(new_dir):
                self.current_dir = os.path.abspath(new_dir)
                if 'path_text' in self.controls:
                    self.controls['path_text']['text'] = self.current_dir
                self.selected_index = -1
                self.refresh_file_list()
        except Exception as e:
            print(f"Error changing directory: {e}")
    
    def _move_selection(self, delta: int):
        """選択位置を移動"""
        if not self.filtered_files:
            return
            
        new_index = max(0, min(len(self.filtered_files) - 1, self.selected_index + delta))
        if new_index != self.selected_index:
            self.selected_index = new_index
            selected = self.filtered_files[new_index]
            
            # ファイル名を入力フィールドに設定
            if 'filename_input' in self.controls and selected.file_type == FileType.FILE:
                self.controls['filename_input']['text'] = selected.name
            
            # スクロール位置を調整
            self._ensure_visible(new_index)
    
    def _ensure_visible(self, index: int):
        """指定したインデックスが表示されるようにスクロール位置を調整"""
        if not hasattr(self, 'controls') or 'file_list' not in self.controls:
            return
            
        listbox = self.controls['file_list']
        visible_items = listbox['height'] // 12  # 1行の高さが12pxと仮定
        
        if index < self.scroll_offset:
            self.scroll_offset = index
        elif index >= self.scroll_offset + visible_items:
            self.scroll_offset = index - visible_items + 1
    
    def _is_point_in_rect(self, x: int, y: int, rect: Dict) -> bool:
        """点が矩形内にあるかどうかを判定（絶対座標）"""
        abs_x = self.x + rect['x']
        abs_y = self.y + rect['y']
        return (abs_x <= x < abs_x + rect['width'] and 
                abs_y <= y < abs_y + rect['height'])
    
    def draw(self):
        """ダイアログを描画"""
        # 背景
        pyxel.rect(self.x, self.y, self.width, self.height, pyxel.COLOR_NAVY)
        pyxel.rectb(self.x, self.y, self.width, self.height, pyxel.COLOR_WHITE)
        
        # タイトルバー
        pyxel.rect(self.x, self.y, self.width, 20, pyxel.COLOR_DARK_BLUE)
        pyxel.text(self.x + 10, self.y + 6, self.title, pyxel.COLOR_WHITE)
        
        # コントロールを描画
        self._draw_controls()
        
        # ファイルリストを描画
        self._draw_file_list()
    
    def _draw_controls(self):
        """コントロールを描画"""
        for ctrl in self.controls.values():
            if ctrl['type'] == 'label':
                pyxel.text(
                    self.x + ctrl['x'], 
                    self.y + ctrl['y'], 
                    ctrl['text'], 
                    ctrl.get('color', pyxel.COLOR_WHITE)
                )
            elif ctrl['type'] == 'textbox':
                self._draw_textbox(ctrl)
            elif ctrl['type'] == 'button':
                self._draw_button(ctrl)
    
    def _draw_textbox(self, ctrl: Dict):
        """テキストボックスを描画"""
        x = self.x + ctrl['x']
        y = self.y + ctrl['y']
        
        # 背景
        pyxel.rect(x, y, ctrl['width'], ctrl['height'], pyxel.COLOR_BLACK)
        pyxel.rectb(x, y, ctrl['width'], ctrl['height'], pyxel.COLOR_WHITE)
        
        # テキスト
        text = ctrl.get('text', '')
        pyxel.text(x + 4, y + 4, text, pyxel.COLOR_WHITE)
    
    def _draw_button(self, ctrl: Dict):
        """ボタンを描画"""
        x = self.x + ctrl['x']
        y = self.y + ctrl['y']
        
        # ボタンの状態に応じた色
        is_hovered = self._is_mouse_over(ctrl)
        color = pyxel.COLOR_GREEN if is_hovered else pyxel.COLOR_PURPLE
        
        # ボタン本体
        pyxel.rect(x, y, ctrl['width'], ctrl['height'], color)
        pyxel.rectb(x, y, ctrl['width'], ctrl['height'], pyxel.COLOR_WHITE)
        
        # ボタンテキスト（中央揃え）
        text = ctrl['text']
        text_width = len(text) * 4  # 1文字4pxと仮定
        text_x = x + (ctrl['width'] - text_width) // 2
        text_y = y + (ctrl['height'] - 6) // 2 + 1
        pyxel.text(text_x, text_y, text, pyxel.COLOR_WHITE)
    
    def _draw_file_list(self):
        """ファイルリストを描画"""
        listbox = self.controls.get('file_list', {})
        if not listbox:
            return
            
        x = self.x + listbox['x']
        y = self.y + listbox['y']
        width = listbox['width']
        height = listbox['height']
        
        # リストボックスの背景
        pyxel.rect(x, y, width, height, pyxel.COLOR_BLACK)
        pyxel.rectb(x, y, width, height, pyxel.COLOR_WHITE)
        
        # スクロールバーが必要かどうか
        item_height = 12
        visible_items = height // item_height
        total_items = len(self.filtered_files)
        
        if total_items > visible_items:
            # スクロールバーを描画
            scrollbar_width = 8
            scrollbar_x = x + width - scrollbar_width - 1
            
            # スクロールバーのつまみの位置と高さを計算
            thumb_height = max(20, (visible_items * height) // total_items)
            thumb_pos = y + 1 + (self.scroll_offset * (height - thumb_height)) // max(1, total_items - visible_items)
            
            # スクロールバーの背景
            pyxel.rect(scrollbar_x + 1, y + 1, scrollbar_width - 1, height - 2, pyxel.COLOR_NAVY)
            # つまみ
            pyxel.rect(scrollbar_x + 1, thumb_pos, scrollbar_width - 1, thumb_height, pyxel.COLOR_GREEN)
        
        # 表示範囲内のアイテムだけを描画
        start_idx = self.scroll_offset
        end_idx = min(start_idx + visible_items, total_items)
        
        for i in range(start_idx, end_idx):
            item_y = y + (i - start_idx) * item_height + 2
            item = self.filtered_files[i]
            
            # 選択中のアイテムはハイライト
            if i == self.selected_index:
                pyxel.rect(x + 1, item_y - 1, width - 2, item_height - 1, pyxel.COLOR_GREEN)
            
            # アイコン（簡易的なテキスト表現）
            icon = "[DIR]" if item.file_type == FileType.DIRECTORY else "[FILE]"
            pyxel.text(x + 4, item_y, icon, pyxel.COLOR_WHITE if i != self.selected_index else pyxel.COLOR_BLACK)
            
            # ファイル名
            name = item.name
            if item.file_type == FileType.DIRECTORY:
                name += "/"
            
            # テキストが長すぎる場合は省略
            max_width = width - 40
            if len(name) * 4 > max_width:  # 1文字4pxと仮定
                name = name[:max_width // 4 - 3] + "..."
            
            pyxel.text(x + 24, item_y, name, pyxel.COLOR_WHITE if i != self.selected_index else pyxel.COLOR_BLACK)
    
    def _is_mouse_over(self, ctrl: Dict) -> bool:
        """マウスがコントロールの上にあるかどうかを判定"""
        abs_x = self.x + ctrl['x']
        abs_y = self.y + ctrl['y']
        return (abs_x <= pyxel.mouse_x < abs_x + ctrl['width'] and 
                abs_y <= pyxel.mouse_y < abs_y + ctrl['height'])
    
    def show_load_dialog(self) -> tuple:
        """
        既存FileManagerとの互換性のためのメソッド
        ファイル読み込みダイアログを表示し、結果を返す
        
        Returns:
            tuple: (success: bool, file_path: str)
                success: ファイル選択が成功した場合True
                file_path: 選択されたファイルのパス（失敗時は空文字列）
        """
        try:
            # ダイアログを表示状態に設定
            self.visible = True
            self.cancelled = False
            self.selected_file = None
            
            # メインループ（既存システムと同じ方式）
            while self.visible:
                self.update()
                
                # 画面をクリアして描画
                pyxel.cls(pyxel.COLOR_BLACK)
                self.draw()
                pyxel.flip()
                
                # ESCキーで強制終了
                if pyxel.btnp(pyxel.KEY_ESCAPE):
                    self.cancelled = True
                    self.visible = False
            
            # 結果を返す（既存FileManagerと同じインターフェース）
            if self.cancelled or self.selected_file is None:
                return False, ""  # キャンセル時
            else:
                return True, self.selected_file  # 成功時
                
        except Exception as e:
            print(f"[FileLoadDialogJSON] Error in show_load_dialog: {e}")
            return False, ""

def show_file_load_dialog(
    initial_dir: Optional[str] = None,
    file_pattern: str = "*",
    title: str = "Open File"
) -> Optional[str]:
    """
    ファイル読み込みダイアログを表示する便利関数
    
    Args:
        initial_dir: 初期ディレクトリパス
        file_pattern: ファイルパターン（例: "*.txt"）
        title: ダイアログタイトル
        
    Returns:
        選択されたファイルのパス、またはキャンセル時はNone
    """
    dialog = FileLoadDialogJSON(
        initial_dir=initial_dir,
        file_pattern=file_pattern,
        title=title
    )
    
    # ダイアログを表示状態に設定
    dialog.visible = True
    
    # メインループ（簡易実装）
    try:
        while dialog.visible:
            dialog.update()
            
            # 画面をクリアして描画
            pyxel.cls(pyxel.COLOR_BLACK)
            dialog.draw()
            pyxel.flip()
            
            # ESCキーで強制終了
            if pyxel.btnp(pyxel.KEY_ESCAPE):
                dialog.cancelled = True
                dialog.visible = False
                
    except Exception as e:
        print(f"Dialog error: {e}")
        return None
    
    return dialog.selected_file if not dialog.cancelled else None

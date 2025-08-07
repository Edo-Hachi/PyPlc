# PyPlc Ver3 File Dialog System  
# 作成日: 2025-08-07
# 目標: ファイル保存・読み込み専用ダイアログ実装

import pyxel
import os
import glob
from datetime import datetime
from typing import Tuple, List, Optional
from .file_validation import FileNameValidator

class FileSaveDialog:
    """
    ファイル保存専用ダイアログ
    Ver3画面サイズ（384x384）対応の中央配置ダイアログ
    """
    
    def __init__(self):
        self.dialog_w = 280
        self.dialog_h = 160
        self.dialog_x = (384 - self.dialog_w) // 2  # Ver3画面サイズ対応
        self.dialog_y = (384 - self.dialog_h) // 2
        
        self.input_text = ""
        self.cursor_pos = 0
        self.is_visible = False
        self.result_ready = False
        self.save_success = False
        self.selected_filename = ""
        self.error_message = ""
        
    def show(self, default_name: str = "my_circuit") -> Tuple[bool, str]:
        """
        保存ダイアログ表示・実行
        
        Args:
            default_name: デフォルトファイル名
            
        Returns:
            Tuple[bool, str]: (success, filename)
        """
        self.input_text = default_name
        self.cursor_pos = len(default_name)
        self.is_visible = True
        self.result_ready = False
        self.save_success = False
        self.error_message = ""
        
        # モーダルループ
        while self.is_visible and not self.result_ready:
            self._handle_input()
            self._draw()
            pyxel.flip()
            
        return self.save_success, self.selected_filename
    
    def _handle_input(self) -> None:
        """キーボード入力処理（Ver1準拠）"""
        
        # ESCキー: キャンセル
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.is_visible = False
            self.result_ready = True
            self.save_success = False
            return
            
        # Enterキー: 保存実行
        if pyxel.btnp(pyxel.KEY_RETURN):
            self._execute_save()
            return
            
        # バックスペース: 文字削除
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            if self.cursor_pos > 0:
                self.input_text = (self.input_text[:self.cursor_pos-1] + 
                                 self.input_text[self.cursor_pos:])
                self.cursor_pos -= 1
                self.error_message = ""
                
        # Delete: 右文字削除
        if pyxel.btnp(pyxel.KEY_DELETE):
            if self.cursor_pos < len(self.input_text):
                self.input_text = (self.input_text[:self.cursor_pos] + 
                                 self.input_text[self.cursor_pos+1:])
                self.error_message = ""
                
        # カーソル移動
        if pyxel.btnp(pyxel.KEY_LEFT) and self.cursor_pos > 0:
            self.cursor_pos -= 1
        if pyxel.btnp(pyxel.KEY_RIGHT) and self.cursor_pos < len(self.input_text):
            self.cursor_pos += 1
        if pyxel.btnp(pyxel.KEY_HOME):
            self.cursor_pos = 0
        if pyxel.btnp(pyxel.KEY_END):
            self.cursor_pos = len(self.input_text)
            
        # 文字入力（0-9, A-Z, 記号）
        self._handle_character_input()
    
    def _handle_character_input(self) -> None:
        """文字入力処理"""
        new_char = ""
        
        # 数字入力
        for i in range(10):
            if pyxel.btnp(pyxel.KEY_0 + i):
                new_char = str(i)
                break
                
        # アルファベット入力（大文字）
        if not new_char:
            for i in range(26):
                if pyxel.btnp(pyxel.KEY_A + i):
                    new_char = chr(ord('A') + i)
                    break
                    
        # 記号入力（限定的）
        if not new_char:
            if pyxel.btnp(pyxel.KEY_MINUS):
                new_char = "_"  # ハイフンをアンダースコアに変換
            elif pyxel.btnp(pyxel.KEY_SPACE):
                new_char = "_"  # スペースをアンダースコアに変換
                
        # 文字が入力された場合
        if new_char and len(self.input_text) < FileNameValidator.MAX_LENGTH:
            self.input_text = (self.input_text[:self.cursor_pos] + 
                             new_char + 
                             self.input_text[self.cursor_pos:])
            self.cursor_pos += 1
            self.error_message = ""
    
    def _execute_save(self) -> None:
        """保存実行処理"""
        # ファイル名バリデーション
        is_valid, error_msg = FileNameValidator.validate(self.input_text)
        if not is_valid:
            self.error_message = error_msg
            return
            
        # .csv拡張子付加
        filename = FileNameValidator.add_csv_extension(self.input_text)
        
        # 既存ファイルチェック・上書き確認
        if os.path.exists(filename):
            if not self._show_overwrite_confirm(filename):
                return  # 上書き拒否
                
        self.selected_filename = filename
        self.save_success = True
        self.result_ready = True
        self.is_visible = False
    
    def _show_overwrite_confirm(self, filename: str) -> bool:
        """上書き確認ダイアログ"""
        confirm_dialog = OverwriteConfirmDialog()
        return confirm_dialog.show(filename)
    
    def _draw(self) -> None:
        """ダイアログ描画"""
        # 背景暗転効果（縞模様）
        for y in range(0, 384, 4):
            pyxel.line(0, y, 384, y, pyxel.COLOR_BLACK)
        for x in range(0, 384, 4):
            pyxel.line(x, 0, x, 384, pyxel.COLOR_BLACK)
            
        # ダイアログ本体
        pyxel.rect(self.dialog_x, self.dialog_y, self.dialog_w, self.dialog_h, pyxel.COLOR_DARK_BLUE)
        pyxel.rectb(self.dialog_x, self.dialog_y, self.dialog_w, self.dialog_h, pyxel.COLOR_WHITE)
        
        # タイトル
        title = "Save Circuit File"
        title_x = self.dialog_x + (self.dialog_w - len(title) * 4) // 2
        pyxel.text(title_x, self.dialog_y + 10, title, pyxel.COLOR_WHITE)
        
        # ファイル名入力ラベル
        pyxel.text(self.dialog_x + 20, self.dialog_y + 35, "Enter filename:", pyxel.COLOR_WHITE)
        
        # テキスト入力ボックス
        input_x = self.dialog_x + 20
        input_y = self.dialog_y + 55
        input_w = self.dialog_w - 40
        input_h = 20
        
        pyxel.rect(input_x, input_y, input_w, input_h, pyxel.COLOR_WHITE)
        pyxel.rectb(input_x, input_y, input_w, input_h, pyxel.COLOR_BLACK)
        
        # 入力テキスト表示
        if self.input_text:
            pyxel.text(input_x + 4, input_y + 6, self.input_text, pyxel.COLOR_BLACK)
            
        # カーソル描画（点滅効果）
        if pyxel.frame_count % 60 < 30:  # 0.5秒間隔で点滅
            cursor_x = input_x + 4 + self.cursor_pos * 4
            pyxel.line(cursor_x, input_y + 2, cursor_x, input_y + 16, pyxel.COLOR_RED)
            
        # 拡張子表示
        pyxel.text(self.dialog_x + 20, self.dialog_y + 85, "Extension: .csv (auto)", pyxel.COLOR_GRAY)
        
        # エラーメッセージ表示
        if self.error_message:
            pyxel.text(self.dialog_x + 20, self.dialog_y + 100, self.error_message, pyxel.COLOR_RED)
            
        # ボタン
        self._draw_buttons()
        
    def _draw_buttons(self) -> None:
        """OK/Cancelボタン描画"""
        # OKボタン
        ok_x = self.dialog_x + 60
        ok_y = self.dialog_y + self.dialog_h - 35
        ok_w = 50
        ok_h = 25
        
        pyxel.rect(ok_x, ok_y, ok_w, ok_h, pyxel.COLOR_GREEN)
        pyxel.rectb(ok_x, ok_y, ok_w, ok_h, pyxel.COLOR_WHITE)
        pyxel.text(ok_x + 18, ok_y + 9, "OK", pyxel.COLOR_WHITE)
        
        # Cancelボタン
        cancel_x = self.dialog_x + 170
        cancel_y = ok_y
        
        pyxel.rect(cancel_x, cancel_y, ok_w, ok_h, pyxel.COLOR_RED)
        pyxel.rectb(cancel_x, cancel_y, ok_w, ok_h, pyxel.COLOR_WHITE)
        pyxel.text(cancel_x + 10, cancel_y + 9, "Cancel", pyxel.COLOR_WHITE)
        
        # 操作ヒント
        hint_y = self.dialog_y + self.dialog_h - 10
        pyxel.text(self.dialog_x + 20, hint_y, "Enter:Save  ESC:Cancel", pyxel.COLOR_GRAY)


class FileLoadDialog:
    """
    ファイル読み込み専用ダイアログ
    CSVファイル一覧表示・選択機能
    """
    
    def __init__(self):
        self.dialog_w = 320
        self.dialog_h = 240
        self.dialog_x = (384 - self.dialog_w) // 2
        self.dialog_y = (384 - self.dialog_h) // 2
        
        self.csv_files: List[str] = []
        self.selected_index = 0
        self.is_visible = False
        self.result_ready = False
        self.load_success = False
        self.selected_filename = ""
        
    def show(self) -> Tuple[bool, str]:
        """
        読み込みダイアログ表示・実行
        
        Returns:
            Tuple[bool, str]: (success, filename)
        """
        # CSVファイル検索（全CSVファイル対象）
        self.csv_files = glob.glob("*.csv")
        self.csv_files.sort(key=os.path.getctime, reverse=True)  # 新しい順
        
        if not self.csv_files:
            # CSVファイルが存在しない場合
            NoFilesDialog().show()
            return False, ""
            
        self.selected_index = 0
        self.is_visible = True
        self.result_ready = False
        self.load_success = False
        
        # モーダルループ
        while self.is_visible and not self.result_ready:
            self._handle_input()
            self._draw()
            pyxel.flip()
            
        return self.load_success, self.selected_filename
    
    def _handle_input(self) -> None:
        """キーボード入力処理"""
        
        # ESCキー: キャンセル
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.is_visible = False
            self.result_ready = True
            self.load_success = False
            return
            
        # Enterキー: 読み込み実行
        if pyxel.btnp(pyxel.KEY_RETURN):
            if self.csv_files:
                self.selected_filename = self.csv_files[self.selected_index]
                self.load_success = True
                self.result_ready = True
                self.is_visible = False
            return
            
        # 上下矢印: ファイル選択
        if pyxel.btnp(pyxel.KEY_UP) and self.selected_index > 0:
            self.selected_index -= 1
        if pyxel.btnp(pyxel.KEY_DOWN) and self.selected_index < len(self.csv_files) - 1:
            self.selected_index += 1
            
    def _draw(self) -> None:
        """ダイアログ描画"""
        # 背景暗転効果
        for y in range(0, 384, 4):
            pyxel.line(0, y, 384, y, pyxel.COLOR_BLACK)
        for x in range(0, 384, 4):
            pyxel.line(x, 0, x, 384, pyxel.COLOR_BLACK)
            
        # ダイアログ本体
        pyxel.rect(self.dialog_x, self.dialog_y, self.dialog_w, self.dialog_h, pyxel.COLOR_DARK_BLUE)
        pyxel.rectb(self.dialog_x, self.dialog_y, self.dialog_w, self.dialog_h, pyxel.COLOR_WHITE)
        
        # タイトル
        title = "Load Circuit File"
        title_x = self.dialog_x + (self.dialog_w - len(title) * 4) // 2
        pyxel.text(title_x, self.dialog_y + 10, title, pyxel.COLOR_WHITE)
        
        # ファイル選択ラベル
        pyxel.text(self.dialog_x + 20, self.dialog_y + 35, "Select file:", pyxel.COLOR_WHITE)
        
        # ファイルリスト表示
        self._draw_file_list()
        
        # 選択ファイル情報表示
        self._draw_file_info()
        
        # ボタン・操作ヒント
        self._draw_buttons()
        
    def _draw_file_list(self) -> None:
        """ファイルリスト描画"""
        list_x = self.dialog_x + 20
        list_y = self.dialog_y + 55
        list_w = self.dialog_w - 40
        list_h = 120
        
        # リスト背景
        pyxel.rect(list_x, list_y, list_w, list_h, pyxel.COLOR_WHITE)
        pyxel.rectb(list_x, list_y, list_w, list_h, pyxel.COLOR_BLACK)
        
        # ファイル項目表示（最大14行）
        max_visible = min(14, len(self.csv_files))
        start_index = max(0, self.selected_index - 6)  # 選択項目を中央付近に
        
        for i in range(max_visible):
            file_index = start_index + i
            if file_index >= len(self.csv_files):
                break
                
            item_y = list_y + 4 + i * 8
            filename = self.csv_files[file_index]
            display_name = FileNameValidator.get_display_name(filename)
            
            # 選択状態表示
            if file_index == self.selected_index:
                # 選択ハイライト
                pyxel.rect(list_x + 2, item_y - 1, list_w - 4, 9, pyxel.COLOR_CYAN)
                pyxel.text(list_x + 6, item_y, f"> {display_name}", pyxel.COLOR_BLACK)
            else:
                pyxel.text(list_x + 6, item_y, f"  {display_name}", pyxel.COLOR_BLACK)
                
    def _draw_file_info(self) -> None:
        """選択ファイル情報表示"""
        if not self.csv_files:
            return
            
        filename = self.csv_files[self.selected_index]
        
        # ファイル情報取得
        try:
            file_stat = os.stat(filename)
            file_size = file_stat.st_size
            file_time = datetime.fromtimestamp(file_stat.st_mtime)
            
            size_text = f"Size: {file_size}B"
            time_text = f"Modified: {file_time.strftime('%m/%d %H:%M')}"
            
        except Exception:
            size_text = "Size: Unknown"
            time_text = "Modified: Unknown"
            
        # 情報表示
        info_y = self.dialog_y + 185
        pyxel.text(self.dialog_x + 20, info_y, size_text, pyxel.COLOR_WHITE)
        pyxel.text(self.dialog_x + 160, info_y, time_text, pyxel.COLOR_WHITE)
        
    def _draw_buttons(self) -> None:
        """ボタン・操作ヒント描画"""
        # OKボタン
        ok_x = self.dialog_x + 70
        ok_y = self.dialog_y + self.dialog_h - 35
        ok_w = 50
        ok_h = 25
        
        pyxel.rect(ok_x, ok_y, ok_w, ok_h, pyxel.COLOR_GREEN)
        pyxel.rectb(ok_x, ok_y, ok_w, ok_h, pyxel.COLOR_WHITE)
        pyxel.text(ok_x + 18, ok_y + 9, "OK", pyxel.COLOR_WHITE)
        
        # Cancelボタン
        cancel_x = self.dialog_x + 200
        
        pyxel.rect(cancel_x, ok_y, ok_w, ok_h, pyxel.COLOR_RED)
        pyxel.rectb(cancel_x, ok_y, ok_w, ok_h, pyxel.COLOR_WHITE)
        pyxel.text(cancel_x + 10, ok_y + 9, "Cancel", pyxel.COLOR_WHITE)
        
        # 操作ヒント
        hint_y = self.dialog_y + self.dialog_h - 10
        pyxel.text(self.dialog_x + 20, hint_y, "Arrow:Select  Enter:Load  ESC:Cancel", pyxel.COLOR_GRAY)


class OverwriteConfirmDialog:
    """上書き確認ダイアログ"""
    
    def __init__(self):
        self.dialog_w = 260
        self.dialog_h = 120
        self.dialog_x = (384 - self.dialog_w) // 2
        self.dialog_y = (384 - self.dialog_h) // 2
        
    def show(self, filename: str) -> bool:
        """
        上書き確認ダイアログ表示
        
        Args:
            filename: 対象ファイル名
            
        Returns:
            bool: True=上書き許可, False=キャンセル
        """
        is_visible = True
        overwrite_confirmed = False
        result_ready = False
        
        while is_visible and not result_ready:
            # 入力処理
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_Y):
                overwrite_confirmed = True
                result_ready = True
            elif pyxel.btnp(pyxel.KEY_ESCAPE) or pyxel.btnp(pyxel.KEY_N):
                overwrite_confirmed = False
                result_ready = True
                
            # 描画
            self._draw(filename)
            pyxel.flip()
            
        return overwrite_confirmed
        
    def _draw(self, filename: str) -> None:
        """確認ダイアログ描画"""
        # 背景暗転
        for y in range(0, 384, 4):
            pyxel.line(0, y, 384, y, pyxel.COLOR_BLACK)
            
        # ダイアログ本体
        pyxel.rect(self.dialog_x, self.dialog_y, self.dialog_w, self.dialog_h, pyxel.COLOR_DARK_BLUE)
        pyxel.rectb(self.dialog_x, self.dialog_y, self.dialog_w, self.dialog_h, pyxel.COLOR_WHITE)
        
        # タイトル
        title = "File Exists"
        title_x = self.dialog_x + (self.dialog_w - len(title) * 4) // 2
        pyxel.text(title_x, self.dialog_y + 15, title, pyxel.COLOR_WHITE)
        
        # メッセージ
        display_name = FileNameValidator.get_display_name(filename)
        msg1 = f"'{display_name}' already exists"
        msg2 = "Do you want to overwrite it?"
        
        msg1_x = self.dialog_x + (self.dialog_w - len(msg1) * 4) // 2
        msg2_x = self.dialog_x + (self.dialog_w - len(msg2) * 4) // 2
        
        pyxel.text(msg1_x, self.dialog_y + 40, msg1, pyxel.COLOR_WHITE)
        pyxel.text(msg2_x, self.dialog_y + 55, msg2, pyxel.COLOR_WHITE)
        
        # ボタン
        overwrite_x = self.dialog_x + 50
        cancel_x = self.dialog_x + 150
        button_y = self.dialog_y + 80
        
        # Overwriteボタン
        pyxel.rect(overwrite_x, button_y, 70, 25, pyxel.COLOR_YELLOW)
        pyxel.rectb(overwrite_x, button_y, 70, 25, pyxel.COLOR_WHITE)
        pyxel.text(overwrite_x + 8, button_y + 9, "Overwrite", pyxel.COLOR_BLACK)
        
        # Cancelボタン  
        pyxel.rect(cancel_x, button_y, 50, 25, pyxel.COLOR_RED)
        pyxel.rectb(cancel_x, button_y, 50, 25, pyxel.COLOR_WHITE)
        pyxel.text(cancel_x + 10, button_y + 9, "Cancel", pyxel.COLOR_WHITE)


class NoFilesDialog:
    """CSVファイルが存在しない場合のエラーダイアログ"""
    
    def show(self) -> None:
        """エラーダイアログ表示"""
        dialog_w = 220
        dialog_h = 100
        dialog_x = (384 - dialog_w) // 2
        dialog_y = (384 - dialog_h) // 2
        
        is_visible = True
        
        while is_visible:
            # 入力処理
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_ESCAPE):
                is_visible = False
                
            # 描画
            # 背景暗転
            for y in range(0, 384, 4):
                pyxel.line(0, y, 384, y, pyxel.COLOR_BLACK)
                
            # ダイアログ本体
            pyxel.rect(dialog_x, dialog_y, dialog_w, dialog_h, pyxel.COLOR_DARK_BLUE)
            pyxel.rectb(dialog_x, dialog_y, dialog_w, dialog_h, pyxel.COLOR_WHITE)
            
            # メッセージ
            title = "No Files Found"
            title_x = dialog_x + (dialog_w - len(title) * 4) // 2
            pyxel.text(title_x, dialog_y + 20, title, pyxel.COLOR_WHITE)
            
            msg = "No circuit files to load"
            msg_x = dialog_x + (dialog_w - len(msg) * 4) // 2
            pyxel.text(msg_x, dialog_y + 40, msg, pyxel.COLOR_WHITE)
            
            # OKボタン
            ok_x = dialog_x + (dialog_w - 50) // 2
            ok_y = dialog_y + 60
            
            pyxel.rect(ok_x, ok_y, 50, 25, pyxel.COLOR_GREEN)
            pyxel.rectb(ok_x, ok_y, 50, 25, pyxel.COLOR_WHITE)
            pyxel.text(ok_x + 18, ok_y + 9, "OK", pyxel.COLOR_WHITE)
            
            pyxel.flip()
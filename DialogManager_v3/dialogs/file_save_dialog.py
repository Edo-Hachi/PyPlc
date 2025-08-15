"""
PyPlc Ver3 Dialog System - FileSaveDialog (JSON版)
DialogManager_v3用ファイル保存ダイアログ
Phase Fパターン（TextBoxControl統合）を適用した実装
"""
import os
import re
import pyxel
from typing import Optional, Tuple
from pathlib import Path

from ..core.base_dialog import BaseDialog
from ..control_factory import ControlFactory
from ..json_dialog_loader import JsonDialogLoader
from ..controls.textbox_control import TextBoxControl


class FileSaveDialogJSON(BaseDialog):
    """
    JSON定義によるファイル保存ダイアログ
    Phase Fパターン適用: TextBoxControl統合による高度なファイル名編集機能
    """
    
    def __init__(self, 
                 default_filename: str = "my_circuit",
                 title: str = "Save Circuit File", 
                 width: int = 340,
                 height: int = 280):
        """
        ファイル保存ダイアログの初期化
        
        Args:
            default_filename: デフォルトファイル名
            title: ダイアログタイトル
            width: ダイアログ幅（PyPlc Ver3最適化済み）
            height: ダイアログ高さ（PyPlc Ver3最適化済み）
        """
        # ダイアログ設定（LoadDialogと同じサイズ・位置計算）
        x = (pyxel.width - width) // 2
        y = (pyxel.height - height) // 2
        
        super().__init__(title=title, x=x, y=y, width=width, height=height)
        
        # ファイル保存関連の状態
        self.default_filename = default_filename
        self.input_filename = default_filename
        self.dialog_result = None
        self.error_message = ""
        
        # TextBoxControl統合（Phase Fパターン）
        self.filename_textbox: Optional[TextBoxControl] = None
        
        # コントロールファクトリとJSONローダー
        self.control_factory = ControlFactory()
        self.json_loader = JsonDialogLoader()
        
        # コントロール辞書（FileLoadDialogJSONパターン）
        self.controls = {}
        
        # ダイアログレイアウトを構築
        self._setup_dialog_layout()
        
        print(f"[FileSaveDialogJSON] Initialized: {title} ({width}x{height})")
    
    def _setup_dialog_layout(self) -> None:
        """
        ダイアログレイアウトを構築
        LoadDialogと同様の構造で保存用にカスタマイズ
        """
        # ファイル名ラベル
        self._add_label("filename_label", 20, 30, 80, 20, "File name:", pyxel.COLOR_WHITE)
        
        # ファイル名入力（TextBoxControl使用・Phase Fパターン）
        self.filename_textbox = TextBoxControl(
            x=20, y=55, width=300, height=25,
            max_length=50,
            input_filter="filename_safe"  # Phase Fで実装されたフィルター
        )
        # Phase Fパターン: 高度API使用
        self.filename_textbox.suggest_filename(self.default_filename, ".csv")
        
        # コントロール辞書にも追加（FileLoadDialogJSONパターン）
        self.controls["filename_input"] = {
            "type": "textbox",
            "x": 20, "y": 55, "width": 300, "height": 25,
            "text": self.default_filename, "max_length": 50
        }
        
        # 拡張子説明ラベル
        self._add_label("extension_label", 20, 90, 300, 20, 
                       "File will be saved as: [filename].csv", pyxel.COLOR_YELLOW)
        
        # ステータスメッセージ
        self._add_label("status_label", 20, 115, 300, 20, 
                       "Enter filename and click Save", pyxel.COLOR_WHITE)
        
        # エラーメッセージ（初期は非表示）
        self._add_label("error_label", 20, 140, 300, 20, "", pyxel.COLOR_RED)
        self.controls["error_label"]["visible"] = False
        
        # 保存ボタン
        self._add_button("save_button", 70, 190, 80, 30, "Save",
                        pyxel.COLOR_GREEN, pyxel.COLOR_LIME)
        
        # キャンセルボタン  
        self._add_button("cancel_button", 190, 190, 80, 30, "Cancel",
                        pyxel.COLOR_GRAY, pyxel.COLOR_LIGHT_BLUE)
        
        # イベント設定
        self._setup_events()
    
    def _add_label(self, control_id: str, x: int, y: int, width: int, height: int, 
                   text: str, color: int):
        """ラベル追加のヘルパーメソッド（FileLoadDialogJSONパターン）"""
        self.controls[control_id] = {
            "type": "label",
            "x": x, "y": y, "width": width, "height": height,
            "text": text, "color": color
        }
        return self.controls[control_id]
    
    def _add_button(self, control_id: str, x: int, y: int, width: int, height: int, 
                    text: str, bg_color: int, hover_color: int):
        """ボタン追加のヘルパーメソッド（FileLoadDialogJSONパターン）"""
        self.controls[control_id] = {
            "type": "button",
            "x": x, "y": y, "width": width, "height": height,
            "text": text, "bg_color": bg_color, "hover_color": hover_color
        }
        return self.controls[control_id]
    
    def _setup_events(self) -> None:
        """イベント処理を設定"""
        if self.filename_textbox:
            # Phase Fパターン: TextBoxControlのイベント統合
            # Enterキーで保存実行
            def on_enter_key(control):
                self._on_save_pressed()
            self.filename_textbox.on_enter = on_enter_key
    
    def _on_save_pressed(self) -> None:
        """保存ボタン押下時の処理"""
        # Phase Fパターン: 高度API使用
        filename = self.filename_textbox.get_edited_filename()
        
        if filename and self.filename_textbox.has_valid_filename():
            self.input_filename = filename
            self.dialog_result = True
            self.close(True)
            print(f"[FileSaveDialogJSON] Save confirmed: '{filename}'")
        else:
            # バリデーションエラー
            self._show_error_message("Invalid filename")
            print(f"[FileSaveDialogJSON] Invalid filename: '{self.filename_textbox.text}'")
    
    def _on_cancel_pressed(self) -> None:
        """キャンセルボタン押下時の処理"""
        self.dialog_result = False
        self.close(False)
        print("[FileSaveDialogJSON] Save canceled")
    
    def _show_error_message(self, message: str) -> None:
        """
        エラーメッセージを表示
        
        Args:
            message: エラーメッセージ
        """
        self.error_message = message
        if "error_label" in self.controls:
            self.controls["error_label"]["text"] = message
            self.controls["error_label"]["visible"] = True
    
    def _clear_error_message(self) -> None:
        """エラーメッセージをクリア"""
        self.error_message = ""
        if "error_label" in self.controls:
            self.controls["error_label"]["text"] = ""
            self.controls["error_label"]["visible"] = False
    
    def show_save_dialog(self) -> Tuple[bool, str]:
        """
        保存ダイアログを表示
        既存FileManagerとの互換性インターフェース
        
        Returns:
            (success: bool, filename: str): 成功フラグとファイル名のタプル
        """
        try:
            # ダイアログ表示
            result = self.show()
            
            # 結果判定
            if self.dialog_result and self.input_filename:
                return True, self.input_filename
            else:
                return False, ""
                
        except Exception as e:
            print(f"[FileSaveDialogJSON] Error: {e}")
            return False, ""


def show_file_save_dialog(default_filename: str = "my_circuit") -> Tuple[bool, str]:
    """
    ファイル保存ダイアログを表示する便利関数
    
    Args:
        default_filename: デフォルトファイル名
        
    Returns:
        (success: bool, filename: str): 成功フラグとファイル名のタプル
    """
    try:
        dialog = FileSaveDialogJSON(default_filename)
        return dialog.show_save_dialog()
    except Exception as e:
        print(f"[show_file_save_dialog] Error: {e}")
        return False, ""
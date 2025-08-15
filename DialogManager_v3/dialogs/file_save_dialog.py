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
        
        # ダイアログ状態プロパティ（FileLoadDialogJSONと同様）
        self.visible = False
        self.cancelled = False
        self.focused_control = None
        
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
        
        # Phase Fパターン: フォーカス設定とイベントハンドリング
        self.filename_textbox.focus = True
        self.filename_textbox.parent = self
        
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
        """イベント処理を設定（Phase Fパターン適用）"""
        if self.filename_textbox:
            # Phase Fパターン: TextBoxControlのイベント統合
            # Enterキーで保存実行
            def on_enter_key(control):
                self._on_save_pressed()
            self.filename_textbox.on_enter = on_enter_key
            
            # テキスト変更時のリアルタイムバリデーション（Phase Fパターン）
            def on_text_changed(control):
                self._update_filename_preview()
                self._validate_filename_realtime()
            self.filename_textbox.on_text_change = on_text_changed
    
    def _on_save_pressed(self) -> None:
        """保存ボタン押下時の処理"""
        # Phase Fパターン: 高度API使用
        filename = self.filename_textbox.get_edited_filename()
        
        if filename and self.filename_textbox.has_valid_filename():
            self.input_filename = filename
            self.dialog_result = True
            self.visible = False  # close(True)の代わり
            print(f"[FileSaveDialogJSON] Save confirmed: '{filename}'")
        else:
            # バリデーションエラー
            self._show_error_message("Invalid filename")
            print(f"[FileSaveDialogJSON] Invalid filename: '{self.filename_textbox.text}'")
    
    def _on_cancel_pressed(self) -> None:
        """キャンセルボタン押下時の処理"""
        self.dialog_result = False
        self.cancelled = True
        self.visible = False  # close(False)の代わり
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
    
    def _update_filename_preview(self) -> None:
        """
        ファイル名プレビューを更新（Phase Fパターン）
        """
        if self.filename_textbox:
            current_text = self.filename_textbox.text
            if current_text:
                preview_text = f"File will be saved as: {current_text}.csv"
            else:
                preview_text = "File will be saved as: [filename].csv"
            
            if "extension_label" in self.controls:
                self.controls["extension_label"]["text"] = preview_text
    
    def _validate_filename_realtime(self) -> None:
        """
        リアルタイムファイル名バリデーション（Phase Fパターン）
        """
        if self.filename_textbox:
            if self.filename_textbox.has_valid_filename():
                self._clear_error_message()
                if "status_label" in self.controls:
                    self.controls["status_label"]["text"] = "Ready to save"
            else:
                current_text = self.filename_textbox.text
                if current_text:
                    self._show_error_message("Invalid filename characters")
                else:
                    self._clear_error_message()
                    if "status_label" in self.controls:
                        self.controls["status_label"]["text"] = "Enter filename and click Save"
    
    def update(self):
        """ダイアログの状態を更新（FileLoadDialogJSONと同様）"""
        if not self.visible:
            return
            
        # マウスクリック処理
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self._handle_mouse_click(pyxel.mouse_x, pyxel.mouse_y)
    
    def _handle_mouse_click(self, x: int, y: int):
        """マウスクリック処理"""
        # ボタンクリックを処理
        for ctrl_id, ctrl in self.controls.items():
            if ctrl['type'] == 'button' and self._is_point_in_rect(x, y, ctrl):
                if ctrl_id == 'save_button':
                    self._on_save_pressed()
                elif ctrl_id == 'cancel_button':
                    self._on_cancel_pressed()
                return
        
        # TextBoxControlクリック処理
        if self.filename_textbox and self._is_textbox_clicked(x, y):
            self.focused_control = self.filename_textbox
            # TextBoxControlのクリック処理
            local_x = x - (self.x + 20)  # TextBoxControlのx位置
            local_y = y - (self.y + 55)  # TextBoxControlのy位置
            self.filename_textbox.handle_mouse_click(local_x, local_y)
    
    def _is_point_in_rect(self, x: int, y: int, rect: dict) -> bool:
        """点が矩形内にあるかどうかを判定（絶対座標）"""
        abs_x = self.x + rect['x']
        abs_y = self.y + rect['y']
        return (abs_x <= x < abs_x + rect['width'] and 
                abs_y <= y < abs_y + rect['height'])
    
    def _is_textbox_clicked(self, x: int, y: int) -> bool:
        """TextBoxControlがクリックされたかどうかを判定"""
        textbox_x = self.x + 20
        textbox_y = self.y + 55
        textbox_width = 300
        textbox_height = 25
        return (textbox_x <= x < textbox_x + textbox_width and 
                textbox_y <= y < textbox_y + textbox_height)
    
    def draw(self):
        """ダイアログを描画（FileLoadDialogJSONと同様）"""
        # 背景
        pyxel.rect(self.x, self.y, self.width, self.height, pyxel.COLOR_NAVY)
        pyxel.rectb(self.x, self.y, self.width, self.height, pyxel.COLOR_WHITE)
        
        # タイトルバー
        pyxel.rect(self.x, self.y, self.width, 20, pyxel.COLOR_DARK_BLUE)
        pyxel.text(self.x + 10, self.y + 6, self.title, pyxel.COLOR_WHITE)
        
        # コントロールを描画
        self._draw_controls()
    
    def _draw_controls(self):
        """コントロールを描画"""
        for ctrl_id, ctrl in self.controls.items():
            if not ctrl.get('visible', True):
                continue
                
            if ctrl['type'] == 'label':
                pyxel.text(
                    self.x + ctrl['x'], 
                    self.y + ctrl['y'], 
                    ctrl['text'], 
                    ctrl.get('color', pyxel.COLOR_WHITE)
                )
            elif ctrl['type'] == 'button':
                self._draw_button(ctrl)
        
        # TextBoxControlを描画
        if self.filename_textbox:
            self.filename_textbox.draw(self.x, self.y)
    
    def _draw_button(self, ctrl: dict):
        """ボタンを描画"""
        x = self.x + ctrl['x']
        y = self.y + ctrl['y']
        
        # ボタンの状態に応じた色
        is_hovered = self._is_mouse_over(ctrl)
        bg_color = ctrl.get('hover_color', pyxel.COLOR_GREEN) if is_hovered else ctrl.get('bg_color', pyxel.COLOR_PURPLE)
        
        # ボタン本体
        pyxel.rect(x, y, ctrl['width'], ctrl['height'], bg_color)
        pyxel.rectb(x, y, ctrl['width'], ctrl['height'], pyxel.COLOR_WHITE)
        
        # ボタンテキスト（中央揃え）
        text = ctrl['text']
        text_width = len(text) * 4  # 1文字4pxと仮定
        text_x = x + (ctrl['width'] - text_width) // 2
        text_y = y + (ctrl['height'] - 6) // 2 + 1
        pyxel.text(text_x, text_y, text, pyxel.COLOR_WHITE)
    
    def _is_mouse_over(self, ctrl: dict) -> bool:
        """マウスがコントロールの上にあるかどうかを判定"""
        abs_x = self.x + ctrl['x']
        abs_y = self.y + ctrl['y']
        return (abs_x <= pyxel.mouse_x < abs_x + ctrl['width'] and 
                abs_y <= pyxel.mouse_y < abs_y + ctrl['height'])
    
    def handle_key_input(self, key: int) -> bool:
        """キーボード入力を処理"""
        # フォーカスされたコントロールにキーイベントを転送
        if self.focused_control and hasattr(self.focused_control, 'on_key'):
            return self.focused_control.on_key(key)
        return False
    
    def handle_text_input(self, char: str) -> bool:
        """テキスト入力を処理"""
        # フォーカスされたコントロールにテキスト入力を転送
        if self.focused_control and hasattr(self.focused_control, 'on_text'):
            return self.focused_control.on_text(char)
        return False
    
    def show_save_dialog(self) -> Tuple[bool, str]:
        """
        保存ダイアログを表示
        既存FileManagerとの互換性インターフェース（統一モーダルループ使用）
        
        Returns:
            (success: bool, filename: str): 成功フラグとファイル名のタプル
        """
        try:
            # ダイアログ状態初期化
            self.dialog_result = None
            
            # 初期フォーカス設定
            self.focused_control = self.filename_textbox
            
            print("[FileSaveDialogJSON] Starting dialog using unified modal loop")
            
            # BaseDialog統一モーダルループを使用（Phase G2-1で実装）
            result = self.show_modal_loop(
                escape_key_enabled=True,
                background_color=pyxel.COLOR_BLACK
            )
            
            print(f"[FileSaveDialogJSON] Modal loop ended, dialog_result: {self.dialog_result}, cancelled: {self.cancelled}")
            
            # 結果を返す（既存FileManagerと同じインターフェース）
            if self.cancelled or not self.dialog_result:
                return False, ""  # キャンセル時
            else:
                return True, self.input_filename  # 成功時
                
        except Exception as e:
            print(f"[FileSaveDialogJSON] Error: {e}")
            import traceback
            traceback.print_exc()
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
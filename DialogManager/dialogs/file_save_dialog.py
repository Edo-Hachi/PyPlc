# PyPlc Ver3 Dialog System - FileSaveDialog (JSON版)  
# Phase 2: JSON定義によるファイル保存ダイアログ
# 作成日: 2025-08-08

import pyxel
import os
import re
from typing import Optional, Tuple
from DialogManager.core.base_dialog import BaseDialog
from DialogManager.core.json_dialog_loader import JSONDialogLoader
from DialogManager.core.control_factory import ControlFactory


class FileSaveDialogJSON(BaseDialog):
    """
    JSON定義によるファイル保存ダイアログ
    TextInputControlを使用したファイル名入力
    """
    
    def __init__(self, default_filename: str = "my_circuit"):
        """
        FileSaveDialogJSON初期化
        
        Args:
            default_filename: デフォルトファイル名
        """
        super().__init__()
        
        self.default_filename = default_filename
        self.input_filename = default_filename
        self.dialog_result = None
        self.error_message = ""
        
        # JSON定義からダイアログを構築
        self.loader = JSONDialogLoader()
        self.factory = ControlFactory()
        
        # ダイアログ定義を読み込み
        dialog_definition = self.loader.load_dialog_definition(
            "file_save_dialog.json"
        )
        
        if dialog_definition:
            # ダイアログ基本設定
            self.title = dialog_definition.get("title", "Save File")
            self.width = dialog_definition.get("width", 320)
            self.height = dialog_definition.get("height", 180)
            
            # 位置を再計算
            self.x = (384 - self.width) // 2  # Ver3画面サイズ対応
            self.y = (384 - self.height) // 2
            
            # コントロールを生成・追加
            self._create_controls(dialog_definition.get("controls", []))
            
            # イベント登録
            self._setup_events()
        else:
            # フォールバック: 基本設定
            print("Warning: Could not load file_save_dialog.json")
            self.title = "Save Circuit File"
            self.width = 320
            self.height = 180
            self.x = (384 - self.width) // 2
            self.y = (384 - self.height) // 2
        
        print(f"FileSaveDialogJSON initialized: {self.title}")
    
    def _draw_custom(self) -> None:
        """
        カスタム描画処理（BaseDialogの抽象メソッド実装）
        """
        # FileSaveDialogJSONは標準描画のみ使用
        # 特別なカスタム描画は不要
        pass
    
    def _create_controls(self, control_definitions: list) -> None:
        """
        JSON定義からコントロールを作成・追加
        
        Args:
            control_definitions: コントロール定義リスト
        """
        for control_def in control_definitions:
            try:
                control = self.factory.create_control(control_def)
                if control:
                    self.add_control(control_def["id"], control)
                    print(f"Control added: {control_def['id']}")
            except Exception as e:
                print(f"Failed to create control {control_def.get('id', 'unknown')}: {e}")
        
        # デフォルトファイル名を入力フィールドに設定
        filename_input = self.get_control("filename_input")
        if filename_input and hasattr(filename_input, 'set_text'):
            filename_input.set_text(self.default_filename)
            self.input_filename = self.default_filename
    
    def _setup_events(self) -> None:
        """イベント処理を設定"""
        # ファイル名入力の変更イベント
        filename_input = self.get_control("filename_input")
        if filename_input:
            filename_input.on("change", self._on_filename_changed)
            filename_input.on("enter", self._on_save_pressed)
        
        # ボタンクリックイベント
        save_button = self.get_control("save_button")
        if save_button:
            save_button.on("click", self._on_save_pressed)
        
        cancel_button = self.get_control("cancel_button")
        if cancel_button:
            cancel_button.on("click", self._on_cancel_pressed)
    
    def _on_filename_changed(self, control, old_text: str, new_text: str) -> None:
        """
        ファイル名入力変更時の処理
        
        Args:
            control: 入力コントロール
            old_text: 変更前のテキスト  
            new_text: 変更後のテキスト
        """
        self.input_filename = new_text
        
        # エラーメッセージをクリア
        self._clear_error_message()
        
        # ステータス更新
        self._update_status_message(f"File will be saved as: {new_text}.csv")
        
        print(f"Filename changed: '{old_text}' -> '{new_text}'")
    
    def _on_save_pressed(self, *args) -> None:
        """保存ボタン押下時の処理"""
        if self._validate_filename():
            self.dialog_result = True
            self.close(True)  # BaseDialogのresultにもTrueを設定
            print(f"Save dialog: OK pressed with filename '{self.input_filename}'")
        else:
            print("Save dialog: Invalid filename")
    
    def _on_cancel_pressed(self, *args) -> None:
        """キャンセルボタン押下時の処理"""
        self.dialog_result = False
        self.close(False)  # BaseDialogのresultにもFalseを設定
        print("Save dialog: Cancel pressed")
    
    def _validate_filename(self) -> bool:
        """
        ファイル名バリデーション
        
        Returns:
            有効なファイル名の場合True
        """
        filename = self.input_filename.strip()
        
        if not filename:
            self._show_error_message("Filename cannot be empty")
            return False
        
        # 無効文字チェック
        invalid_chars = r'[<>:"/\\|?*]'
        if re.search(invalid_chars, filename):
            self._show_error_message("Invalid characters in filename")
            return False
        
        # 長さチェック
        if len(filename) > 50:
            self._show_error_message("Filename too long (max 50 characters)")
            return False
        
        return True
    
    def _show_error_message(self, message: str) -> None:
        """
        エラーメッセージを表示
        
        Args:
            message: エラーメッセージ
        """
        self.error_message = message
        error_label = self.get_control("error_label")
        if error_label:
            error_label.text = message
            error_label.visible = True
    
    def _clear_error_message(self) -> None:
        """エラーメッセージをクリア"""
        self.error_message = ""
        error_label = self.get_control("error_label")
        if error_label:
            error_label.text = ""
            error_label.visible = False
    
    def _update_status_message(self, message: str) -> None:
        """
        ステータスメッセージを更新
        
        Args:
            message: ステータスメッセージ
        """
        status_label = self.get_control("status_label")
        if status_label:
            status_label.text = message
    
    def show_save_dialog(self) -> Tuple[bool, str]:
        """
        保存ダイアログを表示
        
        Returns:
            (success: bool, filename: str)
        """
        try:
            result = self.show()
            # self.dialog_resultを確認（OKボタン押下時にTrueに設定される）
            if self.dialog_result and self.input_filename:
                return True, self.input_filename
            else:
                return False, ""
        except Exception as e:
            print(f"FileSaveDialogJSON error: {e}")
            return False, ""


def show_file_save_dialog(default_filename: str = "my_circuit") -> Tuple[bool, str]:
    """
    ファイル保存ダイアログを表示する便利関数
    
    Args:
        default_filename: デフォルトファイル名
        
    Returns:
        (success: bool, filename: str)
    """
    try:
        dialog = FileSaveDialogJSON(default_filename)
        return dialog.show_save_dialog()
    except Exception as e:
        print(f"show_file_save_dialog error: {e}")
        return False, ""
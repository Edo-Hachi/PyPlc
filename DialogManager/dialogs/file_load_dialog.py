# PyPlc Ver3 Dialog System - FileLoadDialog (JSON版)
# Phase 3: FileListControlを使用したファイル読み込みダイアログ
# 作成日: 2025-08-08

import pyxel
from typing import Optional, Dict, Any
from DialogManager.core.base_dialog import BaseDialog
from DialogManager.core.json_dialog_loader import JSONDialogLoader
from DialogManager.core.control_factory import ControlFactory

class FileLoadDialogJSON(BaseDialog):
    """
    JSON定義によるファイル読み込みダイアログ
    FileListControlを使用した実装
    """
    
    def __init__(self):
        """FileLoadDialogJSON初期化"""
        super().__init__()
        
        # JSON定義からダイアログを構築
        self.loader = JSONDialogLoader()
        self.factory = ControlFactory()
        
        # ダイアログ定義を読み込み
        dialog_definition = self.loader.load_dialog_definition(
            "file_load_dialog.json"
        )
        
        if dialog_definition:
            # ダイアログ基本設定
            self.title = dialog_definition.get("title", "Load File")
            self.width = dialog_definition.get("width", 350)
            self.height = dialog_definition.get("height", 280)
            
            # 位置を再計算
            self.x = (384 - self.width) // 2  # Ver3画面サイズ対応
            self.y = (384 - self.height) // 2
            
            # コントロールを生成・追加
            for control_def in dialog_definition.get("controls", []):
                control = self.factory.create_control(control_def)
                if control:
                    self.add_control(control_def["id"], control)
        
        # ダイアログ状態
        self.selected_file = None
        self.load_success = False
        
        # イベントハンドラー登録
        self._setup_event_handlers()
    
    def _setup_event_handlers(self) -> None:
        """イベントハンドラーを設定"""
        # FileListControlのイベント
        self.event_system.on('file_selected', self._on_file_selected)
        self.event_system.on('file_double_clicked', self._on_file_double_clicked)
        self.event_system.on('selection_changed', self._on_selection_changed)
        
        # ボタンクリックイベント
        load_button = self.get_control('load_button')
        if load_button:
            load_button.on('click', self._on_load_clicked)
        
        cancel_button = self.get_control('cancel_button')
        if cancel_button:
            cancel_button.on('click', self._on_cancel_clicked)
        
        refresh_button = self.get_control('refresh_button')
        if refresh_button:
            refresh_button.on('click', self._on_refresh_clicked)
    
    def _on_file_selected(self, event_data: Dict[str, Any]) -> None:
        """ファイル選択時のイベントハンドラー"""
        file_info = event_data.get('file_info')
        if file_info:
            self.selected_file = file_info
            self._update_file_info_display(file_info)
            self._update_status("File selected: " + file_info['display_name'])
    
    def _on_file_double_clicked(self, event_data: Dict[str, Any]) -> None:
        """ファイルダブルクリック時のイベントハンドラー（即座に読み込み）"""
        file_info = event_data.get('file_info')
        if file_info:
            self.selected_file = file_info
            self._execute_load()
    
    def _on_selection_changed(self, event_data: Dict[str, Any]) -> None:
        """選択変更時のイベントハンドラー"""
        file_info = event_data.get('file_info')
        if file_info:
            self._update_file_info_display(file_info)
        else:
            self._clear_file_info_display()
    
    def _on_load_clicked(self, control) -> None:
        """Loadボタンクリック時のハンドラー"""
        if self.selected_file:
            self._execute_load()
        else:
            self._update_status("No file selected")
    
    def _on_cancel_clicked(self, control) -> None:
        """Cancelボタンクリック時のハンドラー"""
        self.close(False)
    
    def _on_refresh_clicked(self, control) -> None:
        """Refreshボタンクリック時のハンドラー"""
        file_list = self.get_control('file_list')
        if file_list and hasattr(file_list, 'refresh_file_list'):
            file_list.refresh_file_list()
            self._update_status("File list refreshed")
    
    def _execute_load(self) -> None:
        """ファイル読み込み実行"""
        if self.selected_file:
            self.load_success = True
            self.close(self.selected_file['path'])
        else:
            self._update_status("No file selected")
    
    def _update_file_info_display(self, file_info: Dict[str, Any]) -> None:
        """ファイル情報表示を更新"""
        info_label = self.get_control('selected_info')
        if info_label:
            # ファイル情報を整形
            name = file_info['display_name']
            size = self._format_file_size(file_info['size'])
            modified = file_info['modified'].strftime("%m/%d %H:%M")
            
            # 表示テキストを作成（改行で区切り）
            info_text = f"{name[:10]}...\n{size}\n{modified}" if len(name) > 10 else f"{name}\n{size}\n{modified}"
            info_label.text = info_text
    
    def _clear_file_info_display(self) -> None:
        """ファイル情報表示をクリア"""
        info_label = self.get_control('selected_info')
        if info_label:
            info_label.text = "No file\nselected"
    
    def _update_status(self, message: str) -> None:
        """ステータス表示を更新"""
        status_label = self.get_control('status_label')
        if status_label:
            # メッセージを適切な長さに切り詰め
            max_chars = 25  # 180px / 4px per char ≈ 45, but conservative
            if len(message) > max_chars:
                message = message[:max_chars-3] + "..."
            status_label.text = message
    
    def _format_file_size(self, size_bytes: int) -> str:
        """ファイルサイズを読みやすい形式にフォーマット"""
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes // 1024}KB"
        else:
            return f"{size_bytes // (1024 * 1024)}MB"
    
    def show_load_dialog(self) -> tuple:
        """
        ファイル読み込みダイアログを表示
        
        Returns:
            tuple: (success: bool, file_path: str)
        """
        result = self.show()
        return self.load_success, result if result else ""
    
    def _draw_custom(self) -> None:
        """カスタム描画処理"""
        # 基本的な描画はBaseDialogとコントロールが行うため、
        # 特別な描画が必要な場合のみここに実装
        pass

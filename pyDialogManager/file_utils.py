"""
ファイルオープンダイアログ用のファイルシステムユーティリティ

シンプルなファイル操作とディレクトリ一覧機能を提供
"""
import os
from typing import List, Dict, Optional
from pathlib import Path

class FileItem:
    """ファイルまたはディレクトリの情報を保持するクラス"""
    def __init__(self, path: str):
        self.path = path
        self.name = os.path.basename(path)
        self.is_directory = os.path.isdir(path)
        self.is_file = os.path.isfile(path)
        
        # サイズ情報
        try:
            if self.is_file:
                self.size = os.path.getsize(path)
            else:
                self.size = 0
        except:
            self.size = 0
    
    def get_display_name(self) -> str:
        """表示用の名前を取得（ディレクトリには[DIR]プレフィックス）"""
        if self.is_directory:
            return f"[DIR] {self.name}"
        else:
            return self.name

class FileManager:
    """ファイルマネージャークラス"""
    def __init__(self, initial_path: Optional[str] = None):
        # 初期パスが指定されていない場合はカレントディレクトリから開始
        if initial_path and os.path.exists(initial_path) and os.path.isdir(initial_path):
            self.current_path = os.path.abspath(initial_path)
        else:
            self.current_path = os.getcwd()  # カレントディレクトリから開始
        self.file_filters = ["*.*"]  # デフォルトはすべてのファイル
    
    def get_current_path(self) -> str:
        """現在のパスを取得"""
        return self.current_path
    
    def set_current_path(self, path: str) -> bool:
        """現在のパスを設定"""
        try:
            if os.path.exists(path) and os.path.isdir(path):
                self.current_path = os.path.abspath(path)
                return True
        except:
            pass
        return False
    
    def get_parent_directory(self) -> Optional[str]:
        """親ディレクトリのパスを取得"""
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:  # ルートディレクトリでない場合
            return parent
        return None
    
    def go_up(self) -> bool:
        """親ディレクトリに移動"""
        parent = self.get_parent_directory()
        if parent:
            return self.set_current_path(parent)
        return False
    
    def list_directory(self) -> List[FileItem]:
        """現在のディレクトリの内容を取得"""
        items = []
        try:
            # ディレクトリとファイルを分けて取得
            entries = os.listdir(self.current_path)
            
            # ディレクトリを先に追加
            for entry in sorted(entries):
                full_path = os.path.join(self.current_path, entry)
                if os.path.isdir(full_path):
                    items.append(FileItem(full_path))
            
            # ファイルを後に追加
            for entry in sorted(entries):
                full_path = os.path.join(self.current_path, entry)
                if os.path.isfile(full_path):
                    # フィルターチェック
                    if self._matches_filter(entry):
                        items.append(FileItem(full_path))
        except:
            pass  # アクセス権限エラーなどは無視
        
        return items
    
    def _matches_filter(self, filename: str) -> bool:
        """ファイルがフィルターにマッチするかチェック"""
        import fnmatch
        for filter_pattern in self.file_filters:
            if fnmatch.fnmatch(filename.lower(), filter_pattern.lower()):
                return True
        return False
    
    def set_file_filter(self, filters: List[str]):
        """ファイルフィルターを設定"""
        self.file_filters = filters if filters else ["*.*"]
    
    def get_display_path(self) -> str:
        """表示用のパスを取得（短縮版）"""
        path = self.current_path
        # パスが長すぎる場合は短縮
        if len(path) > 40:
            parts = path.split(os.sep)
            if len(parts) > 3:
                return os.sep.join(["...", parts[-2], parts[-1]])
        return path
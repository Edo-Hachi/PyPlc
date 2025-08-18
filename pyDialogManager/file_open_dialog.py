"""
ファイルオープンダイアログの連携機能

ファイルシステムとダイアログウィジェットを連携させる機能を提供
"""
import os
from .dialog_manager import DialogManager
from .file_utils import FileManager, FileItem
from .system_settings import settings

class FileOpenDialogController:
    """ファイルオープンダイアログのコントローラークラス"""
    
    def __init__(self, dialog_manager: DialogManager, initial_directory: str = None):
        self.dialog_manager = dialog_manager
        self.file_manager = FileManager(initial_directory)
        self.active_dialog = None
        self.result = None
        
    def show_file_open_dialog(self):
        """ファイルオープンダイアログを表示し、ファイルシステムと連携"""
        self.result = None # 表示時に結果をリセット
        # ダイアログを表示
        self.dialog_manager.show("IDD_FILE_OPEN")
        self.active_dialog = self.dialog_manager.active_dialog
        
        if self.active_dialog:
            # 初期化処理
            self._initialize_dialog()
            self._refresh_file_list()
            self._setup_event_handlers()

    def get_result(self):
        """Get the result and clear it."""
        result = self.result
        self.result = None
        return result
    
    def _initialize_dialog(self):
        """ダイアログの初期化"""
        if not self.active_dialog:
            return
            
        # パス表示ウィジェットを見つけて現在パスを設定
        path_widget = self._find_widget("IDC_PATH_DISPLAY")
        if path_widget:
            display_path = self.file_manager.get_display_path()
            path_widget.text = display_path
            
        # ファイル名入力ウィジェットをクリア
        filename_widget = self._find_widget("IDC_FILENAME_INPUT")
        if filename_widget:
            filename_widget.text = ""
        
        # デフォルトフィルターを適用
        self._apply_initial_filter()
    
    def _apply_initial_filter(self):
        """ダイアログ初期化時にデフォルトフィルターを適用"""
        filter_widget = self._find_widget("IDC_FILE_FILTER")
        if filter_widget and hasattr(filter_widget, 'get_selected_value'):
            selected_filter = filter_widget.get_selected_value()
            if selected_filter:
                print(f"[DEBUG] Applying initial filter: {selected_filter}")
                
                # フィルターマッピング
                filter_mapping = {
                    "All Files (*.*)": ["*.*"],
                    "CSV Files (*.csv)": ["*.csv"],
                    "Text Files (*.txt)": ["*.txt"],
                    "Python Files (*.py)": ["*.py"]
                }
                
                filters = filter_mapping.get(selected_filter, ["*.*"])
                self.file_manager.set_file_filter(filters)
                print(f"[DEBUG] Initial filter applied: {filters}")
    
    def _find_widget(self, widget_id: str):
        """ウィジェットIDでウィジェットを検索"""
        if not self.active_dialog:
            return None
            
        for widget in self.active_dialog.widgets:
            if hasattr(widget, 'id') and widget.id == widget_id:
                return widget
        return None
    
    def _refresh_file_list(self):
        """ファイルリストを更新"""
        if not self.active_dialog:
            return
            
        # ファイルリストウィジェットを取得
        file_list_widget = self._find_widget("IDC_FILE_LIST")
        if not file_list_widget:
            return
            
        try:
            # ディレクトリ内容を取得
            file_items = self.file_manager.list_directory()
            
            # 表示用の文字列リストを作成
            display_items = []
            self.file_items_map = {}  # 表示インデックスと実際のFileItemのマッピング
            
            for i, item in enumerate(file_items):
                display_name = item.get_display_name()
                display_items.append(display_name)
                self.file_items_map[i] = item
            
            # リストボックスにアイテムを設定
            file_list_widget.set_items(display_items)
            
            print(f"Loaded {len(display_items)} items from {self.file_manager.get_current_path()}")
            
        except Exception as e:
            print(f"Error loading directory: {e}")
            file_list_widget.set_items([f"Error: {str(e)}"])
    
    def _setup_event_handlers(self):
        """イベントハンドラーを設定"""
        file_list_widget = self._find_widget("IDC_FILE_LIST")
        if file_list_widget:
            # クリックモードに応じたイベントハンドラーを設定
            if settings.is_single_click_mode():
                # シングルクリックモード: アクティベートで即座に処理
                file_list_widget.on_item_activated = self.handle_file_activation
            else:
                # ダブルクリックモード: 選択とアクティベートを分離
                file_list_widget.on_selection_changed = self.handle_file_selection
                file_list_widget.on_item_activated = self.handle_file_activation
        
        # フィルタードロップダウンのイベントハンドラーを設定
        filter_widget = self._find_widget("IDC_FILE_FILTER")
        if filter_widget:
            print(f"[DEBUG] Setting up filter dropdown event handler for widget: {filter_widget}")
            filter_widget.on_selection_changed = self.handle_filter_changed
            print(f"[DEBUG] Event handler set successfully")
        else:
            print(f"[DEBUG] Filter widget 'IDC_FILE_FILTER' not found!")
        
        # ディレクトリ表示チェックボックスのイベントハンドラーを設定
        checkbox_widget = self._find_widget("IDC_SHOW_DIRECTORIES")
        if checkbox_widget:
            print(f"[DEBUG] Setting up directory checkbox event handler for widget: {checkbox_widget}")
            checkbox_widget.on_checked_changed = self.handle_directory_display_changed
            print(f"[DEBUG] Checkbox event handler set successfully")
        else:
            print(f"[DEBUG] Directory checkbox widget 'IDC_SHOW_DIRECTORIES' not found!")

    def handle_file_selection(self, selected_index: int):
        """ファイル選択時の処理（ダブルクリックモードでの選択のみ）"""
        if selected_index < 0 or selected_index not in self.file_items_map:
            return
            
        selected_item = self.file_items_map[selected_index]
        
        # ダブルクリックモードでは、ファイルの場合のみファイル名を設定
        # ディレクトリの場合はダブルクリック待ち
        if not selected_item.is_directory:
            filename_widget = self._find_widget("IDC_FILENAME_INPUT")
            if filename_widget:
                filename_widget.text = selected_item.name
                print(f"Selected file: {selected_item.name}")
    
    def handle_file_activation(self, selected_index: int):
        """ファイルアクティベート時の処理（実際の動作実行）"""
        if selected_index < 0 or selected_index not in self.file_items_map:
            return
            
        selected_item = self.file_items_map[selected_index]
        
        if selected_item.is_directory:
            # ディレクトリの場合は移動
            self._navigate_to_directory(selected_item.path)
        else:
            # ファイルの場合はファイル名入力ボックスに設定
            filename_widget = self._find_widget("IDC_FILENAME_INPUT")
            if filename_widget:
                filename_widget.text = selected_item.name
                print(f"Activated file: {selected_item.name}")
    
    def _navigate_to_directory(self, directory_path: str):
        """ディレクトリに移動"""
        if self.file_manager.set_current_path(directory_path):
            print(f"Navigated to: {directory_path}")
            self._initialize_dialog()
            self._refresh_file_list()
            self._setup_event_handlers()  # イベントハンドラーを再設定
        else:
            print(f"Failed to navigate to: {directory_path}")
    
    def handle_up_button(self):
        """上ディレクトリボタンが押された時の処理"""
        if self.file_manager.go_up():
            print(f"Moved up to: {self.file_manager.get_current_path()}")
            self._initialize_dialog()
            self._refresh_file_list()
            self._setup_event_handlers()  # イベントハンドラーを再設定
        else:
            print("Already at root directory")
    
    def handle_open_button(self):
        """Openボタンが押された時の処理"""
        filename_widget = self._find_widget("IDC_FILENAME_INPUT")
        if not filename_widget or not filename_widget.text.strip():
            print("No file selected")
            return None
            
        selected_filename = filename_widget.text.strip()
        full_path = os.path.join(self.file_manager.get_current_path(), selected_filename)
        
        print(f"Opening file: {full_path}")
        return full_path
    
    def handle_cancel_button(self):
        """Cancelボタンが押された時の処理"""
        print("File open dialog cancelled")
        self.result = None
        self.dialog_manager.close()
        return None
    
    def handle_filter_changed(self, selected_index: int, selected_value: str):
        """フィルタードロップダウンの選択が変更された時の処理"""
        print(f"[DEBUG] Filter changed to: {selected_value} (index: {selected_index})")
        
        # 選択されたフィルターに応じてファイルマネージャーのフィルターを設定
        filter_mapping = {
            "All Files (*.*)": ["*.*"],
            "CSV Files (*.csv)": ["*.csv"],
            "Text Files (*.txt)": ["*.txt"],
            "Python Files (*.py)": ["*.py"]
        }
        
        filters = filter_mapping.get(selected_value, ["*.*"])
        print(f"[DEBUG] Setting file filters to: {filters}")
        self.file_manager.set_file_filter(filters)
        
        # ファイルリストを更新
        print(f"[DEBUG] Refreshing file list...")
        self._refresh_file_list()
        self._setup_event_handlers()  # イベントハンドラーを再設定
        print(f"[DEBUG] Filter change complete.")
    
    def handle_directory_display_changed(self, show_directories: bool):
        """ディレクトリ表示チェックボックスの状態が変更された時の処理"""
        print(f"[DEBUG] Directory display changed to: {show_directories}")
        
        # FileManagerに表示設定を保存
        self.file_manager.show_directories = show_directories
        
        # ファイルリストを更新
        print(f"[DEBUG] Refreshing file list for directory display change...")
        self._refresh_file_list()
        self._setup_event_handlers()  # イベントハンドラーを再設定
        print(f"[DEBUG] Directory display change complete.")
    
    def update(self):
        """フレームごとの更新処理"""
        # マネージャーと自身のアクティブダイアログが一致しない場合、自身を非アクティブ化
        if self.active_dialog and self.active_dialog != self.dialog_manager.active_dialog:
            self.active_dialog = None

        if not self.active_dialog:
            return
            
        # ボタンクリックのチェック
        self._check_button_clicks()
            
        # ファイルリストの選択状態をチェック
        file_list_widget = self._find_widget("IDC_FILE_LIST")
        if file_list_widget and hasattr(file_list_widget, 'selected_index'):
            if (file_list_widget.selected_index >= 0 and 
                hasattr(self, '_last_selected_index') and
                file_list_widget.selected_index != self._last_selected_index):
                
                # 選択が変わった場合
                self.handle_file_selection(file_list_widget.selected_index)
                self._last_selected_index = file_list_widget.selected_index
            
            if not hasattr(self, '_last_selected_index'):
                self._last_selected_index = -1
    
    def _check_button_clicks(self):
        """ボタンクリックをチェックして対応する処理を実行"""
        if not self.active_dialog:
            return
            
        # 各ボタンのクリック状態をチェック
        for widget in self.active_dialog.widgets:
            if hasattr(widget, 'id') and hasattr(widget, 'is_pressed') and widget.is_pressed:
                if widget.id == "IDC_UP_BUTTON":
                    self.handle_up_button()
                elif widget.id == "IDOK":
                    result = self.handle_open_button()
                    if result:
                        print(f"File selected for opening: {result}")
                        self.result = result
                        self.dialog_manager.close()
                elif widget.id == "IDCANCEL":
                    self.handle_cancel_button()

    def _find_widget(self, widget_id: str):
        """ウィジェットIDでウィジェットを検索"""
        if not self.active_dialog:
            return None
        for widget in self.active_dialog.widgets:
            if hasattr(widget, 'id') and widget.id == widget_id:
                return widget
        return None

    def is_active(self) -> bool:
        """ダイアログがアクティブかどうかを返す"""
        return self.dialog_manager.active_dialog is not None and self.active_dialog is not None
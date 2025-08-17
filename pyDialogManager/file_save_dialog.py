"""
ファイル保存ダイアログの連携機能

ファイルシステムとダイアログウィジェットを連携させる機能を提供
"""
import os
from file_utils import FileManager
from dialog_manager import DialogManager
from system_settings import settings

class FileSaveDialogController:
    """ファイル保存ダイアログのコントローラークラス"""
    
    def __init__(self, dialog_manager: DialogManager, initial_directory: str = None):
        self.dialog_manager = dialog_manager
        self.file_manager = FileManager(initial_directory)
        self.active_dialog = None
        
        # デフォルト拡張子（空文字列なら拡張子なし）
        self.default_extension = ".txt"
        self.last_filename = ""
        
    def show_save_dialog(self, default_filename: str = "", default_extension: str = None):
        """ファイル保存ダイアログを表示し、ファイルシステムと連携"""
        # デフォルト拡張子の設定
        if default_extension is not None:
            self.default_extension = default_extension
            
        # ダイアログを表示
        self.dialog_manager.show("IDD_SAVE_AS")
        self.active_dialog = self.dialog_manager.active_dialog
        
        if self.active_dialog:
            # 初期化処理
            self._initialize_dialog(default_filename)
            self._refresh_file_list()
            self._setup_event_handlers()
    
    def _initialize_dialog(self, default_filename: str):
        """ダイアログの初期化"""
        if not self.active_dialog:
            return
            
        # パス表示ウィジェットを見つけて現在パスを設定
        path_widget = self._find_widget("IDC_PATH_DISPLAY")
        if path_widget:
            display_path = self.file_manager.get_display_path()
            path_widget.text = display_path
            
        # ファイル名入力ウィジェットにデフォルトファイル名を設定
        filename_widget = self._find_widget("IDC_FILENAME_INPUT")
        if filename_widget:
            if default_filename:
                # 表示用ファイル名を取得（+ [.ext] 形式）
                display_filename = self._get_display_filename(default_filename)
                filename_widget.text = display_filename
                self.last_filename = display_filename
            elif not filename_widget.text:
                # デフォルトファイル名
                base_name = "untitled"
                display_filename = self._get_display_filename(base_name)
                filename_widget.text = display_filename
                self.last_filename = display_filename
    
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
        
        # ファイル名入力ウィジェットのイベントハンドラー
        filename_widget = self._find_widget("IDC_FILENAME_INPUT")
        if filename_widget:
            # テキスト変更時にプレビューを更新
            filename_widget.on_text_changed = self._on_filename_changed

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
                # ファイルリストから選択された場合は、元のファイル名をそのまま使用
                display_name = selected_item.name
                filename_widget.text = display_name
                self.last_filename = display_name
                print(f"Selected file: {display_name}")
    
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
                # ファイルリストから選択された場合は、元のファイル名をそのまま使用
                display_name = selected_item.name
                filename_widget.text = display_name
                self.last_filename = display_name
                print(f"Activated file: {display_name}")
    
    def _navigate_to_directory(self, directory_path: str):
        """ディレクトリに移動"""
        if self.file_manager.set_current_path(directory_path):
            print(f"Navigated to: {directory_path}")
            self._initialize_dialog("")
            self._refresh_file_list()
            self._setup_event_handlers()  # イベントハンドラーを再設定
        else:
            print(f"Failed to navigate to: {directory_path}")
    
    def handle_up_button(self):
        """上ディレクトリボタンが押された時の処理"""
        if self.file_manager.go_up():
            print(f"Moved up to: {self.file_manager.get_current_path()}")
            self._initialize_dialog("")
            self._refresh_file_list()
            self._setup_event_handlers()  # イベントハンドラーを再設定
        else:
            print("Already at root directory")
    
    def _get_display_filename(self, base_filename: str) -> str:
        """表示用ファイル名を取得（拡張子付き形式）"""
        base_name = base_filename.strip()
        
        # 既に拡張子が含まれている場合は分離
        name_part, existing_ext = os.path.splitext(base_name)
        if existing_ext:
            base_name = name_part
        
        if self.default_extension:
            # デフォルト拡張子が設定されている場合：拡張子を付与
            return base_name + self.default_extension
        else:
            # デフォルト拡張子が空の場合：ベース名のみ
            return base_name
    
    def _get_final_filename(self, input_filename: str) -> str:
        """最終的な保存ファイル名を取得（拡張子処理込み）"""
        filename = input_filename.strip()
        
        # デフォルト拡張子が設定されていて、まだ拡張子がついていない場合
        if self.default_extension and not os.path.splitext(filename)[1]:
            filename += self.default_extension
        
        return filename
    
    def _on_filename_changed(self, new_text: str):
        """ファイル名が変更された時の処理"""
        filename_widget = self._find_widget("IDC_FILENAME_INPUT")
        if not filename_widget:
            return
            
        # デフォルト拡張子が設定されている場合のリアルタイム処理
        if self.default_extension:
            actual_name = new_text.strip()
            base_name, existing_ext = os.path.splitext(actual_name)
            
            if not existing_ext and base_name:
                # 拡張子がない場合は自動付与
                display_text = base_name + self.default_extension
                if display_text != new_text:
                    filename_widget.on_text_changed = None
                    filename_widget.text = display_text
                    filename_widget.on_text_changed = self._on_filename_changed
                self.last_filename = display_text
                print(f"Auto extension applied: '{display_text}'")
            elif existing_ext:
                # ユーザーが独自の拡張子を入力した場合はそのまま
                self.last_filename = new_text
                print(f"User extension detected: '{existing_ext}'")
            else:
                self.last_filename = new_text
        else:
            # デフォルト拡張子が設定されていない場合
            self.last_filename = new_text
    
    
    def set_default_extension(self, extension: str):
        """デフォルト拡張子を設定"""
        # ドットで始まっていない場合は追加
        if extension and not extension.startswith('.'):
            extension = '.' + extension
        self.default_extension = extension
        print(f"Default extension set to: {extension}")
        
        # 現在の入力内容でプレビューを更新
        if self.last_filename:
            self._on_filename_changed(self.last_filename)
    
    def handle_save_button(self):
        """Saveボタンが押された時の処理"""
        filename_widget = self._find_widget("IDC_FILENAME_INPUT")
        if not filename_widget or not filename_widget.text.strip():
            print("No filename entered")
            return None
            
        # 最終的なファイル名を取得（拡張子処理込み）
        final_filename = self._get_final_filename(filename_widget.text)
        
        # 絶対パスでない場合は現在のディレクトリと結合
        if not os.path.isabs(final_filename):
            full_path = os.path.join(self.file_manager.get_current_path(), final_filename)
        else:
            full_path = final_filename
        
        # ファイルが既に存在する場合の確認（今回は簡単に警告のみ）
        if os.path.exists(full_path):
            print(f"Warning: File already exists: {full_path}")
        
        print(f"Saving file to: {full_path}")
        print(f"Default extension: {self.default_extension if self.default_extension else 'None'}")
        return full_path
    
    def handle_cancel_button(self):
        """Cancelボタンが押された時の処理"""
        print("Save dialog cancelled")
        return None
    
    def update(self):
        """フレームごとの更新処理"""
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
                    result = self.handle_save_button()
                    if result:
                        print(f"File selected for saving: {result}")
                elif widget.id == "IDCANCEL":
                    self.handle_cancel_button()
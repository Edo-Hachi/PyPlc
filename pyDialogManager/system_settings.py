"""
システム設定管理

ダイアログシステムの全体的な設定を管理
"""

class SystemSettings:
    """システム設定を管理するシングルトンクラス"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemSettings, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # クリック動作設定
        self.click_mode = "single"  # "single" または "double"
        
        # ファイルダイアログ設定
        self.show_hidden_files = False
        self.default_file_filter = "*.*"
        
        # UI設定
        self.double_click_interval = 0.5  # 秒
        
        self._initialized = True
    
    def set_click_mode(self, mode: str):
        """クリックモードを設定"""
        if mode in ["single", "double"]:
            self.click_mode = mode
            print(f"Click mode changed to: {mode}")
        else:
            print(f"Invalid click mode: {mode}")
    
    def get_click_mode(self) -> str:
        """現在のクリックモードを取得"""
        return self.click_mode
    
    def is_single_click_mode(self) -> bool:
        """シングルクリックモードかどうか"""
        return self.click_mode == "single"
    
    def is_double_click_mode(self) -> bool:
        """ダブルクリックモードかどうか"""
        return self.click_mode == "double"
    
    def toggle_click_mode(self):
        """クリックモードを切り替え"""
        if self.click_mode == "single":
            self.set_click_mode("double")
        else:
            self.set_click_mode("single")
    
    def get_double_click_interval(self) -> float:
        """ダブルクリック判定間隔を取得"""
        return self.double_click_interval
    
    def set_double_click_interval(self, interval: float):
        """ダブルクリック判定間隔を設定"""
        if 0.1 <= interval <= 2.0:
            self.double_click_interval = interval
        else:
            print(f"Invalid double click interval: {interval}")
    
    def get_settings_info(self) -> str:
        """設定情報の文字列を取得"""
        mode_text = "Single-click" if self.is_single_click_mode() else "Double-click"
        return f"Mode: {mode_text} | Interval: {self.double_click_interval}s"

# シングルトンインスタンス
settings = SystemSettings()
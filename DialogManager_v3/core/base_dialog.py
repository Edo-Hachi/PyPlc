"""
ダイアログの基底クラスを定義するモジュール

座標変換、イベントディスパッチ、モーダル表示機能を提供します。
"""
import pyxel
from typing import List, Tuple, Optional, Dict, Any, Callable


class BaseDialog:
    """
    ダイアログの基底クラス
    
    座標変換とイベントディスパッチを担当します。
    """
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 300, height: int = 200, title: str = "", modal: bool = False):
        """
        ダイアログを初期化します。
        
        Args:
            x: ダイアログのX座標（画面左上基準、デフォルト: 0）
            y: ダイアログのY座標（画面左上基準、デフォルト: 0）
            width: ダイアログの幅（デフォルト: 300）
            height: ダイアログの高さ（デフォルト: 200）
            title: ダイアログのタイトル（デフォルト: 空文字列）
            modal: モーダルダイアログとして表示するかどうか（デフォルト: False）
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.visible = False
        self.modal = modal
        self.controls = []  # type: List[Any]  # ControlBase のリスト
        self.result = None
        self.focused_control = None  # type: Optional[Any]
        self.hovered_control = None  # type: Optional[Any]
        
    def to_local_coords(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """
        画面座標をダイアログローカル座標に変換します。
        
        Args:
            screen_x: 画面X座標
            screen_y: 画面Y座標
            
        Returns:
            Tuple[int, int]: (local_x, local_y) ダイアログローカル座標
        """
        return (screen_x - self.x, screen_y - self.y)
    
    def to_screen_coords(self, local_x: int, local_y: int) -> Tuple[int, int]:
        """
        ダイアログローカル座標を画面座標に変換します。
        
        Args:
            local_x: ローカルX座標
            local_y: ローカルY座標
            
        Returns:
            Tuple[int, int]: (screen_x, screen_y) 画面座標
        """
        return (self.x + local_x, self.y + local_y)
    
    def show_modal(self) -> Any:
        """
        モーダルダイアログとして表示します。
        
        Returns:
            Any: ダイアログの結果（OKボタンが押された場合の値など）
        """
        self.visible = True
        self.modal = True
        # メインループは外部で実装（Pyxelのループに統合）
        return self.result
    
    def show_modal_loop(self, escape_key_enabled: bool = True, 
                       background_color: int = None) -> Any:
        """
        統一モーダルループ実装
        各ダイアログの重複コードを削減
        
        Args:
            escape_key_enabled: ESCキーでの終了を有効にするか（デフォルト: True）
            background_color: 背景クリア色（Noneの場合はpyxel.COLOR_BLACK）
            
        Returns:
            Any: ダイアログの結果
        """
        # デフォルト背景色設定（pyxelをインポート確認後）
        if background_color is None:
            background_color = pyxel.COLOR_BLACK
            
        # ダイアログ状態初期化
        self.visible = True
        self.modal = True
        if not hasattr(self, 'cancelled'):
            self.cancelled = False
        
        print(f"[BaseDialog] Starting modal loop for '{self.title}'")
        
        try:
            while self.visible:
                # 更新処理
                self.update()
                
                # マウス処理（ダイアログが独自実装を持つ場合はスキップ）
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    print(f"[DEBUG] BaseDialog.show_modal_loop: Mouse LEFT clicked at ({pyxel.mouse_x}, {pyxel.mouse_y})")
                    if hasattr(self, '_handle_mouse_click') and callable(self._handle_mouse_click):
                        # ダイアログが独自のマウス処理を持つ場合
                        print(f"[DEBUG] BaseDialog: Using custom _handle_mouse_click")
                        self._handle_mouse_click(pyxel.mouse_x, pyxel.mouse_y)
                    else:
                        # BaseDialogの標準マウス処理
                        print(f"[DEBUG] BaseDialog: Using standard handle_mouse")
                        self.handle_mouse(pyxel.mouse_x, pyxel.mouse_y, True)
                
                # キーボード処理（ダイアログが独自実装を持つ場合は併用）
                for key in range(256):
                    if pyxel.btnp(key):
                        if key == pyxel.KEY_ESCAPE and escape_key_enabled:
                            print(f"[BaseDialog] ESC key pressed - closing dialog")
                            self.cancelled = True
                            self.visible = False
                            break
                        else:
                            # ダイアログが独自のキーボード処理を持つ場合はそれを使用
                            if hasattr(self, 'handle_key_input') and callable(self.handle_key_input):
                                self.handle_key_input(key)
                            else:
                                # BaseDialogの標準キーボード処理
                                self.handle_key(key)
                
                # 描画
                pyxel.cls(background_color)
                self.draw()
                pyxel.flip()
                
            print(f"[BaseDialog] Modal loop ended for '{self.title}', result: {self.result}")
            return self.result
            
        except Exception as e:
            print(f"[BaseDialog] Modal loop error: {e}")
            import traceback
            traceback.print_exc()
            self.visible = False
            self.cancelled = True
            return None
    
    def close(self, result: Any = None) -> None:
        """
        ダイアログを閉じます。
        
        Args:
            result: ダイアログの結果
        """
        self.result = result
        self.visible = False
        self.modal = False
        
        # フォーカスをクリア
        if self.focused_control:
            self.focused_control.on_lose_focus()
            self.focused_control = None
    
    def handle_mouse(self, x: int, y: int, clicked: bool) -> bool:
        """
        マウス入力を処理します。
        
        Args:
            x: マウスのX座標（画面座標）
            y: マウスのY座標（画面座標）
            clicked: マウスボタンが押されているか
            
        Returns:
            bool: イベントが処理された場合はTrue、それ以外はFalse
        """
        # ダイアログが表示されていない場合は何もしない
        if not self.visible:
            return False
            
        # 画面座標をローカル座標に変換
        local_x, local_y = self.to_local_coords(x, y)
        
        # ダイアログの外側をクリックした場合
        if not (0 <= local_x < self.width and 0 <= local_y < self.height):
            if clicked:
                # モーダルダイアログの外側をクリックしても閉じない
                pass
            return False
        
        # ホバー状態の更新
        new_hovered = None
        for control in reversed(self.controls):
            if control.is_inside(local_x, local_y):
                new_hovered = control
                break
        
        # ホバー状態の変化を検出
        if new_hovered != self.hovered_control:
            if self.hovered_control:
                self.hovered_control.on_mouse_leave()
            if new_hovered:
                new_hovered.on_mouse_enter()
            self.hovered_control = new_hovered
        
        # クリック処理
        if clicked and new_hovered:
            # フォーカスの移動
            if self.focused_control and self.focused_control != new_hovered:
                self.focused_control.on_lose_focus()
                self.focused_control = None
            
            if new_hovered.can_focus:
                if self.focused_control != new_hovered:
                    self.focused_control = new_hovered
                    new_hovered.on_gain_focus()
            
            # コントロールのクリックイベントを発火
            new_hovered.on_click(local_x - new_hovered.x, local_y - new_hovered.y)
            return True
            
        return False
    
    def handle_key(self, key: int) -> bool:
        """
        キーボード入力を処理します。
        
        Args:
            key: 押されたキーのコード
            
        Returns:
            bool: イベントが処理された場合はTrue、それ以外はFalse
        """
        if not self.visible or not self.focused_control:
            return False
            
        # フォーカスされたコントロールにキー入力を転送
        return self.focused_control.on_key(key)
    
    def handle_text_input(self, char: str) -> bool:
        """
        テキスト入力イベントを処理します。
        
        Args:
            char: 入力された文字
            
        Returns:
            bool: イベントが処理された場合はTrue、それ以外はFalse
        """
        if not self.visible or not self.focused_control:
            return False
            
        # フォーカスされたコントロールにテキスト入力を転送
        if hasattr(self.focused_control, 'on_text'):
            return self.focused_control.on_text(char)
        return False
    
    def update(self) -> None:
        """
        ダイアログの状態を更新します。
        フレームごとに呼び出されます。
        """
        if not self.visible:
            return
            
        # コントロールの状態を更新
        for control in self.controls:
            if hasattr(control, 'update'):
                control.update()
    
    def draw(self) -> None:
        """
        ダイアログを描画します。
        """
        if not self.visible:
            return
            
        # ダイアログの背景を描画（明るいグレー）
        pyxel.rect(self.x, self.y, self.width, self.height, 7)  # 7: ライトグレー
        
        # ダイアログの枠を描画（黒）
        pyxel.rectb(self.x, self.y, self.width, self.height, 0)  # 0: 黒
        
        # タイトルバーを描画（青）
        if self.title:
            title_bar_height = 16
            pyxel.rect(self.x, self.y, self.width, title_bar_height, 1)  # 1: 濃い青
            pyxel.text(self.x + 4, self.y + 4, self.title, 7)  # 7: 白
        
        # コントロールの描画（ダイアログの相対座標を渡す）
        for control in self.controls:
            if hasattr(control, 'visible') and control.visible:
                # コントロールの描画メソッドが存在することを確認
                if hasattr(control, 'draw'):
                    # コントロールの座標はダイアログからの相対座標で管理されていると仮定
                    control.draw(self.x, self.y)
                else:
                    print(f"Warning: Control {control} does not have a draw method")
    
    def add_control(self, control: Any) -> None:
        """
        コントロールを追加します。
        
        Args:
            control: 追加するコントロール
        """
        self.controls.append(control)
        control.parent = self
    
    def remove_control(self, control: Any) -> None:
        """
        コントロールを削除します。
        
        Args:
            control: 削除するコントロール
        """
        if control in self.controls:
            self.controls.remove(control)
            if self.focused_control == control:
                self.focused_control = None
            if self.hovered_control == control:
                self.hovered_control = None
    
    def find_control_by_id(self, control_id: str) -> Optional[Any]:
        """
        指定されたIDのコントロールを検索します。
        
        Args:
            control_id: 検索するコントロールのID
            
        Returns:
            見つかったコントロール、見つからない場合はNone
        """
        for control in self.controls:
            if hasattr(control, 'id') and control.id == control_id:
                return control
        return None

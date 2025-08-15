"""
コントロールの基底クラスを定義するモジュール

すべてのUIコントロールが継承する基本クラスを提供します。
"""
from typing import Optional, Dict, Any, Callable, Tuple


class ControlBase:
    """
    すべてのUIコントロールの基底クラス
    
    共通のプロパティとメソッドを定義します。
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, **kwargs):
        """
        コントロールを初期化します。
        
        Args:
            x: 親要素からの相対X座標
            y: 親要素からの相対Y座標
            width: コントロールの幅
            height: コントロールの高さ
            **kwargs: 追加のプロパティ
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = kwargs.get('visible', True)
        self.enabled = kwargs.get('enabled', True)
        self.can_focus = kwargs.get('can_focus', False)
        self.has_focus = False  # フォーカス状態を自身で管理
        self.id = kwargs.get('id', '')
        self.tag = kwargs.get('tag', '')
        self.parent = None  # type: Optional[Any]  # 親コントロールやダイアログへの参照
        self._event_handlers = {}  # type: Dict[str, Callable]
        self._dirty = True  # 再描画が必要かどうか
        
    def is_inside(self, x: int, y: int) -> bool:
        """
        指定された座標がコントロール内にあるかどうかを判定します。
        
        Args:
            x: 親要素からの相対X座標
            y: 親要素からの相対Y座標
            
        Returns:
            bool: 座標がコントロール内にある場合はTrue
        """
        if not self.visible or not self.enabled:
            return False
            
        return (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height)
    
    def on_click(self, local_x: int, local_y: int) -> bool:
        """
        クリックイベントを処理します。
        
        Args:
            local_x: コントロールからの相対X座標
            local_y: コントロールからの相対Y座標
            
        Returns:
            bool: イベントが処理された場合はTrue
        """
        if not self.enabled or not self.visible:
            return False
            
        self.emit('click', {'x': local_x, 'y': local_y})
        return True
    
    def on_mouse_enter(self) -> None:
        """
        マウスがコントロール上に入ったときに呼び出されます。
        """
        if not self.enabled or not self.visible:
            return
            
        self.emit('mouse_enter')
    
    def on_mouse_leave(self) -> None:
        """
        マウスがコントロールから出たときに呼び出されます。
        """
        if not self.enabled or not self.visible:
            return
            
        self.emit('mouse_leave')
    
    def on_gain_focus(self) -> None:
        """
        コントロールがフォーカスを得たときに呼び出されます。
        """
        if not self.enabled or not self.visible:
            return
        
        self.has_focus = True
        self._dirty = True
        self.emit('focus')
    
    def on_lose_focus(self) -> None:
        """
        コントロールがフォーカスを失ったときに呼び出されます。
        """
        if not self.enabled or not self.visible:
            return
            
        self.has_focus = False
        self._dirty = True
        self.emit('blur')
    
    def on_key(self, key: int) -> bool:
        """
        キーボード入力を処理します。
        
        Args:
            key: 押されたキーのコード
            
        Returns:
            bool: イベントが処理された場合はTrue
        """
        if not self.enabled or not self.visible:
            return False
            
        self.emit('key', {'key': key})
        return False
    
    def update(self) -> None:
        """
        コントロールの状態を更新します。
        フレームごとに呼び出されます。
        """
        pass
    
    def draw(self, offset_x: int, offset_y: int) -> None:
        """
        コントロールを描画します。
        
        Args:
            offset_x: 親要素のXオフセット
            offset_y: 親要素のYオフセット
        """
        # 子クラスで実装
        pass
    
    def emit(self, event_name: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        イベントを発行します。
        
        Args:
            event_name: イベント名
            data: イベントデータ
        """
        if data is None:
            data = {}
            
        # コントロールに登録されたイベントハンドラを呼び出す
        handler = self._event_handlers.get(event_name)
        if handler:
            handler(self, data)
        
        # 親ダイアログにもイベントを伝播
        if self.parent and hasattr(self.parent, 'on_control_event'):
            self.parent.on_control_event(self, event_name, data)
    
    def on(self, event_name: str, handler: Callable) -> None:
        """
        イベントハンドラを登録します。
        
        Args:
            event_name: イベント名
            handler: イベントハンドラ関数
        """
        self._event_handlers[event_name] = handler
    
    def off(self, event_name: str) -> None:
        """
        イベントハンドラを削除します。
        
        Args:
            event_name: イベント名
        """
        if event_name in self._event_handlers:
            del self._event_handlers[event_name]
    
    def set_position(self, x: int, y: int) -> None:
        """
        コントロールの位置を設定します。
        
        Args:
            x: 新しいX座標
            y: 新しいY座標
        """
        if self.x != x or self.y != y:
            self.x = x
            self.y = y
            self._dirty = True
    
    def set_size(self, width: int, height: int) -> None:
        """
        コントロールのサイズを設定します。
        
        Args:
            width: 新しい幅
            height: 新しい高さ
        """
        if self.width != width or self.height != height:
            self.width = width
            self.height = height
            self._dirty = True
    
    def set_visible(self, visible: bool) -> None:
        """
        コントロールの表示/非表示を設定します。
        
        Args:
            visible: 表示する場合はTrue
        """
        if self.visible != visible:
            self.visible = visible
            self._dirty = True
    
    def set_enabled(self, enabled: bool) -> None:
        """
        コントロールの有効/無効を設定します。
        
        Args:
            enabled: 有効にする場合はTrue
        """
        if self.enabled != enabled:
            self.enabled = enabled
            self._dirty = True
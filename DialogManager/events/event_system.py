"""
EventSystem - 疎結合イベントシステム

PyPlc Ver3 Dialog System - Phase 1 MVP Implementation
コールバック/サブスクライバーパターンによる疎結合イベント処理システム
"""

from typing import Dict, List, Callable, Any, Optional
from abc import ABC, abstractmethod
import weakref


class EventEmitter:
    """
    イベント発火・購読システムの基底クラス
    
    機能:
    - イベントの登録・解除
    - イベント発火
    - 弱参照による自動クリーンアップ
    """
    
    def __init__(self):
        """
        EventEmitter初期化
        """
        # イベント名 -> コールバック関数リスト
        self._event_callbacks: Dict[str, List[Callable]] = {}
        
        # 弱参照によるコールバック管理（メモリリーク防止）
        self._weak_callbacks: Dict[str, List[weakref.ref]] = {}
    
    def on(self, event_name: str, callback: Callable, use_weak_ref: bool = False) -> None:
        """
        イベントリスナーを登録
        
        Args:
            event_name: イベント名
            callback: コールバック関数
            use_weak_ref: 弱参照を使用するか（メモリリーク防止）
        """
        if use_weak_ref:
            # 弱参照でコールバックを管理
            if event_name not in self._weak_callbacks:
                self._weak_callbacks[event_name] = []
            
            weak_callback = weakref.ref(callback)
            self._weak_callbacks[event_name].append(weak_callback)
        else:
            # 通常の参照でコールバックを管理
            if event_name not in self._event_callbacks:
                self._event_callbacks[event_name] = []
            
            self._event_callbacks[event_name].append(callback)
    
    def off(self, event_name: str, callback: Callable = None) -> None:
        """
        イベントリスナーを解除
        
        Args:
            event_name: イベント名
            callback: 解除するコールバック関数（Noneの場合は全て解除）
        """
        # 通常の参照から解除
        if event_name in self._event_callbacks:
            if callback is None:
                # 全てのコールバックを解除
                self._event_callbacks[event_name].clear()
            else:
                # 指定されたコールバックのみ解除
                if callback in self._event_callbacks[event_name]:
                    self._event_callbacks[event_name].remove(callback)
        
        # 弱参照から解除
        if event_name in self._weak_callbacks:
            if callback is None:
                # 全ての弱参照を解除
                self._weak_callbacks[event_name].clear()
            else:
                # 指定されたコールバックの弱参照を解除
                self._weak_callbacks[event_name] = [
                    ref for ref in self._weak_callbacks[event_name]
                    if ref() is not None and ref() != callback
                ]
    
    def emit(self, event_name: str, *args, **kwargs) -> int:
        """
        イベントを発火
        
        Args:
            event_name: イベント名
            *args: イベント引数
            **kwargs: イベントキーワード引数
            
        Returns:
            実行されたコールバック数
        """
        executed_count = 0
        
        # 通常の参照のコールバックを実行
        if event_name in self._event_callbacks:
            for callback in self._event_callbacks[event_name][:]:  # コピーして安全に実行
                try:
                    callback(*args, **kwargs)
                    executed_count += 1
                except Exception as e:
                    print(f"Event callback error for '{event_name}': {e}")
        
        # 弱参照のコールバックを実行
        if event_name in self._weak_callbacks:
            # 無効な弱参照を除去しながら実行
            valid_callbacks = []
            for weak_ref in self._weak_callbacks[event_name]:
                callback = weak_ref()
                if callback is not None:
                    valid_callbacks.append(weak_ref)
                    try:
                        callback(*args, **kwargs)
                        executed_count += 1
                    except Exception as e:
                        print(f"Event callback error for '{event_name}': {e}")
            
            # 有効な弱参照のみ保持
            self._weak_callbacks[event_name] = valid_callbacks
        
        return executed_count
    
    def has_listeners(self, event_name: str) -> bool:
        """
        指定されたイベントにリスナーが登録されているかチェック
        
        Args:
            event_name: イベント名
            
        Returns:
            リスナーが存在する場合True
        """
        # 通常の参照をチェック
        if event_name in self._event_callbacks and self._event_callbacks[event_name]:
            return True
        
        # 弱参照をチェック（有効な参照のみ）
        if event_name in self._weak_callbacks:
            for weak_ref in self._weak_callbacks[event_name]:
                if weak_ref() is not None:
                    return True
        
        return False
    
    def get_event_names(self) -> List[str]:
        """
        登録されているイベント名の一覧を取得
        
        Returns:
            イベント名のリスト
        """
        event_names = set()
        event_names.update(self._event_callbacks.keys())
        event_names.update(self._weak_callbacks.keys())
        return list(event_names)
    
    def clear_all_listeners(self) -> None:
        """
        すべてのイベントリスナーをクリア
        """
        self._event_callbacks.clear()
        self._weak_callbacks.clear()


class DialogEventSystem(EventEmitter):
    """
    ダイアログ専用のイベントシステム
    
    機能:
    - ダイアログ固有のイベント管理
    - コントロール間のイベント伝播
    - イベントの優先度制御
    """
    
    def __init__(self):
        """
        DialogEventSystem初期化
        """
        super().__init__()
        
        # イベント優先度管理
        self._event_priorities: Dict[str, int] = {}
        
        # イベント伝播制御
        self._propagation_stopped: Dict[str, bool] = {}
        
        # 標準ダイアログイベントを定義
        self._define_standard_events()
    
    def _define_standard_events(self) -> None:
        """
        標準ダイアログイベントを定義
        """
        standard_events = {
            # ダイアログレベルイベント
            "dialog_show": 100,
            "dialog_close": 100,
            "dialog_resize": 90,
            
            # コントロールレベルイベント
            "control_click": 80,
            "control_hover": 70,
            "control_focus": 75,
            "control_blur": 75,
            "control_change": 85,
            
            # 入力イベント
            "key_press": 60,
            "mouse_move": 50,
            "mouse_click": 80,
            
            # カスタムイベント（デフォルト優先度）
            "custom": 50
        }
        
        self._event_priorities.update(standard_events)
    
    def set_event_priority(self, event_name: str, priority: int) -> None:
        """
        イベントの優先度を設定
        
        Args:
            event_name: イベント名
            priority: 優先度（高い値ほど高優先度）
        """
        self._event_priorities[event_name] = priority
    
    def get_event_priority(self, event_name: str) -> int:
        """
        イベントの優先度を取得
        
        Args:
            event_name: イベント名
            
        Returns:
            イベント優先度
        """
        return self._event_priorities.get(event_name, 50)  # デフォルト優先度
    
    def stop_propagation(self, event_name: str) -> None:
        """
        イベント伝播を停止
        
        Args:
            event_name: イベント名
        """
        self._propagation_stopped[event_name] = True
    
    def is_propagation_stopped(self, event_name: str) -> bool:
        """
        イベント伝播が停止されているかチェック
        
        Args:
            event_name: イベント名
            
        Returns:
            伝播が停止されている場合True
        """
        return self._propagation_stopped.get(event_name, False)
    
    def emit_with_priority(self, event_name: str, *args, **kwargs) -> int:
        """
        優先度を考慮してイベントを発火
        
        Args:
            event_name: イベント名
            *args: イベント引数
            **kwargs: イベントキーワード引数
            
        Returns:
            実行されたコールバック数
        """
        # 伝播が停止されている場合は実行しない
        if self.is_propagation_stopped(event_name):
            return 0
        
        # 通常のemitを実行
        executed_count = self.emit(event_name, *args, **kwargs)
        
        # イベント実行後に伝播停止フラグをリセット
        if event_name in self._propagation_stopped:
            del self._propagation_stopped[event_name]
        
        return executed_count
    
    def create_event_context(self, source_control_id: str = None) -> 'EventContext':
        """
        イベントコンテキストを作成
        
        Args:
            source_control_id: イベント発生元のコントロールID
            
        Returns:
            イベントコンテキスト
        """
        return EventContext(self, source_control_id)


class EventContext:
    """
    イベント実行時のコンテキスト情報
    
    機能:
    - イベント発生元の情報
    - イベント伝播制御
    - イベントデータの管理
    """
    
    def __init__(self, event_system: DialogEventSystem, source_control_id: str = None):
        """
        EventContext初期化
        
        Args:
            event_system: イベントシステム
            source_control_id: イベント発生元のコントロールID
        """
        self.event_system = event_system
        self.source_control_id = source_control_id
        self.data: Dict[str, Any] = {}
        self.timestamp = None
        
        # タイムスタンプ設定（利用可能な場合）
        try:
            import time
            self.timestamp = time.time()
        except ImportError:
            pass
    
    def set_data(self, key: str, value: Any) -> None:
        """
        イベントデータを設定
        
        Args:
            key: データキー
            value: データ値
        """
        self.data[key] = value
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """
        イベントデータを取得
        
        Args:
            key: データキー
            default: デフォルト値
            
        Returns:
            データ値
        """
        return self.data.get(key, default)
    
    def stop_propagation(self, event_name: str) -> None:
        """
        イベント伝播を停止
        
        Args:
            event_name: イベント名
        """
        self.event_system.stop_propagation(event_name)


# グローバルイベントシステムインスタンス（シングルトンパターン）
_global_dialog_event_system: Optional[DialogEventSystem] = None


def get_dialog_event_system() -> DialogEventSystem:
    """
    グローバルダイアログイベントシステムを取得
    
    Returns:
        ダイアログイベントシステムインスタンス
    """
    global _global_dialog_event_system
    
    if _global_dialog_event_system is None:
        _global_dialog_event_system = DialogEventSystem()
    
    return _global_dialog_event_system


def reset_dialog_event_system() -> None:
    """
    グローバルダイアログイベントシステムをリセット
    """
    global _global_dialog_event_system
    _global_dialog_event_system = None


# EventSystemエイリアス（後方互換性のため）
EventSystem = DialogEventSystem

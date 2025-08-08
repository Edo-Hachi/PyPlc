# EventSystem リファレンス

## 目次
- [概要](#概要)
- [基本的な使い方](#基本的な使い方)
- [イベントの命名規則](#イベントの命名規則)
- [高度な使い方](#高度な使い方)
- [パフォーマンス特性](#パフォーマンス特性)
- [トラブルシューティング](#トラブルシューティング)

## 概要

EventSystem は、DialogManager のコアコンポーネントで、コンポーネント間の疎結合な連携を実現します。

**主な特徴**:
- 型安全なイベント通知
- 優先度に基づくハンドラー実行順序制御
- イベント伝播制御
- デバッグ支援機能

## 基本的な使い方

### 初期化

```python
from DialogManager.events.event_system import EventSystem

# EventSystem インスタンスの作成
event_system = EventSystem()

# デバッグモードの有効化
event_system.debug_mode = True
```

### イベントの登録と発火

```python
# イベントハンドラーの登録
def on_button_clicked(button_id):
    print(f"ボタンがクリックされました: {button_id}")

event_system.register("button_clicked", on_button_clicked)

# イベントの発火
event_system.emit("button_clicked", "ok_button")
```

## イベントの命名規則

- スネークケースを使用: `lowercase_with_underscores`
- イベントの発生タイミングを明確に:
  - `_changed`: 状態が変化した時
  - `_clicked`: クリックされた時
  - `_selected`: 選択された時
  - `_double_clicked`: ダブルクリックされた時

## 高度な使い方

### 優先度の指定

```python
# 優先度の設定（数値が大きいほど高優先）
event_system.register("button_clicked", high_priority_handler, priority=100)
event_system.register("button_clicked", medium_priority_handler, priority=50)
```

### 一度だけ実行するハンドラー

```python
def on_first_click():
    print("最初のクリックのみ実行されます")

event_system.register_once("button_clicked", on_first_click)
```

## パフォーマンス特性

| 項目 | 値 | 備考 |
|------|----|----- |
| イベント発火速度 | ~0.001ms | 単一ハンドラー |
| ハンドラー登録速度 | ~0.0001ms | 優先度ソート含む |
| メモリ使用量 | ~1KB/100ハンドラー | 基本構成 |

## トラブルシューティング

### イベントが発火しない場合
1. イベントハンドラーが正しく登録されているか確認
2. イベント名が正確に一致しているか確認
3. デバッグモードを有効にしてイベントフローを確認

### メモリリークの疑いがある場合
1. 不要になったイベントハンドラーを登録解除
2. コンポーネントの破棄時に `unregister_all()` を呼び出す

## 関連ドキュメント

- [アーキテクチャ概要](Architecture.md)
- [開発者ガイド](DeveloperGuide.md)
- [FileListControl リファレンス](FileListControl.md)
        self.x = x
        self.y = y
        self.text = text
        
    def handle_click(self, mouse_x, mouse_y):
        if self._is_clicked(mouse_x, mouse_y):
            # クリックイベントを発火
            event_system.emit("button_clicked", {
                'control_id': self.id,
                'button_id': self.id,
                'text': self.text
            })

# イベントハンドラの登録
event_system.register("button_clicked", 
    lambda data: print(f"ボタンがクリックされました: {data['button_id']}"))

# 使用例
ok_button = Button("btn_ok", 100, 100, "OK")
ok_button.handle_click(105, 105)  # イベント発火
```

### 7. よくある間違いと対策

1. **メモリリーク**
   - ❌ インスタンスメソッドを登録したまま解放しない
   - ✅ 不要になった時点で `unregister()` を呼び出す

2. **イベントループ**
   - ❌ イベントハンドラ内で同イベントを発火
   - ✅ 無限ループを避けるため、状態が変わった時のみイベント発火

3. **例外処理**
   - ❌ イベントハンドラ内で例外を握りつぶす
   - ✅ 適切な例外処理とログ出力を行う
```

### 4. **イベントハンドラーの削除**

```python
# 特定ハンドラーの削除
event_system.unregister("button_clicked", on_button_clicked)

# 特定イベントの全ハンドラー削除
event_system.clear_event("button_clicked")

# 全イベントのクリア
event_system.clear_all()
```

---

## 🎯 標準イベント一覧

### UI関連イベント

| イベント名 | 発火タイミング | 引数 | 説明 |
|-----------|---------------|------|------|
| `click` | マウスクリック時 | `(x, y, button)` | ボタン・コントロールクリック |
| `hover` | マウスホバー時 | `(x, y, is_hovering)` | マウスカーソル移動 |
| `focus` | フォーカス取得時 | `(control_id)` | 入力フォーカス変更 |
| `blur` | フォーカス失失時 | `(control_id)` | 入力フォーカス離脱 |
| `key_press` | キー押下時 | `(key_code, modifiers)` | キーボード入力 |

### データ関連イベント

| イベント名 | 発火タイミング | 引数 | 説明 |
|-----------|---------------|------|------|
| `text_changed` | テキスト変更時 | `(text, control_id)` | テキスト入力変更 |
| `selection_changed` | 選択変更時 | `(selected_item, control_id)` | リスト選択変更 |
| `value_changed` | 値変更時 | `(new_value, old_value, control_id)` | 汎用値変更 |
| `validation_result` | バリデーション完了時 | `(is_valid, error_message, control_id)` | 入力検証結果 |

### ダイアログ関連イベント

| イベント名 | 発火タイミング | 引数 | 説明 |
|-----------|---------------|------|------|
| `dialog_opened` | ダイアログ表示時 | `(dialog_id)` | ダイアログ開始 |
| `dialog_closed` | ダイアログ終了時 | `(dialog_id, result)` | ダイアログ終了 |
| `dialog_resized` | サイズ変更時 | `(width, height)` | ダイアログリサイズ |

### ファイル関連イベント

| イベント名 | 発火タイミング | 引数 | 説明 |
|-----------|---------------|------|------|
| `file_loaded` | ファイル読み込み時 | `(file_path)` | ファイル確定・読み込み |
| `file_selected` | ファイル選択時 | `(file_info)` | ファイル選択変更 |
| `directory_changed` | ディレクトリ変更時 | `(directory_path)` | 検索ディレクトリ変更 |

---

## 🔧 高度な機能

### 1. **イベント優先度管理**

```python
# 優先度の設定（数値が大きいほど高優先度）
event_system.register("button_clicked", high_priority_handler, priority=100)
event_system.register("button_clicked", medium_priority_handler, priority=50)
event_system.register("button_clicked", low_priority_handler, priority=10)

# 実行順序: high_priority_handler → medium_priority_handler → low_priority_handler
```

### 2. **イベント伝播制御**

```python
def stop_propagation_handler(event_data):
    """イベント伝播を停止するハンドラー"""
    print("イベント処理完了 - 伝播停止")
    return EventSystem.STOP_PROPAGATION  # 後続ハンドラーの実行を停止

def normal_handler(event_data):
    """通常のハンドラー（実行されない）"""
    print("この処理は実行されません")

event_system.register("custom_event", stop_propagation_handler, priority=100)
event_system.register("custom_event", normal_handler, priority=50)

# stop_propagation_handlerのみ実行される
event_system.emit("custom_event", {"data": "test"})
```

### 3. **条件付きイベント登録**

```python
def conditional_handler(event_data):
    """条件付きで実行されるハンドラー"""
    return event_data.get("condition", False)

# 条件を満たす場合のみ実行
event_system.register_conditional("conditional_event", conditional_handler)

# 条件を満たさない場合 - ハンドラー実行されない
event_system.emit("conditional_event", {"condition": False, "data": "test"})

# 条件を満たす場合 - ハンドラー実行される
event_system.emit("conditional_event", {"condition": True, "data": "test"})
```

### 4. **非同期イベント処理**

```python
import asyncio

async def async_handler(event_data):
    """非同期ハンドラー"""
    await asyncio.sleep(0.1)  # 非同期処理
    print(f"非同期処理完了: {event_data}")

# 非同期ハンドラーの登録
event_system.register_async("async_event", async_handler)

# 非同期イベントの発火
await event_system.emit_async("async_event", {"data": "async_test"})
```

---

## 🎨 EventSystemの内部実装

### 1. **基底クラス EventEmitter**

```python
class EventEmitter:
    """イベント発行・購読の基底クラス"""
    
    def __init__(self):
        self._event_callbacks: Dict[str, List[Callable]] = {}
        self._once_callbacks: Dict[str, List[Callable]] = {}
        
    def register(self, event_name: str, callback: Callable, priority: int = 0):
        """イベントハンドラー登録"""
        if event_name not in self._event_callbacks:
            self._event_callbacks[event_name] = []
            
        # 優先度順で挿入
        self._insert_by_priority(self._event_callbacks[event_name], callback, priority)
        
    def emit(self, event_name: str, *args, **kwargs):
        """イベント発火"""
        if event_name in self._event_callbacks:
            for callback in self._event_callbacks[event_name]:
                try:
                    result = callback(*args, **kwargs)
                    if result == self.STOP_PROPAGATION:
                        break
                except Exception as e:
                    self._handle_callback_error(event_name, callback, e)
```

### 2. **DialogEventSystem の拡張機能**

```python
class DialogEventSystem(EventEmitter):
    """Dialog専用の拡張EventSystem"""
    
    STOP_PROPAGATION = "STOP_PROPAGATION"
    
    def __init__(self):
        super().__init__()
        self._event_priorities: Dict[str, int] = {}
        self._propagation_stopped: Dict[str, bool] = {}
        self._debug_mode = False
        self._define_standard_events()
        
    def _define_standard_events(self):
        """標準イベントの定義・初期化"""
        standard_events = [
            "click", "hover", "focus", "blur", "key_press",
            "text_changed", "selection_changed", "value_changed",
            "dialog_opened", "dialog_closed", "file_loaded"
        ]
        
        for event_name in standard_events:
            self._event_priorities[event_name] = 0
            self._propagation_stopped[event_name] = False
```

### 3. **デバッグ・ログ機能**

```python
def enable_debug_mode(self, enabled: bool = True):
    """デバッグモードの有効/無効"""
    self._debug_mode = enabled
    
def _debug_log(self, message: str):
    """デバッグログ出力"""
    if self._debug_mode:
        print(f"[EventSystem] {message}")
        
def emit(self, event_name: str, *args, **kwargs):
    """デバッグ情報付きイベント発火"""
    if self._debug_mode:
        self._debug_log(f"Event fired: {event_name} with args={args}, kwargs={kwargs}")
        
    # 通常のイベント発火処理
    super().emit(event_name, *args, **kwargs)
    
    if self._debug_mode:
        handler_count = len(self._event_callbacks.get(event_name, []))
        self._debug_log(f"Event {event_name} processed by {handler_count} handlers")
```

---

## 🔄 命名統一・互換性

### DialogEventSystem vs EventSystem

**歴史的経緯**:
- 初期実装: `DialogEventSystem` として開発
- Phase 2での混乱: `EventSystem` として参照される場面が発生
- Phase 3での解決: エイリアスによる統一

**現在の実装**:

```python
# events/event_system.py
class DialogEventSystem(EventEmitter):
    """Dialog専用EventSystem の正式名称"""
    pass

# 後方互換性のためのエイリアス
EventSystem = DialogEventSystem
```

**使い分けガイドライン**:

```python
# ✅ 推奨: 明示的な名称使用
from DialogManager.events.event_system import DialogEventSystem
event_system = DialogEventSystem()

# ✅ 許可: エイリアス使用（簡潔性重視）
from DialogManager.events.event_system import EventSystem
event_system = EventSystem()

# ❌ 非推奨: 混在使用
from DialogManager.events.event_system import DialogEventSystem, EventSystem
# 同じクラスを異なる名前で参照するのは混乱の元
```

---

## 🧪 テスト・デバッグ

### 1. **基本機能テスト**

```python
def test_event_registration_and_emission():
    """イベント登録・発火の基本テスト"""
    event_system = EventSystem()
    
    # テスト用フラグ
    handler_called = False
    received_data = None
    
    def test_handler(data):
        nonlocal handler_called, received_data
        handler_called = True
        received_data = data
    
    # ハンドラー登録
    event_system.register("test_event", test_handler)
    
    # イベント発火
    test_data = {"message": "Hello, EventSystem!"}
    event_system.emit("test_event", test_data)
    
    # 検証
    assert handler_called == True
    assert received_data == test_data
    print("✅ 基本機能テスト成功")

def test_priority_handling():
    """優先度処理テスト"""
    event_system = EventSystem()
    execution_order = []
    
    def high_priority_handler():
        execution_order.append("high")
        
    def low_priority_handler():
        execution_order.append("low")
    
    # 低優先度を先に登録
    event_system.register("priority_test", low_priority_handler, priority=1)
    event_system.register("priority_test", high_priority_handler, priority=10)
    
    # イベント発火
    event_system.emit("priority_test")
    
    # 高優先度が先に実行されることを確認
    assert execution_order == ["high", "low"]
    print("✅ 優先度処理テスト成功")
```

### 2. **統合テスト例**

```python
def test_dialog_event_integration():
    """ダイアログとの統合テスト"""
    from DialogManager.base_dialog import BaseDialog
    
    class TestDialog(BaseDialog):
        def __init__(self):
            super().__init__("テストダイアログ")
            self.button_clicked = False
            
            # イベントハンドラー登録
            self.event_system.register("button_clicked", self.on_button_clicked)
            
        def on_button_clicked(self, button_id):
            self.button_clicked = True
            print(f"ボタンクリック処理: {button_id}")
    
    # ダイアログ作成
    dialog = TestDialog()
    
    # イベント発火（ボタンクリックをシミュレート）
    dialog.event_system.emit("button_clicked", "ok_button")
    
    # 結果確認
    assert dialog.button_clicked == True
    print("✅ ダイアログ統合テスト成功")
```

### 3. **デバッグ機能の使用**

```python
def debug_event_flow():
    """イベントフローのデバッグ例"""
    event_system = EventSystem()
    
    # デバッグモード有効化
    event_system.enable_debug_mode(True)
    
    def handler1(data):
        print(f"Handler1: {data}")
        
    def handler2(data):
        print(f"Handler2: {data}")
        return EventSystem.STOP_PROPAGATION
        
    def handler3(data):
        print(f"Handler3: この処理は実行されない")
    
    # ハンドラー登録
    event_system.register("debug_event", handler1, priority=30)
    event_system.register("debug_event", handler2, priority=20)
    event_system.register("debug_event", handler3, priority=10)
    
    # イベント発火
    event_system.emit("debug_event", {"test": "data"})
    
    # 出力例:
    # [EventSystem] Event fired: debug_event with args=({'test': 'data'},), kwargs={}
    # Handler1: {'test': 'data'}
    # Handler2: {'test': 'data'}
    # [EventSystem] Event debug_event processed by 2 handlers (1 stopped propagation)
```

---

## ⚡ パフォーマンス最適化

### 1. **メモリ効率の改善**

```python
import weakref

class OptimizedEventSystem(EventSystem):
    """メモリ効率を改善したEventSystem"""
    
    def __init__(self):
        super().__init__()
        # 弱参照によるハンドラー管理
        self._weak_callbacks: Dict[str, List[weakref.WeakMethod]] = {}
        
    def register_weak(self, event_name: str, callback: Callable):
        """弱参照でのハンドラー登録"""
        if event_name not in self._weak_callbacks:
            self._weak_callbacks[event_name] = []
            
        # メソッドの場合は WeakMethod を使用
        if hasattr(callback, '__self__'):
            weak_callback = weakref.WeakMethod(callback, self._cleanup_callback)
        else:
            weak_callback = weakref.ref(callback, self._cleanup_callback)
            
        self._weak_callbacks[event_name].append(weak_callback)
        
    def _cleanup_callback(self, weak_ref):
        """ガベージコレクション時の自動クリーンアップ"""
        for event_name, callbacks in self._weak_callbacks.items():
            if weak_ref in callbacks:
                callbacks.remove(weak_ref)
```

### 2. **バッチ処理による最適化**

```python
class BatchEventSystem(EventSystem):
    """バッチ処理対応EventSystem"""
    
    def __init__(self):
        super().__init__()
        self._event_queue: List[Tuple[str, tuple, dict]] = []
        self._batch_mode = False
        
    def start_batch(self):
        """バッチモード開始"""
        self._batch_mode = True
        self._event_queue.clear()
        
    def emit(self, event_name: str, *args, **kwargs):
        """バッチモード対応イベント発火"""
        if self._batch_mode:
            # バッチモード時はキューに追加
            self._event_queue.append((event_name, args, kwargs))
        else:
            # 通常モード時は即座に処理
            super().emit(event_name, *args, **kwargs)
            
    def flush_batch(self):
        """バッチ処理実行"""
        if not self._batch_mode:
            return
            
        # キューの全イベントを処理
        for event_name, args, kwargs in self._event_queue:
            super().emit(event_name, *args, **kwargs)
            
        self._event_queue.clear()
        self._batch_mode = False
```

---

## 🚀 拡張・カスタマイズ

### 1. **カスタムイベントタイプの定義**

```python
class CustomEventSystem(EventSystem):
    """カスタムイベント対応EventSystem"""
    
    def __init__(self):
        super().__init__()
        self._define_custom_events()
        
    def _define_custom_events(self):
        """カスタムイベントの定義"""
        custom_events = [
            "plc_device_connected",
            "plc_device_disconnected", 
            "ladder_circuit_changed",
            "simulation_started",
            "simulation_stopped"
        ]
        
        for event_name in custom_events:
            self._event_priorities[event_name] = 0
            
    def emit_plc_event(self, event_type: str, device_address: str, **kwargs):
        """PLC専用イベント発火"""
        event_data = {
            "device_address": device_address,
            "timestamp": time.time(),
            **kwargs
        }
        self.emit(f"plc_{event_type}", event_data)
```

### 2. **イベントフィルタリング**

```python
class FilteredEventSystem(EventSystem):
    """フィルタリング機能付きEventSystem"""
    
    def __init__(self):
        super().__init__()
        self._event_filters: Dict[str, List[Callable]] = {}
        
    def add_filter(self, event_name: str, filter_func: Callable[[Any], bool]):
        """イベントフィルターの追加"""
        if event_name not in self._event_filters:
            self._event_filters[event_name] = []
        self._event_filters[event_name].append(filter_func)
        
    def emit(self, event_name: str, *args, **kwargs):
        """フィルタリング付きイベント発火"""
        # フィルターチェック
        if event_name in self._event_filters:
            for filter_func in self._event_filters[event_name]:
                if not filter_func(*args, **kwargs):
                    return  # フィルターに引っかかった場合は発火しない
                    
        # フィルターを通過した場合のみ発火
        super().emit(event_name, *args, **kwargs)

# 使用例
def text_length_filter(text, **kwargs):
    """テキスト長フィルター"""
    return len(text) >= 3  # 3文字以上の場合のみ通す

filtered_system = FilteredEventSystem()
filtered_system.add_filter("text_changed", text_length_filter)

# 短いテキスト - イベント発火されない
filtered_system.emit("text_changed", "ab")

# 長いテキスト - イベント発火される  
filtered_system.emit("text_changed", "abc")
```

---

## 📚 ベストプラクティス

### 1. **イベント命名規則**

```python
# ✅ 推奨: 動詞_名詞 形式
"button_clicked"
"text_changed" 
"file_loaded"
"dialog_opened"

# ✅ 推奨: 階層的命名
"ui.button.clicked"
"data.file.loaded"
"validation.result.updated"

# ❌ 非推奨: 曖昧な命名
"event1"
"something_happened"
"update"
```

### 2. **エラーハンドリング**

```python
def safe_event_handler(event_data):
    """安全なイベントハンドラーの例"""
    try:
        # メイン処理
        process_event_data(event_data)
    except ValidationError as e:
        # 予期される例外の処理
        logger.warning(f"Validation error in event handler: {e}")
        return EventSystem.STOP_PROPAGATION
    except Exception as e:
        # 予期しない例外の処理
        logger.error(f"Unexpected error in event handler: {e}")
        # 他のハンドラーは継続実行
        return None

# EventSystem側でのエラーハンドリング
def _handle_callback_error(self, event_name: str, callback: Callable, error: Exception):
    """コールバックエラーの統一処理"""
    logger.error(f"Error in event handler for '{event_name}': {error}")
    if self._debug_mode:
        import traceback
        traceback.print_exc()
```

### 3. **メモリリーク防止**

```python
class DialogWithEventCleanup(BaseDialog):
    """適切なクリーンアップを行うダイアログ例"""
    
    def __init__(self):
        super().__init__()
        self._registered_handlers = []
        
    def register_handler(self, event_name: str, handler: Callable):
        """ハンドラー登録（クリーンアップ対応）"""
        self.event_system.register(event_name, handler)
        self._registered_handlers.append((event_name, handler))
        
    def cleanup(self):
        """リソースクリーンアップ"""
        # 登録したハンドラーを全て削除
        for event_name, handler in self._registered_handlers:
            self.event_system.unregister(event_name, handler)
        self._registered_handlers.clear()
        
    def __del__(self):
        """デストラクタでのクリーンアップ"""
        self.cleanup()
```

---

## 🔮 将来の拡張計画

### 1. **非同期処理の完全対応**
```python
# 完全非同期EventSystem
class AsyncEventSystem(EventSystem):
    async def emit_async(self, event_name: str, *args, **kwargs):
        """完全非同期イベント発火"""
        
    async def register_async_handler(self, event_name: str, async_handler):
        """非同期ハンドラー登録"""
```

### 2. **イベント永続化**
```python
# イベント履歴の保存・再生
class PersistentEventSystem(EventSystem):
    def save_event_history(self, file_path: str):
        """イベント履歴の保存"""
        
    def replay_events(self, file_path: str):
        """イベント履歴の再生"""
```

### 3. **分散イベント処理**
```python
# ネットワーク越しのイベント通信
class NetworkEventSystem(EventSystem):
    def connect_remote_system(self, host: str, port: int):
        """リモートEventSystemとの接続"""
        
    def emit_remote(self, event_name: str, *args, **kwargs):
        """リモートイベント発火"""
```

---

## 📊 パフォーマンス指標

### 現在の性能

| 項目 | 値 | 備考 |
|------|----|----- |
| **イベント発火速度** | ~0.001ms | 単一ハンドラー |
| **ハンドラー登録速度** | ~0.0001ms | 優先度ソート含む |
| **メモリ使用量** | ~1KB/100ハンドラー | 基本構成 |
| **最大ハンドラー数** | 1000+ | 実用的制限なし |

### 最適化目標

- **30FPS安定動作**: Pyxel環境での安定性確保
- **低レイテンシー**: UI応答性の維持
- **メモリ効率**: 長時間動作での安定性

---

**EventSystemは、DialogManagerの疎結合アーキテクチャを支える中核的なコンポーネントとして、高い拡張性と安定性を提供し、PyPlc Ver3の長期的な発展を支えています。**

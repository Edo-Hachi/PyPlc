# 開発者ガイド: カスタムコントロール開発

このガイドでは、DialogManager システムに新しいカスタムコントロールを追加する方法を説明します。

## 目次
- [はじめに](#はじめに)
- [コントロール開発の基本](#コントロール開発の基本)
  - [コントロールのライフサイクル](#コントロールのライフサイクル)
  - [BaseControl の基本](#basecontrol-の基本)
- [ステップバイステップガイド](#ステップバイステップガイド)
  - [1. コントロールクラスの作成](#1-コントロールクラスの作成)
  - [2. コントロールファクトリの拡張](#2-コントロールファクトリの拡張)
  - [3. JSON 定義のサポート](#3-json-定義のサポート)
  - [4. イベント処理の実装](#4-イベント処理の実装)
  - [5. テストとデバッグ](#5-テストとデバッグ)
- [高度なトピック](#高度なトピック)
  - [カスタムイベント](#カスタムイベント)
  - [アニメーションの実装](#アニメーションの実装)
  - [パフォーマンス最適化](#パフォーマンス最適化)
- [ベストプラクティス](#ベストプラクティス)
- [トラブルシューティング](#トラブルシューティング)
- [実装例: スライダーコントロール](#実装例-スライダーコントロール)

## はじめに

DialogManager は、拡張可能なコントロールシステムを提供しており、独自のカスタムコントロールを簡単に追加できます。このガイドでは、カスタムコントロールの作成からテストまでの流れを説明します。

## コントロール開発の基本

### コントロールのライフサイクル

1. **初期化** (`__init__`)
   - プロパティの初期化
   - リソースの事前読み込み

2. **セットアップ** (`setup` - 必要に応じて)
   - 依存関係の解決
   - サブコントロールの初期化

3. **入力処理** (`handle_input`)
   - マウス/キーボード入力の処理
   - 状態の更新

4. **更新** (`update` - 必要に応じて)
   - アニメーションの更新
   - 状態の更新

5. **描画** (`draw`)
   - コントロールの描画

6. **破棄** (`dispose` - 必要に応じて)
   - リソースの解放
   - イベントリスナーの削除

### BaseControl の基本

すべてのカスタムコントロールは `BaseControl` クラスを継承します。主な機能は以下の通りです：

- **座標管理**: 相対座標と絶対座標の変換
- **イベント処理**: イベントの発行と購読
- **プロパティ管理**: 可視性、有効/無効状態など
- **入力処理**: マウス/キーボード入力の基本処理

## ステップバイステップガイド

### 1. コントロールクラスの作成

新しいコントロールを作成するには、`BaseControl` を継承したクラスを作成します。以下の例では、基本的なカスタムコントロールの実装方法を示します。

```python
from typing import Dict, Any, Optional
from DialogManager.control_factory import BaseControl

class MyCustomControl(BaseControl):
    """カスタムコントロールの実装例"""
    
    def __init__(self, control_id: str, x: int, y: int, width: int, height: int, **kwargs):
        """
        カスタムコントロールの初期化
        
        Args:
            control_id: コントロールの一意識別子
            x, y: コントロールの位置
            width, height: コントロールのサイズ
            **kwargs: 追加のプロパティ
        """
        super().__init__(control_id, x, y, width, height, **kwargs)
        
        # カスタムプロパティの初期化
        self.custom_property = kwargs.get('custom_property', 'default_value')
        self.value = 0  # 例: スライダーの現在値など
        
    def handle_input(self, mouse_x: int, mouse_y: int, mouse_clicked: bool) -> None:
        """
        入力処理を実装
        
        Args:
            mouse_x, mouse_y: マウス座標
            mouse_clicked: マウスクリック状態
        """
        if not self.enabled or not self.visible:
            return
            
        # マウスがコントロール上にあるかチェック
        if self.point_in_control(mouse_x, mouse_y, 0, 0):  # ダイアログ座標は親が処理
            # マウスクリック処理
            if mouse_clicked:
                # クリックイベントを発行
                self.emit_event('click', {'value': self.value})
    
    def draw(self, dialog_x: int, dialog_y: int) -> None:
        """
        描画処理を実装
        
        Args:
            dialog_x, dialog_y: 親ダイアログの座標
        """
        if not self.visible:
            return
            
        # 絶対座標を計算
        abs_x, abs_y, width, height = self.get_absolute_rect(dialog_x, dialog_y)
        
        # 背景を描画
        pyxel.rect(abs_x, abs_y, width, height, self.bg_color)
        
        # ボーダーを描画
        pyxel.rectb(abs_x, abs_y, width, height, self.color)
        
        # カスタム描画処理
        # 例: テキスト表示
        pyxel.text(abs_x + 2, abs_y + 2, f"{self.custom_property}: {self.value}", self.color)
```

### 2. コントロールファクトリの拡張

新しいコントロールを JSON から生成できるようにするには、`ControlFactory` クラスを拡張します。

```python
class ControlFactory:
    # ... 既存のコード ...
    
    def _create_mycustom_control(self, definition: Dict[str, Any]) -> BaseControl:
        """
        カスタムコントロールを生成
        
        Args:
            definition: JSON定義
            
        Returns:
            生成されたカスタムコントロール
        """
        return MyCustomControl(
            control_id=definition["id"],
            x=definition["x"],
            y=definition["y"],
            width=definition["width"],
            height=definition["height"],
            custom_property=definition.get("custom_property", "default"),
            color=definition.get("color", 7),  # 白
            bg_color=definition.get("bg_color", 0)  # 黒
        )
    
    def __init__(self):
        # 既存の初期化コード...
        
        # カスタムコントロールの生成関数を登録
        self.control_creators["mycustom"] = self._create_mycustom_control
```

### 3. JSON 定義のサポート

新しいコントロールを JSON 定義で使用できるようにします。

```json
{
  "title": "カスタムコントロールテスト",
  "width": 300,
  "height": 200,
  "controls": [
    {
      "id": "my_control",
      "type": "mycustom",
      "x": 20,
      "y": 30,
      "width": 200,
      "height": 30,
      "custom_property": "カスタム値",
      "color": 7,
      "bg_color": 0,
      "events": ["click", "change"]
    }
  ]
}
```

### 4. イベント処理の実装

コントロールからイベントを発行する例：

```python
# コントロールクラス内で
self.emit_event('change', {'value': self.value, 'control_id': self.id})
```

イベントを購読する例：

```python
# ダイアログクラス内で
def _setup_event_handlers(self):
    self.event_system.subscribe('my_control', 'click', self._on_my_control_click)

def _on_my_control_click(self, event_data):
    print(f"Custom control clicked: {event_data}")
```

### 5. テストとデバッグ

新しいコントロールをテストするには：

1. テスト用の JSON 定義ファイルを作成
2. テスト用のダイアログクラスを作成
3. イベントハンドラを実装して動作を確認

```python
class TestCustomControlDialog(BaseDialog):
    def __init__(self):
        super().__init__("カスタムコントロールテスト", 300, 200)
        
        # JSONからロード
        self.loader = JSONDialogLoader()
        self.factory = ControlFactory()
        
        # コントロールを追加
        control = self.factory.create_control({
            "id": "test_control",
            "type": "mycustom",
            "x": 20,
            "y": 30,
            "width": 200,
            "height": 30,
            "custom_property": "テスト値"
        })
        
        self.add_control("test_control", control)
        
        # イベントハンドラを設定
        self.event_system.subscribe('test_control', 'click', self._on_click)
    
    def _on_click(self, event_data):
        print(f"Test control clicked: {event_data}")
```

## 高度なトピック

### カスタムイベント

独自のイベントを定義して発行することができます。例えば、スライダーコントロールの値が特定の閾値を超えたときに発火するイベントなどが考えられます。

```python
# カスタムイベントの発行例
if self.value > self.threshold:
    self.emit_event('threshold_exceeded', {
        'value': self.value,
        'threshold': self.threshold,
        'timestamp': time.time()
    })
```

### アニメーションの実装

コントロールにアニメーションを追加するには、`update` メソッドをオーバーライドします。

```python
def update(self, dt: float) -> None:
    """
    アニメーションの更新
    
    Args:
        dt: 前回の更新からの経過時間（秒）
    """
    if self.is_animating:
        self.animation_progress = min(1.0, self.animation_progress + dt / self.animation_duration)
        # イージング関数を適用して値を計算
        eased = self._ease_out_quad(self.animation_progress)
        self.animated_value = self.start_value + (self.target_value - self.start_value) * eased
        
        if self.animation_progress >= 1.0:
            self.is_animating = False
            self.emit_event('animation_complete')

def _ease_out_quad(self, t: float) -> float:
    """二次のイージング関数"""
    return t * (2 - t)
```

### パフォーマンス最適化

- **再描画の最適化**: `needs_redraw` フラグを使用して、必要な場合のみ再描画
- **メモリ管理**: 大きなリソースは必要に応じてロード/アンロード
- **イベントリスナーの管理**: 不要なイベントリスナーを削除

## ベストプラクティス

### コード品質
- **型ヒント**: すべてのメソッドと変数に適切な型ヒントを追加
- **ドキュメンテーション**: 公開APIには必ずdocstringを記述
- **エラーハンドリング**: 予期しない状況に備えた堅牢なエラーハンドリング

### パフォーマンス
- **描画の最適化**: 変更のない領域は再描画しない
- **メモリ効率**: 大きなリソースは共有する
- **イベント処理**: 高頻度で発生するイベントはスロットリングする

### アクセシビリティ
- **キーボードナビゲーション**: タブ順とキーボード操作をサポート
- **スクリーンリーダー**: 代替テキストと役割を適切に設定

## トラブルシューティング

### コントロールが表示されない
- 親コントロールの `visible` プロパティを確認
- 座標が正しく設定されているか確認
- `draw` メソッドがオーバーライドされているか確認

### イベントが発火しない
- イベント名が正しいか確認
- イベントリスナーが正しく登録されているか確認
- コントロールが有効 (`enabled: true`) になっているか確認

### パフォーマンスの問題
- 不要な再描画がないか確認
- メモリリークがないかプロファイリング
- 高コストな操作を最適化

## 実装例: スライダーコントロール

以下に、スライダーコントロールの実装例を示します。

```python
class SliderControl(BaseControl):
    """スライダーコントロールの実装例"""
    
    def __init__(self, control_id: str, x: int, y: int, width: int, height: int, **kwargs):
        super().__init__(control_id, x, y, width, height, **kwargs)
        self.min_value = kwargs.get('min', 0)
        self.max_value = kwargs.get('max', 100)
        self.value = kwargs.get('value', self.min_value)
        self.dragging = False
        
    def handle_input(self, mouse_x: int, mouse_y: int, mouse_clicked: bool) -> None:
        if not self.enabled or not self.visible:
            return
            
        abs_x, abs_y, width, _ = self.get_absolute_rect(0, 0)
        
        # マウスがスライダー上にあるかチェック
        if (abs_x <= mouse_x <= abs_x + width and 
            abs_y <= mouse_y <= abs_y + self.height):
            
            if mouse_clicked and not self.dragging:
                self.dragging = True
                # クリック位置に応じて値を更新
                self._update_value(mouse_x, abs_x, width)
                self.emit_event('drag_start', {'value': self.value})
            
            # ドラッグ中
            elif self.dragging and pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                self._update_value(mouse_x, abs_x, width)
                self.emit_event('change', {'value': self.value})
            
            elif not pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                if self.dragging:
                    self.dragging = False
                    self.emit_event('drag_end', {'value': self.value})
    
    def _update_value(self, mouse_x: int, abs_x: int, width: int) -> None:
        """マウス位置に基づいて値を更新"""
        ratio = (mouse_x - abs_x) / width
        new_value = int(self.min_value + (self.max_value - self.min_value) * ratio)
        new_value = max(self.min_value, min(self.max_value, new_value))
        
        if new_value != self.value:
            self.value = new_value
            self.emit_event('change', {'value': self.value})
    
    def draw(self, dialog_x: int, dialog_y: int) -> None:
        if not self.visible:
            return
            
        abs_x, abs_y, width, height = self.get_absolute_rect(dialog_x, dialog_y)
        
        # トラックを描画
        track_y = abs_y + height // 2 - 2
        pyxel.rect(abs_x, track_y, width, 4, 13)  # グレーのトラック
        
        # つまみの位置を計算
        ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        thumb_x = int(abs_x + (width - 8) * ratio)
        
        # つまみを描画
        pyxel.rect(thumb_x, abs_y, 8, height - 1, 7 if self.enabled else 13)
        pyxel.rectb(thumb_x, abs_y, 8, height - 1, 7)
        
        # 値のテキストを表示
        value_text = str(self.value)
        text_x = abs_x + width + 5
        text_y = abs_y + (height - 6) // 2
        pyxel.text(text_x, text_y, value_text, 7)
```

このスライダーコントロールは、以下のように使用できます：

```json
{
  "id": "volume_slider",
  "type": "slider",
  "x": 20,
  "y": 50,
  "width": 200,
  "height": 20,
  "min": 0,
  "max": 100,
  "value": 50,
  "events": ["change", "drag_start", "drag_end"]
}
```

このガイドを参考に、独自のカスタムコントロールを作成してください。

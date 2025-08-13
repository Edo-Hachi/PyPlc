# DialogManager v2 アーキテクチャ解説

## 📐 設計思想

DialogManager v2は、以下の設計原則に基づいて構築されています：

### 1. 単一責任原則 (SRP)
- 各クラスは明確に定義された単一の責任を持つ
- `DialogManager`: ダイアログの統合管理
- `BaseDialog`: ダイアログの基本機能
- `ControlFactory`: UIコントロールの生成

### 2. 開放閉鎖原則 (OCP)
- 新しいダイアログタイプの追加が容易
- 既存コードを変更せずに機能拡張可能
- JSON定義による設定変更

### 3. 依存性逆転原則 (DIP)
- 抽象に依存し、具象に依存しない
- インターフェースベースの設計
- 疎結合なイベントシステム

## 🏗️ クラス図

```
┌─────────────────┐    ┌─────────────────┐
│  DialogManager  │────│   BaseDialog    │
│                 │    │                 │
│ +show_device_   │    │ +show()         │
│  edit_dialog()  │    │ +close()        │
│                 │    │ +add_control()  │
└─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ ControlFactory  │    │ JSONDialogLoader│
│                 │    │                 │
│ +create_        │    │ +load_dialog_   │
│  control()      │    │  definition()   │
└─────────────────┘    └─────────────────┘
```

## 💾 データフロー

### 1. ダイアログ表示フロー
```
User Action
    ↓
DialogManager.show_device_edit_dialog()
    ↓
Device Type Detection
    ↓
Specific Dialog Creation
    ↓
JSON Definition Loading
    ↓
Control Factory Usage
    ↓
UI Rendering
    ↓
Modal Loop
```

### 2. イベント処理フロー
```
User Input
    ↓
Control Event Detection
    ↓
Event System Emission
    ↓
Dialog Event Handler
    ↓
Validation Processing
    ↓
Result Generation
    ↓
Dialog Close/Continue
```

## 🔧 コンポーネント詳細

### DialogManager (統合管理)
- **責任**: すべてのダイアログの統合管理
- **機能**: デバイス種別判定、適切なダイアログ選択、共通処理
- **依存関係**: 各種ダイアログクラス、DeviceType

### BaseDialog (基底クラス)
- **責任**: ダイアログの基本機能提供
- **機能**: モーダル処理、イベント管理、共通UI処理
- **継承関係**: すべての具象ダイアログクラスの親

### ControlFactory (UI生成)
- **責任**: JSON定義からUIコントロール生成
- **機能**: 動的コントロール生成、タイプ別ファクトリ
- **対応コントロール**: Button, Label, TextInput, FileList

### JSONDialogLoader (定義読み込み)
- **責任**: JSON定義ファイルの読み込み・検証
- **機能**: ファイル読み込み、スキーマ検証、エラーハンドリング
- **検証**: Schema Validator連携

## 📋 拡張ポイント

### 1. 新しいダイアログタイプの追加

```python
# 1. dialogs/new_dialog.py を作成
class NewDialog(BaseDialog):
    def __init__(self):
        super().__init__(title="New Dialog")
        # 実装

# 2. definitions/new_dialog.json を作成
{
    "title": "New Dialog",
    "controls": [...]
}

# 3. DialogManager に処理追加
def show_device_edit_dialog(self, device, ...):
    if device.device_type == DeviceType.NEW_TYPE:
        self._show_new_dialog(device, ...)
```

### 2. 新しいコントロールタイプの追加

```python
# 1. controls/new_control.py を作成
class NewControl(BaseControl):
    def handle_input(self, ...):
        # 実装

# 2. ControlFactory に追加
def _create_new_control(self, definition):
    return NewControl(...)

# 3. JSON スキーマ更新
```

## 🔒 セキュリティ考慮事項

### 1. 入力検証
- すべてのユーザー入力に対する厳格な検証
- PLC標準準拠のバリデーションルール
- SQLインジェクション等の攻撃への対策

### 2. ファイルアクセス
- JSON定義ファイルへの制限されたアクセス
- パストラバーサル攻撃の防止
- 適切なファイル権限設定

### 3. エラーハンドリング
- 機密情報の漏洩を防ぐエラーメッセージ
- 適切なログ記録
- グレースフルな失敗処理

## 📊 パフォーマンス考慮事項

### 1. メモリ管理
- ダイアログの適切な破棄
- コントロールのライフサイクル管理
- イベントリスナーのクリーンアップ

### 2. レスポンス性
- 30FPS要件への適合
- 非同期処理の活用
- UI更新の最適化

### 3. スケーラビリティ
- 大量のコントロールへの対応
- 複雑なダイアログ構成のサポート
- リソース使用量の最適化

## 🧪 テスト戦略

### 1. 単体テスト
- 各クラスの個別機能テスト
- モックオブジェクトの活用
- エッジケースの網羅

### 2. 統合テスト
- コンポーネント間の連携テスト
- JSON定義との整合性確認
- エンドツーエンドフロー検証

### 3. UI テスト
- ユーザーインタラクションシミュレーション
- 視覚的回帰テスト
- アクセシビリティテスト

---

**DialogManager v2** - 堅牢で拡張可能なアーキテクチャ
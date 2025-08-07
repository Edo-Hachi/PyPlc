# PyPlc Ver3 ダイアログシステム改良プラン v2.0

**作成日**: 2025-08-07  
**バージョン**: 2.0 (Geminiレビュー反映版)  
**目標**: 段階的MVP実装による堅牢なダイアログシステム構築  
**参考**: Ver2のJSON定義システム + Geminiの建設的提案  

## 📋 プロジェクト概要

### 🎯 改良された設計コンセプト

**Geminiレビューを反映した実用的アプローチ**:
- **MVP優先**: 最小限の機能から段階的に構築
- **疎結合イベント**: コールバック/サブスクライバーパターン採用
- **カスタムコントロール**: FileListControlによる完全JSON化
- **標準準拠**: JSON Schemaによる堅牢な定義検証

### 🔍 Geminiレビューの主要提案

**✅ 採用する提案**:
1. **イベント処理の汎用化**: 疎結合なコールバックシステム
2. **FileListControlの作成**: ファイルダイアログの完全JSON化
3. **JSON Schemaの導入**: 標準的なスキーマ定義言語の利用
4. **段階的MVP実装**: リスクを最小化した実装戦略

**🎯 改良された目標**:
- 技術的負債を抱えない堅牢な設計
- 再利用性を最大化した疎結合アーキテクチャ
- 確実な成功を保証するMVP戦略

## 🏗️ 改良されたアーキテクチャ設計

### 1. 疎結合イベントシステム

```python
# 従来のアプローチ（JSON内で関数名指定）
{
  "events": {
    "on_change": "validate_device_address"  # 特定実装に依存
  }
}

# 改良されたアプローチ（疎結合コールバック）
# JSON定義（UI構造のみ）
{
  "type": "textinput",
  "id": "device_address",
  "events": ["change", "focus"]  # イベント種別のみ定義
}

# Python側（ビジネスロジック）
dialog = dialog_manager.show_dialog_from_json("device_settings.json")
address_input = dialog.get_control("device_address")
address_input.on("change", self.validate_device_address)
address_input.on("focus", self.highlight_field)
```

### 2. カスタムコントロールシステム

```
BaseControl
├── LabelControl         # テキスト表示
├── TextInputControl     # テキスト入力
├── ButtonControl        # ボタン
├── FileListControl      # ファイル一覧（新規）
├── CheckboxControl      # チェックボックス
└── NumberSpinControl    # 数値スピン
```

### 3. JSON Schema定義

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "title": {"type": "string"},
    "width": {"type": "integer", "minimum": 100},
    "height": {"type": "integer", "minimum": 50},
    "controls": {
      "type": "array",
      "items": {"$ref": "#/definitions/control"}
    }
  },
  "required": ["title", "width", "height", "controls"]
}
```

## 📝 改良版実装TODOプラン

### Phase 1: コアフレームワーク構築 (MVP) - 最優先

#### 1.1 BaseDialog基底クラス
- [ ] **ファイル**: `dialogs/base_dialog.py`
- [ ] **機能**:
  - モーダル処理の統一化
  - 疎結合イベントシステムの実装
  - コントロール管理システム
  - 30FPS維持の最適化
- [ ] **所要時間**: 3時間
- [ ] **成功条件**: シンプルなOK/Cancelダイアログが表示できる

#### 1.2 JSONDialogLoader実装
- [ ] **ファイル**: `dialogs/json_dialog_loader.py`
- [ ] **機能**:
  - JSON定義ファイルの読み込み
  - 基本的なバリデーション（JSON Schema後回し可）
  - エラーハンドリング
  - デフォルト値の適用
- [ ] **所要時間**: 2時間
- [ ] **成功条件**: JSONからダイアログ構造を生成できる

#### 1.3 ControlFactory実装
- [ ] **ファイル**: `dialogs/control_factory.py`
- [ ] **機能**:
  - 動的コントロール生成
  - タイプ別ファクトリーパターン
  - コントロール登録システム
  - 拡張可能な設計
- [ ] **所要時間**: 2時間
- [ ] **成功条件**: JSON定義からコントロールを動的生成できる

#### 1.4 基本コントロール実装
- [ ] **BaseControl** (`dialogs/controls/base_control.py`)
  - 共通プロパティ定義
  - イベント処理インターフェース
  - 描画メソッド抽象化
  - 所要時間: 1時間

- [ ] **LabelControl** (`dialogs/controls/label_control.py`)
  - テキスト表示
  - カラー・フォント設定
  - 所要時間: 30分

- [ ] **ButtonControl** (`dialogs/controls/button_control.py`)
  - ボタン表示・クリック処理
  - ホバーエフェクト
  - 疎結合イベント対応
  - 所要時間: 1.5時間

#### 1.5 イベントシステム実装
- [ ] **ファイル**: `dialogs/events/event_system.py`
- [ ] **機能**:
  - コールバック/サブスクライバーパターン
  - イベント登録・解除システム
  - イベント伝播制御
- [ ] **所要時間**: 2時間
- [ ] **成功条件**: `control.on("event", callback)`が動作する

**Phase 1 合計所要時間**: 約12時間  
**Phase 1 成功条件**: OK/Cancelのみの確認ダイアログをJSONから表示

### Phase 2: 最初の実用ダイアログ完成 - 高優先度

#### 2.1 TextInputControl実装
- [ ] **ファイル**: `dialogs/controls/text_input_control.py`
- [ ] **機能**:
  - テキスト入力フィールド
  - カーソル制御
  - 疎結合イベント対応（change, focus, blur）
- [ ] **所要時間**: 2.5時間

#### 2.2 バリデーションシステム
- [ ] **ファイル**: `dialogs/validation/validator.py`
- [ ] **機能**:
  - 入力値検証エンジン
  - PLC標準準拠バリデーター
  - エラーメッセージ管理
  - コールバック連携
- [ ] **所要時間**: 2時間

#### 2.3 DeviceIDDialogのJSON化
- [ ] **JSON定義**: `dialogs/definitions/device_settings.json`
- [ ] **Python実装**: 既存DeviceIDDialogの置き換え
- [ ] **機能**:
  - 完全なJSON定義による実装
  - バリデーション連携
  - 疎結合イベント活用
- [ ] **所要時間**: 2時間
- [ ] **成功条件**: 既存DeviceIDDialogと同等の機能をJSONで実現

**Phase 2 合計所要時間**: 約6.5時間  
**Phase 2 成功条件**: DeviceIDDialogの完全なJSON実装（フレームワーク成功の証明）

### Phase 3: 既存システムの段階的移行 - 中優先度

#### 3.1 FileListControl実装
- [ ] **ファイル**: `dialogs/controls/file_list_control.py`
- [ ] **機能**:
  - ファイル一覧の取得・表示
  - ディレクトリ操作のカプセル化
  - ソート・フィルタリング機能
  - 選択状態管理
- [ ] **所要時間**: 3時間

#### 3.2 ファイルダイアログのJSON化
- [ ] **JSON定義**: `dialogs/definitions/file_operations.json`
- [ ] **機能**:
  - FileListControlを使用した完全JSON化
  - 保存・読み込み両対応
  - 既存機能の完全移行
- [ ] **所要時間**: 2時間

#### 3.3 タイマー・カウンター設定ダイアログ
- [ ] **JSON定義**: `dialogs/definitions/timer_settings.json`
- [ ] **JSON定義**: `dialogs/definitions/counter_settings.json`
- [ ] **機能**:
  - 数値入力バリデーション
  - プリセット値設定
  - Ver2定義の改良版
- [ ] **所要時間**: 1.5時間

**Phase 3 合計所要時間**: 約6.5時間  
**Phase 3 成功条件**: 全ての既存ダイアログのJSON化完了

### Phase 4: 品質向上・高度機能 - 低優先度

#### 4.1 JSON Schema導入
- [ ] **ファイル**: `dialogs/schema/dialog_schema.json`
- [ ] **機能**:
  - 標準JSON Schemaによる定義
  - 自動バリデーション
  - 開発者支援機能
- [ ] **所要時間**: 2時間

#### 4.2 テーマシステム
- [ ] **ファイル**: `dialogs/themes/theme_manager.py`
- [ ] **機能**:
  - カラーテーマ定義
  - ダークモード対応
  - 動的テーマ切り替え
- [ ] **所要時間**: 2時間

#### 4.3 高度コントロール
- [ ] **CheckboxControl**: チェックボックス (1時間)
- [ ] **NumberSpinControl**: 数値スピンボックス (1.5時間)
- [ ] **DropdownControl**: ドロップダウンリスト (2時間)

**Phase 4 合計所要時間**: 約8.5時間

## 📁 改良されたファイル構成

```
dialogs/
├── __init__.py
├── base_dialog.py              # 基底ダイアログクラス
├── json_dialog_loader.py       # JSON読み込み・解析
├── control_factory.py          # コントロールファクトリー
├── dialog_manager.py           # 既存ファイル（統合管理）
├── controls/
│   ├── __init__.py
│   ├── base_control.py         # 基底コントロールクラス
│   ├── label_control.py        # ラベル
│   ├── text_input_control.py   # テキスト入力
│   ├── button_control.py       # ボタン
│   ├── file_list_control.py    # ファイル一覧（新規）
│   ├── checkbox_control.py     # チェックボックス
│   ├── dropdown_control.py     # ドロップダウン
│   └── number_spin_control.py  # 数値スピン
├── events/
│   ├── __init__.py
│   └── event_system.py         # 疎結合イベントシステム
├── validation/
│   ├── __init__.py
│   └── validator.py            # バリデーションシステム
├── themes/
│   ├── __init__.py
│   ├── theme_manager.py        # テーマ管理
│   ├── default_theme.json      # デフォルトテーマ
│   └── dark_theme.json         # ダークテーマ
├── schema/
│   ├── __init__.py
│   └── dialog_schema.json      # JSON Schema定義
└── definitions/                # JSON定義ファイル
    ├── device_settings.json    # デバイス設定ダイアログ
    ├── timer_settings.json     # タイマー設定ダイアログ
    ├── counter_settings.json   # カウンター設定ダイアログ
    ├── file_operations.json    # ファイル操作ダイアログ
    └── confirmation.json       # 確認ダイアログ
```

## 🎯 改良された実装戦略

### MVP戦略 (Minimum Viable Product)

**Phase 1の成功が全体の成功を決定**:
1. **最小限の機能**: OK/Cancelダイアログのみ
2. **完全な動作**: JSON定義→表示→イベント処理
3. **拡張可能性**: 新しいコントロール追加の容易さ

**リスク最小化アプローチ**:
- 各Phaseで動作するプロトタイプを作成
- 既存システムとの並行運用期間を設ける
- 段階的な移行により安全性を確保

### 疎結合イベントシステムの実装例

```python
# dialogs/base_dialog.py
class BaseDialog:
    def __init__(self, json_definition):
        self.controls = {}
        self.event_system = EventSystem()
        
    def get_control(self, control_id: str) -> BaseControl:
        return self.controls.get(control_id)
    
    def show_modal(self) -> dict:
        # モーダルループ実装
        pass

# 使用例 (main.py)
def show_device_settings():
    dialog = dialog_manager.show_dialog_from_json("device_settings.json")
    
    # イベント登録（疎結合）
    address_input = dialog.get_control("device_address")
    address_input.on("change", self.validate_device_address)
    address_input.on("focus", self.highlight_field)
    
    ok_button = dialog.get_control("ok_button")
    ok_button.on("click", self.save_device_settings)
    
    result = dialog.show_modal()
    return result

def validate_device_address(control, new_value):
    if is_valid_device_address(new_value):
        control.set_style("valid")
    else:
        control.set_style("invalid")
```

### FileListControlの実装例

```json
{
  "title": "Load Circuit File",
  "width": 320,
  "height": 240,
  "controls": [
    {
      "type": "label",
      "id": "title_label",
      "x": 10, "y": 20,
      "text": "Select Circuit File"
    },
    {
      "type": "file_list",
      "id": "file_selector",
      "x": 10, "y": 40,
      "width": 280, "height": 150,
      "target_extension": ".csv",
      "sort_by": "creation_date_desc"
    },
    {
      "type": "button",
      "id": "load_button",
      "x": 70, "y": 200,
      "width": 50, "height": 25,
      "text": "Load"
    },
    {
      "type": "button",
      "id": "cancel_button",
      "x": 200, "y": 200,
      "width": 50, "height": 25,
      "text": "Cancel"
    }
  ]
}
```

## 💡 期待される効果（改良版）

### 1. 技術的負債の回避
- **疎結合設計**: UI定義とビジネスロジックの完全分離
- **標準準拠**: JSON Schemaによる堅牢な定義管理
- **段階的実装**: 各フェーズでの動作保証

### 2. 開発効率の劇的向上
- **JSON定義**: 新しいダイアログを数分で作成
- **再利用性**: カスタムコントロールによる柔軟な組み合わせ
- **保守性**: 明確な責任分離による修正の容易さ

### 3. 長期的な拡張性
- **プラグイン対応**: 新しいコントロールタイプの容易な追加
- **テーマ対応**: 外観の統一・カスタマイズ
- **国際化対応**: 将来的な多言語サポート

## 🚀 実装開始ガイド（改良版）

### ステップ1: MVP構築 (Phase 1)
1. **BaseDialog**から開始
2. **シンプルな確認ダイアログ**でテスト
3. **疎結合イベントシステム**の動作確認

### ステップ2: 実用性証明 (Phase 2)
1. **DeviceIDDialog**のJSON実装
2. **既存機能との完全互換性**確認
3. **フレームワークの成功証明**

### ステップ3: 全面移行 (Phase 3)
1. **FileListControl**による完全JSON化
2. **既存ダイアログの段階的移行**
3. **品質・性能の最終確認**

## 🔧 成功指標

### Phase 1成功条件
- [ ] OK/CancelダイアログがJSONから表示される
- [ ] ボタンクリックイベントが正常に動作する
- [ ] 30FPS維持でスムーズに動作する

### Phase 2成功条件
- [ ] DeviceIDDialogが完全にJSON実装される
- [ ] 既存機能と100%互換性がある
- [ ] バリデーション機能が正常に動作する

### Phase 3成功条件
- [ ] 全ての既存ダイアログがJSON化される
- [ ] ファイルダイアログが完全にJSON定義される
- [ ] コードの重複が大幅に削減される

---

**この改良プランにより、Geminiの建設的提案を反映した、より実用的で堅牢なダイアログシステムを段階的に構築できます。**

MVP戦略により技術的リスクを最小化し、疎結合設計により長期的な保守性を確保します。各フェーズの成功条件を満たしながら進めることで、確実に目標を達成できます。

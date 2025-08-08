# PyPlc Ver3 JSONスキーマ導入実装プラン

## 作成日: 2025-08-08
## 目的: DialogManager定義ファイルのVSCode補完・検証強化
## Geminiレビューフィードバック対応

---

## 1. プロジェクト概要

### 目的
- JSON定義ファイルの編集時にVSCode補完を有効化
- CI/CDプロセスでのJSON検証自動化
- 定義ファイルの品質向上と開発効率向上

### 適用範囲
```
DialogManager/definitions/
├── timer_settings.json      # タイマー設定
├── counter_settings.json    # カウンター設定
├── file_save_dialog.json    # ファイル保存ダイアログ
└── [将来の定義ファイル]
```

### 期待効果
- JSON編集時の入力補完・リアルタイム検証
- CI段階での不正定義検出
- 新規ダイアログ定義作成の効率化

---

## 2. 実装フェーズ

### Phase 1: スキーマ設計・基本構造作成 (45分)
```
P1-1. スキーマディレクトリ構造設計
P1-2. 基本ダイアログスキーマ設計
P1-3. コントロール種別スキーマ設計
P1-4. バリデーションルールスキーマ設計
```

**成果物:**
- `DialogManager/definitions/schemas/` ディレクトリ
- 基本スキーマ設計仕様書

### Phase 2: 個別スキーマファイル実装 (60分)
```
P2-1. 基本ダイアログスキーマ実装
    - dialog_base_schema.json
    - 共通プロパティ定義

P2-2. コントロール固有スキーマ実装
    - button_schema.json
    - textinput_schema.json
    - label_schema.json
    - filelist_schema.json

P2-3. ダイアログ種別スキーマ実装
    - timer_settings_schema.json
    - counter_settings_schema.json
    - file_save_dialog_schema.json
```

**成果物:**
- 各JSON定義に対応するスキーマファイル
- プロパティ定義・制約ルール

### Phase 3: 既存定義ファイル更新 (30分)
```
P3-1. $schema参照追加
    - 各JSONファイルに$schemaプロパティ追加
    - スキーマファイルへの相対パス設定

P3-2. VSCode設定ファイル更新
    - .vscode/settings.json更新
    - JSON補完・検証有効化

P3-3. 動作確認
    - VSCodeでの補完動作確認
    - 検証エラー表示確認
```

**成果物:**
- $schema参照付き定義ファイル群
- VSCode統合設定

### Phase 4: 検証システム統合 (45分)
```
P4-1. JSON検証ユーティリティ作成
    - DialogManager/schema_validator.py
    - スキーマ検証機能実装

P4-2. 起動時検証組み込み
    - JSONDialogLoaderに検証処理追加
    - エラーハンドリング強化

P4-3. 開発用検証スクリプト作成
    - validate_definitions.py
    - 全定義ファイル一括検証
```

**成果物:**
- スキーマ検証システム
- 開発用検証ツール

---

## 3. 技術仕様詳細

### スキーマディレクトリ構造
```
DialogManager/definitions/schemas/
├── dialog_base_schema.json          # 基本ダイアログ構造
├── controls/                        # コントロール固有スキーマ
│   ├── button_schema.json
│   ├── textinput_schema.json
│   ├── label_schema.json
│   └── filelist_schema.json
├── dialogs/                         # ダイアログ種別スキーマ
│   ├── timer_settings_schema.json
│   ├── counter_settings_schema.json
│   └── file_save_dialog_schema.json
└── common/                          # 共通定義
    ├── color_definitions.json
    ├── event_definitions.json
    └── validation_definitions.json
```

### スキーマ設計方針

#### 1. 基本ダイアログ構造
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "dialog_base_schema.json",
  "type": "object",
  "required": ["title", "width", "height", "controls"],
  "properties": {
    "title": { "type": "string", "minLength": 1 },
    "width": { "type": "integer", "minimum": 100, "maximum": 800 },
    "height": { "type": "integer", "minimum": 80, "maximum": 600 },
    "controls": {
      "type": "array",
      "items": { "$ref": "#/definitions/control" }
    }
  }
}
```

#### 2. コントロール種別定義
```json
{
  "definitions": {
    "control": {
      "type": "object",
      "required": ["id", "type", "x", "y", "width", "height"],
      "properties": {
        "id": { "type": "string", "pattern": "^[a-z_]+$" },
        "type": { 
          "enum": ["button", "textinput", "label", "filelist"] 
        }
      },
      "allOf": [
        { "if": { "properties": { "type": { "const": "button" } } },
          "then": { "$ref": "controls/button_schema.json" } },
        { "if": { "properties": { "type": { "const": "textinput" } } },
          "then": { "$ref": "controls/textinput_schema.json" } }
      ]
    }
  }
}
```

#### 3. バリデーション定義
```json
{
  "validation_types": {
    "timer_preset_range": {
      "type": "integer_range",
      "min": 0,
      "max": 32767
    },
    "counter_preset_range": {
      "type": "integer_range", 
      "min": 0,
      "max": 65535
    }
  }
}
```

### VSCode統合設定
```json
{
  "json.schemas": [
    {
      "fileMatch": ["**/timer_settings.json"],
      "url": "./schemas/dialogs/timer_settings_schema.json"
    },
    {
      "fileMatch": ["**/counter_settings.json"], 
      "url": "./schemas/dialogs/counter_settings_schema.json"
    },
    {
      "fileMatch": ["**/file_save_dialog.json"],
      "url": "./schemas/dialogs/file_save_dialog_schema.json"
    }
  ]
}
```

---

## 4. 品質保証計画

### 検証項目
1. **スキーマ妥当性**
   - JSON Schema Draft-07準拠
   - 循環参照なし
   - プロパティ制約適正

2. **既存定義ファイル互換性**
   - 全既存JSONファイルがスキーマ検証を通過
   - 機能動作に影響なし

3. **VSCode統合動作**
   - 入力補完正常動作
   - リアルタイム検証表示
   - エラーメッセージ適切表示

### テスト手順
```bash
# Phase 2完了後
python DialogManager/schema_validator.py --validate-all

# Phase 3完了後  
# VSCodeで各JSONファイルを開き、補完・検証動作確認

# Phase 4完了後
python validate_definitions.py
```

---

## 5. リスク分析と対策

### リスク1: スキーマ複雑性
**リスク**: スキーマ定義が複雑化し、保守困難
**対策**: 
- 段階的実装（基本→詳細）
- 共通定義の活用
- 十分なコメント・ドキュメント

### リスク2: 既存システム影響
**リスク**: スキーマ導入による既存機能破綻
**対策**:
- 段階的検証導入
- バックワード互換性維持
- 充分な動作テスト

### リスク3: 開発効率低下
**リスク**: スキーマメンテナンスによる開発速度低下
**対策**:
- スキーマ自動生成ツール検討
- 最小限の制約から開始
- 段階的精密化

---

## 6. 成功指標

### 定量的指標
- JSON編集時のタイポエラー: 80%削減
- 新規定義ファイル作成時間: 30%短縮
- CI段階でのJSON検証エラー: 100%検出

### 定性的指標
- VSCode補完の快適性向上
- JSON定義ファイルの品質向上
- 新規開発者の理解速度向上

---

## 7. 実装後の拡張計画

### 短期拡張 (1ヶ月)
- CI/CD統合 (GitHub Actions)
- スキーマ検証レポート生成
- エラーメッセージ日本語化

### 中期拡張 (3ヶ月)  
- スキーマからTypeScript型定義生成
- 視覚的スキーマエディター
- 多言語定義対応

### 長期拡張 (6ヶ月)
- スキーマバージョニング
- 自動マイグレーション機能
- パフォーマンス最適化

---

## 8. チェックリスト

### Phase 1: スキーマ設計
- [ ] スキーマディレクトリ構造確定
- [ ] 基本ダイアログスキーマ設計
- [ ] コントロール種別スキーマ設計
- [ ] バリデーションルールスキーマ設計
- [ ] 設計仕様書作成

### Phase 2: 実装
- [ ] dialog_base_schema.json作成
- [ ] 各コントロールスキーマ作成
- [ ] 各ダイアログスキーマ作成
- [ ] 共通定義スキーマ作成
- [ ] スキーマ妥当性検証

### Phase 3: 統合
- [ ] 既存JSONに$schema追加
- [ ] VSCode設定ファイル更新
- [ ] 補完動作確認
- [ ] 検証動作確認

### Phase 4: システム統合
- [ ] schema_validator.py作成
- [ ] JSONDialogLoader統合
- [ ] validate_definitions.py作成
- [ ] 全体動作確認

### 最終確認
- [ ] 全既存機能正常動作
- [ ] VSCode開発環境改善確認
- [ ] ドキュメント更新
- [ ] Git commit & レビュー

---

*プラン作成日: 2025-08-08*  
*推定実装時間: 3-4時間*  
*承認待ち: ユーザー承認後実装開始*
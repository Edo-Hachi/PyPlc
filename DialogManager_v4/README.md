# DialogManager v4 - JSON Complete Definition System

**JSON完全定義主義**に基づくダイアログシステム  
DESIGN.md完全準拠のクリーンアーキテクチャ実装

## 🎯 設計思想

DialogManager v4は**Windowsリソース(.rc)ファイル**的なアプローチで、UI定義からイベント処理まで**すべてをJSON**で定義します。

### ✅ 正しい使用方法
```python
# JSON定義からダイアログを完全構築
dialog_engine = DialogEngine()
dialog = dialog_engine.create_dialog_from_json("file_dialog.json")

# 全ロジックがJSON定義済み
success, result = dialog.show_modal()
```

### ❌ 禁止事項
```python
# PythonコードでのUI定義は禁止
dialog.add_control(ButtonControl(...))  # ❌
dialog.on_click = handler  # ❌
```

## 📁 ディレクトリ構造

```
DialogManager_v4/
├── core/                    # コアシステム
│   ├── dialog_engine.py     # JSON→ダイアログ変換エンジン  ✅
│   ├── action_engine.py     # アクション実行エンジン      ✅
│   ├── event_binder.py      # イベントバインディング     ✅
│   ├── coordinate_system.py # 座標系管理                ✅
│   └── debug_system.py      # デバッグ・ログシステム     ✅
├── schema/                  # JSONスキーマ定義
│   └── dialog_schema.json   # ダイアログスキーマ         ✅
├── controls/                # UIコントロール（v3から移植予定）
├── dialogs/                 # JSON定義ダイアログ
│   ├── simple_test.json     # テスト用ダイアログ         ✅
│   └── file_load.json       # ファイルロードダイアログ    ✅
├── tests/                   # テストスイート
└── examples/                # 使用例
    └── example_usage.py     # 使用方法デモ              ✅
```

## 🚀 JSON定義例

### ダイアログ定義
```json
{
  "dialog": {
    "title": "File Load Dialog",
    "width": 340,
    "height": 280,
    "modal": true
  },
  "controls": [
    {
      "type": "dropdown",
      "id": "filter_dropdown",
      "x": 80, "y": 228,
      "items": ["All Files", "CSV Files"],
      "selected_index": 1
    }
  ],
  "events": {
    "filter_dropdown.change": "update_file_filter"
  },
  "actions": {
    "update_file_filter": {
      "type": "file_filter",
      "filter_source": "filter_dropdown.selected_value"
    }
  }
}
```

## 📋 実装状況

### ✅ Phase V4-0 完了 (アーキテクチャ設計)
- [x] ディレクトリ構造作成
- [x] 中核クラス設計（空の実装）
- [x] JSONスキーマファイル作成
- [x] パッケージ初期化
- [x] 基本テストスイート作成

### 🚧 次期実装予定
- [ ] **Phase V4-1**: DebugSystem・CoordinateSystem完全実装
- [ ] **Phase V4-2**: 最小限JSONダイアログ動作
- [ ] **Phase V4-3**: v3コントロール移植・統合

## 🎯 v4の優位性

### 設計品質
- ✅ **JSON完全定義**: 最初からDESIGN.md準拠
- ✅ **エラーハンドリング**: アーキテクチャ組み込み
- ✅ **座標系**: 明確・テスト済み
- ✅ **デバッグ**: 標準機能

### 開発効率
- ✅ **クリーンスタート**: 技術的負債なし
- ✅ **段階的構築**: Gemini推奨アプローチ
- ✅ **安全移行**: v3稼働中にv4構築
- ✅ **テスト容易**: 最小限から確実に拡張

## 🔧 開発者向け情報

### 必読ドキュメント
- `../DESIGN.md` - 設計思想・開発原則
- `examples/example_usage.py` - 正しい使用方法

### 開発原則
1. **JSON完全定義主義の徹底**
2. **Pythonコード最小化**
3. **宣言的UI設計**
4. **設計思想違反の回避**

---

**Created**: 2025-08-15  
**Author**: Claude (Sonnet 4)  
**Status**: Phase V4-0 完了 → Phase V4-1 開始準備完了
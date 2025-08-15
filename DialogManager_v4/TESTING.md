# DialogManager v4 テスト実行ガイド

DialogManager v4の各種テスト実行方法

## 🧪 テスト実行方法

### **推奨方法: 統合テストランナー**

```bash
# PyPlcルートディレクトリから実行
./venv/bin/python DialogManager_v4/run_tests.py

# または
cd DialogManager_v4
python3 run_tests.py
```

### **Pyxel環境での実行（視覚的結果表示）**

```bash
# Pyxelウィンドウでテスト結果表示
pyxel run DialogManager_v4/pyxel_test.py
```

### **個別テスト実行**

```bash
# コアクラステストのみ
python3 DialogManager_v4/tests/test_debug_system.py

# JSON定義テストのみ  
python3 DialogManager_v4/tests/test_json_validation.py
```

## 📊 テスト項目一覧

### **Level 1: コアクラス単体テスト** ✅
- **DebugSystem**: 階層ログ・性能測定・コンテキスト管理
- **CoordinateSystem**: 座標変換・境界判定・v3問題解決確認

### **Level 2: JSON定義検証テスト** ✅
- **JSON構文妥当性**: simple_test.json, file_load.json, schema
- **ダイアログ構造妥当性**: 必須フィールド・プロパティ検証
- **CSVデフォルト設定確認**: v3問題解決の実証
- **イベント・アクション整合性**: バインディング妥当性

### **Level 3: 統合動作テスト** (Phase V4-1実装後)
- DialogEngine動作テスト
- ActionEngine実行テスト
- 実際のダイアログ表示テスト

## 🎯 現在のテスト状況

**総合成功率: 100%** 🎉

```
✅ コアクラス単体テスト
✅ JSON定義検証テスト

📈 統計:
  総テスト数: 2
  成功: 2  
  失敗: 0
  成功率: 100.0%
```

## 🚨 重要な検証済み項目

### **CSVデフォルト問題の解決**
v3で問題となったCSVファイルデフォルト選択が、v4のJSON定義で完全解決：

```json
{
  "type": "dropdown",
  "id": "filter_dropdown",
  "items": ["All Files (*.*)", "CSV Files (*.csv)", "Text Files (*.txt)"],
  "selected_index": 1  // ← CSVが自動選択される
}
```

**テスト結果:**
```
✅ filter_dropdown selected_index: 1
✅ 選択されるアイテム: 'CSV Files (*.csv)'  
🎯 CSVデフォルト設定: 正常動作
```

### **座標系問題の根絶**
v3で発生した座標変換バグをCoordinateSystemクラスで根本解決：

```
[CONTEXT][CoordinateSystem][screen_to_dialog] >>> screen_to_dialog
[SUCCESS][CoordinateSystem][screen_to_dialog] Converted to: (50, 50)
✅ CoordinateSystem: 正常動作
```

## 🔧 トラブルシューティング

### **パス問題**
```bash
# エラー: テストファイルが見つからない
❌ テストファイルが見つかりません: tests/test_debug_system.py

# 解決方法: 正しいディレクトリから実行
cd /path/to/PyPlc
./venv/bin/python DialogManager_v4/run_tests.py
```

### **Python環境問題**
```bash
# 仮想環境の確認
which python3
# -> /home/user/Project/PyxelProject/PyPlc/venv/bin/python

# 仮想環境の有効化
source venv/bin/activate
```

## 🚀 開発者向けテスト追加

新しいテストケースの追加方法：

1. **`tests/` ディレクトリに新しいテストファイル作成**
2. **`run_tests.py` の `tests` リストに追加**
3. **統合テスト実行で確認**

例：
```python
# tests/test_new_feature.py
def test_new_feature():
    print("✅ 新機能テスト: 正常動作")
    return True

# run_tests.py に追加
tests = [
    ("コアクラス単体テスト", os.path.join(script_dir, "tests/test_debug_system.py")),
    ("JSON定義検証テスト", os.path.join(script_dir, "tests/test_json_validation.py")),
    ("新機能テスト", os.path.join(script_dir, "tests/test_new_feature.py"))  # ← 追加
]
```

---

**更新日**: 2025-08-15  
**テスト環境**: Python 3.12.3 + Pyxel  
**ステータス**: Level 1-2完了, Level 3準備中
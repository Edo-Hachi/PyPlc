# DialogManager_v4 設計思想・開発原則

**作成日**: 2025-08-15  
**目的**: 開発時の設計思想の堅持・AI開発支援での原則遵守

# 変数は型宣言する！

## pyxelは２バイト文字が扱えない。必ず１バイトの英数字を出力する
## ターミナルへの出力は２バイト文字も大丈夫
## ソースコード内に絵文字は使わない

## 実行環境は .vscode/以下の環境を確認する

## 色定義はpyxelの定義している色コードを使う。 pyxel.COLOR_xxxxx で定義されている

---

## 🎯 **中核設計原則**

### **1. JSON完全定義主義**
DialogManager_v4は**Windowsリソース(.rc)ファイル**的な設計思想に基づく

```json
{
  "title": "File Load Dialog",
  "controls": [...],
  "events": {
    "open_button.click": "open_file_action",
    "filter_dropdown.change": "update_file_filter"
  },
  "actions": {
    "open_file_action": {
      "type": "file_operation",
      "operation": "load_file",
      "source": "filename_textbox.text"
    }
  }
}
```

### **2. 宣言的UI設計**
- **コントロール配置**: JSON定義
- **デフォルト値**: JSON定義
- **イベントハンドリング**: JSON定義
- **ビジネスロジック**: JSON定義（可能な範囲で）

### **3. Pythonコード最小化**
Pythonは以下の用途のみ：
- JSONローダー・パーサー
- ファイルシステム操作
- 低レベルイベント実行エンジン
- OS固有処理

---

## ❌ **絶対禁止事項**

### **Pythonコード内でのUI定義**
```python
# ❌ 絶対にやってはいけない
self.filter_dropdown = DropdownControl(
    x=80, y=228, width=150, height=20, 
    items=["All Files", "CSV Files"], 
    selected_index=1  # ← JSONで定義すべき
)
```

### **Pythonコード内でのイベントハンドラー定義**
```python
# ❌ 絶対にやってはいけない
self.open_button.on('click', self._on_open_clicked)
self.filter_dropdown.on('change', self._on_filter_changed)
```

### **JSONとPythonの責任混在**
```python
# ❌ 混在例（設計思想違反）
dialog = JsonDialogLoader.load_dialog("file_dialog.json")
dialog.get_control("filter_dropdown").selected_index = 1  # ← JSONで定義すべき
dialog.get_control("open_button").on('click', self._handle_open)  # ← JSONで定義すべき
```

---

## ✅ **正しい設計例**

### **理想的な使用方法**
```python
# ✅ 完全JSON定義ベース
dialog = JsonDialogLoader.load_complete_dialog("file_load_dialog.json")
success, result = dialog.show_modal()  # 全ロジックがJSON定義済み

if success:
    file_path = result.get("selected_file")
    self.csv_manager.load_circuit_from_file(file_path)
```

### **JSON定義ファイル例**
```json
{
  "title": "Open Circuit File",
  "width": 340,
  "height": 280,
  "modal": true,
  "controls": [
    {
      "type": "dropdown",
      "id": "filter_dropdown",
      "items": ["All Files (*.*)", "CSV Files (*.csv)", "Text Files (*.txt)"],
      "selected_index": 1,
      "x": 80,
      "y": 228
    }
  ],
  "events": {
    "filter_dropdown.change": "update_file_filter",
    "open_button.click": "open_selected_file",
    "cancel_button.click": "close_dialog"
  },
  "actions": {
    "update_file_filter": {
      "type": "file_filter",
      "filter_source": "filter_dropdown.selected_value",
      "target": "file_list"
    },
    "open_selected_file": {
      "type": "file_operation",
      "operation": "select_file",
      "source": "filename_textbox.text",
      "result_key": "selected_file"
    },
    "close_dialog": {
      "type": "dialog_action",
      "operation": "close",
      "result": false
    }
  }
}
```

---

## 🚨 **設計思想違反の危険パターン**

### **パターン1: 「とりあえず動かす」病**
```python
# 一時的な修正のつもりが、設計思想違反になるパターン
dialog = JsonDialogLoader.load_dialog("file_dialog.json")
# とりあえずCSVをデフォルトに...
dialog.get_control("filter").selected_index = 1  # ❌ JSON定義すべき
```

### **パターン2: 段階的実装の罠**
```python
# Phase 1: JSON定義のみ（正しい）
dialog = JsonDialogLoader.load_dialog("file_dialog.json")

# Phase 2: 一部機能をPythonで（設計思想違反の始まり）
dialog.add_event_handler("open", self._handle_open)  # ❌

# Phase 3: 完全にPython化（設計思想完全放棄）
self.setup_dialog_events()  # ❌
```

### **パターン3: 便利すぎるヘルパー関数**
```python
# 便利だが設計思想違反
def setup_csv_default_dialog(dialog):  # ❌
    """CSVデフォルト設定の便利関数（設計思想違反）"""
    dialog.get_control("filter").selected_index = 1
    dialog.get_control("filename").placeholder = "Select CSV file"
    # → 全てJSON定義で行うべき
```

---

## 📋 **AI開発支援での注意事項**

### **AIアシスタント（Claude等）への指示**
1. **必ずこのDESIGN.mdを参照**
2. **JSON完全定義主義の徹底**
3. **Pythonコード最小化の遵守**
4. **設計思想違反パターンの回避**

### **開発開始時の確認事項**
- [ ] JSON定義ファイルが作成されているか
- [ ] Pythonコードがグルーコードのみか
- [ ] イベントハンドラーがJSONで定義されているか
- [ ] デフォルト値がJSONで設定されているか

### **開発中の定期チェック**
- [ ] 新しいPythonコードが設計思想に準拠しているか
- [ ] UI定義がJSON側に移動されているか
- [ ] 「とりあえず」の修正が設計思想違反になっていないか

---

## 🎯 **成功の指標**

### **最終目標状態**
```python
# 理想的なアプリケーションコード（超シンプル）
class PyPlcApp:
    def __init__(self):
        self.dialogs = JsonDialogManager("dialogs/")
    
    def show_file_dialog(self):
        success, result = self.dialogs.show("file_load_dialog")
        if success:
            self.load_file(result["selected_file"])
```

### **成功基準**
- [ ] main.pyからUI定義コードが完全除去
- [ ] 全ダイアログがJSON定義ベース
- [ ] Pythonコードが50行以下（グルーコードのみ）
- [ ] 新機能追加時にPythonコード修正不要

---

## 💡 **開発時のリマインダー**

> **「これをJSONで定義できないか？」**  
> **「Pythonでやる必要が本当にあるのか？」**  
> **「Windowsのリソースエディターならどうやるか？」**

このDESIGN.mdを定期的に見返し、設計思想を堅持すること。

---

**最終更新**: 2025-08-15  
**次回レビュー予定**: 新機能実装時
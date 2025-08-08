# FileListControl 詳細仕様書

**CSVファイル一覧表示・選択・スクロール機能を持つ高度なコントロール**

---

## 📋 概要

FileListControlは、DialogManager Phase 3で実装された高度なファイル選択コントロールです。CSVファイルの一覧表示、選択、スクロール機能を提供し、実用的なファイル読み込みダイアログの中核を担います。

### 🎯 主要機能

- **ファイル一覧表示**: 指定ディレクトリ内のCSVファイル自動検出・表示
- **ファイル情報表示**: ファイルサイズ・更新日時の詳細表示
- **選択機能**: マウスクリック・キーボード操作による選択
- **スクロール機能**: 大量ファイル対応の縦スクロール
- **ダブルクリック対応**: 即座のファイル確定機能
- **リアルタイム更新**: Refreshボタンによるファイル一覧更新

---

## 🎮 基本的な使用方法

### JSON定義での使用

```json
{
  "title": "ファイル読み込み",
  "width": 400,
  "height": 300,
  "controls": [
    {
      "type": "filelist",
      "id": "file_selector",
      "x": 20,
      "y": 40,
      "width": 360,
      "height": 200,
      "directory": "./",
      "file_pattern": "*.csv",
      "events": ["selection_changed", "file_double_clicked"]
    }
  ]
}
```

### Python コードでの使用

```python
from DialogManager.controls.file_list_control import FileListControl

# 直接インスタンス生成
file_list = FileListControl(
    x=20, y=40, width=360, height=200,
    directory="./", file_pattern="*.csv"
)

# イベントハンドラー登録
def on_selection_changed(selected_file):
    print(f"選択されたファイル: {selected_file}")

def on_file_loaded(file_path):
    print(f"ファイル読み込み: {file_path}")

file_list.set_event_system(event_system)
event_system.register("selection_changed", on_selection_changed)
event_system.register("file_loaded", on_file_loaded)
```

---

## 🔧 設定オプション

### 基本設定

| プロパティ | 型 | デフォルト | 説明 |
|------------|----|-----------|----|
| `x` | int | 0 | X座標位置 |
| `y` | int | 0 | Y座標位置 |
| `width` | int | 300 | コントロール幅 |
| `height` | int | 200 | コントロール高さ |
| `directory` | str | "./" | 検索対象ディレクトリ |
| `file_pattern` | str | "*.csv" | ファイルパターン |

### 表示設定

| プロパティ | 型 | デフォルト | 説明 |
|------------|----|-----------|----|
| `show_file_size` | bool | True | ファイルサイズ表示 |
| `show_date_time` | bool | True | 更新日時表示 |
| `max_filename_length` | int | 30 | ファイル名最大表示文字数 |
| `items_per_page` | int | 10 | 1ページあたりの表示項目数 |

### スタイル設定

| プロパティ | 型 | デフォルト | 説明 |
|------------|----|-----------|----|
| `header_height` | int | 20 | ヘッダー部分の高さ |
| `item_height` | int | 16 | 各項目の高さ |
| `scrollbar_width` | int | 6 | スクロールバーの幅 |
| `selection_color` | int | pyxel.COLOR_YELLOW | 選択項目の背景色 |
| `focus_border_color` | int | pyxel.COLOR_CYAN | フォーカス時の枠線色 |

---

## 🎯 イベント体系

### 1. **selection_changed**
ファイル選択が変更された時に発火

```python
def on_selection_changed(file_info):
    """
    Args:
        file_info (dict): 選択されたファイルの情報
            {
                'name': 'example.csv',
                'path': './example.csv',
                'size': 1024,
                'modified': '2025-08-08 10:00:00'
            }
    """
    print(f"選択変更: {file_info['name']}")
```

### 2. **file_double_clicked**
ダブルクリックまたはEnterキーでファイルが確定された時に発火

```python
def on_file_double_clicked(event_data):
    """
    Args:
        event_data (dict): イベントデータ
            {
                'control_id': 'file_selector',
                'file_info': {
                    'name': 'example.csv',
                    'path': './example.csv',
                    'size': 1024,
                    'modified': '2025-08-08 10:00:00',
                    'display_name': 'example'
                }
            }
    """
    file_path = event_data['file_info']['path']
    print(f"ファイルダブルクリック: {file_path}")
    # 実際のファイル読み込み処理
    with open(file_path, 'r') as f:
        content = f.read()
```

### 3. **scroll_changed**
スクロール位置が変更された時に発火

```python
def on_scroll_changed(scroll_position, total_items):
    """
    Args:
        scroll_position (int): 現在のスクロール位置
        total_items (int): 総項目数
    """
    print(f"スクロール: {scroll_position}/{total_items}")
```

---

## UI構成・レイアウト

### 全体構成

```
┌─────────────────────────────────────────────────────────┐
│                    Header Area                          │
│  Files: 15 | Selected: example.csv                      │
├─────────────────────────────────────────────────────────┤
│                   File List Area                        │
│  📄 file1.csv          1.2KB    2025-08-08 09:30    ┃  │
│  📄 file2.csv          2.5KB    2025-08-08 09:25    ┃  │
│  🟡 example.csv        3.1KB    2025-08-08 10:00    ┃  │ ← 選択中
│  📄 data.csv           0.8KB    2025-08-07 15:20    ┃  │
│  📄 test.csv           4.2KB    2025-08-06 11:45    ┃  │
│                                                     ┃  │
│                                                     ┃  │
│                                                     ┃  │
│                                                     ┃  │
│                                                     ┃  │
│                                                     ┗━━│ ← スクロールバー
└─────────────────────────────────────────────────────────┘
```

### ヘッダー部分

- **左側**: ファイル総数表示 (`Files: {count}`)
- **右側**: 選択中ファイル名表示 (`Selected: {filename}`)
- **背景色**: `pyxel.COLOR_LIGHT_BLUE`
- **文字色**: `pyxel.COLOR_BLACK`

### ファイル一覧部分

- **項目表示**: アイコン + ファイル名 + サイズ + 更新日時
- **選択表示**: 黄色背景 (`pyxel.COLOR_YELLOW`)
- **通常表示**: 白背景 (`pyxel.COLOR_WHITE`)
- **文字色**: 選択時は黒、非選択時は濃青

### スクロールバー

- **背景**: グレー (`pyxel.COLOR_GRAY`)
- **ハンドル**: 濃青 (`pyxel.COLOR_DARK_BLUE`)
- **幅**: 6ピクセル
- **位置**: 右端

---

## 操作方法

### マウス操作

| 操作 | 動作 |
|------|------|
| **左クリック** | ファイル選択 |
| **ダブルクリック** | ファイル確定・読み込み |
| **スクロールホイール** | 上下スクロール |
| **スクロールバードラッグ** | 直接スクロール位置指定 |

### キーボード操作

| キー | 動作 |
|------|------|
| **↑** | 前のファイルを選択 |
| **↓** | 次のファイルを選択 |
| **Page Up** | 1ページ上にスクロール |
| **Page Down** | 1ページ下にスクロール |
| **Home** | リストの先頭に移動 |
| **End** | リストの末尾に移動 |
| **Enter** | 選択中ファイルを確定・読み込み |

---

## 🔧 カスタマイズ方法

### 1. **ファイルパターンの変更**

```json
{
  "type": "filelist",
  "file_pattern": "*.json",  // JSONファイルのみ表示
  "directory": "./data/"
}
```

```python
# 複数パターン対応（実装拡張が必要）
file_list.set_file_patterns(["*.csv", "*.json", "*.txt"])
```

### 2. **表示項目のカスタマイズ**

```python
class CustomFileListControl(FileListControl):
    def _format_file_info(self, file_info):
        """ファイル情報表示形式をカスタマイズ"""
        name = file_info['name'][:20] + "..." if len(file_info['name']) > 20 else file_info['name']
        size = self._format_file_size(file_info['size'])
        return f"{name:25} {size:>8}"
        
    def _format_file_size(self, size_bytes):
        """ファイルサイズ表示形式をカスタマイズ"""
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes // 1024}KB"
        else:
            return f"{size_bytes // (1024 * 1024)}MB"
```

### 3. **色・スタイルのカスタマイズ**

```python
# 初期化時にスタイル設定
file_list = FileListControl(
    selection_color=pyxel.COLOR_GREEN,      # 選択色を緑に変更
    focus_border_color=pyxel.COLOR_RED,     # フォーカス枠を赤に変更
    header_height=25,                       # ヘッダーを高く
    item_height=18                          # 項目を高く
)
```

---

## 🔄 FileListControlWrapper

ControlFactoryとの統合のため、FileListControlWrapperが提供されています。

### 主要メソッド

```python
class FileListControlWrapper:
    def get_selected_file(self) -> Optional[str]:
        """選択中ファイルのパスを取得"""
        return self.file_list_control.get_selected_file()
        
    def refresh_file_list(self):
        """ファイル一覧を更新"""
        self.file_list_control.refresh_files()
        
    def set_directory(self, directory: str):
        """検索ディレクトリを変更"""
        self.file_list_control.directory = directory
        self.refresh_file_list()
        
    def set_event_system(self, event_system):
        """イベントシステムを設定"""
        self.event_system = event_system
        self.file_list_control.set_event_system(event_system)
```

### 使用例

```python
# ControlFactory経由での生成
control_def = {
    "type": "filelist",
    "id": "my_file_list",
    "directory": "./data/",
    "width": 400,
    "height": 250
}

wrapper = control_factory.create_control(control_def)

# 選択ファイル取得
selected_file = wrapper.get_selected_file()
if selected_file:
    print(f"選択されたファイル: {selected_file}")

# ファイル一覧更新
wrapper.refresh_file_list()
```

---

## 🧪 テスト・デバッグ

### 単体テスト例

```python
def test_file_list_basic_functionality():
    """FileListControlの基本機能テスト"""
    file_list = FileListControl(directory="./test_data/")
    
    # ファイル一覧読み込みテスト
    file_list.refresh_file_list()
    assert len(file_list.files) > 0
    
    # ファイル選択テスト
    file_list.selected_index = 0
    selected = file_list.get_selected_file()
    assert selected is not None
    assert selected.endswith('.csv')

def test_file_list_events():
    """FileListControlのイベントテスト"""
    event_system = EventSystem()
    file_list = FileListControl()
    file_list.set_event_system(event_system)
    
    # イベント発火テスト
    event_fired = False
    def on_selection_changed(file_info):
        nonlocal event_fired
        event_fired = True
        
    event_system.register("selection_changed", on_selection_changed)
    file_list._emit_selection_changed()
    assert event_fired
```

### デバッグ用ログ出力

```python
# デバッグモード有効化
file_list = FileListControl(debug=True)

# ログ出力例
# [FileListControl] Directory: ./
# [FileListControl] Found 5 CSV files
# [FileListControl] Selected: example.csv
# [FileListControl] Event fired: selection_changed
```

---

## ⚠️ 制限事項・注意点

### 現在の制限

1. **ファイル形式**: CSVファイルのみ対応
2. **ディレクトリ**: 単一ディレクトリのみ（サブディレクトリ非対応）
3. **ファイルサイズ**: 大容量ファイル（>100MB）の表示が遅い場合がある
4. **文字エンコーディング**: 日本語ファイル名の表示に制限がある場合がある

### パフォーマンス注意点

```python
# ❌ 大量ファイルがある場合の問題
file_list = FileListControl(directory="./huge_directory/")  # 1000+ファイル

# ✅ 推奨: ファイル数制限または分割表示
file_list = FileListControl(
    directory="./data/",
    max_files=100  # 最大表示ファイル数制限（実装拡張が必要）
)
```

### メモリ使用量

- **小規模**: ~50ファイル → ~1MB
- **中規模**: ~200ファイル → ~3MB  
- **大規模**: ~1000ファイル → ~15MB

---

## 🚀 将来の拡張計画

### Phase 4候補機能

1. **複数ファイル形式対応**
   ```python
   file_patterns = ["*.csv", "*.json", "*.txt", "*.xml"]
   ```

2. **サブディレクトリ対応**
   ```python
   recursive_search = True
   show_directory_tree = True
   ```

3. **ファイルプレビュー機能**
   ```python
   show_preview = True
   preview_lines = 5
   ```

4. **ファイルフィルタ機能**
   ```python
   filters = {
       "size_min": "1KB",
       "size_max": "10MB", 
       "date_from": "2025-01-01",
       "name_contains": "test"
   }
   ```

5. **ソート機能**
   ```python
   sort_options = ["name", "size", "date", "type"]
   sort_order = "ascending"  # or "descending"
   ```

---

## 📚 関連ドキュメント

- **[README.md](README.md)**: DialogManager全体概要
- **[Architecture.md](Architecture.md)**: システム設計・アーキテクチャ
- **[EventSystem.md](EventSystem.md)**: イベントシステム詳細仕様
- **[JSONDefinition.md](JSONDefinition.md)**: JSON定義リファレンス
- **[DeveloperGuide.md](DeveloperGuide.md)**: 新規コントロール作成ガイド

---

## 💡 実用的な使用例

### 1. **基本的なファイル選択ダイアログ**

```python
class FileLoadDialog(BaseDialog):
    def __init__(self):
        super().__init__("ファイル読み込み", 450, 350)
        
        # FileListControl追加
        self.file_list = FileListControlWrapper({
            "type": "filelist",
            "directory": "./data/",
            "width": 400,
            "height": 250
        })
        self.add_control(self.file_list)
        
        # イベントハンドラー登録
        self.event_system.register("file_loaded", self.on_file_loaded)
        
    def on_file_loaded(self, file_path):
        """ファイル読み込み処理"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.result = {"success": True, "file_path": file_path, "content": content}
            self.close()
        except Exception as e:
            print(f"ファイル読み込みエラー: {e}")
```

### 2. **設定ファイル選択ダイアログ**

```python
class ConfigFileDialog(BaseDialog):
    def __init__(self):
        super().__init__("設定ファイル選択", 500, 400)
        
        # 複数ディレクトリ対応
        self.config_list = FileListControlWrapper({
            "type": "filelist",
            "directory": "./config/",
            "file_pattern": "*.json",
            "width": 450,
            "height": 300
        })
        self.add_control(self.config_list)
        
        # プレビュー機能（将来実装）
        self.preview_enabled = True
```

---

**FileListControlは、PyPlc Ver3 DialogManagerの中核的なコントロールとして、実用的なファイル操作機能を提供し、教育ツールとしての価値を大幅に向上させています。**

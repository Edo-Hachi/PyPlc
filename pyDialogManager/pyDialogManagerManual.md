# pyDialogManager 使用マニュアル

## 📋 概要

pyDialogManagerは、Pyxelを使用したJSON駆動の汎用ダイアログシステムです。  
PyPlcプロジェクトのような大規模アプリケーションに統合して、ファイル操作ダイアログやカスタムダイアログを簡単に実装できます。

## 🎯 主要な特徴

- **JSON駆動設計**: ダイアログレイアウトをJSONで定義
- **ウィジェットベースUI**: ボタン、テキストボックス、リストボックス等の豊富なコントロール
- **動的属性システム**: Python hasattrパターンによる疎結合なイベントハンドリング
- **ファイルシステム連携**: リアルタイムディレクトリブラウジング機能
- **拡張子自動管理**: 保存時の拡張子自動付与システム

## 📁 プロジェクト構成

```
pyDialogManager/
├── main.py                    # デモアプリケーション（参考用）
├── dialog_manager.py          # 中核システム
├── dialogs.json              # ダイアログレイアウト定義
├── widgets.py                # UIウィジェット実装
├── file_open_dialog.py       # ファイルオープンダイアログ制御
├── file_save_dialog.py       # ファイル保存ダイアログ制御
├── file_utils.py             # ファイルシステムユーティリティ
├── system_settings.py        # グローバル設定管理
└── DESIGN.md                 # 設計制約事項
```

## 🚀 基本的な使用方法

### 1. 基本統合手順

```python
import pyxel
from dialog_manager import DialogManager
from file_open_dialog import FileOpenDialogController
from file_save_dialog import FileSaveDialogController

class YourApp:
    def __init__(self):
        pyxel.init(256, 256, title="Your Application")
        
        # ダイアログマネージャーを初期化
        self.dialog_manager = DialogManager("dialogs.json")
        
        # ファイルダイアログコントローラーを初期化
        self.file_open_controller = FileOpenDialogController(self.dialog_manager)
        self.file_save_controller = FileSaveDialogController(self.dialog_manager)
        
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def update(self):
        # ダイアログシステムの更新
        self.dialog_manager.update()
        self.file_open_controller.update()
        self.file_save_controller.update()

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)
        # ダイアログシステムの描画
        self.dialog_manager.draw()
```

### 2. ダイアログ表示

```python
# シンプルなダイアログ表示
self.dialog_manager.show("IDD_MAIN_DIALOG")

# ファイルオープンダイアログ表示
self.file_open_controller.show_file_open_dialog()

# ファイル保存ダイアログ表示（拡張子自動付与）
self.file_save_controller.show_save_dialog(
    default_filename="myfile", 
    default_extension=".txt"
)

# 拡張子なし保存ダイアログ
self.file_save_controller.show_save_dialog(
    default_filename="script", 
    default_extension=""
)
```

## 📄 dialogs.json の構造

### 基本ダイアログ定義

```json
{
  "IDD_YOUR_DIALOG": {
    "title": "Your Dialog Title",
    "x": 10,
    "y": 10,
    "width": 200,
    "height": 150,
    "widgets": [
      {
        "type": "label",
        "id": "IDC_LABEL",
        "text": "Hello World",
        "x": 10,
        "y": 20
      },
      {
        "type": "button",
        "id": "IDOK",
        "text": "OK",
        "x": 75,
        "y": 110,
        "width": 50,
        "height": 20
      }
    ]
  }
}
```

### サポートされるウィジェットタイプ

#### Label（ラベル）
```json
{
  "type": "label",
  "id": "IDC_LABEL",
  "text": "表示テキスト",
  "x": 10,
  "y": 20
}
```

#### Button（ボタン）
```json
{
  "type": "button",
  "id": "IDOK",
  "text": "OK",
  "x": 75,
  "y": 110,
  "width": 50,
  "height": 20
}
```

#### TextBox（テキスト入力）
```json
{
  "type": "textbox",
  "id": "IDC_INPUT",
  "text": "初期値",
  "x": 10,
  "y": 30,
  "width": 200,
  "height": 20,
  "max_length": 100,
  "readonly": false
}
```

#### ListBox（リスト表示）
```json
{
  "type": "listbox",
  "id": "IDC_LIST",
  "x": 5,
  "y": 70,
  "width": 225,
  "height": 120,
  "item_height": 10
}
```

## 🎮 操作方法

### キーボード操作
- **TAB**: シングル/ダブルクリックモード切り替え
- **マウス操作**: ウィジェットクリック、ドラッグなど

### ファイルダイアログ操作
- **ディレクトリ移動**: リスト内ディレクトリをクリック
- **上位ディレクトリ**: "Up"ボタンクリック
- **ファイル選択**: リスト内ファイルをクリック（ファイル名が入力欄に自動入力）

## 🔧 カスタムダイアログの作成

### 1. dialogs.json への追加

```json
{
  "IDD_CUSTOM_DIALOG": {
    "title": "Custom Dialog",
    "x": 50,
    "y": 50,
    "width": 300,
    "height": 200,
    "widgets": [
      {
        "type": "label",
        "id": "IDC_LABEL_MESSAGE",
        "text": "Enter your name:",
        "x": 10,
        "y": 20
      },
      {
        "type": "textbox",
        "id": "IDC_NAME_INPUT",
        "text": "",
        "x": 10,
        "y": 40,
        "width": 280,
        "height": 20,
        "max_length": 50
      },
      {
        "type": "button",
        "id": "IDOK",
        "text": "OK",
        "x": 180,
        "y": 160,
        "width": 50,
        "height": 20
      },
      {
        "type": "button",
        "id": "IDCANCEL", 
        "text": "Cancel",
        "x": 240,
        "y": 160,
        "width": 50,
        "height": 20
      }
    ]
  }
}
```

### 2. カスタムコントローラの実装

```python
class CustomDialogController:
    def __init__(self, dialog_manager: DialogManager):
        self.dialog_manager = dialog_manager
        self.active_dialog = None
        self.result = None

    def show_custom_dialog(self):
        """カスタムダイアログを表示"""
        self.dialog_manager.show("IDD_CUSTOM_DIALOG")
        self.active_dialog = self.dialog_manager.active_dialog
        self.result = None

    def get_user_input(self):
        """ユーザー入力値を取得"""
        if not self.active_dialog:
            return None
            
        name_widget = self._find_widget("IDC_NAME_INPUT")
        if name_widget:
            return name_widget.text
        return None

    def _find_widget(self, widget_id: str):
        """ウィジェットIDでウィジェットを検索"""
        if not self.active_dialog:
            return None
            
        for widget in self.active_dialog.widgets:
            if hasattr(widget, 'id') and widget.id == widget_id:
                return widget
        return None

    def update(self):
        """フレームごとの更新処理"""
        if not self.active_dialog:
            return
            
        # ボタンクリックをチェック
        for widget in self.active_dialog.widgets:
            if hasattr(widget, 'id') and hasattr(widget, 'is_pressed') and widget.is_pressed:
                if widget.id == "IDOK":
                    self.result = self.get_user_input()
                    print(f"User entered: {self.result}")
                    # ダイアログを閉じる場合はここで処理
                elif widget.id == "IDCANCEL":
                    self.result = None
                    print("Dialog cancelled")
```

## 📤 ダイアログの戻り値取得

### ファイル保存ダイアログの結果取得

```python
class YourApp:
    def __init__(self):
        # ... 初期化処理 ...
        self.save_result = None

    def update(self):
        # キー入力でダイアログ表示
        if pyxel.btnp(pyxel.KEY_S):
            self.file_save_controller.show_save_dialog(
                default_filename="data", 
                default_extension=".csv"
            )

        # ダイアログ更新
        self.file_save_controller.update()
        
        # 保存結果をチェック（カスタムコントローラで実装が必要）
        if self.save_result:
            print(f"File will be saved to: {self.save_result}")
            self.save_result = None
```

### カスタム戻り値ハンドリング

```python
# file_save_dialog.py の handle_save_button メソッドを参考に
def handle_save_button(self):
    filename_widget = self._find_widget("IDC_FILENAME_INPUT")
    if not filename_widget or not filename_widget.text.strip():
        return None
        
    final_filename = self._get_final_filename(filename_widget.text)
    full_path = os.path.join(self.file_manager.get_current_path(), final_filename)
    
    # 戻り値として返す
    return full_path
```

## 🎨 デザイン制約事項

### 表示文字制限
- **ASCII文字のみ**: Pyxelの制限により2バイト文字（日本語、絵文字）は表示不可
- **コメント**: ソースコード内のコメントは日本語OK

### 色定数の使用
```python
# ❌ 悪い例
BLACK = pyxel.COLOR_BLACK

# ✅ 良い例  
pyxel.cls(pyxel.COLOR_BLACK)
pyxel.text(x, y, "text", pyxel.COLOR_WHITE)
```

## 🔧 高度な機能

### 動的属性システム（hasattrパターン）

```python
# ウィジェット側でイベントハンドラーをチェック
if hasattr(self, 'on_item_activated'):
    self.on_item_activated(self.selected_index)

# コントローラー側でハンドラーを動的に追加
listbox.on_item_activated = self.handle_file_activation
listbox.on_selection_changed = self.handle_file_selection
```

### ファイルシステム連携

```python
# ファイルマネージャーの直接操作
file_manager = FileManager("/path/to/directory")
file_items = file_manager.list_directory()

for item in file_items:
    print(f"{item.get_display_name()} - {'DIR' if item.is_directory else 'FILE'}")
```

## 🐛 トラブルシューティング

### よくある問題

1. **ダイアログが表示されない**
   - `dialogs.json`の記述を確認
   - ダイアログIDが正しいかチェック

2. **ボタンクリックが反応しない**
   - `update()`メソッドが呼ばれているか確認
   - マウスが有効になっているか確認（`pyxel.mouse(True)`）

3. **テキストが文字化けする**
   - ASCII文字以外を使用していないか確認
   - 表示文字列を英数字に変更

4. **ファイルが保存されない**
   - ファイルパスが正しいか確認
   - 書き込み権限があるか確認

## 📚 参考実装

### main.py のエントリポイント

現在の`main.py`は以下のようなデモ機能を提供しています：

```python
# F1: メインダイアログ
# F2: ファイルオープンダイアログ（カレントディレクトリから開始）
# F3: ファイル保存ダイアログ（.txt拡張子自動付与）
# F4: テキスト入力ダイアログ
# F5: CSV保存ダイアログ（.csv拡張子自動付与）
# F6: 拡張子なし保存ダイアログ
# TAB: シングル/ダブルクリックモード切り替え
```

### PyPlcプロジェクトへの統合例

```python
# PyPlcのmain.pyに統合する場合
class PyPlcApp:
    def __init__(self):
        # ... 既存の初期化 ...
        
        # ダイアログシステム追加
        self.dialog_manager = DialogManager("dialogs.json")
        self.file_save_controller = FileSaveDialogController(self.dialog_manager)
        
    def update(self):
        # ... 既存の更新処理 ...
        
        # ダイアログシステム更新
        self.dialog_manager.update()
        self.file_save_controller.update()
        
        # 回路保存機能
        if pyxel.btnp(pyxel.KEY_S) and pyxel.btn(pyxel.KEY_CTRL):
            self.file_save_controller.show_save_dialog(
                default_filename="circuit", 
                default_extension=".csv"
            )

    def draw(self):
        # ... 既存の描画処理 ...
        
        # ダイアログシステム描画（最前面）
        self.dialog_manager.draw()
```

## 🎯 次のステップ

1. **基本統合**: まずシンプルなダイアログから統合開始
2. **ファイル操作**: ファイル保存・読み込み機能の統合
3. **カスタムダイアログ**: プロジェクト固有のダイアログ追加
4. **UI/UX改善**: ユーザー体験の向上

このマニュアルを参考に、PyPlcプロジェクトでpyDialogManagerの強力なダイアログシステムを活用してください！


# Message
---

● ありがとうございます！pyDialogManagerの開発、とても充実したプロジェクトで
  した。

  🎉 開発成果まとめ

  完成した機能

  - ✅ JSONベース汎用ダイアログシステム
  - ✅ リアルタイムファイルブラウジング
  - ✅ 拡張子自動管理システム
  - ✅ 動的属性システム（hasattrパターン）
  - ✅ LoadダイアログとSaveダイアログの統一UI
  - ✅ シンプルで分かりやすいAPI設計

  技術的価値

  - 疎結合設計: ウィジェットとコントローラーの独立性
  - 再利用性: PyPlcのような大規模プロジェクトへの統合容易性
  - 保守性: JSON駆動によるUIとロジックの分離
  - 拡張性: 新しいダイアログの簡単な追加

  PyPlcプロジェクトでの統合時には、CLAUDE_pyPlc.mdで見られる高品質なコード
  基準と同じレベルで、pyDialogManagerが強力なダイアログ機能を提供できると思
  います。

  メインシステムでの再会を楽しみにしています！ 🚀

  pyDialogManagerがPyPlcプロジェクトの素晴らしいユーザーエクスペリエンス向
  上に貢献できることを願っています。

---

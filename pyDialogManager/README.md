# pyDialogManager

**JSON駆動の汎用ダイアログシステム for Pyxel**

PyxelベースのアプリケーションにプロフェッショナルなダイアログUI機能を提供する統合ライブラリです。

![pyDialogManager](https://img.shields.io/badge/Python-3.8+-blue)  ![Pyxel](https://img.shields.io/badge/Pyxel-1.9.0+-green)  ![License](https://img.shields.io/badge/License-MIT-yellow)

**最終更新**: 2025-08-22 (Phase 2リファクタリング完了版)

---

## ⚠️ **重要: 複数ダイアログ対応とStale参照問題**

pyDialogManagerは一度に1つのダイアログのみ表示されます。  
複数のダイアログコントローラーを使用する場合は、**Stale参照問題**を避けるため、以下の推奨パターンを必ず使用してください。

### 🚨 **避けるべきパターン（危険）**
```python
class BadController:
    def is_active(self):
        # 危険: Stale参照を検出できない
        return self.active_dialog is not None
```

### ✅ **推奨パターン1: 基底クラス継承（推奨）**
```python
# PyPlc環境での推奨パターン
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.base_dialog_controller import PyPlcDialogController

class MyDialogController(PyPlcDialogController):
    def __init__(self, dialog_manager):
        super().__init__(dialog_manager)
    
    def show_my_dialog(self):
        if self._safe_show_dialog("IDD_MY_DIALOG"):
            # 初期化処理
            self._initialize_dialog()
    
    # is_active()は自動的に安全な実装になります
```

### ✅ **推奨パターン2: 手動でStale参照対応**
```python
class SafeController:
    def __init__(self, dialog_manager):
        self.dialog_manager = dialog_manager
        self.active_dialog = None
        self.result = None
    
    def is_active(self) -> bool:
        """Stale参照を検出する安全な実装"""
        return (self.dialog_manager.active_dialog is not None and 
                self.active_dialog is not None and
                self.active_dialog is self.dialog_manager.active_dialog)
    
    def show_dialog(self, dialog_id):
        self.result = None
        self.dialog_manager.show(dialog_id)
        self.active_dialog = self.dialog_manager.active_dialog
```

---

## 🚀 **クイックスタート**

### 基本統合（基底クラス継承パターン）

```python
import pyxel
from pyDialogManager.dialog_manager import DialogManager
from pyDialogManager.file_open_dialog import FileOpenDialogController

class MyApp:
    def __init__(self):
        pyxel.init(256, 256, title="My Application")
        
        # DialogManager初期化
        self.dialog_manager = DialogManager("dialogs.json")
        
        # コントローラー作成（基底クラス継承済み）
        self.file_controller = FileOpenDialogController(self.dialog_manager, "/home")
        
        pyxel.run(self.update, self.draw)
    
    def update(self):
        # ダイアログ更新
        self.dialog_manager.update()
        self.file_controller.update()
        
        # Ctrl+O でファイルダイアログ表示
        if pyxel.btnp(pyxel.KEY_O) and pyxel.btn(pyxel.KEY_CTRL):
            self.file_controller.show_file_open_dialog()
        
        # 結果取得
        if not self.file_controller.is_active():
            result = self.file_controller.get_result()
            if result:
                print(f"Selected file: {result}")
    
    def draw(self):
        pyxel.cls(0)
        
        # ダイアログ描画
        self.dialog_manager.draw()
        
        # UI情報表示
        pyxel.text(10, 10, "Press Ctrl+O to open file dialog", 7)

# 実行
MyApp()
```

---

## 📋 **主要コンポーネント**

### 1. DialogManager（コア）
ダイアログの表示・管理を行う中核クラス

```python
from pyDialogManager.dialog_manager import DialogManager

# 初期化
manager = DialogManager("path/to/dialogs.json")

# ダイアログ表示
manager.show("IDD_MY_DIALOG")

# 更新・描画
manager.update()
manager.draw()

# ダイアログ終了
manager.close()
```

### 2. 基底クラス（PyPlcDialogController）
安全なダイアログ制御を提供する基底クラス

```python
from core.base_dialog_controller import PyPlcDialogController

class MyController(PyPlcDialogController):
    def __init__(self, dialog_manager):
        super().__init__(dialog_manager)
    
    def show_custom_dialog(self):
        if self._safe_show_dialog("IDD_CUSTOM"):
            # 安全にダイアログが表示された
            widget = self._find_widget("IDC_INPUT")
            if widget:
                widget.text = "Initial value"
    
    def update(self):
        # Stale参照チェック付きアップデート
        if self.active_dialog and self.active_dialog != self.dialog_manager.active_dialog:
            self.active_dialog = None
        
        if not self.active_dialog:
            return
        
        # ボタン処理
        ok_button = self._find_widget("IDOK")
        if ok_button and ok_button.is_pressed:
            self.result = {"status": "ok"}
            self.dialog_manager.close()
```

### 3. 既存コントローラー
すぐに使用できる実装済みコントローラー

```python
# ファイル開くダイアログ
from pyDialogManager.file_open_dialog import FileOpenDialogController

controller = FileOpenDialogController(manager, initial_directory="/home")
controller.show_file_open_dialog()

# ファイル保存ダイアログ
from pyDialogManager.file_save_dialog import FileSaveDialogController

save_controller = FileSaveDialogController(manager, initial_directory="/home")
save_controller.show_save_dialog(default_filename="document", default_extension=".txt")

# デバイスID編集ダイアログ
from pyDialogManager.device_id_dialog_controller import DeviceIdDialogController
from config import DeviceType

device_controller = DeviceIdDialogController(manager)
device_controller.show_dialog(DeviceType.CONTACT_A, initial_value="X001")
```

---

## 🛠️ **カスタムダイアログ実装手順**

### Step 1: JSON定義ファイル作成

```json
{
  "dialogs": {
    "IDD_CUSTOM_DIALOG": {
      "title": "Custom Dialog",
      "width": 300,
      "height": 200,
      "widgets": [
        {
          "id": "IDC_NAME_INPUT",
          "type": "textbox",
          "x": 50,
          "y": 50,
          "width": 200,
          "height": 25,
          "text": ""
        },
        {
          "id": "IDC_TYPE_DROPDOWN",
          "type": "dropdown",
          "x": 50,
          "y": 90,
          "width": 150,
          "height": 25,
          "items": ["Type A", "Type B", "Type C"],
          "selected_index": 0
        },
        {
          "id": "IDOK",
          "type": "button",
          "x": 150,
          "y": 150,
          "width": 60,
          "height": 25,
          "text": "OK"
        },
        {
          "id": "IDCANCEL",
          "type": "button",
          "x": 220,
          "y": 150,
          "width": 60,
          "height": 25,
          "text": "Cancel"
        }
      ]
    }
  }
}
```

### Step 2: コントローラー実装

```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.base_dialog_controller import PyPlcDialogController
from pyDialogManager.dialog_manager import DialogManager

class CustomDialogController(PyPlcDialogController):
    """カスタムダイアログのコントローラー"""
    
    def __init__(self, dialog_manager: DialogManager):
        super().__init__(dialog_manager)
    
    def show_custom_dialog(self, initial_name="", initial_type=0):
        """カスタムダイアログを表示"""
        if self._safe_show_dialog("IDD_CUSTOM_DIALOG"):
            # 初期値設定
            name_widget = self._find_widget("IDC_NAME_INPUT")
            if name_widget:
                name_widget.text = initial_name
            
            type_widget = self._find_widget("IDC_TYPE_DROPDOWN")
            if type_widget:
                type_widget.selected_index = initial_type
    
    def update(self):
        """フレームごとの更新処理"""
        # Stale参照チェック（基底クラスパターン）
        if self.active_dialog and self.active_dialog != self.dialog_manager.active_dialog:
            self.active_dialog = None

        if not self.active_dialog:
            return
        
        # ボタンイベント処理
        ok_button = self._find_widget("IDOK")
        if ok_button and ok_button.is_pressed:
            self._handle_ok()

        cancel_button = self._find_widget("IDCANCEL")
        if cancel_button and cancel_button.is_pressed:
            self._handle_cancel()
    
    def _handle_ok(self):
        """OKボタンが押された時の処理"""
        name_widget = self._find_widget("IDC_NAME_INPUT")
        type_widget = self._find_widget("IDC_TYPE_DROPDOWN")
        
        if name_widget and type_widget:
            # バリデーション
            name = name_widget.text.strip()
            if not name:
                # エラー処理
                return
            
            # 結果設定
            self.result = {
                "name": name,
                "type": type_widget.get_selected_value(),
                "type_index": type_widget.selected_index
            }
            self.dialog_manager.close()
    
    def _handle_cancel(self):
        """Cancelボタンが押された時の処理"""
        self.result = None
        self.dialog_manager.close()
```

### Step 3: メインアプリケーションでの使用

```python
class MainApp:
    def __init__(self):
        # DialogManager初期化
        self.dialog_manager = DialogManager("custom_dialogs.json")
        self.custom_controller = CustomDialogController(self.dialog_manager)
    
    def update(self):
        # ダイアログ更新
        self.dialog_manager.update()
        self.custom_controller.update()
        
        # F1キーでカスタムダイアログ表示
        if pyxel.btnp(pyxel.KEY_F1):
            self.custom_controller.show_custom_dialog("Sample Name", 1)
        
        # 結果取得
        if not self.custom_controller.is_active():
            result = self.custom_controller.get_result()
            if result:
                print(f"Dialog result: {result}")
```

---

## 🎨 **利用可能なウィジェット**

### Button
```json
{
  "id": "IDC_MY_BUTTON",
  "type": "button",
  "x": 100,
  "y": 50,
  "width": 80,
  "height": 25,
  "text": "Click Me"
}
```

### TextBox
```json
{
  "id": "IDC_TEXT_INPUT",
  "type": "textbox",
  "x": 50,
  "y": 30,
  "width": 200,
  "height": 25,
  "text": "Initial text",
  "readonly": false
}
```

### ListBox
```json
{
  "id": "IDC_FILE_LIST",
  "type": "listbox",
  "x": 10,
  "y": 40,
  "width": 280,
  "height": 180,
  "max_visible_items": 8
}
```

### Dropdown
```json
{
  "id": "IDC_TYPE_SELECT",
  "type": "dropdown",
  "x": 50,
  "y": 80,
  "width": 150,
  "height": 25,
  "items": ["Option 1", "Option 2", "Option 3"],
  "selected_index": 0,
  "max_visible_items": 5
}
```

### Label
```json
{
  "id": "IDC_INFO_LABEL",
  "type": "label",
  "x": 20,
  "y": 20,
  "text": "Information:",
  "color": 7
}
```

---

## 📚 **実装パターン集**

### パターン1: バリデーション付きフォーム
```python
def _handle_ok(self):
    name_widget = self._find_widget("IDC_NAME")
    email_widget = self._find_widget("IDC_EMAIL")
    error_widget = self._find_widget("IDC_ERROR_MESSAGE")
    
    name = name_widget.text.strip() if name_widget else ""
    email = email_widget.text.strip() if email_widget else ""
    
    # バリデーション
    if not name:
        if error_widget:
            error_widget.text = "Name is required"
        return
    
    if "@" not in email:
        if error_widget:
            error_widget.text = "Invalid email format"
        return
    
    # 成功時
    if error_widget:
        error_widget.text = ""
    
    self.result = {"name": name, "email": email}
    self.dialog_manager.close()
```

### パターン2: ドロップダウン連動処理
```python
def setup_event_handlers(self):
    """イベントハンドラーを設定"""
    category_widget = self._find_widget("IDC_CATEGORY")
    if category_widget:
        category_widget.on_selection_changed = self.handle_category_changed

def handle_category_changed(self, selected_index: int, selected_value: str):
    """カテゴリ選択時の処理"""
    subcategory_widget = self._find_widget("IDC_SUBCATEGORY")
    if subcategory_widget:
        # カテゴリに応じてサブカテゴリを更新
        subcategories = {
            "Electronics": ["Computers", "Phones", "Cameras"],
            "Books": ["Fiction", "Non-fiction", "Technical"],
            "Clothing": ["Men", "Women", "Kids"]
        }
        items = subcategories.get(selected_value, [])
        subcategory_widget.set_items(items)
        subcategory_widget.selected_index = 0
```

### パターン3: 動的ウィジェット制御
```python
def update_ui_state(self):
    """UIの状態を動的に更新"""
    enable_advanced = self._find_widget("IDC_ENABLE_ADVANCED")
    advanced_panel = [
        "IDC_ADVANCED_OPTION1",
        "IDC_ADVANCED_OPTION2",
        "IDC_ADVANCED_SETTINGS"
    ]
    
    if enable_advanced and hasattr(enable_advanced, 'is_checked'):
        enabled = enable_advanced.is_checked
        
        # 詳細設定の有効/無効切り替え
        for widget_id in advanced_panel:
            widget = self._find_widget(widget_id)
            if widget:
                widget.enabled = enabled
                if hasattr(widget, 'color'):
                    widget.color = 7 if enabled else 5
```

---

## ⚡ **パフォーマンス最適化**

### 重い処理の分散実行
```python
def update(self):
    if not self.active_dialog:
        return
    
    # 重い処理を数フレームに分散
    if hasattr(self, '_processing_frame'):
        self._processing_frame += 1
        
        if self._processing_frame % 5 == 0:  # 5フレームに1回実行
            self._update_file_list()
        
        if self._processing_frame % 10 == 0:  # 10フレームに1回実行
            self._update_preview()
    else:
        self._processing_frame = 0
    
    # 軽い処理は毎フレーム実行
    self._check_button_clicks()
```

### メモリ効率的なリスト管理
```python
def _refresh_large_list(self):
    """大量データのリスト表示最適化"""
    list_widget = self._find_widget("IDC_DATA_LIST")
    if not list_widget:
        return
    
    # 仮想化: 表示領域のアイテムのみ生成
    start_index = list_widget.scroll_position
    end_index = min(start_index + list_widget.max_visible_items + 2, len(self.all_data))
    
    visible_items = [self.all_data[i].display_name for i in range(start_index, end_index)]
    list_widget.set_items(visible_items)
    list_widget._data_offset = start_index  # オフセット保存
```

---

## 🔧 **デバッグとトラブルシューティング**

### デバッグ情報表示
```python
def debug_dialog_state(self):
    """ダイアログ状態のデバッグ情報を表示"""
    if self.active_dialog:
        print(f"Dialog ID: {self.active_dialog.dialog_id}")
        print(f"Dialog Title: {self.active_dialog.definition.get('title', 'Untitled')}")
        print(f"Widgets count: {len(self.active_dialog.widgets)}")
        print(f"Is Active: {self.is_active()}")
        print(f"Manager Active: {self.dialog_manager.active_dialog is not None}")
```

### 一般的な問題と解決策

1. **ダイアログが表示されない**
   - JSON定義ファイルのパスが正しいか確認
   - dialog_idが正確に指定されているか確認
   - `manager.update()`と`manager.draw()`が呼ばれているか確認

2. **ボタンクリックが反応しない**
   - ボタンのIDが正確か確認
   - `update()`メソッドが正しく実装されているか確認
   - `is_pressed`プロパティのチェック方法を確認

3. **Stale参照エラー**
   - 基底クラスを継承しているか確認
   - `is_active()`の実装が安全なパターンを使用しているか確認

---

## 🤝 **コントリビューション**

### 開発環境セットアップ
```bash
# リポジトリクローン
git clone <repository-url>
cd PyPlc/pyDialogManager

# 依存関係インストール
pip install pyxel>=1.9.0

# テスト実行
python -m pytest tests/
```

### コーディング規約
- 日本語コメント推奨
- 型ヒントの使用必須
- docstring（日本語）の記載
- pyxel.COLOR_xxx定数の使用

---

## 📜 **ライセンス**

MIT License - 詳細は`LICENSE`ファイルを参照してください。

---

## 📞 **サポート**

- **Issues**: GitHub Issues でバグ報告・機能要求
- **Documentation**: 本READMEおよび`/docs`ディレクトリ
- **Examples**: `examples/`ディレクトリの実装例

---

**pyDialogManager v2.0** - 2025-08-22リリース  
*Phase 2リファクタリング完了版 - 安全性・保守性大幅向上*

---

# これ以降は古いバージョンの情報です

**以下の情報は古いバージョン（Phase 2リファクタリング前）のものです。**  
**最新の実装では上記の推奨パターンを使用してください。**

---

## 📋 **概要（旧版）**

pyDialogManagerは、Pyxelを使用したJSON駆動の汎用ダイアログシステムです。  
PyPlcプロジェクトのような大規模アプリケーションに統合して、ファイル操作ダイアログやカスタムダイアログを簡単に実装できます。
テキストボックス、リストボックス、ボタン、カスタムボタン、ドロップダウンリスト等のWidgetを組み合わせて独自のダイアログボックスを構築できます。

### 🎯 **主要な特徴（旧版）**

- **JSON駆動設計**: ダイアログレイアウトをJSONで定義
- **ウィジェットベースUI**: 豊富なコントロール（Button, TextBox, ListBox, Dropdown, Checkbox）
- **動的属性システム**: Python hasattrパターンによる疎結合なイベントハンドリング
- **ファイルシステム連携**: リアルタイムディレクトリブラウジング機能
- **一元管理システム**: DialogSystemによるコントローラー統合管理
- **拡張子自動管理**: 保存時の拡張子自動付与システム
- **エラーハンドリング**: 堅牢なファイル操作エラー処理

---

## 🚀 **クイックスタート（旧版）**

### インストールと基本統合

```python
import pyxel
from pyDialogManager.dialog_manager import DialogManager
from pyDialogManager.dialog_system import DialogSystem
from pyDialogManager.file_open_dialog import FileOpenDialogController
from pyDialogManager.file_save_dialog import FileSaveDialogController

class MyApp:
    def __init__(self):
        pyxel.init(256, 256, title="My Application")
        
        # ダイアログシステム初期化
        self.py_dialog_manager = DialogManager("pyDialogManager/dialogs.json")
        self.dialog_system = DialogSystem()
        
        # コントローラー作成・登録
        self.file_open_controller = FileOpenDialogController(self.py_dialog_manager)
        self.file_save_controller = FileSaveDialogController(self.py_dialog_manager)
        
        # システムに登録
        self.dialog_system.register_controller("file_open", self.file_open_controller)
        self.dialog_system.register_controller("file_save", self.file_save_controller)
        
        pyxel.run(self.update, self.draw)
    
    def update(self):
        # ダイアログシステム更新
        self.py_dialog_manager.update()
        self.dialog_system.update()
        
        # Ctrl+O でファイルダイアログ
        if pyxel.btnp(pyxel.KEY_O, True, True) and pyxel.btn(pyxel.KEY_CTRL):
            self.file_open_controller.show_file_open_dialog()
        
        # Ctrl+S で保存ダイアログ
        if pyxel.btnp(pyxel.KEY_S, True, True) and pyxel.btn(pyxel.KEY_CTRL):
            self.file_save_controller.show_save_dialog("document", ".txt")
    
    def draw(self):
        pyxel.cls(0)
        
        # ダイアログ描画
        self.py_dialog_manager.draw()
        
        # UI情報表示
        if self.dialog_system.has_active_dialogs():
            pyxel.text(10, 10, "Dialog Active", 14)
        else:
            pyxel.text(10, 10, "Press Ctrl+O/S for dialogs", 7)

# 実行
MyApp()
```

**注意: この旧版のコードではStale参照問題が発生する可能性があります。最新版の推奨パターンを使用してください。**
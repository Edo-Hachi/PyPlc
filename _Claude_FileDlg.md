# PyPlc Ver3 ファイルダイアログ実装プラン

作成日: 2025-08-07  
対象: ファイル保存・読み込みダイアログシステム実装  
優先度: タイマー実装より高優先

## 1. 実装背景・目的

### 現状の課題
- Ctrl+S/O: 自動ファイル名生成・最新ファイル選択（ユーザー制御不可）
- ファイル名指定不可、ファイル選択不可
- 既存ファイル上書き確認なし

### 目標
- ユーザー指定ファイル名での保存
- ファイル一覧からの選択読み込み
- PLC標準準拠のファイル管理UI
- Ver1ダイアログシステムの活用

## 2. Ver1調査結果・技術基盤

### 既存資産（活用可能）
```
Project Ver01/pyxdlg.py (577行)
├── PyxDialog: メインダイアログクラス
├── JsonDialogBuilder: JSON定義システム
├── InputType: バリデーション(TEXT/NUMBER/DEVICE_ADDRESS)
├── キーボード入力処理: 完全実装済み
└── UI部品: DialogLabel, DialogControl
```

### Ver3統合ポイント
```
dialogs/DialogManager (既存)
core/CircuitCsvManager (既存)
```

## 3. 実装設計仕様

### 3.1 ファイル保存ダイアログ
```python
class FileSaveDialog:
    """ファイル保存専用ダイアログ"""
    
    def show(self, default_name: str = "circuit") -> Tuple[bool, str]:
        """
        Returns:
            (success: bool, filename: str)
        """
        
    # UI仕様:
    # - ファイル名入力テキストボックス
    # - .csv拡張子自動付加
    # - 上書き確認ダイアログ
    # - OK/Cancelボタン
```

### 3.2 ファイル読み込みダイアログ
```python
class FileLoadDialog:
    """ファイル読み込み専用ダイアログ"""
    
    def show(self) -> Tuple[bool, str]:
        """
        Returns:
            (success: bool, selected_file: str)
        """
        
    # UI仕様:
    # - CSVファイル一覧表示（作成日時順）
    # - ファイル選択（マウス/キーボード）
    # - ファイル情報表示（サイズ・日時）
    # - OK/Cancelボタン
```

### 3.3 統合ダイアログマネージャー
```python
class FileDialogManager:
    """ファイルダイアログ統合管理"""
    
    def __init__(self, csv_manager: CircuitCsvManager):
        self.csv_manager = csv_manager
        
    def show_save_dialog(self) -> bool:
        """保存ダイアログ表示→CSV保存実行"""
        
    def show_load_dialog(self) -> bool:
        """読み込みダイアログ表示→CSV読み込み実行"""
```

## 4. ファイル構成

### 新規作成ファイル
```
dialogs/
├── file_dialogs.py          # メインダイアログクラス（新規）
├── file_dialog_manager.py   # 統合管理クラス（新規）
└── file_validation.py       # バリデーション機能（新規）
```

### 設定ファイル（JSON定義）
```
dialogs/configs/
├── save_dialog.json         # 保存ダイアログレイアウト
└── load_dialog.json         # 読み込みダイアログレイアウト
```

### 既存ファイル変更
```
main.py                      # Ctrl+S/O→ダイアログ呼び出し変更
dialogs/__init__.py          # エクスポート追加
```

## 5. 詳細実装仕様

### 5.1 ファイル名バリデーション
```python
class FileNameValidator:
    """ファイル名検証・サニタイズ"""
    
    # 不正文字: < > : " | ? * / \
    # 長さ制限: 50文字以内
    # 拡張子: 自動.csv付加
    
    @staticmethod
    def validate(filename: str) -> bool:
        """バリデーション実行"""
        
    @staticmethod
    def sanitize(filename: str) -> str:
        """サニタイズ実行"""
```

### 5.2 ファイル一覧表示
```python
class FileListDisplay:
    """CSVファイル一覧表示UI"""
    
    # 表示項目:
    # - ファイル名
    # - ファイルサイズ
    # - 作成日時
    # - 選択状態（ハイライト）
    
    # 操作:
    # - 上下矢印キー選択
    # - マウスクリック選択
    # - ダブルクリック確定
```

### 5.3 キーボード入力処理（Ver1準拠）
```python
class KeyboardHandler:
    """キーボード入力統合処理"""
    
    # 文字入力: 0-9, A-Z（大文字変換）
    # 制御キー: BackSpace, Delete, Home, End
    # カーソル移動: Left, Right
    # 確定: Enter→OK, ESC→Cancel
    
    def handle_text_input(self, current_text: str) -> str:
        """テキスト入力処理"""
        
    def handle_list_navigation(self, current_index: int) -> int:
        """リスト選択処理"""
```

## 6. UI設計仕様（Ver3画面サイズ対応）

### 6.1 保存ダイアログレイアウト
```
画面サイズ: 384x384
ダイアログサイズ: 280x160 (中央配置)

┌─────────────────────────────────┐
│ Save Circuit File               │
├─────────────────────────────────┤
│ Enter filename:                 │
│ ┌─────────────────────────────┐ │
│ │ my_circuit              │ │ │ ← テキスト入力
│ └─────────────────────────────┘ │
│                                 │
│ Extension: .csv (auto)          │
│                                 │
│    ┌───────┐    ┌───────┐      │
│    │  OK   │    │Cancel │      │
│    └───────┘    └───────┘      │
└─────────────────────────────────┘
```

### 6.2 読み込みダイアログレイアウト  
```
ダイアログサイズ: 320x240

┌─────────────────────────────────┐
│ Load Circuit File               │
├─────────────────────────────────┤
│ Select file:                    │
│ ┌─────────────────────────────┐ │
│ │ > circuit_20250807_184743   │ │ ← 選択状態
│ │   circuit_20250806_120430   │ │
│ │   circuit_20250805_093215   │ │
│ │   circuit_20250804_154520   │ │
│ └─────────────────────────────┘ │
│                                 │
│ Size: 1.2KB  Modified: 18:47    │
│                                 │
│    ┌───────┐    ┌───────┐      │
│    │  OK   │    │Cancel │      │
│    └───────┘    └───────┘      │
└─────────────────────────────────┘
```

### 6.3 上書き確認ダイアログ
```
ダイアログサイズ: 260x120

┌─────────────────────────────────┐
│ File Exists                     │
├─────────────────────────────────┤
│                                 │
│ 'my_circuit.csv' already exists │
│ Do you want to overwrite it?    │
│                                 │
│  ┌────────┐    ┌───────┐       │
│  │Overwrite│    │Cancel │       │
│  └────────┘    └───────┘       │
└─────────────────────────────────┘
```

## 7. 実装Todo（フェーズ別）

### Phase 1: 設計・準備（2項目）
```
□ ファイル保存ダイアログ設計
  - UI仕様確定（レイアウト・サイズ・配色）
  - JSON設定ファイル作成
  - Ver1 pyxdlg.py統合方法確定

□ ファイル読み込みダイアログ設計  
  - ファイル一覧表示UI仕様
  - 選択・操作方法設計
  - ファイル情報表示仕様
```

### Phase 2: コア機能実装（6項目）
```
□ dialogs/file_dialogs.py実装
  - FileSaveDialog クラス実装
  - FileLoadDialog クラス実装
  - Ver1 PyxDialog 基底クラス継承

□ ファイル名バリデーション実装
  - FileNameValidator クラス実装
  - 不正文字チェック（< > : " | ? * / \）
  - 長さ制限（50文字以内）
  - サニタイズ機能（不正文字→_変換）

□ ファイル一覧表示UI実装
  - FileListDisplay クラス実装
  - CSVファイル検索・ソート（作成日時順）
  - リスト表示・選択状態管理
  - ファイル情報取得・表示

□ キーボード入力処理統合
  - Ver1準拠の文字入力処理
  - カーソル移動（Left/Right/Home/End）
  - リスト選択（Up/Down矢印キー）
  - 確定処理（Enter→OK、ESC→Cancel）

□ 上書き確認ダイアログ実装
  - OverwriteConfirmDialog クラス
  - 既存ファイル検出機能
  - 3択確認（Overwrite/Cancel）

□ DialogManager統合
  - FileDialogManager クラス実装
  - 既存 DialogManager との統合
  - CircuitCsvManager 連携
```

### Phase 3: 統合・完成（3項目）
```
□ main.py統合
  - Ctrl+S → FileDialogManager.show_save_dialog()
  - Ctrl+O → FileDialogManager.show_load_dialog()
  - 現在の自動保存・読み込み処理置き換え

□ 統合テスト
  - 保存ダイアログ動作確認
  - 読み込みダイアログ動作確認
  - ファイル名バリデーション確認
  - 上書き確認動作確認
  - キーボード・マウス操作確認

□ 最終調整
  - デバッグ出力削除
  - コード最適化
  - ドキュメント更新
```

## 8. 技術的実装ポイント

### 8.1 Ver1 pyxdlg.py活用パターン
```python
# Ver1の成功パターンを継承
from Project_Ver01.pyxdlg import PyxDialog, InputType

class FileSaveDialog(PyxDialog):
    def __init__(self):
        super().__init__()
        
    def show(self, default_name: str) -> Tuple[bool, str]:
        # Ver1のinput_text_dialog()メソッド活用
        return self.input_text_dialog(
            "Save Circuit File",
            "Enter filename:",
            default_name,
            InputType.TEXT
        )
```

### 8.2 JSON設定ファイル例
```json
{
  "save_dialog": {
    "title": "Save Circuit File",
    "width": 280,
    "height": 160,
    "controls": [
      {
        "type": "label",
        "text": "Enter filename:",
        "x": 20, "y": 30
      },
      {
        "type": "textinput",
        "id": "filename",
        "x": 20, "y": 50,
        "width": 240, "height": 20,
        "placeholder": "my_circuit"
      }
    ]
  }
}
```

### 8.3 CircuitCsvManager統合
```python
class FileDialogManager:
    def show_save_dialog(self) -> bool:
        success, filename = FileSaveDialog().show("my_circuit")
        if success:
            # 既存のCSV管理システムを活用
            return self.csv_manager.save_circuit_to_csv(filename)
        return False
```

## 9. 期待効果・完成後機能

### 9.1 ユーザビリティ向上
- 任意ファイル名での保存
- ファイル選択での読み込み
- 上書き確認による安全性
- 直感的なファイル管理

### 9.2 システム品質向上
- Ver1実績システムの活用
- 責任分離設計の維持
- PLC標準準拠UI
- 拡張性の確保

### 9.3 Ver3完成度向上
- 商用製品レベルのファイル管理
- プロフェッショナルUI
- 実PLC同等の操作感
- 教育価値の向上

## 10. 次段階への影響

ファイルダイアログ実装完了後:
1. タイマー・カウンター実装への移行
2. より高度なファイル管理機能（プロジェクト管理等）
3. 回路図エクスポート機能への拡張

---

実装優先度: ★★★★★（最優先）  
完成予想時間: 8-10時間  
技術難易度: 中（Ver1資産活用により軽減）
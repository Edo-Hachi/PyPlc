# PyPlc Ver3 DialogManager

**JSON駆動ダイアログシステム - 疎結合・拡張可能・宣言的UI定義**

---

## 📋 概要

DialogManagerは、PyPlc Ver3のために開発された次世代ダイアログシステムです。JSON定義による宣言的UI構築、疎結合なイベントシステム、高い拡張性を特徴とし、PLC教育ツールに最適化されています。

### 🎯 主要な特徴

- **JSON駆動UI**: 宣言的なJSON定義によるダイアログ構築
- **疎結合アーキテクチャ**: イベントシステムによる柔軟な連携
- **高い拡張性**: 新しいコントロールタイプの容易な追加
- **PLC標準準拠**: デバイスアドレス検証・バリデーション機能
- **実用的なコントロール**: テキスト入力・ファイル選択等の実装済み
- **包括的テスト**: 各Phase毎の統合テスト・実機動作確認

---

## 🚀 クイックスタート

### 基本的な使用方法

```python
from DialogManager.json_dialog_loader import JSONDialogLoader
from DialogManager.base_dialog import BaseDialog

# JSON定義からダイアログを作成
loader = JSONDialogLoader()
dialog_data = loader.load_dialog("definitions/test_confirm.json")

# ダイアログを表示・実行
dialog = TestConfirmDialog(dialog_data)
result = dialog.show_modal()
```

### JSON定義例

```json
{
  "title": "確認ダイアログ",
  "width": 300,
  "height": 150,
  "controls": [
    {
      "type": "label",
      "id": "message",
      "text": "この操作を実行しますか？",
      "x": 20,
      "y": 30
    },
    {
      "type": "button",
      "id": "ok_button",
      "text": "OK",
      "x": 80,
      "y": 100,
      "events": ["click"]
    }
  ]
}
```

---

## 🏗️ システムアーキテクチャ

### コアコンポーネント

```
JSON定義 → JSONDialogLoader → ControlFactory → BaseDialog → EventSystem
                                     ↓
各種Control + ValidationSystem + 座標変換システム
```

### 主要クラス

- **BaseDialog**: 全ダイアログの基底クラス（モーダル処理・座標変換）
- **JSONDialogLoader**: JSON定義ファイルの読み込み・解析
- **ControlFactory**: 動的コントロール生成（ファクトリーパターン）
- **EventSystem**: 疎結合イベント通知システム
- **ValidationSystem**: PLC標準準拠バリデーション

---

## 📁 ディレクトリ構造

```
DialogManager/
├── README.md                    # このファイル
├── base_dialog.py              # ダイアログ基底クラス
├── json_dialog_loader.py       # JSON定義読み込み
├── control_factory.py          # 動的コントロール生成
├── controls/                   # コントロール実装
│   ├── text_input_control.py   # テキスト入力コントロール
│   └── file_list_control.py    # ファイル一覧コントロール
├── events/                     # イベントシステム
│   └── event_system.py         # 疎結合イベント通知
├── validation/                 # バリデーションシステム
│   └── validator.py            # PLC標準準拠検証
├── definitions/                # JSON定義ファイル
│   ├── test_confirm.json       # テスト用確認ダイアログ
│   ├── device_settings.json    # デバイスID設定ダイアログ
│   └── file_load_dialog.json   # ファイル読み込みダイアログ
├── Document/                   # ドキュメント（このディレクトリ）
│   ├── README.md               # 概要・使い方
│   ├── Architecture.md         # アーキテクチャ設計
│   ├── FileListControl.md      # FileListControl仕様
│   ├── EventSystem.md          # イベントシステム仕様
│   ├── JSONDefinition.md       # JSON定義リファレンス
│   ├── DeveloperGuide.md       # 開発者ガイド
│   └── Environment.md          # 実行環境・依存関係
└── [テスト・統合ファイル群]
```

---

## 🎮 実装済みコントロール

### TextInputControl
- **機能**: リアルタイムテキスト入力・編集
- **特徴**: PLC標準準拠バリデーション、フォーカス管理、カーソル表示
- **用途**: デバイスアドレス入力、設定値入力

### FileListControl  
- **機能**: ファイル一覧表示・選択・スクロール
- **特徴**: CSVファイル対応、ファイル情報表示、キーボード・マウス操作
- **用途**: 回路図ファイル選択、データファイル読み込み

### ButtonControl
- **機能**: クリック可能ボタン
- **特徴**: ホバー効果、正確なマウス座標判定
- **用途**: OK/Cancel、Load/Save等の操作ボタン

### LabelControl
- **機能**: 静的テキスト表示
- **特徴**: 色・フォント・配置カスタマイズ
- **用途**: 説明文、ステータス表示

---

## 🧪 テスト・動作確認

### 統合テスト

DialogManagerには包括的な統合テストが実装されています：

```bash
# PyPlc Ver3を起動
./venv/bin/python main.py

# キーボードショートカット
T キー: Phase 1統合テスト（基本機能）
U キー: Phase 2統合テスト（テキスト入力）
V キー: Phase 3統合テスト（ファイル選択）
W キー: FileLoadDialog実装テスト
```

### テスト結果
- **Phase 1統合テスト**: 3/3成功 ✅
- **Phase 2統合テスト**: 3/3成功 ✅  
- **Phase 3統合テスト**: 3/3成功 ✅
- **実機動作確認**: 全キー完全動作 ✅

---

## 📈 開発履歴

### Phase 1: MVPコアフレームワーク構築 ✅
**Git commit**: 0e018c0 "Phase1 commit"
- BaseDialog、JSONDialogLoader、ControlFactory、EventSystem実装
- JSON定義からの動的ダイアログ生成確認

### Phase 2: 実用ダイアログシステム構築 ✅  
**Git commit**: beb5e5a "Dialog Text Box Fixed"
- TextInputControl、ValidationSystem、座標変換システム実装
- 全ての技術的課題（座標系問題、フォーカス問題等）解決

### Phase 3: FileListControl実装 ✅
**Git commit**: 0c47dca "FileListDlg Finish"
- CSVファイル一覧表示・選択・スクロール機能実装
- 実機動作確認完了（V/Wキーテスト成功）

---

## 🔧 実行環境・依存関係

### 必要な環境
- **Python**: 3.8+ 
- **Pyxel**: 1.9.x（色定数制限あり）
- **仮想環境**: `/home/yukikaze/Project/PyxelProject/PyPlc/venv/` 必須

### 実行方法
```bash
# 仮想環境有効化
source /home/yukikaze/Project/PyxelProject/PyPlc/venv/bin/activate

# PyPlc Ver3起動
python main.py
```

### 注意点
- **Pyxel色定数**: `COLOR_BLUE`等は使用不可（`COLOR_CYAN`等を使用）
- **EventSystem命名**: `DialogEventSystem`と`EventSystem`のエイリアス混在
- **Git管理**: `DialogSystemRefact`ブランチで開発中

---

## 📚 詳細ドキュメント

- **[Architecture.md](Architecture.md)**: システム設計・アーキテクチャ詳細
- **[FileListControl.md](FileListControl.md)**: FileListControl仕様・使用方法
- **[EventSystem.md](EventSystem.md)**: イベントシステム仕様・拡張方法
- **[JSONDefinition.md](JSONDefinition.md)**: JSON定義書式・リファレンス
- **[DeveloperGuide.md](DeveloperGuide.md)**: 新規コントロール作成ガイド
- **[Environment.md](Environment.md)**: 実行環境・トラブルシューティング

---

## 🎯 今後の拡張計画

### 最優先（ドキュメント整備完了後）
- **プロダクション統合**: 既存file_dialogs.pyとの置き換え
- **ファイル機能拡張**: CSV以外の形式対応、プレビュー機能
- **UI/UX改善**: エラーハンドリング強化、パフォーマンス最適化

### 将来検討
- **高度なコントロール**: NumericUpDown、CheckBox、ComboBox等
- **テーマシステム**: カラーテーマ・外観カスタマイズ
- **多言語対応**: 国際化・ローカライゼーション

---

## 🏆 DialogManager の価値

DialogManagerは、PyPlc Ver3の**拡張性・保守性を大幅に向上**させ、将来の機能拡張への**強固な基盤**を提供します。

- **教育的価値**: PLC標準準拠の正確な実装
- **実用的価値**: 実際に使える高品質なダイアログシステム  
- **技術的価値**: 疎結合・拡張可能なアーキテクチャ設計
- **保守的価値**: 包括的なドキュメント・テスト体系

**PyPlc Ver3 DialogManager - 次世代PLC教育ツールの中核システム**

# PyPlc Ver3 DialogManager

## 概要

DialogManager は、PyPlc Ver3 向けに開発された JSON 駆動のダイアログシステムです。宣言的な UI 定義と疎結合なイベントシステムを特徴とし、PLC 教育ツールに最適化されています。

## 主な特徴

- **JSON 駆動の UI 構築**: 宣言的な JSON 定義による柔軟なダイアログ構築
- **疎結合アーキテクチャ**: イベント駆動型のコンポーネント連携
- **拡張可能な設計**: 新しいコントロールタイプの容易な追加
- **PLC 標準準拠**: デバイスアドレス検証機能を内蔵
- **包括的なテスト**: 各フェーズの統合テストを実装

## クイックスタート

### インストール

```bash
# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Linux/macOS
# または
# .\venv\Scripts\activate  # Windows

# 依存関係のインストール
pip install -r requirements.txt
```

### 基本的な使い方

```python
from DialogManager.json_dialog_loader import JSONDialogLoader
from DialogManager.base_dialog import BaseDialog

# JSON 定義からダイアログを作成
loader = JSONDialogLoader()
dialog_data = loader.load_dialog("definitions/test_confirm.json")

# ダイアログを表示・実行
dialog = TestConfirmDialog(dialog_data)
result = dialog.show_modal()
```

## アーキテクチャ

DialogManager は以下の主要コンポーネントで構成されています：

- **BaseDialog**: 全ダイアログの基底クラス
- **JSONDialogLoader**: JSON 定義の読み込みと解析
- **ControlFactory**: 動的コントロール生成
- **EventSystem**: 疎結合なイベント通知システム
- **ValidationSystem**: PLC 標準準拠のバリデーション

詳細は [Architecture.md](Architecture.md) を参照してください。

## 実装済みコントロール

### TextInputControl
- **機能**: テキスト入力と編集
- **特徴**: リアルタイムバリデーション、フォーカス管理
- **用途**: デバイスアドレス入力、設定値入力

### FileListControl
- **機能**: ファイル一覧の表示と選択
- **特徴**: CSV ファイル対応、スクロール機能
- **用途**: 回路図ファイルの選択

### ButtonControl
- **機能**: クリック可能なボタン
- **特徴**: ホバー効果、正確なマウス判定
- **用途**: 操作ボタン

### LabelControl
- **機能**: 静的テキスト表示
- **特徴**: 書式設定可能
- **用途**: ラベル、説明文

## ドキュメント

- [アーキテクチャ概要](Architecture.md)
- [FileListControl リファレンス](FileListControl.md)
- [イベントシステム](EventSystem.md)
- [JSON 定義リファレンス](JSONDefinition.md)
- [開発者ガイド](DeveloperGuide.md)
- [環境設定ガイド](Environment.md)

## 開発

### テストの実行

```bash
# 統合テストの実行
python -m unittest discover DialogManager/tests
```

### 開発ガイド

新しいコントロールの作成方法については [開発者ガイド](DeveloperGuide.md) を参照してください。

## ライセンス

[ライセンス情報]

## 貢献について

[貢献ガイドライン]
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

# PyPlc Ver3 DialogManager v2

PyPlc Ver3の統合ダイアログシステム - 整理・最適化版

## 📋 概要

DialogManager v2は、PyPlc Ver3のすべてのダイアログ機能を統合管理するクリーンなシステムです。JSON駆動による柔軟なUI構成と、デバイス種別に応じた適切なダイアログ表示を提供します。

## 🏗️ アーキテクチャ

### ディレクトリ構造
```
DialogManager/
├── __init__.py              # パッケージエクスポート
├── core/                    # コアシステム
│   ├── dialog_manager.py    # メイン管理クラス
│   ├── base_dialog.py       # ダイアログ基底クラス
│   ├── control_factory.py   # UIコントロール生成
│   ├── json_dialog_loader.py # JSON定義読み込み
│   └── schema_validator.py  # JSON検証システム
├── dialogs/                 # 個別ダイアログ実装
│   ├── data_register_dialog.py   # データレジスタ編集
│   ├── device_id_dialog.py       # デバイスID編集
│   ├── timer_counter_dialog.py   # タイマー・カウンター編集
│   ├── file_load_dialog.py       # ファイル読み込み
│   └── file_save_dialog.py       # ファイル保存
├── controls/                # UIコントロール
│   ├── text_input_control.py     # テキスト入力
│   └── file_list_control.py      # ファイルリスト
├── events/                  # イベントシステム
│   └── event_system.py      # イベント処理
├── validation/              # バリデーション
│   └── validator.py         # 入力検証
├── definitions/             # JSON定義ファイル
│   ├── schemas/             # JSONスキーマ
│   └── *.json               # ダイアログ定義
└── docs/                    # ドキュメント
    ├── README.md            # このファイル
    ├── ARCHITECTURE.md      # アーキテクチャ解説
    └── API.md               # API リファレンス
```

## 🚀 主要機能

### 1. 統合ダイアログ管理
- デバイス種別に応じた適切なダイアログ自動選択
- 統一されたインターフェース
- モーダル処理とイベント管理

### 2. JSON駆動UI構成
- 定義ファイルによる柔軟なレイアウト
- JSONスキーマによる検証
- リアルタイム設定変更対応

### 3. 高度なバリデーション
- PLC標準準拠の入力検証
- リアルタイムエラー表示
- カスタムバリデーションルール

### 4. イベントシステム
- 疎結合イベント処理
- コールバック管理
- 非同期処理対応

## 💻 使用方法

### 基本的な使用例

```python
from DialogManager import DialogManager

# DialogManager初期化
dialog_manager = DialogManager()

# デバイス編集ダイアログ表示
dialog_manager.show_device_edit_dialog(
    device=device,
    row=row,
    col=col,
    background_draw_func=draw_background,
    grid_system=grid_system
)
```

### カスタムダイアログの作成

```python
from DialogManager import BaseDialog, ControlFactory

class CustomDialog(BaseDialog):
    def __init__(self):
        super().__init__(title="カスタムダイアログ", width=300, height=200)
        self.factory = ControlFactory()
        self._create_controls()
    
    def _create_controls(self):
        # JSON定義からコントロール生成
        pass
```

## 🔧 開発・メンテナンス

### テスト実行
```bash
cd DialogManager
python -m pytest tests/
```

### 新しいダイアログの追加
1. `dialogs/` ディレクトリに新しいダイアログクラスを作成
2. `definitions/` にJSON定義ファイルを追加
3. 必要に応じてスキーマファイルを作成
4. `core/dialog_manager.py` に処理を追加
5. `__init__.py` にエクスポートを追加

## 📚 API リファレンス

### DialogManager クラス
- `show_device_edit_dialog()`: デバイス編集ダイアログ表示
- `validate_device_for_id_edit()`: デバイスID編集可能性検証
- `generate_default_device_id()`: デフォルトID生成

### BaseDialog クラス
- `show()`: モーダルダイアログ表示
- `close()`: ダイアログ終了
- `add_control()`: コントロール追加
- `emit()`: イベント発火

## 🔄 旧システムからの移行

### 移行済み機能
- ✅ データレジスタダイアログ（完全動作確認済み）
- ✅ デバイスIDダイアログ
- ✅ タイマー・カウンタープリセット値ダイアログ
- ✅ ファイル読み込み・保存ダイアログ
- ✅ JSON駆動UI システム
- ✅ スキーマ検証システム

### 削除された機能
- ❌ テストファイル群（integration_test, phase2_test等）
- ❌ 実験的実装（*_simple.py）
- ❌ 古いドキュメント
- ❌ 未使用のテーマ・レイアウトシステム

## 📝 更新履歴

### v2.0.0 (2025-08-13)
- 初回リリース
- DialogManagerシステムの完全整理・統合
- 不要ファイルの除去
- ドキュメント更新
- アーキテクチャの最適化

## 🤝 貢献

DialogManager v2の改善にご協力いただける場合は、以下のガイドラインに従ってください：

1. 新機能は小さな単位で実装
2. 既存のJSON駆動アーキテクチャに準拠
3. 適切なテストの作成
4. ドキュメントの更新

---

**DialogManager v2** - PyPlc Ver3 統合ダイアログシステム
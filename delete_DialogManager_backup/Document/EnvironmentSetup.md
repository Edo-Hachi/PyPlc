# 環境構築ガイド

DialogManagerを開発・実行するための環境構築手順と依存関係について説明します。

## 必要条件

### 1. ハードウェア要件
- OS: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)
- CPU: 2コア以上を推奨
- メモリ: 4GB以上を推奨
- ストレージ: 100MB以上の空き容量

### 2. ソフトウェア要件
- Python 3.8 以上
- pip (Pythonパッケージマネージャ)
- Git (ソース管理)

## セットアップ手順

### 1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/PyPlc.git
cd PyPlc
```

### 2. 仮想環境の作成と有効化
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 依存パッケージのインストール
```bash
# コア依存関係
pip install -r requirements.txt

# 開発用依存関係（必要な場合）
pip install -r requirements-dev.txt
```

## 依存関係一覧

### コア依存関係
| パッケージ | バージョン | 説明 |
|------------|-----------|------|
| Pyxel      | 1.9.0+    | 2Dゲームエンジン（UIレンダリング用） |
| numpy      | 1.21.0+   | 数値計算ライブラリ |
| pyyaml     | 6.0+      | YAML設定ファイルの読み書き |

### 開発用依存関係
| パッケージ | バージョン | 説明 |
|------------|-----------|------|
| pytest     | 7.0.0+    | テストフレームワーク |
| pylint     | 2.12.0+   | コード静的解析ツール |
| black      | 22.3.0+   | コードフォーマッタ |

## 開発環境設定

### VSCode 設定
1. 拡張機能のインストール:
   - Python
   - Pylance
   - Python Test Explorer

2. `.vscode/settings.json` に以下を追加:
```json
{
    "python.pythonPath": "venv/bin/python",
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true
}
```

### PyCharm 設定
1. プロジェクトを開く
2. インタプリタ設定:
   - `File` > `Settings` > `Project: PyPlc` > `Python Interpreter`
   - 歯車アイコン > `Add` > 仮想環境を選択

## 実践的なセットアップ例

### 例1: 新規開発環境のセットアップ

```bash
# 1. リポジトリをクローン
git clone https://github.com/yourusername/PyPlc.git
cd PyPlc

# 2. 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Linux/macOS
# または
.\venv\Scripts\activate  # Windows

# 3. 依存関係のインストール
pip install -r requirements.txt

# 4. VS Codeの設定
cat > .vscode/settings.json << 'EOL'
{
    "python.pythonPath": "venv/bin/python",
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true
}
EOL

# 5. テストの実行
pytest DialogManager/tests/
```

### 例2: 既存プロジェクトへの参加

```bash
# 1. リポジトリをクローン
git clone https://github.com/yourusername/PyPlc.git
cd PyPlc

# 2. 依存関係のインストール（開発者モード）
pip install -e .[dev]

# 3. 環境変数の設定（必要に応じて）
echo "PYTHONPATH=$PWD" > .env

# 4. コードのフォーマットとチェック
black .
pylint DialogManager/

# 5. アプリケーションの起動
python main.py
```

## トラブルシューティング

### 1. Pyxelのインストールエラー
```
ERROR: Failed building wheel for pyxel
```
**解決策**:
- ビルドツールをインストール:
  - Windows: Visual Studio Build Tools (C++ ビルドツール)
  - macOS: `xcode-select --install`
  - Ubuntu: `sudo apt-get install python3-dev libsdl2-dev libpython3-dev`

### 2. 仮想環境が認識されない
**解決策**:
- VSCodeで `Ctrl+Shift+P` > "Python: Select Interpreter" を選択
- 仮想環境のPythonを手動で選択

### 3. 依存関係の競合
**解決策**:
```bash
# 依存関係のクリーンインストール
pip uninstall -y -r requirements.txt
pip install -r requirements.txt
```

## 開発ワークフロー

### 1. 開発開始時
```bash
# 仮想環境を有効化
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\activate  # Windows

# 依存関係を更新
pip install -r requirements.txt
```

### 2. コードのテスト
```bash
# すべてのテストを実行
pytest

# 特定のテストを実行
pytest tests/test_dialog_manager.py -v
```

### 3. コードのフォーマットとリント
```bash
# コードフォーマット
black .

# コード解析
pylint DialogManager/
```

## デプロイメント

### スタンドアロン実行ファイルの作成
```bash
# PyInstallerのインストール
pip install pyinstaller

# 実行ファイルのビルド
pyinstaller --onefile --windowed main.py
```

## 依存関係の更新

### 依存関係の更新方法
```bash
# パッケージの更新
pip install --upgrade package_name

# 更新された依存関係をrequirements.txtに保存
pip freeze > requirements.txt
```

## サポート

問題が発生した場合は、以下の情報を添えてIssueを作成してください：
- エラーメッセージ
- 再現手順
- 環境情報（OS, Pythonバージョンなど）
- 期待される動作と実際の動作の違い

# CLAUDE.md

# ユーザーには日本語で応答、対応してください

# pythonですが、型は宣言してください

# ソース内のコメントは日本語でお願いします
# このプロジェクトではUTF-8のベタテキストのみを使って下さい。絵文字は使わないで下さい。 
# pyxelは2バイト文字は扱えません。出力する文字は1バイトの英数字、記号にしてください

#ubuntu での実行環境は以下のようになっています
// For Ubuntu 
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python デバッガー: 現在のファイル",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
//            "program": "${workspaceFolder}/SpriteDefiner.py",
            "console": "integratedTerminal",
            "python": "${workspaceFolder}/../venv/bin/python",            
        }
    ]
}

//For Ubuntu
{
 "python.pythonPath": "../venv/bin/python"
}



# windows での実行環境は以下のようになっています
//For Windows
{
    "version": "0.2.0",
    "configurations": [

        {
            "name": "Python デバッガー: main.py",
            "type": "debugpy",
            "request": "launch",
//            "program": "${workspaceFolder}/homing.py",
            "program": "${workspaceFolder}/main.py",
//            "program": "${workspaceFolder}/SpriteDefiner.py",
            "console": "integratedTerminal"
        }
    ]
}

//For Windows
{
    "python.defaultInterpreterPath": "python.exe",
    "python.terminal.activateEnvironment": false,
    "files.encoding": "utf8",
    "files.eol": "\n",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}

#「commit.txt」を作成するときはgitに上げるので、UTF8のベタな文字コードで作成してください

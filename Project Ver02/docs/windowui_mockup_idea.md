# PyxelベースWindowUI システム

## 概要
Pyxelを使って軽量なモックアップ作成環境を構築する。日本語は使えないが、サクサク動作するUIシステムを目指す。

## 基本コンセプト
- **軽快な動作**: Pyxelの60FPS描画を活用
- **JSON定義**: レイアウトとロジックの分離
- **モックアップ特化**: 見た目よりも機能確認重視
- **再利用性**: UIコンポーネントのライブラリ化

## 必要なUIコンポーネント

### 基本コントロール
- **Button** - OK、Cancel等の基本ボタン
- **TextInput** - 英数字入力ボックス
- **Label** - テキスト表示
- **Checkbox** - チェックボックス
- **RadioButton** - ラジオボタン（グループ対応）
- **DropdownList** - ドロップダウンリスト

### 拡張コントロール
- **Scrollbar** - 縦/横スクロール
- **Slider** - 数値調整スライダー
- **ProgressBar** - 進捗表示バー
- **Tab** - タブ切り替え
- **ListBox** - 複数項目選択リスト
- **Table/Grid** - データ表形式表示

### レイアウト系
- **Panel/Frame** - UIグループ化
- **Separator** - 区切り線
- **Splitter** - 画面分割バー

### メニュー系
- **MenuBar** - ファイル、編集等のメニュー
- **ContextMenu** - 右クリックメニュー
- **Tooltip** - マウスオーバー説明

## JSON定義システム

### 基本構造
```json
{
  "windows": [
    {
      "id": "window_id",
      "title": "Window Title",
      "x": 100, "y": 100, "w": 400, "h": 300,
      "controls": [
        {
          "type": "control_type",
          "id": "control_id",
          "x": 0, "y": 0, "w": 100, "h": 30,
          "properties": {}
        }
      ]
    }
  ]
}
```

### 具体例
```json
{
  "windows": [
    {
      "id": "settings_dialog",
      "title": "Settings",
      "x": 100, "y": 100, "w": 400, "h": 300,
      "controls": [
        {
          "type": "label",
          "id": "title_label", 
          "x": 20, "y": 20,
          "text": "Configure Options"
        },
        {
          "type": "textinput",
          "id": "name_input",
          "x": 100, "y": 60, "w": 200, "h": 24,
          "placeholder": "Enter name"
        },
        {
          "type": "checkbox",
          "id": "enable_feature",
          "x": 20, "y": 100,
          "text": "Enable advanced mode",
          "checked": false
        },
        {
          "type": "radiobutton",
          "id": "option1",
          "x": 20, "y": 130,
          "text": "Option 1",
          "group": "main_options",
          "checked": true
        },
        {
          "type": "radiobutton",
          "id": "option2",
          "x": 20, "y": 155,
          "text": "Option 2",
          "group": "main_options",
          "checked": false
        },
        {
          "type": "dropdown",
          "id": "theme_select",
          "x": 20, "y": 190, "w": 150, "h": 25,
          "options": ["Light", "Dark", "Auto"],
          "selected": 0
        },
        {
          "type": "button",
          "id": "cancel_btn",
          "x": 180, "y": 250, "w": 60, "h": 30,
          "text": "Cancel",
          "action": "cancel"
        },
        {
          "type": "button",
          "id": "ok_btn",
          "x": 250, "y": 250, "w": 60, "h": 30,
          "text": "OK",
          "action": "submit"
        }
      ]
    }
  ]
}
```

## 実装アーキテクチャ

### クラス設計
```python
class WindowManager:
    # JSON読み込み、ウィンドウ管理
    
class BaseControl:
    # 全コントロールの基底クラス
    
class Dialog:
    # ダイアログウィンドウ
    
class Button(BaseControl):
    # ボタンコントロール
    
class TextInput(BaseControl):
    # テキスト入力
    
# 他のコントロール類...
```

### イベント処理
- マウスクリック検出
- キーボード入力処理
- フォーカス管理
- コールバック機能

## 利点
1. **環境構築不要** - Pyxel標準機能のみ使用
2. **高速動作** - ゲームエンジンベースの軽快さ
3. **柔軟なレイアウト** - JSON編集で簡単変更
4. **配布容易** - 実行ファイル化が簡単
5. **デザイン分離** - プログラマーとデザイナーの分業可能

## 開発ステップ
1. 基本的なWindowManagerとBaseControlクラス作成
2. Button, Label, TextInputの実装
3. JSON読み込み機能の実装
4. イベント処理システムの構築
5. 拡張コントロールの追加
6. サンプルモックアップでテスト

## 参考
- Windowsリソースファイル(.rc)の概念
- TkinterのようなGUIツールキット
- Pyxelの描画・イベント機能
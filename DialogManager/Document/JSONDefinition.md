# JSON定義リファレンス

DialogManagerで使用するJSON定義の完全なリファレンスです。

## 目次
- [基本構造](#基本構造)
- [共通プロパティ](#共通プロパティ)
- [コントロールタイプ](#コントロールタイプ)
  - [ダイアログ](#ダイアログ)
  - [ボタン (button)](#ボタン-button)
  - [ラベル (label)](#ラベル-label)
  - [テキスト入力 (textinput)](#テキスト入力-textinput)
  - [ファイルリスト (filelist)](#ファイルリスト-filelist)
- [イベント](#イベント)
- [実装例](#実装例)

## 基本構造

DialogManagerのJSON定義は、以下の基本構造を持ちます：

```json
{
  "title": "ダイアログのタイトル",
  "width": 400,
  "height": 300,
  "controls": [
    // コントロールの定義
  ]
}
```

## 共通プロパティ

すべてのコントロールで使用できる共通プロパティ：

| プロパティ | 型 | 必須 | デフォルト値 | 説明 |
|-----------|----|------|------------|------|
| `id` | string | はい | - | コントロールの一意識別子 |
| `type` | string | はい | - | コントロールのタイプ |
| `x` | number | はい | - | X座標 |
| `y` | number | はい | - | Y座標 |
| `width` | number | はい | - | 幅 |
| `height` | number | はい | - | 高さ |
| `visible` | boolean | いいえ | `true` | 表示/非表示 |
| `enabled` | boolean | いいえ | `true` | 有効/無効 |
| `color` | number | いいえ | `7` | テキスト色 (Pyxel色番号) |
| `bg_color` | number | いいえ | `0` | 背景色 (Pyxel色番号) |
| `events` | array | いいえ | `[]` | 購読するイベントのリスト |

## コントロールタイプ

### ダイアログ

ダイアログ全体を定義します。すべてのJSON定義のルート要素です。

**プロパティ**

| プロパティ | 型 | 必須 | デフォルト値 | 説明 |
|-----------|----|------|------------|------|
| `title` | string | はい | - | ダイアログのタイトル |
| `width` | number | はい | - | ダイアログの幅 |
| `height` | number | はい | - | ダイアログの高さ |
| `controls` | array | はい | - | 子コントロールの配列 |

### ボタン (button)

クリック可能なボタンコントロールです。

**プロパティ**

| プロパティ | 型 | 必須 | デフォルト値 | 説明 |
|-----------|----|------|------------|------|
| `text` | string | はい | - | ボタンに表示するテキスト |
| `hover_color` | number | いいえ | `1` | ホバー時の色 (Pyxel色番号) |

**イベント**
- `click`: ボタンがクリックされたときに発生

**例**
```json
{
  "id": "ok_button",
  "type": "button",
  "x": 50,
  "y": 70,
  "width": 60,
  "height": 25,
  "text": "OK",
  "color": 7,
  "bg_color": 11,
  "hover_color": 3,
  "events": ["click"]
}
```

### ラベル (label)

テキストを表示する静的なコントロールです。

**プロパティ**

| プロパティ | 型 | 必須 | デフォルト値 | 説明 |
|-----------|----|------|------------|------|
| `text` | string | はい | - | 表示するテキスト |

**例**
```json
{
  "id": "message_label",
  "type": "label",
  "x": 20,
  "y": 30,
  "width": 200,
  "height": 20,
  "text": "こんにちは、世界！",
  "color": 7
}
```

### テキスト入力 (textinput)

ユーザーがテキストを入力できるコントロールです。

**プロパティ**

| プロパティ | 型 | 必須 | デフォルト値 | 説明 |
|-----------|----|------|------------|------|
| `text` | string | いいえ | `""` | 初期テキスト |
| `max_length` | number | いいえ | `32` | 最大文字数 |
| `is_password` | boolean | いいえ | `false` | パスワード入力モード |

**イベント**
- `change`: テキストが変更されたときに発生
- `enter`: Enterキーが押されたときに発生
- `focus`: フォーカスが当たったときに発生
- `blur`: フォーカスが外れたときに発生

**例**
```json
{
  "id": "username_input",
  "type": "textinput",
  "x": 20,
  "y": 50,
  "width": 150,
  "height": 20,
  "text": "",
  "max_length": 20,
  "events": ["change", "enter"]
}
```

### ファイルリスト (filelist)

ファイルの一覧を表示・選択するコントロールです。

**プロパティ**

| プロパティ | 型 | 必須 | デフォルト値 | 説明 |
|-----------|----|------|------------|------|
| `directory` | string | いいえ | `"./"` | 表示するディレクトリパス |
| `file_pattern` | string | いいえ | `"*.*"` | 表示するファイルのパターン |
| `show_details` | boolean | いいえ | `true` | 詳細情報を表示するか |

**イベント**
- `selection_changed`: 選択が変更されたときに発生
- `file_double_clicked`: ファイルがダブルクリックされたときに発生

**例**
```json
{
  "id": "file_list",
  "type": "filelist",
  "x": 10,
  "y": 30,
  "width": 250,
  "height": 180,
  "file_pattern": "*.csv",
  "directory": "./",
  "show_details": true,
  "events": ["selection_changed", "file_double_clicked"]
}
```

## イベント

コントロールは、様々なイベントを発行・購読できます。イベントを購読するには、`events` 配列にイベント名を追加します。

**イベントの購読例**
```json
{
  "id": "my_button",
  "type": "button",
  // ... その他のプロパティ ...
  "events": ["click", "mouse_enter", "mouse_leave"]
}
```

**主なイベント一覧**
- `click`: クリック時
- `mouse_enter`: マウスが入ったとき
- `mouse_leave`: マウスが出たとき
- `change`: 値が変更されたとき
- `focus`: フォーカスが当たったとき
- `blur`: フォーカスが外れたとき
- `enter`: Enterキーが押されたとき
- `selection_changed`: 選択が変更されたとき
- `file_double_clicked`: ファイルがダブルクリックされたとき

## 実装例

### 確認ダイアログ

```json
{
  "title": "確認",
  "width": 250,
  "height": 120,
  "controls": [
    {
      "id": "message_label",
      "type": "label",
      "x": 20,
      "y": 30,
      "width": 210,
      "height": 20,
      "text": "本当に実行しますか？",
      "color": 7
    },
    {
      "id": "ok_button",
      "type": "button",
      "x": 50,
      "y": 70,
      "width": 60,
      "height": 25,
      "text": "OK",
      "color": 7,
      "bg_color": 11,
      "hover_color": 3,
      "events": ["click"]
    },
    {
      "id": "cancel_button",
      "type": "button",
      "x": 140,
      "y": 70,
      "width": 60,
      "height": 25,
      "text": "キャンセル",
      "color": 7,
      "bg_color": 8,
      "hover_color": 2,
      "events": ["click"]
    }
  ]
}
```

### ファイル読み込みダイアログ

```json
{
  "title": "ファイルを開く",
  "width": 350,
  "height": 280,
  "controls": [
    {
      "id": "file_list",
      "type": "filelist",
      "x": 10,
      "y": 30,
      "width": 250,
      "height": 180,
      "file_pattern": "*.csv",
      "directory": "./",
      "show_details": true,
      "events": ["selection_changed", "file_double_clicked"]
    },
    {
      "id": "file_info",
      "type": "label",
      "x": 270,
      "y": 30,
      "width": 70,
      "height": 100,
      "text": "ファイルを選択してください",
      "color": 7
    },
    {
      "id": "load_button",
      "type": "button",
      "x": 270,
      "y": 150,
      "width": 70,
      "height": 25,
      "text": "開く",
      "color": 7,
      "bg_color": 11,
      "events": ["click"]
    },
    {
      "id": "cancel_button",
      "type": "button",
      "x": 270,
      "y": 185,
      "width": 70,
      "height": 25,
      "text": "キャンセル",
      "color": 7,
      "bg_color": 8,
      "events": ["click"]
    },
    {
      "id": "refresh_button",
      "type": "button",
      "x": 10,
      "y": 220,
      "width": 60,
      "height": 25,
      "text": "更新",
      "color": 7,
      "bg_color": 5,
      "events": ["click"]
    },
    {
      "id": "status_label",
      "type": "label",
      "x": 80,
      "y": 225,
      "width": 180,
      "height": 15,
      "text": "ファイルを選択してください",
      "color": 7
    }
  ]
}
```

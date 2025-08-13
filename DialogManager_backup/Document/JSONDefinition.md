# JSON 定義リファレンス

このドキュメントでは、DialogManager で使用するJSON定義の仕様について説明します。

## 目次
- [基本構造](#基本構造)
- [プロパティリファレンス](#プロパティリファレンス)
  - [共通プロパティ](#共通プロパティ)
  - [スタイルプロパティ](#スタイルプロパティ)
- [コントロールリファレンス](#コントロールリファレンス)
  - [ダイアログ](#ダイアログ)
  - [ボタン (button)](#ボタン-button)
  - [ラベル (label)](#ラベル-label)
  - [テキスト入力 (textinput)](#テキスト入力-textinput)
  - [ファイルリスト (filelist)](#ファイルリスト-filelist)
  - [チェックボックス (checkbox)](#チェックボックス-checkbox)
  - [ラジオボタン (radio)](#ラジオボタン-radio)
  - [コンボボックス (combobox)](#コンボボックス-combobox)
- [イベントシステム](#イベントシステム)
- [バリデーションルール](#バリデーションルール)
- [実装例](#実装例)
- [ベストプラクティス](#ベストプラクティス)
- [トラブルシューティング](#トラブルシューティング)
- [付録: 色コード一覧](#付録色コード一覧)

## 基本構造

DialogManagerのJSON定義は、宣言的なUI定義を可能にします。以下に基本的な構造を示します：

```json
{
  "title": "アプリケーション設定",
  "width": 500,
  "height": 400,
  "modal": true,
  "theme": "light",
  "styles": {
    "default": {
      "font_size": 12,
      "font_color": 7,
      "bg_color": 0,
      "border_color": 7,
      "border_width": 1
    },
    "primary_button": {
      "bg_color": 12,
      "font_color": 7,
      "hover_color": 9
    }
  },
  "controls": [
    // コントロール定義の配列
  ],
  "event_handlers": {
    "onLoad": "function() { console.log('Dialog loaded'); }",
    "onClose": "function() { console.log('Dialog closing'); }"
  },
  "data": {
    // アプリケーションで使用するデータ
  }
}
```

## プロパティリファレンス

### 共通プロパティ

すべてのコントロールで使用できる共通のプロパティです。

| プロパティ | 型 | 必須 | デフォルト | 説明 |
|------------|--------|------|------------|------|
| id | string | はい | - | コントロールの一意識別子 |
| type | string | はい | - | コントロールのタイプ (`button`, `label` など) |
| x | number | はい | - | 親コントロールからのX座標 |
| y | number | はい | - | 親コントロールからのY座標 |
| width | number | いいえ | 100 | コントロールの幅 |
| height | number | いいえ | 24 | コントロールの高さ |
| visible | boolean | いいえ | true | 表示/非表示 |
| enabled | boolean | いいえ | true | 有効/無効 |
| tooltip | string | いいえ | - | ホバー時のツールチップ |
| style | string/object | いいえ | - | スタイル名またはインラインスタイル |
| data_binding | string | いいえ | - | データバインディング式 |
| events | array | いいえ | [] | 購読するイベントのリスト |

### スタイルプロパティ

`style` オブジェクトで指定可能なプロパティ：

| プロパティ | 型 | デフォルト | 説明 |
|------------|--------|------------|------|
| font_size | number | 12 | フォントサイズ |
| font_bold | boolean | false | 太字 |
| font_color | number | 7 | テキスト色 (Pyxel色番号) |
| bg_color | number | 0 | 背景色 |
| border_width | number | 1 | 枠線の幅 |
| border_color | number | 7 | 枠線の色 |
| border_radius | number | 0 | 角丸の半径 |
| padding | number/object | 2 | パディング |
| margin | number/object | 0 | マージン |
| text_align | string | "left" | テキストの配置 (`left`, `center`, `right`) |
| opacity | number | 1.0 | 不透明度 (0.0 〜 1.0) |
| event_handlers | object | いいえ | {} | グローバルイベントハンドラー |

## コントロールリファレンス

### ダイアログ (dialog)

ダイアログはUIのルート要素で、他のすべてのコントロールを含むコンテナです。

**プロパティ**

| プロパティ | 型 | 必須 | デフォルト | 説明 |
|------------|--------|------|------------|------|
| title | string | はい | - | ダイアログのタイトル |
| width | number | はい | - | ダイアログの幅（ピクセル） |
| height | number | はい | - | ダイアログの高さ（ピクセル） |
| modal | boolean | いいえ | true | モーダルダイアログかどうか |
| resizable | boolean | いいえ | false | リサイズ可能かどうか |
| min_width | number | いいえ | 100 | 最小幅 |
| min_height | number | いいえ | 100 | 最小高さ |
| theme | string | いいえ | "light" | テーマ (`light` または `dark`) |
| styles | object | いいえ | {} | スタイル定義 |
| controls | array | はい | - | 子コントロールの配列 |
| event_handlers | object | いいえ | {} | グローバルイベントハンドラー |

**イベント**
- `onLoad`: ダイアログが読み込まれたときに発生
- `onShow`: ダイアログが表示されたときに発生
- `onHide`: ダイアログが非表示になったときに発生
- `onClose`: ダイアログが閉じられるときに発生
- `onResize`: ダイアログがリサイズされたときに発生

**例**
```json
{
  "title": "アプリケーション設定",
  "width": 600,
  "height": 400,
  "modal": true,
  "theme": "light",
  "styles": {
    "default": {
      "font_size": 12,
      "font_color": 7,
      "bg_color": 0,
      "border_color": 7
    },
    "primary_button": {
      "bg_color": 12,
      "font_color": 7,
      "hover_color": 9
    }
  },
  "controls": [
    // コントロール定義
  ],
  "event_handlers": {
    "onLoad": "function() { console.log('ダイアログが読み込まれました'); }"
  }
}
```

### ボタン (button)

クリック可能なボタンコントロールです。

**プロパティ**

| プロパティ | 型 | 必須 | デフォルト | 説明 |
|------------|--------|------|------------|------|
| text | string | はい | - | ボタンに表示するテキスト |
| icon | string | いいえ | - | アイコン名またはURL |
| hover_color | number | いいえ | 1 | ホバー時の色 |
| disabled_color | number | いいえ | 8 | 無効時の色 |
| text_align | string | いいえ | "center" | テキストの配置 (`left`, `center`, `right`) |
| shortcut | string | いいえ | - | ショートカットキー (例: "Ctrl+S") |

**イベント**
- `click`: ボタンがクリックされたときに発生
- `mouse_enter`: マウスが乗ったときに発生
- `mouse_leave`: マウスが離れたときに発生
- `focus`: フォーカスが当たったときに発生
- `blur`: フォーカスが外れたときに発生

**例**
```json
{
  "id": "save_btn",
  "type": "button",
  "x": 400,
  "y": 320,
  "width": 120,
  "height": 32,
  "text": "保存",
  "shortcut": "Ctrl+S",
  "style": {
    "bg_color": 11,
    "font_color": 7,
    "border_radius": 4,
    "padding": {"top": 4, "right": 12, "bottom": 4, "left": 12}
  },
  "events": ["click", "mouse_enter", "mouse_leave"]
}
```

### ラベル (label)

静的なテキストを表示するコントロールです。

**プロパティ**

| プロパティ | 型 | 必須 | デフォルト | 説明 |
|------------|--------|------|------------|------|
| text | string | はい | - | 表示するテキスト |
| text_align | string | いいえ | "left" | テキストの配置 (`left`, `center`, `right`, `justify`) |
| wrap | boolean | いいえ | true | テキストを折り返すかどうか |
| ellipsis | boolean | いいえ | true | はみ出たテキストを省略記号(...)で表示するか |

**イベント**
- `click`: ラベルがクリックされたときに発生
- `double_click`: ラベルがダブルクリックされたときに発生

**例**
```json
{
  "id": "title_label",
  "type": "label",
  "x": 20,
  "y": 20,
  "width": 200,
  "height": 24,
  "text": "アプリケーション設定",
  "style": {
    "font_size": 16,
    "font_bold": true,
    "font_color": 7
  }
}
```

### テキスト入力 (textinput)

1行のテキスト入力フィールドを提供します。

**プロパティ**

| プロパティ | 型 | 必須 | デフォルト | 説明 |
|------------|--------|------|------------|------|
| text | string | いいえ | "" | 初期テキスト |
| placeholder | string | いいえ | "" | プレースホルダーテキスト |
| max_length | number | いいえ | 256 | 最大入力文字数 |
| password | boolean | いいえ | false | パスワード入力モード |
| read_only | boolean | いいえ | false | 読み取り専用かどうか |
| numeric_only | boolean | いいえ | false | 数値のみ入力可能か |
| select_on_focus | boolean | いいえ | true | フォーカス時に全選択するか |
| validation | object | いいえ | - | バリデーションルール |

**バリデーションルール**

| プロパティ | 型 | デフォルト | 説明 |
|------------|--------|------------|------|
| required | boolean | false | 必須入力かどうか |
| min_length | number | 0 | 最小文字数 |
| max_length | number | 256 | 最大文字数 |
| pattern | string | - | 正規表現パターン |
| error_message | string | - | バリデーションエラーメッセージ |

**イベント**
- `change`: テキストが変更されたときに発生
- `focus`: フォーカスが当たったときに発生
- `blur`: フォーカスが外れたときに発生
- `key_down`: キーが押されたときに発生
- `key_up`: キーが離されたときに発生
- `enter`: Enterキーが押されたときに発生
- `validation`: バリデーション状態が変更されたときに発生

**例**
```json
{
  "id": "username_input",
  "type": "textinput",
  "x": 120,
  "y": 80,
  "width": 200,
  "height": 28,
  "placeholder": "ユーザー名を入力",
  "max_length": 32,
  "validation": {
    "required": true,
    "min_length": 3,
    "pattern": "^[a-zA-Z0-9_]+$",
    "error_message": "3文字以上の英数字で入力してください"
  },
  "style": {
    "border_width": 1,
    "border_color": 7,
    "padding": 4
  },
  "events": ["change", "focus", "blur", "enter"]
}
```

### ファイルリスト (filelist)

ファイルシステムのディレクトリ内容を表示・選択するためのコントロールです。

**プロパティ**

| プロパティ | 型 | 必須 | デフォルト | 説明 |
|------------|--------|------|------------|------|
| directory | string | いいえ | "./" | 表示するディレクトリパス |
| filter | string/array | いいえ | "*" | ファイルフィルタ (例: "*.csv" や ["*.csv", "*.txt"]) |
| show_hidden | boolean | いいえ | false | 隠しファイルを表示するか |
| show_parent | boolean | いいえ | true | 親ディレクトリへのリンクを表示するか |
| multi_select | boolean | いいえ | false | 複数選択を許可するか |
| sort_by | string | いいえ | "name" | ソート基準 (`name`, `size`, `modified`, `type`) |
| sort_asc | boolean | いいえ | true | 昇順でソートするか |

**メソッド**
- `refresh()`: ファイルリストを再読み込み
- `get_selected_files()`: 選択されたファイルの配列を返す
- `get_current_directory()`: 現在のディレクトリパスを返す
- `navigate_to(path)`: 指定したパスに移動

**イベント**
- `file_select`: ファイルが選択されたときに発生
- `directory_change`: ディレクトリが変更されたときに発生
- `file_double_click`: ファイルがダブルクリックされたときに発生
- `error`: エラーが発生したときに発生

**例**
```json
{
  "id": "file_list",
  "type": "filelist",
  "x": 20,
  "y": 60,
  "width": 360,
  "height": 200,
  "directory": "./saved",
  "filter": ["*.csv", "*.json"],
  "multi_select": false,
  "style": {
    "border_width": 1,
    "border_color": 7,
    "bg_color": 0,
    "selection_color": 5
  },
  "events": ["file_select", "directory_change", "file_double_click"]
}
```

## ダイアログの例

### ファイルを開くダイアログ

```json
{
  "title": "ファイルを開く",
  "width": 600,
  "height": 400,
  "modal": true,
  "styles": {
    "default": {
      "font_size": 12,
      "font_color": 7,
      "bg_color": 0,
      "border_color": 7
    },
    "button": {
      "bg_color": 11,
      "font_color": 7,
      "border_radius": 3,
      "padding": 4
    },
    "input": {
      "bg_color": 0,
      "font_color": 7,
      "border_width": 1,
      "border_color": 7,
      "padding": 4
    }
  },
  "controls": [
    {
      "id": "current_dir_label",
      "type": "label",
      "x": 20,
      "y": 20,
      "width": 560,
      "height": 20,
      "text": "現在のフォルダ: ./",
      "style": {
        "font_color": 7,
        "bg_color": 0
      }
    },
    {
      "id": "file_list",
      "type": "filelist",
      "x": 20,
      "y": 50,
      "width": 480,
      "height": 280,
      "directory": "./saved",
      "filter": ["*.csv", "*.json"],
      "style": {
        "border_width": 1,
        "border_color": 7,
        "bg_color": 0,
        "selection_color": 5
      },
      "events": ["file_select", "directory_change"]
    },
    {
      "id": "file_name_input",
      "type": "textinput",
      "x": 20,
      "y": 340,
      "width": 480,
      "height": 28,
      "placeholder": "ファイル名を入力または選択",
      "style": "input"
    },
    {
      "id": "open_btn",
      "type": "button",
      "x": 510,
      "y": 50,
      "width": 70,
      "height": 28,
      "text": "開く",
      "style": "button"
    },
    {
      "id": "cancel_btn",
      "type": "button",
      "x": 510,
      "y": 90,
      "width": 70,
      "height": 28,
      "text": "キャンセル",
      "style": "button"
    }
  ],
  "event_handlers": {
    "onLoad": "function() { console.log('ファイルダイアログが読み込まれました'); }"
  }
}
```
  "color": 7,
  "bg_color": 11,
  "hover_color": 3,
  "tooltip": "フォームを送信します",
  "events": ["click"],
  "style": {
    "border_radius": 4,
    "font_bold": true
  }
}
```

### ラベル (label)

テキストを表示する静的なコントロールです。

**プロパティ**

| プロパティ | 型 | 必須 | デフォルト | 説明 |
|------------|--------|------|------------|------|
| text | string | はい | - | 表示するテキスト |
| text_align | string | いいえ | "left" | テキストの配置 |
| word_wrap | boolean | いいえ | false | テキストの折り返し |
| selectable | boolean | いいえ | false | テキスト選択を有効にするか |

**イベント**
- `click`: ラベルがクリックされたときに発生

**例**
```json
{
  "id": "header_label",
  "type": "label",
  "x": 20,
  "y": 20,
  "width": 200,
  "height": 30,
  "text": "ユーザー設定",
  "color": 7,
  "style": {
    "font_size": 16,
    "font_bold": true
  },
  "events": ["click"]
}
```

### テキスト入力 (textinput)

ユーザーがテキストを入力できるコントロールです。

**プロパティ**

| プロパティ | 型 | 必須 | デフォルト | 説明 |
|------------|--------|------|------------|------|
| text | string | いいえ | "" | 初期テキスト |
| placeholder | string | いいえ | "" | プレースホルダーテキスト |
| max_length | number | いいえ | 256 | 最大文字数 |
| is_password | boolean | いいえ | false | パスワード入力モード |
| read_only | boolean | いいえ | false | 読み取り専用モード |
| multiline | boolean | いいえ | false | 複数行入力モード |
| numeric | boolean | いいえ | false | 数値入力モード |
| validation | object | いいえ | - | バリデーションルール |

**イベント**
- `change`: テキストが変更されたときに発生
- `input`: 入力中に発生
- `enter`: Enterキーが押されたときに発生
- `focus`: フォーカスが当たったときに発生
- `blur`: フォーカスが外れたときに発生
- `validation`: バリデーション状態が変わったときに発生

**例**
```json
{
  "id": "email_input",
  "type": "textinput",
  "x": 20,
  "y": 80,
  "width": 200,
  "height": 24,
  "placeholder": "メールアドレスを入力",
  "max_length": 100,
  "events": ["change", "blur"],
  "validation": {
    "required": true,
    "pattern": "^[^@]+@[^@]+\\.[^@]+$",
    "message": "有効なメールアドレスを入力してください"
  },
  "style": {
    "padding": 4,
    "border_width": 1,
    "border_color": 8
  }
}
```

### チェックボックス (checkbox)

オン/オフの状態を切り替えるチェックボックスコントロールです。

**プロパティ**

| プロパティ | 型 | 必須 | デフォルト | 説明 |
|------------|--------|------|------------|------|
| text | string | いいえ | "" | チェックボックスのラベル |
| checked | boolean | いいえ | false | 初期状態 |
| group | string | いいえ | - | グループ名（複数選択可能な場合） |
| tri_state | boolean | いいえ | false | 3状態（チェック/未チェック/不定）を許可するか |

**イベント**
- `change`: 状態が変更されたときに発生
- `click`: クリックされたときに発生

**例**
```json
{
  "id": "terms_agree",
  "type": "checkbox",
  "x": 20,
  "y": 150,
  "width": 200,
  "height": 20,
  "text": "利用規約に同意する",
  "checked": false,
  "events": ["change"],
  "style": {
    "font_color": 7,
    "check_color": 11
  }
}
```

### ラジオボタン (radio)

複数選択肢から1つを選択するラジオボタンコントロールです。

**プロパティ**

| プロパティ | 型 | 必須 | デフォルト | 説明 |
|------------|--------|------|------------|------|
| text | string | はい | - | ラジオボタンのラベル |
| value | string | いいえ | - | 選択時の値 |
| checked | boolean | いいえ | false | 初期状態 |
| group | string | はい | - | グループ名（同じグループ内で1つだけ選択可能） |

**イベント**
- `change`: 選択状態が変更されたときに発生
- `click`: クリックされたときに発生

**例**
```json
{
  "id": "gender_male",
  "type": "radio",
  "x": 20,
  "y": 180,
  "width": 100,
  "height": 20,
  "text": "男性",
  "value": "male",
  "group": "gender",
  "events": ["change"],
  "style": {
    "font_color": 7,
    "button_color": 11
  }
}
```

### コンボボックス (combobox)

ドロップダウンリストから選択するコントロールです。

**プロパティ**

| プロパティ | 型 | 必須 | デフォルト | 説明 |
|------------|--------|------|------------|------|
| items | array | はい | - | 選択肢の配列 |
| selected_index | number | いいえ | -1 | 選択されているインデックス |
| editable | boolean | いいえ | false | テキスト入力を許可するか |
| placeholder | string | いいえ | "" | 未選択時のプレースホルダーテキスト |
| max_dropdown_items | number | いいえ | 8 | ドロップダウンに表示する最大項目数 |

**メソッド**
- `addItem(text, value)`: 新しい項目を追加
- `removeItem(index)`: 指定したインデックスの項目を削除
- `clearItems()`: すべての項目をクリア
- `getSelectedItem()`: 選択されている項目を返す
- `setSelectedIndex(index)`: 選択されているインデックスを設定

**イベント**
- `change`: 選択が変更されたときに発生
- `dropdown_open`: ドロップダウンが開かれたときに発生
- `dropdown_close`: ドロップダウンが閉じられたときに発生

**例**
```json
{
  "id": "country_select",
  "type": "combobox",
  "x": 20,
  "y": 220,
  "width": 200,
  "height": 28,
  "items": [
    {"text": "日本", "value": "JP"},
    {"text": "アメリカ", "value": "US"},
    {"text": "イギリス", "value": "GB"},
    {"text": "ドイツ", "value": "DE"},
    {"text": "フランス", "value": "FR"}
  ],
  "placeholder": "国を選択",
  "selected_index": 0,
  "events": ["change"],
  "style": {
    "border_width": 1,
    "border_color": 7,
    "bg_color": 0,
    "arrow_color": 7,
    "dropdown_bg": 0,
    "hover_color": 1,
    "selection_color": 5
  }
}
```

### ファイルリスト (filelist)

ファイルシステムのディレクトリ内容を表示・選択するためのコントロールです。

**プロパティ**

| プロパティ | 型 | 必須 | デフォルト | 説明 |
|------------|--------|------|------------|------|
| directory | string | いいえ | "./" | 表示するディレクトリパス |
| file_pattern | string | いいえ | "*.*" | 表示するファイルのパターン |
| show_details | boolean | いいえ | true | 詳細情報を表示するか |
| show_hidden | boolean | いいえ | false | 隠しファイルを表示するか |
| multi_select | boolean | いいえ | false | 複数選択を有効にするか |
| sort_by | string | いいえ | "name" | ソート基準 ("name", "size", "modified") |
| sort_asc | boolean | いいえ | true | 昇順でソート |

**イベント**
- `selection_changed`: 選択が変更されたときに発生
- `file_double_clicked`: ファイルがダブルクリックされたときに発生
- `directory_changed`: ディレクトリが変更されたときに発生
- `file_loaded`: ファイルが読み込まれたときに発生

**例**
```json
{
  "id": "file_selector",
  "type": "filelist",
  "x": 20,
  "y": 60,
  "width": 300,
  "height": 200,
  "directory": "./data",
  "file_pattern": "*.{csv,json}",
  "show_details": true,
  "multi_select": false,
  "sort_by": "modified",
  "sort_asc": false,
  "events": ["selection_changed", "file_double_clicked"],
  "style": {
    "item_height": 20,
    "header_height": 24,
    "selection_color": 3
  }
}
```

## イベントシステム

DialogManagerのイベントシステムは、コントロール間の疎結合な通信を実現します。

### イベントの購読

イベントを購読するには、`events` 配列にイベント名を追加します。

```json
{
  "id": "save_button",
  "type": "button",
  "text": "保存",
  "events": ["click", "mouse_enter"]
}
```

### グローバルイベントハンドラー

ダイアログ全体で共通のイベントハンドラーを定義できます。

```json
{
  "title": "ユーザー設定",
  "width": 400,
  "height": 300,
  "event_handlers": {
    "onSave": "function(data) { console.log('保存しました', data); }"
  },
  "controls": [
    // コントロール定義
  ]
}
```

### 主なイベント一覧

#### マウスイベント
- `click`: クリック時
- `dblclick`: ダブルクリック時
- `mousedown`: マウスボタン押下時
- `mouseup`: マウスボタン解放時
- `mousemove`: マウス移動時
- `mouseenter`: マウスが要素に入った時
- `mouseleave`: マウスが要素から出た時

#### フォーカスイベント
- `focus`: フォーカス取得時
- `blur`: フォーカス喪失時

#### キーボードイベント
- `keydown`: キー押下時
- `keyup`: キー解放時
- `enter`: Enterキー押下時

#### 値変更イベント
- `change`: 値が変更された時
- `input`: 入力中
- `select`: テキスト選択時

#### ファイル関連イベント
- `file_selected`: ファイルが選択された時
- `file_loaded`: ファイルが読み込まれた時
- `directory_changed`: ディレクトリが変更された時

### カスタムイベント

独自のイベントを発行することもできます。

```javascript
// イベントの発行
dialog.trigger('custom_event', { data: 'カスタムデータ' });
```

## バリデーションルール

入力値の検証を行うためのルールを定義できます。

### バリデーションの定義

```json
{
  "id": "age_input",
  "type": "textinput",
  "validation": {
    "required": true,
    "min": 0,
    "max": 120,
    "pattern": "^\\d+$",
    "message": "0〜120の数値を入力してください"
  }
}
```

### バリデーションルール一覧

| ルール | 型 | 説明 |
|--------|------|------|
| required | boolean | 必須入力 |
| min | number | 最小値 |
| max | number | 最大値 |
| minLength | number | 最小文字数 |
| maxLength | number | 最大文字数 |
| pattern | string | 正規表現パターン |
| message | string | エラーメッセージ |
| validator | function | カスタムバリデーション関数 |

## 実装例

### ログインフォーム

```json
{
  "title": "ログイン",
  "width": 320,
  "height": 240,
  "controls": [
    {
      "id": "username_label",
      "type": "label",
      "x": 20,
      "y": 30,
      "width": 100,
      "height": 20,
      "text": "ユーザー名:"
    },
    {
      "id": "username_input",
      "type": "textinput",
      "x": 120,
      "y": 30,
      "width": 180,
      "height": 24,
      "placeholder": "ユーザー名を入力",
      "validation": {
        "required": true,
        "minLength": 3,
        "message": "3文字以上入力してください"
      }
    },
    {
      "id": "password_label",
      "type": "label",
      "x": 20,
      "y": 70,
      "width": 100,
      "height": 20,
      "text": "パスワード:"
    },
    {
      "id": "password_input",
      "type": "textinput",
      "x": 120,
      "y": 70,
      "width": 180,
      "height": 24,
      "is_password": true,
      "validation": {
        "required": true,
        "minLength": 6,
        "message": "6文字以上入力してください"
      }
    },
    {
      "id": "login_button",
      "type": "button",
      "x": 120,
      "y": 120,
      "width": 80,
      "height": 30,
      "text": "ログイン",
      "events": ["click"]
    }
  ]
}
```

## ベストプラクティス

1. **一貫したIDの命名規則を使用する**
   - 例: `userNameInput`, `saveButton`, `errorMessageLabel`

2. **イベントハンドラーは分離する**
   ```javascript
   // 推奨
   dialog.on('button_click', handleButtonClick);
   
   // 非推奨
   dialog.on('button_click', function() {
     // インライン関数は避ける
   });
   ```

3. **バリデーションはJSONで定義する**
   - バリデーションロジックをUIから分離
   - 再利用可能なバリデーションルールを作成

4. **スタイルは一箇所で管理する**
   - 共通のスタイルはテーマとして定義
   - 個別のスタイルは`style`プロパティで上書き

## トラブルシューティング

### イベントが発火しない
- `events`配列にイベント名が正しく指定されているか確認
- イベントハンドラーが正しく登録されているか確認
- コントロールが有効(`enabled: true`)になっているか確認

### スタイルが適用されない
- スタイルプロパティの名前が正しいか確認
- スタイルの優先順位を確認
- 親要素のスタイルを確認

### パフォーマンスが悪い
- 不要なイベントハンドラーを削除
- コントロールの再描画を最適化
- 大量のコントロールがある場合は仮想スクロールを検討
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

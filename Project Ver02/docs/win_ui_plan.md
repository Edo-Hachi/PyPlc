# PyxelベースWindowUIシステム実装プラン

# to Claude >> クラスファイル名、クラス名は「pyxdlg.py」pyxdlgクラスにしましょう
# 目的はウィンドウシステムというよりもっとコンパクトにダイアログボックスに絞りましょう

#xxx- `window_ui.py`: WindowUIシステム本体  これは却下！


## 概要
EDITモード拡張用のダイアログ、テキスト入力、ボタンコンポーネントを実装し、PyPlcプロジェクトにWindowUIシステムを統合する。

## 設計思想
- **軽量でサクサク動作**: Pyxelの60FPS描画を活用
- **JSON定義によるレイアウト分離**: プログラムとUIデザインの分離
- **再利用可能なコンポーネントライブラリ**: 汎用性重視
- **EDITモードでのデバイス設定ダイアログに特化**: 実用性重視

## アーキテクチャ設計

### 基本クラス構造

#### 1. BaseControl（抽象基底クラス）
- 全UIコントロールの共通機能
- 位置、サイズ、可視性、有効性管理
- イベントコールバックシステム
- マウス当たり判定
- 抽象メソッド: `update()`, `draw()`

#### 2. WindowManager
- ダイアログ・ウィンドウの管理システム
- モーダルダイアログ対応
- Z-order管理（最前面制御） : 
- 全体のイベント処理統合


---

# for Claude > 基本的には、入出力UIなので、モーダルダイアログで、常にメインウィンドウの上に表示されるイメージです。
入力文字列をを受け取って、OKを押されたら、return > OKフラグ(true)と、文字列を返す。Cancelを押されたら、カラの文字列とreturn > Cancelフラグ(false)をかえす 。こんな感じ

---

# for Claude なので基本このイメーじです。マルチウィンドウとかは考えなくても良いと思う  
#### 3. Dialog
- ダイアログウィンドウのコンテナ
- タイトルバー付きウィンドウ
- コントロールの配置・管理
- モーダル/非モーダル対応

### コントロール実装

#### Label
- テキスト表示専用
- カラー指定可能
- 動的テキスト変更対応

#### Button
- クリック可能ボタン
- ホバー・押下状態の視覚フィードバック
- 有効/無効状態対応
- イベントコールバック機能

#### TextInput
- テキスト入力フィールド
- 入力タイプ別バリデーション:
  - `TEXT`: 英数字入力
  - `NUMBER`: 数字のみ
  - `DEVICE_ADDRESS`: デバイスアドレス形式（X001, M100等）
- カーソル表示・移動
- フォーカス管理
- プレースホルダー対応

## 技術仕様


# >>For Claude :
# 色番号はpyxelで定義されている色名を使いましょう pyxel.COLOR_xxxxx となっています

### カラーパレット（Pyxel 16色）
```python
class UIColors:
    BACKGROUND = 1      # ダークグレー（ダイアログ背景）
    BORDER = 7          # ライトグレー（枠線）
    TEXT = 7           # ライトグレー（テキスト）
    BUTTON_NORMAL = 5   # ダークブルー（ボタン通常）
    BUTTON_HOVER = 12   # ライトブルー（ボタンホバー）
    BUTTON_PRESSED = 1  # ダークグレー（ボタン押下）
    INPUT_BG = 0       # 黒（入力フィールド背景）
    INPUT_FOCUS = 11   # ライトグリーン（フォーカス枠）
    ACCENT = 8         # 赤（アクセント色）
```

### イベントシステム
```python
class EventType(Enum):
    CLICK = "click"
    KEY_INPUT = "key_input"
    TEXT_CHANGE = "text_change"
    FOCUS_CHANGE = "focus_change"
```

### 入力タイプ
```python
class InputType(Enum):
    TEXT = "text"                    # 英数字
    NUMBER = "number"                # 数字のみ
    DEVICE_ADDRESS = "device_address" # デバイスアドレス（X001等）
```

## ファクトリー関数

### create_device_settings_dialog()
- デバイス設定用ダイアログ
- デバイスアドレス入力フィールド
- OK/Cancelボタン
- EDITモードでのデバイス配置後に使用

### create_number_input_dialog()
- 数値入力専用ダイアログ
- タイマー値、カウンター値設定用
- バリデーション付き数値入力

## PyPlcプロジェクト統合計画

### 1. モジュール追加
- `window_ui.py`: WindowUIシステム本体
- 既存の`main.py`に統合

# for Claude main.pyの中に書かず、独立したpyxdlg.pyを作ってください。


### 2. EDITモード拡張
- デバイス配置後のプロパティ設定ダイアログ
- TABキーでEDIT/RUNモード切り替え
- ENTERキーでデバイス設定ダイアログ表示

### 3. 使用シナリオ
1. EDITモードでデバイス配置
2. ENTERキー押下でデバイス設定ダイアログ表示
3. デバイスアドレス入力（X001, M100等）
4. OKクリックで設定適用、Cancelで取り消し
5. TABキーでRUNモードに切り替え
6. 設定されたデバイスでのシミュレーション実行

## 実装順序

### Phase 1: 基本フレームワーク
1. ✅ WindowUIシステムの基本アーキテクチャ設計
2. BaseControlクラスとWindowManagerクラス実装
3. 基本コントロール（Button, TextInput, Label）実装

### Phase 2: 統合システム
4. JSON定義システム実装
5. イベント処理とフォーカス管理システム実装

### Phase 3: EDITモード統合
6. EDITモード用ダイアログの統合テスト
7. PyPlc main.pyとの統合
8. 実際のデバイス設定ワークフローテスト

## JSON定義システム（将来拡張）

### 基本構造例
```json
{
  "dialogs": [
    {
      "id": "device_settings",
      "title": "Device Settings",
      "x": 100, "y": 100, "w": 200, "h": 150,
      "controls": [
        {
          "type": "label",
          "id": "addr_label",
          "x": 10, "y": 20,
          "text": "Device Address:"
        },
        {
          "type": "textinput",
          "id": "addr_input",
          "x": 10, "y": 35, "w": 120, "h": 20,
          "input_type": "device_address",
          "placeholder": "X001"
        },
        {
          "type": "button",
          "id": "ok_btn",
          "x": 50, "y": 110, "w": 40, "h": 25,
          "text": "OK",
          "action": "submit"
        }
      ]
    }
  ]
}
```

## メリット・特徴

### 技術的メリット
1. **環境構築不要**: Pyxel標準機能のみ使用
2. **高速動作**: ゲームエンジンベースの60FPS描画
3. **軽量実装**: 最小限のコードでUI機能実現
4. **配布容易**: 実行ファイル化が簡単

### 機能的メリット
1. **柔軟なレイアウト**: JSON編集で簡単UI変更
2. **型安全な入力**: 入力タイプ別バリデーション
3. **直感的操作**: WindowsライクなUI操作
4. **拡張性**: 新コントロール追加が容易

### PyPlc統合メリット
1. **EDITモード強化**: デバイス設定の直感化
2. **ユーザビリティ向上**: GUI操作による使いやすさ
3. **実用性向上**: 実際のPLC開発環境に近い操作感
4. **保守性向上**: UI部分の独立したメンテナンス

## 今後の拡張可能性

### 追加コントロール
- Checkbox: チェックボックス
- RadioButton: ラジオボタン（グループ対応）
- DropdownList: ドロップダウンリスト
- Slider: 数値調整スライダー
- ProgressBar: 進捗表示

### 高度な機能
- タブ切り替えダイアログ
- スクロール可能パネル
- ツールチップ表示
- キーボードショートカット

### PyPlc特化機能
- ラダー図エクスポートダイアログ
- デバイスリスト表示パネル
- 回路保存・読み込みダイアログ
- エラー表示ダイアログ

---

**実装準備完了**: 設計仕様確定、コード実装待機中  
**次ステップ**: window_ui.py実装とmain.py統合  
**目標**: EDITモードでの直感的デバイス設定システム実現
# DialogManager v2 API リファレンス

## 📚 DialogManager クラス

### コンストラクタ
```python
DialogManager()
```
DialogManagerの新しいインスタンスを作成します。

### メソッド

#### show_device_edit_dialog()
```python
show_device_edit_dialog(
    device,
    row: int,
    col: int,
    background_draw_func: Callable[[], None],
    grid_system
) -> None
```
デバイス編集ダイアログを表示します。

**パラメータ:**
- `device`: 編集対象デバイス
- `row`: グリッド行座標
- `col`: グリッド列座標  
- `background_draw_func`: バックグラウンド描画関数
- `grid_system`: グリッドシステムインスタンス

**使用例:**
```python
dialog_manager = DialogManager()
dialog_manager.show_device_edit_dialog(device, 5, 10, draw_bg, grid)
```

#### validate_device_for_id_edit()
```python
validate_device_for_id_edit(device) -> bool
```
デバイスがID編集対象かどうかを検証します。

**パラメータ:**
- `device`: 検証対象デバイス

**戻り値:**
- `bool`: ID編集可能な場合True

#### generate_default_device_id()
```python
generate_default_device_id(
    device_type: DeviceType, 
    row: int, 
    col: int
) -> str
```
デバイスタイプに応じたデフォルトIDを生成します。

**パラメータ:**
- `device_type`: デバイスタイプ
- `row`: グリッド行座標
- `col`: グリッド列座標

**戻り値:**
- `str`: デフォルトID

## 📚 BaseDialog クラス

### コンストラクタ
```python
BaseDialog(title: str = "", width: int = 200, height: int = 150)
```
基底ダイアログクラスの新しいインスタンスを作成します。

**パラメータ:**
- `title`: ダイアログタイトル
- `width`: ダイアログ幅
- `height`: ダイアログ高さ

### メソッド

#### show()
```python
show() -> Any
```
ダイアログをモーダル表示します。

**戻り値:**
- `Any`: ダイアログの結果

#### close()
```python
close(result: Any = None) -> None
```
ダイアログを終了します。

**パラメータ:**
- `result`: ダイアログの結果

#### add_control()
```python
add_control(control_id: str, control: Any) -> None
```
コントロールを追加します。

**パラメータ:**
- `control_id`: コントロールID
- `control`: コントロールオブジェクト

#### emit()
```python
emit(event_name: str, *args, **kwargs) -> None
```
イベントを発火します。

**パラメータ:**
- `event_name`: イベント名
- `*args`: イベント引数
- `**kwargs`: イベントキーワード引数

## 📚 ControlFactory クラス

### コンストラクタ
```python
ControlFactory()
```
コントロールファクトリの新しいインスタンスを作成します。

### メソッド

#### create_control()
```python
create_control(definition: Dict[str, Any]) -> BaseControl
```
JSON定義からコントロールを生成します。

**パラメータ:**
- `definition`: コントロール定義辞書

**戻り値:**
- `BaseControl`: 生成されたコントロール

**使用例:**
```python
factory = ControlFactory()
button_def = {
    "id": "ok_button",
    "type": "button",
    "x": 10, "y": 20,
    "width": 60, "height": 20,
    "text": "OK"
}
button = factory.create_control(button_def)
```

## 📚 JSONDialogLoader クラス

### コンストラクタ
```python
JSONDialogLoader(
    definitions_path: str = "DialogManager/definitions",
    enable_validation: bool = True
)
```
JSON定義ローダーの新しいインスタンスを作成します。

**パラメータ:**
- `definitions_path`: 定義ファイルのパス
- `enable_validation`: バリデーション有効化フラグ

### メソッド

#### load_dialog_definition()
```python
load_dialog_definition(filename: str) -> Optional[Dict[str, Any]]
```
ダイアログ定義を読み込みます。

**パラメータ:**
- `filename`: 定義ファイル名

**戻り値:**
- `Optional[Dict[str, Any]]`: 読み込まれた定義、失敗時はNone

## 📚 データレジスタダイアログ

### DataRegisterDialog クラス

#### コンストラクタ
```python
DataRegisterDialog(address: str = "", value: int = 0)
```
データレジスタ設定ダイアログを作成します。

**パラメータ:**
- `address`: 初期アドレス
- `value`: 初期値

#### メソッド

##### get_result()
```python
get_result() -> Optional[Dict[str, Any]]
```
ダイアログの結果を取得します。

**戻り値:**
- `Optional[Dict[str, Any]]`: 確定された場合は{"address": str, "value": int}、キャンセル時はNone

**使用例:**
```python
dialog = DataRegisterDialog("D1", 100)
dialog.show()
result = dialog.get_result()
if result:
    print(f"Address: {result['address']}, Value: {result['value']}")
```

## 📚 デバイスIDダイアログ

### show_device_id_dialog()
```python
show_device_id_dialog(
    device_type: DeviceType, 
    current_id: str
) -> Tuple[bool, Optional[str]]
```
デバイスID編集ダイアログを表示します。

**パラメータ:**
- `device_type`: デバイスタイプ
- `current_id`: 現在のID

**戻り値:**
- `Tuple[bool, Optional[str]]`: (成功フラグ, 新しいID)

**使用例:**
```python
success, new_id = show_device_id_dialog(DeviceType.CONTACT_A, "X001")
if success:
    print(f"New ID: {new_id}")
```

## 📚 ファイルダイアログ

### FileLoadDialogJSON クラス

#### show_load_dialog()
```python
show_load_dialog() -> Tuple[bool, Optional[str]]
```
ファイル読み込みダイアログを表示します。

**戻り値:**
- `Tuple[bool, Optional[str]]`: (成功フラグ, ファイルパス)

### FileSaveDialogJSON クラス

#### show_save_dialog()
```python
show_save_dialog() -> Tuple[bool, Optional[str]]
```
ファイル保存ダイアログを表示します。

**戻り値:**
- `Tuple[bool, Optional[str]]`: (成功フラグ, ファイルパス)

## 🏷️ エラーハンドリング

### 例外タイプ

#### DialogError
```python
class DialogError(Exception):
    """ダイアログ関連のエラー"""
    pass
```

#### ValidationError
```python
class ValidationError(DialogError):
    """バリデーションエラー"""
    pass
```

#### JSONLoadError
```python
class JSONLoadError(DialogError):
    """JSON読み込みエラー"""
    pass
```

### エラーハンドリングの例
```python
try:
    dialog = DataRegisterDialog()
    dialog.show()
except ValidationError as e:
    print(f"入力検証エラー: {e}")
except JSONLoadError as e:
    print(f"JSON読み込みエラー: {e}")
except DialogError as e:
    print(f"ダイアログエラー: {e}")
```

## 🔧 設定とカスタマイズ

### JSON定義ファイルの構造

#### ダイアログ定義
```json
{
    "$schema": "./schemas/dialog_base_schema.json",
    "title": "ダイアログタイトル",
    "width": 250,
    "height": 180,
    "controls": [
        {
            "id": "control_id",
            "type": "button|label|textinput",
            "x": 10, "y": 20,
            "width": 100, "height": 20,
            "text": "テキスト",
            "events": ["click", "change"]
        }
    ]
}
```

#### バリデーション設定
```json
{
    "validation": {
        "type": "required_data_register",
        "min": 0,
        "max": 255,
        "pattern": "^D\\d{1,3}$"
    }
}
```

---

**DialogManager v2** - 包括的なAPI リファレンス
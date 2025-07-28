# PyPlc システム・クラス構造ドキュメント

## 📊 システム全体のアーキテクチャ

PyPlcプロジェクトは、**2つの並行するシステム**で構成されています：

1. **グリッドベースシステム** (`grid_system.py`) - 視覚的な配置管理
2. **従来PLCロジックシステム** (`plc_logic.py`) - 論理演算処理

## 🎯 1. グリッドベースシステム

### GridDevice クラス
**役割**: グリッド上に配置される個々のデバイスを表現

**データ構造**:
```python
class GridDevice:
    # 基本情報
    device_type: DeviceType     # デバイスタイプ（TYPE_A, COIL等）
    grid_x, grid_y: int        # グリッド座標
    device_address: str        # デバイスアドレス（X001, Y001等）
    
    # 共通状態
    active: bool               # 動作状態（通電状態）
    
    # デバイス固有状態
    timer_preset: float        # タイマープリセット値
    timer_current: float       # タイマー現在値
    timer_state: str          # "STANBY"/"CNTUP"/"ON"
    counter_preset: int       # カウンタープリセット値
    counter_current: int      # カウンター現在値
    counter_state: str        # "OFF"/"ON"
    
    # 電気的状態
    contact_state: bool       # 接点状態（A/B接点用）
    coil_energized: bool      # コイル励磁状態
    wire_energized: bool      # ワイヤー通電状態
    
    # バスバー・配線専用
    busbar_direction: BusbarDirection  # 接続方向
    wire_direction: str       # ワイヤー方向（"H": 水平, "V": 垂直）
    connected_devices: List   # 接続デバイスリスト
```

**主要メソッド**:
- `get_sprite_name()`: デバイス状態に応じた表示スプライトを決定
- `update_state()`: PLCデバイスマネージャーとの状態同期

**動作ロジック**:
```python
def get_sprite_name(self) -> Optional[str]:
    """デバイスタイプと状態に応じたスプライト名を返す"""
    if self.device_type == DeviceType.TYPE_A:
        return "TYPE_A_ON" if self.active else "TYPE_A_OFF"
    elif self.device_type == DeviceType.COIL:
        return "OUTCOIL_NML_ON" if self.coil_energized else "OUTCOIL_NML_OFF"
    # その他のデバイスタイプ処理...
```

### GridDeviceManager クラス
**役割**: 10×10グリッド上のデバイス配置を管理

**データ構造**:
```python
class GridDeviceManager:
    grid_cols: int = 10           # グリッド列数
    grid_rows: int = 10           # グリッド行数
    grid: List[List[GridDevice]]  # 2次元配列でデバイス管理
```

**主要メソッド**:
- `place_device(grid_x, grid_y, device_type, device_address)`: 指定位置にデバイス配置
- `get_device(grid_x, grid_y)`: 座標からデバイス取得
- `remove_device(grid_x, grid_y)`: デバイス削除
- `update_all_devices(device_manager)`: 全デバイス状態更新
- `reset_all_devices()`: 全デバイス初期化
- `find_devices_by_address(device_address)`: アドレスでデバイス検索
- `get_coil_relationships(device_address)`: コイル間の連動関係取得

**特殊機能**:
- **デバイス検索**: 同一アドレスのデバイスをタイプ別に分類
- **コイル連動**: Input Coil → Output Coil/Reverse Coil の連動管理
- **状態同期**: PLCロジックシステムとの双方向同期

## 🔧 2. 従来PLCロジックシステム

### PLCDevice クラス
**役割**: 実際のPLCデバイス（X, Y, M, T, C）を表現

**データ構造**:
```python
class PLCDevice:
    address: str          # デバイスアドレス（例: "X001", "Y001"）
    device_type: str      # デバイスタイプ（'X', 'Y', 'M', 'T', 'C'）
    value: bool/int       # デバイス値
    
    # タイマー/カウンター専用フィールド
    preset_value: int     # プリセット値
    current_value: int    # 現在値
    coil_state: bool      # コイル状態
```

**初期化ロジック**:
```python
def __init__(self, address: str, device_type: str):
    if device_type in ['X', 'Y', 'M']:
        self.value = False  # 接点・コイル系はブール値
    elif device_type in ['T', 'C']:
        self.value = 0      # タイマー・カウンター系は数値
        self.preset_value = 0
        self.current_value = 0
        self.coil_state = False
```

### DeviceManager クラス
**役割**: PLCデバイスの集中管理

**データ構造**:
```python
class DeviceManager:
    devices: Dict[str, PLCDevice]  # アドレスをキーとした辞書管理
```

**主要メソッド**:
- `get_device(address)`: デバイス取得（存在しない場合は自動作成）
- `set_device_value(address, value)`: デバイス値設定
- `reset_all_devices()`: 全デバイス初期化

**動作ロジック**:
```python
def get_device(self, address: str) -> PLCDevice:
    """デバイスを取得（存在しない場合は作成）"""
    if address not in self.devices:
        device_type = address[0]  # アドレスの最初の文字でタイプ判定
        self.devices[address] = PLCDevice(address, device_type)
    return self.devices[address]
```

### LogicElement 階層
**役割**: ラダー図の論理素子を表現

**クラス階層**:
```
LogicElement (抽象基底クラス)
├── ContactA (A接点 - ノーマルオープン)
├── ContactB (B接点 - ノーマルクローズ)  
├── Coil (出力コイル)
├── Timer (タイマー - TON)
└── Counter (カウンター - CTU)
```

**共通データ構造**:
```python
class LogicElement(ABC):
    inputs: List[LogicElement]  # 入力素子リスト
    device_address: str         # 関連デバイスアドレス
    last_result: bool          # 最後の演算結果
    
    @abstractmethod
    def evaluate(self, device_manager: DeviceManager) -> bool:
        """論理演算を実行"""
        pass
```

**各素子の動作**:

#### ContactA (A接点)
```python
def evaluate(self, device_manager: DeviceManager) -> bool:
    device = device_manager.get_device(self.device_address)
    return bool(device.value)  # デバイス値がTrueなら通電
```

#### ContactB (B接点)
```python
def evaluate(self, device_manager: DeviceManager) -> bool:
    device = device_manager.get_device(self.device_address)
    return not bool(device.value)  # デバイス値がFalseなら通電
```

#### Timer (タイマー)
```python
def evaluate(self, device_manager: DeviceManager) -> bool:
    input_state = self.inputs[0].evaluate(device_manager)
    
    if input_state and not self.is_timing:
        self.start_time = time.time()  # タイマー開始
        self.is_timing = True
    elif not input_state:
        self.is_timing = False  # タイマーリセット
    
    if self.is_timing:
        elapsed = time.time() - self.start_time
        return elapsed >= self.preset_time  # プリセット時間到達でON
```

## ⚡ 3. 電力フロー管理システム

### LadderRung クラス（electrical_system.py）
**役割**: ラダー図の1行（ラング）の電気的継続性を管理

**データ構造**:
```python
class LadderRung:
    grid_y: int                         # 行番号
    grid_cols: int                      # 列数
    grid_manager: GridDeviceManager     # グリッドマネージャー参照
    devices: List[Tuple]                # (位置, デバイス)のリスト
    power_segments: List                # 電力セグメント
    left_bus_connection: BusConnection  # 左バスバー接続
    right_bus_connection: BusConnection # 右バスバー接続
    is_energized: bool                  # ライン通電状態
```

**主要メソッド**:
- `calculate_power_flow()`: 左から右への電力伝播計算
- `_process_grid_position()`: グリッド位置での電力処理
- `_process_powered_device()`: 通電時のデバイス処理
- `_process_contact_a/b()`: 接点処理
- `_process_load_device()`: 負荷デバイス処理
- `_process_wire()`: ワイヤー処理
- `_process_link_device()`: 縦方向結線デバイス処理

**電力フロー計算ロジック**:
```python
def calculate_power_flow(self) -> bool:
    """左から右への電力フロー計算"""
    power = self.left_bus_connection.is_energized
    self._reset_device_states()
    
    # 左から右へ電力伝播を計算
    for i in range(self.grid_cols):
        device = self.grid_manager.get_device(i, self.grid_y)
        power = self._process_grid_position(i, device, power)
    
    self.is_energized = power
    return power
```

### ElectricalSystem クラス
**役割**: ラダー図全体の電気系統を管理

**データ構造**:
```python
class ElectricalSystem:
    grid_manager: GridDeviceManager     # グリッドマネージャー参照
    rungs: Dict[int, LadderRung]        # 行番号→ラングのマッピング
    vertical_connections: Dict          # 縦方向結線管理
    topology_manager: CircuitTopologyManager  # 回路トポロジー管理
```

**主要メソッド**:
- `update_electrical_state()`: 全体の電気状態を更新
- `get_or_create_rung(grid_y)`: 指定行のラング取得/作成
- `get_wire_color(grid_x, grid_y)`: 配線色取得
- `synchronize_coil_to_device()`: コイル状態とデバイス同期
- `reset_electrical_state()`: 電気状態リセット

### BusConnection クラス
**役割**: バスバー接続点の管理

**データ構造**:
```python
class BusConnection:
    grid_x, grid_y: int       # バスバー座標
    is_energized: bool        # 通電状態
    connected_rungs: List     # 接続されているラング
    bus_type: str            # "LEFT"/"RIGHT"/"MIDDLE"
```

### VerticalConnection クラス
**役割**: 縦方向結線を管理

**データ構造**:
```python
class VerticalConnection:
    grid_x: int                    # X座標
    connection_points: List        # (grid_y, DeviceType)のリスト
    is_energized: bool            # 通電状態
```

**主要メソッド**:
- `add_connection_point()`: 結線点追加
- `remove_connection_point()`: 結線点削除
- `get_connected_pairs()`: 接続ペア取得

## 🔄 4. システム間の連携

### データフロー
```
1. ユーザー操作 → GridDeviceManager（デバイス配置）
2. GridDevice → ElectricalSystem（電力計算）
3. ElectricalSystem → DeviceManager（状態同期）
4. DeviceManager → GridDevice（表示更新）
```

### 状態同期メカニズム
1. **電力計算**: `ElectricalSystem`が各ラングの電力フローを計算
2. **状態更新**: 計算結果を`GridDevice`の`active`、`coil_energized`に反映
3. **PLC同期**: `DeviceManager`と`GridDevice`間で状態同期
4. **表示更新**: `GridDevice.get_sprite_name()`で適切なスプライト選択

### 同期処理の詳細
```python
# ElectricalSystem → GridDevice
def _process_load_device(self, grid_x: int, device, current_power: bool):
    device.active = True
    if device.device_type == DeviceType.COIL:
        device.coil_energized = True
    # 電力の流れは継続
    return current_power

# GridDevice → DeviceManager
def synchronize_coil_to_device(self, device_manager):
    for device in all_grid_devices:
        if device.device_type in COIL_TYPES and device.device_address:
            plc_device = device_manager.get_device(device.device_address)
            plc_device.value = device.coil_energized
```

## 🎮 5. 実行モードと動作

### EDITモード
- **デバイス配置・削除**: `GridDeviceManager.place_device()`
- **設定変更**: デバイス設定ダイアログ
- **回路構築**: ワイヤー配線、縦方向結線

### RUNモード  
- **電力フロー計算実行**: `ElectricalSystem.update_electrical_state()`
- **デバイス状態更新**: リアルタイム状態計算
- **リアルタイム表示更新**: スプライト切り替え

### モード切り替え処理
```python
def _handle_keyboard_input(self):
    if pyxel.btnp(pyxel.KEY_F5):
        if self.plc_run_state == PLCRunState.STOPPED:
            self.plc_run_state = PLCRunState.RUNNING
            # 左バスバー（電源）をONにする
            for rung in self.electrical_system.rungs.values():
                rung.left_bus_connection.is_energized = True
        else:
            self.plc_run_state = PLCRunState.STOPPED
            self._reset_all_systems()
```

## 📈 6. パフォーマンス特性

### 計算複雑度
- **グリッド走査**: O(rows × cols) = O(100)
- **電力計算**: O(devices_per_row × rows)
- **状態同期**: O(total_devices)
- **スプライト更新**: O(visible_devices)

### メモリ使用量
- **GridDevice**: 約100バイト/デバイス
- **PLCDevice**: 約50バイト/デバイス
- **LadderRung**: 約200バイト/ラング
- **総メモリ**: 約15KB（100デバイス想定）

### 最適化ポイント
- **差分更新**: 変更されたデバイスのみ処理
- **キャッシュ**: スプライト名、電力状態のキャッシュ
- **遅延評価**: 非表示領域の計算スキップ

## 🛠️ 7. 拡張性とカスタマイズ

### 新しいデバイスタイプの追加
1. `config.py`の`DeviceType`に追加
2. `GridDevice.get_sprite_name()`に処理追加
3. `ElectricalSystem`に電力処理ロジック追加
4. 対応するスプライト画像を追加

### カスタムロジック素子の追加
```python
class CustomLogicElement(LogicElement):
    def __init__(self, device_address: str, custom_param):
        super().__init__(device_address)
        self.custom_param = custom_param
    
    def evaluate(self, device_manager: DeviceManager) -> bool:
        # カスタムロジック実装
        return custom_logic_result
```

## 🔍 8. デバッグとトラブルシューティング

### ログシステム
```python
debug_logger = logging.getLogger('PyPlc_Debug')
debug_logger.debug(f"[Rung {self.grid_y}] Power flow: {power}")
```

### 状態確認メソッド
- `GridDevice.get_sprite_name()`: 現在の表示状態確認
- `ElectricalSystem.get_wire_color()`: 配線通電状態確認
- `DeviceManager.devices`: 全PLCデバイス状態確認

### よくある問題と解決策
1. **スプライト表示異常**: `get_sprite_name()`の条件分岐確認
2. **電力フロー異常**: `calculate_power_flow()`のデバッグログ確認
3. **状態同期異常**: `synchronize_coil_to_device()`の呼び出し確認

この設計により、視覚的なグリッド配置と論理的なPLC処理を分離しながら、リアルタイムな電力フロー表示を実現しています。各クラスは明確な責任を持ち、拡張性と保守性を両立した構造となっています。

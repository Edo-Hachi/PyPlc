# PyPlc-v2 Remake Plan / PyPlc-v2 再構築計画書

## 📖 Document Overview / 文書概要

**Purpose / 目的**: Complete redesign and implementation plan for PyPlc PLC simulator  
**対象**: PyPLCシミュレーターの完全再設計・実装計画

**Target Audience / 対象読者**: AI Assistant, Development Team  
**想定読者**: AIアシスタント、開発チーム

**Creation Date / 作成日**: 2025-01-27  
**Version / バージョン**: 2.0

---

## 🎯 Project Goals / プロジェクト目標

### Primary Objectives / 主要目標

1. **Simplification / シンプル化**
   - Reduce complexity from existing PyPlc codebase
   - 既存PyPlcコードベースの複雑性削減
   - Target: Main file under 200 lines / メインファイル200行以内

2. **Self-Holding Circuit Resolution / 自己保持回路問題解決**
   - Implement explicit wire objects for proper electrical continuity
   - 電気的継続性のための明示的配線オブジェクト実装
   - Reference: `SimIssue/PLC Sim Plan.txt` problem resolution

3. **Maintainable Architecture / 保守可能アーキテクチャ**
   - Clear separation of concerns
   - 明確な関心事の分離
   - Modular design with minimal dependencies / 最小依存性のモジュール設計

---

## 🏗️ System Architecture / システムアーキテクチャ

### Core Design Principles / 核となる設計原則

1. **10x10 Matrix Foundation / 10x10マトリックス基盤**
   ```
   GRID_ROW = 10  # Rows / 行
   GRID_COL = 10  # Columns / 列
   GridDeviceManager[Row][Col]  # Single 2D array management / 単一2次元配列管理
   ```
   将来的にはRow,Columnsは拡張される。可変になることを前提に設計を行う必要がある。

2. **Fixed Bus Rule / 固定バスルール**
   ```
   Col=0: L_Side (Power Bus) - Non-editable / 電源バス（編集不可）
   Col=9: R_Side (Neutral Bus) - Non-editable / ニュートラルバス（編集不可）
   Col=1-(R_Side-1): User editable area / ユーザー編集可能領域
   ```

3. **Bidirectional Link Structure / 双方向リンク構造**
   ```python
   class LogicElement:
       left_dev: str   # Left connected device ID / 左接続デバイスID
       right_dev: str  # Right connected device ID / 右接続デバイスID
   ```

### Three-Layer Architecture / 3層アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                 Presentation Layer / プレゼンテーション層        │
│  UIRenderer + InputHandler                                 │
│  - Grid rendering / グリッド描画                             │
│  - User interaction / ユーザーインタラクション                  │
└─────────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────────┐
│                   Business Layer / ビジネス層                │
│  GridDeviceManager + PowerFlowCalculator                   │
│  - Device management / デバイス管理                          │
│  - Electrical flow calculation / 電力フロー計算               │
└─────────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer / データ層                     │
│  LogicElement + CircuitSerializer                          │
│  - Device state / デバイス状態                               │
│  - File I/O / ファイル入出力                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Phases / 実装フェーズ

### Phase 1: Foundation System / 基盤システム (1-2 days)

**Objective / 目標**: Establish minimal working system / 最小動作システム確立

**Components / コンポーネント**:
- `LogicElement` base class / 基底クラス
- `GridDeviceManager` (10x10 matrix) / (10x10マトリックス) **将来的な拡張性を考慮。マトリックスサイズは柔軟に変更可能とする）
- Basic `DeviceType` definitions / 基本デバイスタイプ定義
- L_Side/R_Side automatic placement / L_Side/R_Side自動配置

**Success Criteria / 成功基準**:
- 10x10 grid display / 10x10グリッド表示 **将来的な拡張性を考慮。マトリックスサイズは柔軟に変更可能とする）
- Fixed L/R_Side display / L/R_Side固定表示
- Device placement with auto ID generation / 自動ID生成によるデバイス配置

### Phase 2: Basic Devices / 基本デバイス (2-3 days)

**Objective / 目標**: Implement core 3 devices / コア3デバイス実装

**Device Types / デバイスタイプ**:
```python
DeviceType = {
    "ContactA": "A接点（ノーマルオープン）",
    "OutCoilStd": "出力コイル（通常）", 
    "Line": "接続配線（水平）",
    "L_Side": "電源バス",
    "R_Side": "ニュートラルバス"
}
```

**Features / 機能**:
- Left-to-right power trace / 左から右への電力トレース
- Contact state-based conduction / 接点状態による通電制御
- Coil energization management / コイル励磁状態管理

**Success Criteria / 成功基準**:
- Simple AND circuit operation / 単純なAND回路動作
- Circuit: `[L_Side] → [ContactA] → [Line] → [OutCoil] → [R_Side]`

### Phase 3: Self-Holding Circuit / 自己保持回路 (2-3 days)

**Objective / 目標**: Implement explicit wiring for self-holding circuits / 自己保持回路用明示配線実装

**Solution Approach / 解決アプローチ**:
```
従来: [X001] (implicit) [Y01入力] (implicit) [Y01出力]
新方式: [X001]---[Line]---[Y01入力]---[Line]---[Y01出力]---[Line]---[X002]
```

**Components / コンポーネント**:
- Explicit "Line" device implementation / 明示的"Line"デバイス実装
- Vertical connection system (LineUp/LineDown) / 垂直結線システム
- Multi-path power flow calculation / 複数パス電力フロー計算
- Self-holding loop detection / 自己保持ループ検出

**Success Criteria / 成功基準**:
- `SimIssue/PLC Sim Plan.txt` self-holding circuit works correctly
- `SimIssue/PLC Sim Plan.txt`の自己保持回路が正常動作
- Y01 remains energized after X001 turns OFF
- X001がOFF後もY01が自己保持される

### Phase 4: UI/Operation System / UI・操作システム (1-2 days)

**Objective / 目標**: Intuitive editing and execution environment / 直感的編集・実行環境

**Features / 機能**:
- Edit mode: Device placement/deletion / 編集モード: デバイス配置・削除
- Run mode: Real-time simulation / 実行モード: リアルタイムシミュレーション
- Device state monitoring panel / デバイス状態監視パネル
- Power flow visualization / 電力フロー可視化

**Success Criteria / 成功基準**:
- Complete edit-run cycle / 完全な編集・実行サイクル
- Real-time circuit simulation / リアルタイム回路シミュレーション

### Phase 5: Extended Devices / 拡張デバイス (Optional)

**Additional Devices / 追加デバイス**:
- Timer (タイマー)
- Counter (カウンター)  
- ContactB (B接点)
- OutCoilRev (反転出力コイル)

---

## 🔧 Technical Specifications / 技術仕様

### File Structure / ファイル構成

```
PyPlc-v2/
├── main.py                    # Main coordinator (<200 lines) / メインコーディネーター（200行以内）
├── core/                      # Core domain layer / コアドメイン層
│   ├── logic_element.py       # Device base class / デバイス基底クラス
│   ├── grid_manager.py        # Grid management / グリッド管理
│   └── device_types.py        # Device type definitions / デバイスタイプ定義
├── devices/                   # Device implementation layer / デバイス実装層
│   ├── basic_devices.py       # Basic devices / 基本デバイス
│   └── advanced_devices.py    # Advanced devices / 高度デバイス
├── systems/                   # System layer / システム層
│   ├── power_flow.py          # Power flow calculation / 電力フロー計算
│   ├── ui_renderer.py         # UI rendering system / UI描画システム
│   └── input_handler.py       # Input processing / 入力処理
├── utils/                     # Utility layer / ユーティリティ層
│   ├── circuit_serializer.py  # File I/O / ファイル入出力
│   └── sprite_manager.py      # Sprite management / スプライト管理
└── config/                    # Configuration layer / 設定層
    ├── settings.py            # System settings / システム設定
    └── sprites.json           # Sprite definitions / スプライト定義
```

### Core Classes Specification / コアクラス仕様

#### LogicElement Base Class / LogicElement基底クラス

```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum

class DeviceState(Enum):
    OFF = False
    ON = True

class LogicElement(ABC):
    """Logic element base class for ladder diagram / ラダー図論理素子基底クラス"""
    
    def __init__(self, row: int, col: int, device_type: str):
        # Essential attributes / 必須属性
        self.id: str = self._generate_id(row, col)           # "007_005" format
        self.row: int = row                                  # Grid row / グリッド行
        self.col: int = col                                  # Grid column / グリッド列
        self.device_type: str = device_type                  # Device type / デバイスタイプ
        self.name: str = ""                                  # User name (X001, Y001) / ユーザー名
        
        # Connection info (bidirectional link) / 接続情報（双方向リンク）
        self.left_dev: Optional[str] = None                  # Left device ID / 左デバイスID
        self.right_dev: Optional[str] = None                 # Right device ID / 右デバイスID
        
        # State management / 状態管理
        self.now_state: DeviceState = DeviceState.OFF        # Current state / 現在状態
        self.input_state: DeviceState = DeviceState.OFF      # Input state / 入力状態
        self.output_state: DeviceState = DeviceState.OFF     # Output state / 出力状態
        
        # Metadata / メタデータ
        self.is_editable: bool = True                        # Editable flag / 編集可能フラグ
        
    def _generate_id(self, row: int, col: int) -> str:
        """Generate ID in "007_005" format / "007_005"形式でID生成"""
        return f"{row:03d}_{col:03d}"
    
    @abstractmethod
    def evaluate(self) -> DeviceState:
        """Device-specific logic operation / デバイス固有論理演算"""
        pass
    
    @abstractmethod
    def get_sprite_name(self) -> str:
        """Get sprite name based on current state / 現在状態に応じたスプライト名取得"""
        pass
    
    def can_conduct_power(self) -> bool:
        """Power conduction capability check / 電力通電可能性判定"""
        return self.evaluate() == DeviceState.ON
```

#### GridDeviceManager Specification / GridDeviceManager仕様

```python
class GridDeviceManager:
    """10x10 grid device management / 10x10グリッドデバイス管理"""  **将来的な拡張性を考慮。マトリックスサイズは柔軟に変更可能とする）
    
    def __init__(self):
        self.GRID_ROWS = 10
        self.GRID_COLS = 10
        self.grid: List[List[Optional[LogicElement]]] = self._initialize_grid()
        self.device_registry: Dict[str, LogicElement] = {}
        
    def _initialize_grid(self) -> List[List[Optional[LogicElement]]]:
        """Grid initialization with automatic L_Side/R_Side placement"""
        """L_Side/R_Side自動配置によるグリッド初期化"""
        grid = [[None for _ in range(self.GRID_COLS)] for _ in range(self.GRID_ROWS)]
        
        # Fixed bus placement / 固定バス配置
        for row in range(self.GRID_ROWS):
            # Left power bus / 左電源バス
            l_side = L_Side(row)
            grid[row][0] = l_side
            self.device_registry[l_side.id] = l_side
            
            # Right neutral bus / 右ニュートラルバス  **将来的な拡張性を考慮。マトリックスサイズは柔軟に変更可能とする）
            r_side = R_Side(row)
            grid[row][9] = r_side
            self.device_registry[r_side.id] = r_side
            
        return grid
    
    def place_device(self, row: int, col: int, device_type: str, 
                    device_name: str = "") -> bool:
        """Device placement / デバイス配置"""
        # Editable area check / 編集可能領域チェック
        if not self._is_editable_position(row, col):
            return False
            
        # Remove existing device / 既存デバイス削除
        if self.grid[row][col]:
            self.remove_device(row, col)
        
        # Create new device / 新デバイス作成
        device = self._create_device(row, col, device_type)
        if device:
            device.name = device_name
            self.grid[row][col] = device
            self.device_registry[device.id] = device
            self._update_links(device)
            return True
        return False
    
    def _is_editable_position(self, row: int, col: int) -> bool:
        """Editable position check / 編集可能位置判定"""
        return 0 <= row < self.GRID_ROWS and 1 <= col <= 8
```

#### PowerFlowCalculator Specification / PowerFlowCalculator仕様

```python
class PowerFlowCalculator:
    """Power flow calculation engine / 電力フロー計算エンジン"""
    
    def __init__(self, grid_manager: GridDeviceManager):
        self.grid_manager = grid_manager
        self.vertical_connections: Dict[int, List[int]] = {}  # col -> [rows]
    
    def calculate_system_power_flow(self, power_on: bool = True):
        """System-wide power flow calculation / システム全体電力フロー計算"""
        # 1. Set power bus state / 電源状態設定
        self._set_power_bus_state(power_on)
        
        # 2. Reset all device states / 全デバイス状態リセット
        self._reset_all_device_states()
        
        # 3. Calculate power flow by row / 行ごと電力フロー計算
        for row in range(self.grid_manager.GRID_ROWS):
            self._calculate_row_power_flow(row)
        
        # 4. Process vertical connections / 垂直接続処理
        self._process_vertical_connections()
    
    def _calculate_row_power_flow(self, row: int):
        """Row-based power flow calculation / 行単位電力フロー計算"""
        # Left-to-right power propagation / 左から右への電力伝播
        current_power = DeviceState.OFF
        
        for col in range(self.grid_manager.GRID_COLS):
            device = self.grid_manager.get_device(row, col)
            if device:
                # Set input state / 入力状態設定
                device.input_state = current_power
                
                # Execute device operation / デバイス演算実行
                device_output = device.evaluate()
                
                # Power propagation decision / 電力伝播判定
                if device.can_conduct_power():
                    current_power = device_output
                else:
                    current_power = DeviceState.OFF
```

---

## 🎮 Device Types Implementation / デバイスタイプ実装

### Basic Devices / 基本デバイス

#### ContactA (A接点 / Normally Open Contact)

```python
class ContactA(LogicElement):
    """A contact (Normally Open) / A接点（ノーマルオープン）"""
    
    def __init__(self, row: int, col: int):
        super().__init__(row, col, "ContactA")
        self.contact_state: DeviceState = DeviceState.OFF
    
    def evaluate(self) -> DeviceState:
        """A contact operation: Conducts when contact is ON / A接点動作: 接点ONで通電"""
        if self.contact_state == DeviceState.ON:
            self.output_state = self.input_state
        else:
            self.output_state = DeviceState.OFF
        return self.output_state
    
    def get_sprite_name(self) -> str:
        """Sprite name determination / スプライト名決定"""
        return "TYPE_A_ON" if self.contact_state == DeviceState.ON else "TYPE_A_OFF"
    
    def toggle_contact(self):
        """Manual contact operation / 接点手動操作"""
        self.contact_state = (DeviceState.ON if self.contact_state == DeviceState.OFF 
                             else DeviceState.OFF)
```

#### OutCoilStd (出力コイル / Output Coil Standard)

```python
class OutCoilStd(LogicElement):
    """Output coil (Standard) / 出力コイル（通常）"""
    
    def __init__(self, row: int, col: int):
        super().__init__(row, col, "OutCoilStd")
        self.coil_energized: bool = False
    
    def evaluate(self) -> DeviceState:
        """Coil operation: Pass input to output, update coil state"""
        """コイル動作: 入力を出力へ、コイル状態更新"""
        self.output_state = self.input_state
        self.coil_energized = (self.input_state == DeviceState.ON)
        
        # Sync to same address devices (Y001 coil → Y001 contact)
        # 同名デバイス同期（Y001コイル → Y001接点）
        self._sync_to_same_address_devices()
        
        return self.output_state
    
    def get_sprite_name(self) -> str:
        """Sprite name determination / スプライト名決定"""
        return "OUTCOIL_NML_ON" if self.coil_energized else "OUTCOIL_NML_OFF"
```

#### Line (水平配線 / Horizontal Wire)

```python
class Line(LogicElement):
    """Horizontal wire / 水平配線"""
    
    def __init__(self, row: int, col: int):
        super().__init__(row, col, "Line")
        self.wire_energized: bool = False
    
    def evaluate(self) -> DeviceState:
        """Wire operation: Pass input through / 配線動作: 入力をそのまま通す"""
        self.output_state = self.input_state
        self.wire_energized = (self.input_state == DeviceState.ON)
        return self.output_state
    
    def get_sprite_name(self) -> str:
        """Sprite name determination / スプライト名決定"""
        return "WIRE_H_ON" if self.wire_energized else "WIRE_H_OFF"
```

### Bus Devices / バスデバイス

#### L_Side (電源バス / Power Bus)

```python
class L_Side(LogicElement):
    """Left power bus / 左電源バス"""
    
    def __init__(self, row: int):
        super().__init__(row, 0, "L_Side")
        self.is_editable = False  # Non-editable / 編集不可
        self.is_powered = False
    
    def evaluate(self) -> DeviceState:
        """Power bus: Depends on power state / 電源バス: 電源状態に依存"""
        self.output_state = DeviceState.ON if self.is_powered else DeviceState.OFF
        return self.output_state
    
    def set_power(self, powered: bool):
        """Power ON/OFF / 電源ON/OFF"""
        self.is_powered = powered
```

#### R_Side (ニュートラルバス / Neutral Bus)

```python
class R_Side(LogicElement):
    """Right neutral bus / 右ニュートラルバス"""
    
    def __init__(self, row: int):
        super().__init__(row, 9, "R_Side")
        self.is_editable = False  # Non-editable / 編集不可
    
    def evaluate(self) -> DeviceState:
        """Neutral bus: Pass input through / ニュートラルバス: 入力をそのまま通す"""
        self.output_state = self.input_state
        return self.output_state
```

---

## 📊 Quality Assurance / 品質保証

### Testing Strategy / テスト戦略

#### Unit Tests / 単体テスト
```python
class TestLogicElement(unittest.TestCase):
    def test_contact_a_evaluate_on(self):
        """A contact: Conducts when input ON / A接点: 入力ONで通電"""
        contact = ContactA(1, 2)
        contact.contact_state = DeviceState.ON
        contact.input_state = DeviceState.ON
        
        result = contact.evaluate()
        
        self.assertEqual(result, DeviceState.ON)
        self.assertEqual(contact.output_state, DeviceState.ON)
```

#### Integration Tests / 統合テスト
```python
class TestCircuitIntegration(unittest.TestCase):
    def test_simple_and_circuit(self):
        """Simple AND circuit test / 簡単なAND回路テスト"""
        grid = GridDeviceManager()
        
        # Build circuit: L_Side → ContactA → Line → OutCoil → R_Side
        # 回路構築: L_Side → ContactA → Line → OutCoil → R_Side
        grid.place_device(0, 1, "ContactA", "X001")
        grid.place_device(0, 2, "Line")
        grid.place_device(0, 3, "OutCoilStd", "Y001")
        
        # Power calculation / 電力計算
        calc = PowerFlowCalculator(grid)
        calc.calculate_system_power_flow(power_on=True)
        
        # Turn X001 ON and verify result / X001をONにして結果確認
        x001 = grid.get_device(0, 1)
        x001.contact_state = DeviceState.ON
        calc.calculate_system_power_flow(power_on=True)
        
        y001 = grid.get_device(0, 3)
        self.assertTrue(y001.coil_energized)
```

### Performance Requirements / パフォーマンス要件

1. **Real-time Operation / リアルタイム動作**: 60 FPS stable / 60FPS安定
2. **Memory Efficiency / メモリ効率**: <15KB for 100 devices / 100デバイスで15KB以内
3. **Calculation Complexity / 計算複雑度**: O(rows × cols) = O(100)

### Success Criteria / 成功基準

#### Must-Have Requirements / 必須要件
- ✅ 10x10 grid basic device placement / 10x10グリッド基本デバイス配置
- ✅ Self-holding circuit correct operation / 自己保持回路正常動作
- ✅ Real-time power flow display / リアルタイム電力フロー表示
- ✅ Edit/Run mode separation / 編集・実行モード分離

#### Quality Requirements / 品質要件
- ✅ Main file under 200 lines / メインファイル200行以内
- ✅ Clear module responsibility separation / モジュール責任分離明確化
- ✅ 60FPS stable operation / 60FPS安定動作
- ✅ Intuitive UI operation / 直感的UI操作

#### Extensibility Requirements / 拡張性要件
- ✅ Easy addition of new device types / 新デバイスタイプ容易追加
- ✅ Grid size changeability / グリッドサイズ変更可能性
- ✅ External file format save/load / 外部ファイル形式保存・読み込み

---

## 🚀 Expected Benefits / 期待される効果

### Development Efficiency / 開発効率

| Metric / 指標 | Current PyPlc / 現在PyPlc | PyPlc-v2 | Improvement / 改善 |
|---------------|---------------------------|----------|-------------------|
| File Count / ファイル数 | 6 modules | 4 modules | 33% reduction / 33%削減 |
| Main File Lines / メイン行数 | 300+ lines | <200 lines | 33% reduction / 33%削減 |
| Inheritance Levels / 継承レベル | 3-4 levels | 2 levels | 50% simplification / 50%簡略化 |
| State Management / 状態管理 | Complex / 複雑 | Unified / 統一化 | High simplification / 高度簡略化 |
| Debug Difficulty / デバッグ難易度 | Difficult / 困難 | Easy / 容易 | Significant improvement / 大幅改善 |
| New Feature Time / 新機能追加時間 | 2-3 days / 日 | 0.5-1 day / 日 | 66% reduction / 66%短縮 |

### Long-term Benefits / 長期的効果

1. **Development Speed 2x Improvement / 開発速度2倍向上**
   - Simple structure reduces understanding time / シンプル構造による理解時間短縮

2. **Bug Rate 50% Reduction / バグ率50%削減**
   - Clear responsibility separation limits impact scope / 明確責任分離による影響範囲限定

3. **New Feature Development 60% Faster / 新機能開発60%高速化**
   - Plugin architecture enables independent development / プラグインアーキテクチャによる独立開発

4. **Team Development Efficiency / チーム開発効率向上**
   - Module-based parallel development possible / モジュール単位並行開発可能

---

## 🔄 Migration Strategy / 移行戦略

### Phase-by-Phase Migration / 段階的移行

1. **Phase 1**: Create new foundation alongside existing system / 既存システムと並行して新基盤作成
2. **Phase 2**: Migrate core functionality / コア機能移行
3. **Phase 3**: Feature parity achievement / 機能同等性達成
4. **Phase 4**: Complete replacement / 完全置き換え

### Risk Mitigation / リスク軽減

1. **Incremental Implementation / 段階的実装**: Each phase has clear deliverables / 各フェーズで明確な成果物
2. **Parallel Development / 並行開発**: Keep existing system until v2 is stable / v2安定まで既存システム保持
3. **Comprehensive Testing / 包括的テスト**: Unit + Integration + E2E tests / 単体+統合+E2Eテスト

---

## 📝 Implementation Notes for AI / AI向け実装ノート

### Key Implementation Priorities / 重要実装優先度

1. **Start with LogicElement base class / LogicElement基底クラスから開始**
   - This is the foundation for all devices / 全デバイスの基盤
   - Ensure proper abstract method definitions / 適切な抽象メソッド定義確保

2. **Implement GridDeviceManager next / 次にGridDeviceManager実装**
   - Focus on L_Side/R_Side automatic placement / L_Side/R_Side自動配置に重点
   - Bidirectional linking is critical / 双方向リンクが重要

3. **Power flow calculation is complex / 電力フロー計算は複雑**
   - Break down into small methods / 小さなメソッドに分解
   - Test each device type separately / 各デバイスタイプを個別テスト

### Common Pitfalls to Avoid / 回避すべき一般的落とし穴

1. **Over-engineering / 過度設計**: Keep it simple, add complexity only when needed / シンプル保持、必要時のみ複雑化
2. **Circular dependencies / 循環依存**: Maintain clear layer boundaries / 明確な層境界維持
3. **Premature optimization / 早期最適化**: Focus on correctness first / まず正確性に重点

### Code Style Guidelines / コードスタイルガイドライン

1. **Clear naming / 明確な命名**: Use descriptive variable/method names / 説明的な変数・メソッド名使用
2. **Type hints / 型ヒント**: Use typing for all method signatures / 全メソッドシグネチャに型付け使用
3. **Documentation / ドキュメント**: Bilingual comments (JP/EN) when helpful / 有用時は日英併記コメント

### Testing Approach / テストアプローチ

1. **Test-driven development preferred / テスト駆動開発推奨**
2. **Start with unit tests for LogicElement / LogicElement単体テストから開始**
3. **Integration tests for circuit scenarios / 回路シナリオ統合テスト**

---

## 📚 References / 参考資料

### Source Documents / 原文書
- `ReMake_PlcSIm.txt`: Core requirements specification / コア要件仕様
- `docs/SimIssue/PLC Sim Plan.txt`: Self-holding circuit problem definition / 自己保持回路問題定義
- `docs/DeviceDefineTable.csv`: Device behavior specifications / デバイス動作仕様
- `docs/SystemAndClass.md`: Existing system analysis / 既存システム分析

### Design Influences / 設計影響
- Existing PyPlc modular architecture achievements / 既存PyPlcモジュラーアーキテクチャ成果
- Three-layer architecture best practices / 3層アーキテクチャベストプラクティス
- PLC industry standard behaviors / PLC業界標準動作

---

## 📅 Timeline / タイムライン

### Development Schedule / 開発スケジュール

- **Phase 1**: Days 1-2 / 1-2日目
- **Phase 2**: Days 3-5 / 3-5日目  
- **Phase 3**: Days 6-8 / 6-8日目
- **Phase 4**: Days 9-10 / 9-10日目
- **Phase 5**: Days 11+ (Optional) / 11日目以降（オプション）

### Milestones / マイルストーン

- [ ] **M1**: Basic grid system working / 基本グリッドシステム動作
- [ ] **M2**: Simple AND circuit operational / 単純AND回路動作
- [ ] **M3**: Self-holding circuit resolved / 自己保持回路解決
- [ ] **M4**: Complete UI/UX system / 完全UI/UXシステム
- [ ] **M5**: Production-ready system / 本番準備完了システム

---

*Document Version: 2.0*  
*Last Updated: 2025-01-27*  
*Target Implementation: PyPlc-v2 Complete Remake*

---

**End of Document / 文書終了**
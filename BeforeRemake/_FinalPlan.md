# PyPlc-v2 Final Remake Plan / PyPlc-v2 最終再構築計画書

## 📖 Document Overview / 文書概要

**Purpose / 目的**: Comprehensive final implementation plan integrating all remake proposals  
**対象**: 全リメイク提案を統合した包括的最終実装計画

**Target Audience / 対象読者**: AI Assistant, Development Team  
**想定読者**: AIアシスタント、開発チーム

**Creation Date / 作成日**: 2025-01-27  
**Version / バージョン**: Final 1.0  
**Source Plans / 元プラン**: Claude + Gemini + WindSurf Proposals

---

## 🎯 Integrated Project Goals / 統合プロジェクト目標

### Primary Objectives / 主要目標

1. **Maximum Simplification / 最大シンプル化**
   - Single-system architecture (eliminate dual-system complexity)
   - 単一システムアーキテクチャ（二重システム複雑性排除）
   - Target: Main file under 150 lines / メインファイル150行以内

2. **Self-Holding Circuit Resolution / 自己保持回路問題解決**
   - Explicit wire objects for electrical continuity
   - 電気的継続性のための明示的配線オブジェクト
   - Left-to-right power tracing with bidirectional links
   - 双方向リンクによる左→右電力トレース

3. **Practical Implementation Focus / 実用的実装重視**
   - Step-by-step development approach
   - ステップバイステップ開発アプローチ
   - Clear success criteria and measurable milestones
   - 明確な成功基準と測定可能マイルストーン

---

## 🏗️ Unified System Architecture / 統合システムアーキテクチャ

### Core Design Principles / 核となる設計原則

1. **Single Grid-Based System / 単一グリッドベースシステム**
   ```python
   # Foundation: 10x10 Matrix (Expandable)
   # 基盤: 10x10マトリックス（拡張可能）
   GRID_ROWS = 10  # Future expandable / 将来拡張可能
   GRID_COLS = 10  # Future expandable / 将来拡張可能
   GridDeviceManager[Row][Col]  # Single source of truth / 単一の真実源
   ```

2. **Fixed Bus Rule with Flexibility / 柔軟性のある固定バスルール**
   ```python
   # Adaptive bus placement for future expansion
   # 将来拡張のための適応バス配置
   Col=0: L_Side (Power Bus) - Non-editable / 電源バス（編集不可）
   Col=(GRID_COLS-1): R_Side (Neutral Bus) - Non-editable / ニュートラルバス（編集不可）
   Col=1 to (GRID_COLS-2): User editable area / ユーザー編集可能領域
   ```

3. **Unified Device Representation / 統一デバイス表現**
   ```python
   class LogicElement:
       # Identity / アイデンティティ
       id: str = f"{row:03d}_{col:03d}"    # "007_005" format
       name: str                           # User name (X001, Y001)
       device_type: DeviceType             # Unified device type
       
       # Position / 位置
       grid_row: int                       # Row coordinate
       grid_col: int                       # Column coordinate
       
       # Connection (Bidirectional) / 接続（双方向）
       left_dev: Optional[str]             # Left device ID
       right_dev: Optional[str]            # Right device ID
       
       # State Management / 状態管理
       powered: bool = False               # Power state
       active: bool = False                # Operation state
       input_state: bool = False           # Input state
       output_state: bool = False          # Output state
       
       # Device-specific attributes / デバイス固有属性
       timer_preset: float = 0.0           # Timer preset
       timer_current: float = 0.0          # Timer current
       counter_preset: int = 0             # Counter preset
       counter_current: int = 0            # Counter current
   ```

### Simplified Three-Layer Architecture / 簡素化3層アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                 Presentation Layer / プレゼンテーション層        │
│  SimpleRenderer + DeviceEditor + UserInterface             │
│  - Grid rendering / グリッド描画                             │
│  - Mouse/keyboard interaction / マウス・キーボードインタラクション │
│  - Real-time visual feedback / リアルタイム視覚フィードバック     │
└─────────────────────────────────────────────────────────────┘
                           ↕ (Clean APIs / クリーンAPI)
┌─────────────────────────────────────────────────────────────┐
│                   Business Layer / ビジネス層                │
│  GridDeviceManager + ElectricalTracer                      │
│  - Device management / デバイス管理                          │
│  - Power flow calculation / 電力フロー計算                   │
│  - Circuit simulation / 回路シミュレーション                  │
└─────────────────────────────────────────────────────────────┘
                           ↕ (Data access / データアクセス)
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer / データ層                     │
│  LogicElement + CircuitSerializer                          │
│  - Device state persistence / デバイス状態永続化              │
│  - File I/O operations / ファイル入出力操作                   │
│  - Configuration management / 設定管理                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Integrated Implementation Phases / 統合実装フェーズ

### Phase 1: Foundation System / 基盤システム (Day 1-2)

**Objective / 目標**: Establish solid foundation with minimal working system  
**目標**: 最小動作システムによる堅実な基盤確立

**Step 1.1: Project Setup / プロジェクトセットアップ**
```
PyPlc-v2/
├── main.py                    # Main coordinator (<150 lines)
├── core/
│   ├── logic_element.py       # Unified device class
│   ├── grid_manager.py        # Grid management
│   └── device_types.py        # Device type definitions
├── systems/
│   ├── electrical_tracer.py   # Simple power tracing
│   ├── simple_renderer.py     # Visual system
│   └── device_editor.py       # User interaction
├── config/
│   ├── settings.py            # System configuration
│   └── sprites.json           # Sprite definitions
└── tests/                     # Unit tests
```

**Step 1.2: Core Classes Implementation / コアクラス実装**
```python
# 1. LogicElement base class
class LogicElement(ABC):
    @abstractmethod
    def evaluate(self) -> bool:
        """Device-specific logic operation"""
        pass
    
    @abstractmethod
    def get_sprite_name(self) -> str:
        """Get sprite name based on current state"""
        pass

# 2. GridDeviceManager with expandable design
class GridDeviceManager:
    def __init__(self, rows: int = 10, cols: int = 10):
        self.GRID_ROWS = rows
        self.GRID_COLS = cols
        self.grid = self._initialize_grid()
        
    def _initialize_grid(self):
        # Auto-place L_Side/R_Side with expandable logic
        pass

# 3. DeviceType enumeration
class DeviceType(Enum):
    L_SIDE = "L_SIDE"
    R_SIDE = "R_SIDE"
    CONTACT_A = "CONTACT_A"
    CONTACT_B = "CONTACT_B"
    COIL = "COIL"
    WIRE_H = "WIRE_H"
    WIRE_V = "WIRE_V"
    TIMER = "TIMER"
    COUNTER = "COUNTER"
```

**Success Criteria / 成功基準**:
- ✅ 10x10 grid display with auto L/R_Side placement / L/R_Side自動配置による10x10グリッド表示
- ✅ Device placement with auto ID generation / 自動ID生成によるデバイス配置
- ✅ Bidirectional linking system working / 双方向リンクシステム動作

### Phase 2: Basic Electrical System / 基本電気システム (Day 3-4)

**Objective / 目標**: Implement simplified power tracing  
**目標**: 簡素化電力トレース実装

**Step 2.1: ElectricalTracer Implementation / ElectricalTracer実装**
```python
class ElectricalTracer:
    """Simplified left-to-right power tracing"""
    
    def trace_power_flow(self, grid_manager: GridDeviceManager) -> None:
        """Trace all rows sequentially"""
        for row in range(grid_manager.GRID_ROWS):
            self._trace_row(grid_manager, row)
            
    def _trace_row(self, grid_manager: GridDeviceManager, row: int) -> None:
        """Single row left-to-right tracing"""
        current_power = True  # Start from L_Side
        
        for col in range(grid_manager.GRID_COLS):
            device = grid_manager.get_device(row, col)
            if device:
                # Set input state
                device.input_state = current_power
                
                # Evaluate device
                device_output = device.evaluate()
                
                # Update power for next device
                current_power = device_output and device.can_conduct_power()
                device.powered = current_power
```

**Step 2.2: Basic Device Implementation / 基本デバイス実装**
```python
class ContactA(LogicElement):
    """A contact (Normally Open)"""
    
    def evaluate(self) -> bool:
        if self.active:  # Contact is closed
            self.output_state = self.input_state
        else:  # Contact is open
            self.output_state = False
        return self.output_state
    
    def can_conduct_power(self) -> bool:
        return self.active

class Coil(LogicElement):
    """Output coil"""
    
    def evaluate(self) -> bool:
        self.output_state = self.input_state
        self.active = self.input_state  # Coil energized
        return self.output_state
    
    def can_conduct_power(self) -> bool:
        return True  # Always passes power

class WireH(LogicElement):
    """Horizontal wire"""
    
    def evaluate(self) -> bool:
        self.output_state = self.input_state
        return self.output_state
    
    def can_conduct_power(self) -> bool:
        return True  # Always conducts
```

**Success Criteria / 成功基準**:
- ✅ Simple AND circuit: `[L_Side] → [ContactA] → [WireH] → [Coil] → [R_Side]`
- ✅ Real-time power state updates / リアルタイム電力状態更新
- ✅ Contact manual operation working / 接点手動操作動作

### Phase 3: Visual System / 視覚システム (Day 5)

**Objective / 目標**: Implement state-based visual feedback  
**目標**: 状態ベース視覚フィードバック実装

**Step 3.1: SimpleRenderer Implementation / SimpleRenderer実装**
```python
class SimpleRenderer:
    """Unified grid rendering system"""
    
    def render_frame(self, grid_manager: GridDeviceManager) -> None:
        """Render complete frame"""
        pyxel.cls(0)  # Clear screen
        
        self._render_grid_lines()
        self._render_devices(grid_manager)
        self._render_power_flow(grid_manager)
        self._render_ui_elements()
    
    def _render_devices(self, grid_manager: GridDeviceManager) -> None:
        """Render all devices with state-based sprites"""
        for row in range(grid_manager.GRID_ROWS):
            for col in range(grid_manager.GRID_COLS):
                device = grid_manager.get_device(row, col)
                if device:
                    sprite_name = device.get_sprite_name()
                    x = col * CELL_SIZE
                    y = row * CELL_SIZE
                    self._draw_sprite(sprite_name, x, y)
    
    def _render_power_flow(self, grid_manager: GridDeviceManager) -> None:
        """Visual power flow with colors"""
        for row in range(grid_manager.GRID_ROWS):
            for col in range(grid_manager.GRID_COLS - 1):
                device = grid_manager.get_device(row, col)
                if device and device.powered:
                    # Draw power line between devices
                    x1 = (col + 1) * CELL_SIZE
                    x2 = (col + 1) * CELL_SIZE + CELL_SIZE
                    y = row * CELL_SIZE + CELL_SIZE // 2
                    pyxel.line(x1, y, x2, y, 11)  # Green for powered
```

**Step 3.2: Sprite Naming System / スプライト命名システム**
```python
# Unified sprite naming convention
def get_sprite_name(self) -> str:
    """State-based sprite selection"""
    base_name = self.device_type.value
    
    if self.device_type in [DeviceType.L_SIDE, DeviceType.R_SIDE]:
        return base_name  # Bus devices have single sprite
    
    # State-based sprites for interactive devices
    state_suffix = "_ON" if self.active else "_OFF"
    power_suffix = "_POWERED" if self.powered else ""
    
    return f"{base_name}{state_suffix}{power_suffix}"
```

**Success Criteria / 成功基準**:
- ✅ Real-time visual state updates / リアルタイム視覚状態更新
- ✅ Power flow visualization / 電力フロー可視化
- ✅ State-based sprite switching / 状態ベーススプライト切り替え

### Phase 4: User Interaction / ユーザーインタラクション (Day 6)

**Objective / 目標**: Complete editing and operation system  
**目標**: 編集・操作システム完成

**Step 4.1: DeviceEditor Implementation / DeviceEditor実装**
```python
class DeviceEditor:
    """Device placement and editing system"""
    
    def __init__(self, grid_manager: GridDeviceManager):
        self.grid_manager = grid_manager
        self.selected_device_type = None
        self.device_palette = self._create_palette()
    
    def handle_mouse_click(self, mouse_x: int, mouse_y: int) -> None:
        """Unified mouse click handling"""
        grid_x, grid_y = self._screen_to_grid(mouse_x, mouse_y)
        
        if self._is_palette_click(mouse_x, mouse_y):
            self._handle_palette_selection(mouse_x, mouse_y)
        elif self._is_grid_click(grid_x, grid_y):
            self._handle_grid_interaction(grid_x, grid_y)
    
    def _handle_grid_interaction(self, grid_x: int, grid_y: int) -> None:
        """Grid interaction logic"""
        if self.selected_device_type:
            if self._validate_placement(grid_x, grid_y):
                self._place_device(grid_x, grid_y)
        else:
            self._toggle_device(grid_x, grid_y)
    
    def _validate_placement(self, grid_x: int, grid_y: int) -> bool:
        """Placement validation rules"""
        # Bus constraints
        if grid_x == 0 and self.selected_device_type != DeviceType.L_SIDE:
            return False
        if grid_x == (self.grid_manager.GRID_COLS - 1) and self.selected_device_type != DeviceType.R_SIDE:
            return False
        
        # Editable area constraint
        if self.selected_device_type in [DeviceType.L_SIDE, DeviceType.R_SIDE]:
            return False  # Cannot manually place bus devices
            
        return 1 <= grid_x <= (self.grid_manager.GRID_COLS - 2)
```

**Step 4.2: Keyboard Controls / キーボード制御**
```python
def handle_keyboard_input(self) -> None:
    """Keyboard control system"""
    # Device selection (1-9 keys)
    for i in range(1, 10):
        if pyxel.btnp(getattr(pyxel, f'KEY_{i}')):
            self._select_device_type(i)
    
    # Contact toggle (Shift + 1-4)
    if pyxel.btn(pyxel.KEY_SHIFT):
        for i in range(1, 5):
            if pyxel.btnp(getattr(pyxel, f'KEY_{i}')):
                self._toggle_contact(f"X00{i}")
    
    # System controls
    if pyxel.btnp(pyxel.KEY_F5):
        self._toggle_power_system()
    if pyxel.btnp(pyxel.KEY_DELETE):
        self._enter_delete_mode()
```

**Success Criteria / 成功基準**:
- ✅ Complete edit-run-stop cycle / 完全な編集・実行・停止サイクル
- ✅ Device palette with visual selection / 視覚選択によるデバイスパレット
- ✅ Mouse-based device placement / マウスベースデバイス配置
- ✅ Keyboard shortcuts working / キーボードショートカット動作

### Phase 5: Self-Holding Circuit / 自己保持回路 (Day 7-8)

**Objective / 目標**: Resolve self-holding circuit with explicit wiring  
**目標**: 明示配線による自己保持回路解決

**Step 5.1: Vertical Connection System / 垂直接続システム**
```python
class VerticalConnectionManager:
    """Manage vertical connections between rows"""
    
    def __init__(self, grid_manager: GridDeviceManager):
        self.grid_manager = grid_manager
        self.vertical_connections = {}  # col -> [(upper_row, lower_row)]
    
    def add_vertical_connection(self, col: int, upper_row: int, lower_row: int) -> None:
        """Add vertical connection between rows"""
        if col not in self.vertical_connections:
            self.vertical_connections[col] = []
        
        connection = (upper_row, lower_row)
        if connection not in self.vertical_connections[col]:
            self.vertical_connections[col].append(connection)
    
    def process_vertical_power_flow(self) -> None:
        """Process power flow through vertical connections"""
        for col, connections in self.vertical_connections.items():
            for upper_row, lower_row in connections:
                upper_device = self.grid_manager.get_device(upper_row, col)
                lower_device = self.grid_manager.get_device(lower_row, col)
                
                if upper_device and lower_device:
                    # Transfer power from upper to lower
                    if upper_device.powered:
                        lower_device.input_state = True
```

**Step 5.2: Self-Holding Circuit Implementation / 自己保持回路実装**
```python
# Target circuit structure:
# Row 0: [L_Side] → [X001] → [WireH] → [Y01_Input] → [WireH] → [R_Side]
# Row 1: [L_Side] → [Y01_Output] → [WireH] → [X002] → [WireV_UP] → [R_Side]
# Vertical: Y01_Output connects to Y01_Input via vertical wire

def implement_self_holding_test_circuit(self) -> None:
    """Create test self-holding circuit"""
    # Row 0: Input line
    self.grid_manager.place_device(0, 1, DeviceType.CONTACT_A, "X001")
    self.grid_manager.place_device(0, 2, DeviceType.WIRE_H)
    self.grid_manager.place_device(0, 3, DeviceType.COIL, "Y01_INPUT")
    self.grid_manager.place_device(0, 4, DeviceType.WIRE_H)
    
    # Row 1: Self-holding line
    self.grid_manager.place_device(1, 1, DeviceType.COIL, "Y01_OUTPUT")
    self.grid_manager.place_device(1, 2, DeviceType.WIRE_H)
    self.grid_manager.place_device(1, 3, DeviceType.CONTACT_B, "X002")
    self.grid_manager.place_device(1, 4, DeviceType.WIRE_V)
    
    # Vertical connection
    self.vertical_manager.add_vertical_connection(4, 0, 1)
```

**Success Criteria / 成功基準**:
- ✅ Self-holding circuit operates correctly / 自己保持回路正常動作
- ✅ Y01 remains energized after X001 turns OFF / X001がOFF後もY01が自己保持
- ✅ X002 can break the self-holding loop / X002が自己保持ループを切断可能

### Phase 6: Advanced Features / 高度機能 (Day 9-10, Optional)

**Objective / 目標**: Timer, Counter, and file operations  
**目標**: タイマー・カウンター・ファイル操作

**Components / コンポーネント**:
- Timer device with preset/current value management / プリセット・現在値管理付きタイマー
- Counter device with edge detection / エッジ検出付きカウンター
- Circuit save/load functionality / 回路保存・読み込み機能
- Device configuration dialogs / デバイス設定ダイアログ

---

## 📊 Comprehensive Quality Assurance / 包括的品質保証

### Performance Requirements / パフォーマンス要件

| Metric / 指標 | Target / 目標値 | Measurement Method / 測定方法 |
|---------------|----------------|----------------------------|
| Frame Rate / フレームレート | 60 FPS stable / 60FPS安定 | Pyxel FPS counter / PyxelFPSカウンター |
| Mouse Response / マウス応答 | <16ms | Click-to-visual feedback / クリック→視覚フィードバック |
| Memory Usage / メモリ使用量 | <50MB for 100 devices / 100デバイスで50MB以内 | Python memory profiler / Pythonメモリプロファイラー |
| Startup Time / 起動時間 | <2 seconds / 2秒以内 | Application launch measurement / アプリ起動測定 |
| Grid Size Scalability / グリッドサイズ拡張性 | Up to 20x20 without performance loss / 20x20まで性能劣化なし | Stress testing / ストレステスト |

### Testing Strategy / テスト戦略

#### Unit Tests / 単体テスト
```python
class TestLogicElement(unittest.TestCase):
    def test_contact_a_operation(self):
        """Test A contact basic operation"""
        contact = ContactA(1, 2)
        contact.active = True
        contact.input_state = True
        
        result = contact.evaluate()
        
        self.assertTrue(result)
        self.assertTrue(contact.output_state)
        self.assertTrue(contact.can_conduct_power())
    
    def test_coil_energization(self):
        """Test coil energization behavior"""
        coil = Coil(1, 3)
        coil.input_state = True
        
        result = coil.evaluate()
        
        self.assertTrue(result)
        self.assertTrue(coil.active)  # Coil should be energized
```

#### Integration Tests / 統合テスト
```python
class TestCircuitIntegration(unittest.TestCase):
    def test_simple_and_circuit(self):
        """Test simple AND circuit operation"""
        grid = GridDeviceManager()
        tracer = ElectricalTracer()
        
        # Build circuit
        grid.place_device(0, 1, DeviceType.CONTACT_A, "X001")
        grid.place_device(0, 2, DeviceType.WIRE_H)
        grid.place_device(0, 3, DeviceType.COIL, "Y001")
        
        # Test with X001 OFF
        x001 = grid.get_device(0, 1)
        x001.active = False
        tracer.trace_power_flow(grid)
        
        y001 = grid.get_device(0, 3)
        self.assertFalse(y001.active)
        
        # Test with X001 ON
        x001.active = True
        tracer.trace_power_flow(grid)
        
        self.assertTrue(y001.active)
    
    def test_self_holding_circuit(self):
        """Test self-holding circuit operation"""
        # Implementation of SimIssue/PLC Sim Plan.txt test case
        pass
```

#### End-to-End Tests / E2Eテスト
```python
class TestUserInteraction(unittest.TestCase):
    def test_device_placement_workflow(self):
        """Test complete device placement workflow"""
        # Simulate user clicking palette to select device
        # Simulate user clicking grid to place device
        # Verify device is placed and linked correctly
        pass
    
    def test_circuit_simulation_cycle(self):
        """Test complete circuit simulation cycle"""
        # Build circuit via UI simulation
        # Run power simulation
        # Toggle contacts and verify output changes
        pass
```

### Success Criteria Matrix / 成功基準マトリックス

#### Must-Have Requirements / 必須要件
- ✅ **10x10 grid management with expandability** / 拡張性のある10x10グリッド管理
- ✅ **Self-holding circuit correct operation** / 自己保持回路正常動作
- ✅ **Real-time power flow visualization** / リアルタイム電力フロー可視化
- ✅ **Complete edit-run-stop cycle** / 完全な編集・実行・停止サイクル
- ✅ **Mouse-based intuitive operation** / マウスベース直感的操作

#### Quality Requirements / 品質要件
- ✅ **Main file under 150 lines** / メインファイル150行以内
- ✅ **Single-system architecture** / 単一システムアーキテクチャ
- ✅ **60FPS stable operation** / 60FPS安定動作
- ✅ **Clear module responsibility separation** / モジュール責任分離明確化
- ✅ **Comprehensive unit test coverage** / 包括的単体テストカバレッジ

#### Extensibility Requirements / 拡張性要件
- ✅ **Easy addition of new device types** / 新デバイスタイプ容易追加
- ✅ **Grid size runtime changeability** / 実行時グリッドサイズ変更可能性
- ✅ **Plugin architecture readiness** / プラグインアーキテクチャ準備
- ✅ **External file format support** / 外部ファイル形式サポート

---

## 🚀 Expected Comprehensive Benefits / 包括的期待効果

### Development Efficiency / 開発効率

| Aspect / 側面 | Current PyPlc / 現在PyPlc | PyPlc-v2 Final / PyPlc-v2最終 | Improvement / 改善 |
|---------------|---------------------------|-------------------------------|-------------------|
| **File Count** / ファイル数 | 6 modules | 4 core modules | 33% reduction / 33%削減 |
| **Main File Size** / メインファイルサイズ | 300+ lines | <150 lines | 50% reduction / 50%削減 |
| **Architecture Complexity** / アーキテクチャ複雑度 | Dual-system / 二重システム | Single-system / 単一システム | 75% simplification / 75%簡素化 |
| **Debug Time** / デバッグ時間 | 2-3 hours/issue | 30min/issue | 80% reduction / 80%短縮 |
| **New Feature Addition** / 新機能追加 | 2-3 days | 4-6 hours | 75% faster / 75%高速化 |
| **Test Coverage** / テストカバレッジ | Partial / 部分的 | Comprehensive / 包括的 | 100% improvement / 100%向上 |

### System Performance / システム性能

1. **Runtime Performance / 実行時性能**
   - Power calculation: O(rows × cols) = O(100) linear complexity / 電力計算: O(100)線形複雑度
   - Memory usage: <50MB for 100 devices / 100デバイスで50MB以内
   - Frame rate: Stable 60 FPS / 安定60FPS

2. **User Experience / ユーザー体験**
   - Immediate visual feedback (<16ms) / 即座の視覚フィードバック
   - Intuitive grid-based editing / 直感的グリッドベース編集
   - Real-time circuit simulation / リアルタイム回路シミュレーション

3. **Maintainability / 保守性**
   - Clear separation of concerns / 明確な関心事分離
   - Comprehensive unit test suite / 包括的単体テストスイート
   - Plugin-ready architecture / プラグイン対応アーキテクチャ

---

## 🔄 Risk Management & Migration Strategy / リスク管理・移行戦略

### Development Risks / 開発リスク

| Risk / リスク | Probability / 確率 | Impact / 影響 | Mitigation / 軽減策 |
|---------------|-------------------|---------------|-------------------|
| **Phase delays** / フェーズ遅延 | Medium / 中 | Medium / 中 | Clear daily milestones / 明確な日次マイルストーン |
| **Self-holding circuit complexity** / 自己保持回路複雑性 | High / 高 | High / 高 | Dedicated test cases + prototype / 専用テストケース+プロトタイプ |
| **Performance degradation** / 性能劣化 | Low / 低 | Medium / 中 | Performance monitoring / 性能監視 |
| **User acceptance** / ユーザー受容 | Low / 低 | High / 高 | Early user feedback / 早期ユーザーフィードバック |

### Migration Strategy / 移行戦略

#### Safe Development Approach / 安全な開発アプローチ
1. **Parallel Development** / 並行開発
   - Keep existing PyPlc functional during v2 development / v2開発中も既存PyPlc機能維持
   - New directory structure prevents conflicts / 新ディレクトリ構造が競合防止

2. **Incremental Validation** / 段階的検証
   - Each phase has clear acceptance criteria / 各フェーズに明確な受諾基準
   - Daily progress checkpoints / 日次進捗チェックポイント
   - Rollback capability at each phase / 各フェーズでのロールバック機能

3. **Feature Parity Verification** / 機能同等性検証
   - Side-by-side comparison testing / 並行比較テスト
   - Migration checklist completion / 移行チェックリスト完了
   - User acceptance testing / ユーザー受諾テスト

---

## 📝 AI Implementation Guidelines / AI実装ガイドライン

### Critical Implementation Priorities / 重要実装優先度

1. **Foundation First** / 基盤優先
   ```
   Priority 1: LogicElement + GridDeviceManager + DeviceType
   Priority 2: Basic electrical tracing (ContactA + Coil + WireH)
   Priority 3: Visual feedback system
   Priority 4: User interaction system
   Priority 5: Self-holding circuit resolution
   ```

2. **Quality Gates** / 品質ゲート
   ```
   Each phase requires:
   - Unit tests passing / 単体テスト通過
   - Integration tests passing / 統合テスト通過
   - Performance benchmarks met / 性能ベンチマーク達成
   - Code review completion / コードレビュー完了
   ```

### Common Pitfalls & Solutions / 一般的落とし穴・解決策

1. **Over-Engineering Prevention** / 過度設計防止
   - ❌ **Avoid**: Complex inheritance hierarchies / 複雑な継承階層回避
   - ✅ **Do**: Composition over inheritance / 継承より合成
   - ✅ **Do**: Simple, clear interfaces / シンプル・明確インターフェース

2. **Performance Optimization** / 性能最適化
   - ❌ **Avoid**: Premature optimization / 早期最適化回避
   - ✅ **Do**: Profile before optimizing / 最適化前プロファイリング
   - ✅ **Do**: Measure actual performance impact / 実際の性能影響測定

3. **State Management** / 状態管理
   - ❌ **Avoid**: Scattered state variables / 分散状態変数回避
   - ✅ **Do**: Centralized state in LogicElement / LogicElementでの状態集中化
   - ✅ **Do**: Clear state transition rules / 明確な状態遷移ルール

### Code Style Guidelines / コードスタイルガイドライン

```python
# 1. Clear naming conventions / 明確な命名規則
class LogicElement:          # PascalCase for classes
    device_type: DeviceType  # snake_case for variables
    
def evaluate_device() -> bool:  # snake_case for functions
    pass

# 2. Type hints everywhere / 全箇所型ヒント
def place_device(self, row: int, col: int, device_type: DeviceType) -> bool:
    return True

# 3. Docstrings with bilingual support / 日英併記ドキュメント文字列
def trace_power_flow(self) -> None:
    """Trace power flow through all grid rows.
    
    全グリッド行の電力フローをトレースします。
    
    This method processes each row sequentially from left to right,
    updating device states based on electrical continuity rules.
    """
    pass

# 4. Clear error handling / 明確なエラー処理
def place_device(self, row: int, col: int, device_type: DeviceType) -> bool:
    try:
        if not self._validate_position(row, col):
            return False
        # Placement logic
        return True
    except Exception as e:
        logger.error(f"Device placement failed: {e}")
        return False
```

### Testing Approach / テストアプローチ

1. **Test-Driven Development (TDD)** / テスト駆動開発
   ```python
   # Write test first / テスト先行記述
   def test_contact_a_conducts_when_active(self):
       contact = ContactA(1, 2)
       contact.active = True
       contact.input_state = True
       
       result = contact.evaluate()
       
       self.assertTrue(result)
   
   # Then implement / 次に実装
   class ContactA(LogicElement):
       def evaluate(self) -> bool:
           # Implementation to pass test
           pass
   ```

2. **Integration Testing Strategy** / 統合テスト戦略
   ```python
   # Test realistic circuit scenarios / 現実的回路シナリオテスト
   def test_factory_conveyor_circuit(self):
       """Test factory conveyor belt control circuit"""
       # Build complex realistic circuit
       # Verify operation matches industrial expectations
       pass
   ```

---

## 📚 Comprehensive References / 包括的参考資料

### Source Documents / 原文書
- **`ReMake_PlcSIm.txt`**: Core requirements and matrix specifications / コア要件・マトリックス仕様
- **`docs/SimIssue/PLC Sim Plan.txt`**: Self-holding circuit problem definition / 自己保持回路問題定義
- **`docs/DeviceDefineTable.csv`**: Device behavior specifications / デバイス動作仕様
- **`docs/SystemAndClass.md`**: Current system analysis / 現在システム分析
- **`docs/windsurf_refact.md`**: Refactoring lessons learned / リファクタリング教訓

### Plan Integration Analysis / プラン統合分析
- **Claude Plan Strengths**: Theoretical depth, comprehensive architecture / 理論的深度・包括的アーキテクチャ
- **Gemini Plan Strengths**: Practical step-by-step approach, Pyxel integration / 実用的段階アプローチ・Pyxel統合
- **WindSurf Plan Strengths**: Problem analysis, performance focus, simplification / 問題分析・性能重視・簡素化

### Design Philosophy Integration / 設計哲学統合
- **Simplicity First** (WindSurf): Single-system architecture / 単一システムアーキテクチャ
- **Practical Implementation** (Gemini): Step-by-step development / ステップバイステップ開発
- **Comprehensive Design** (Claude): Future-proof extensibility / 将来対応拡張性

---

## 📅 Detailed Timeline / 詳細タイムライン

### Development Schedule / 開発スケジュール

| Phase | Days | Daily Goals | Success Metrics |
|-------|------|-------------|-----------------|
| **Phase 1** | 1-2 | Foundation system | Grid display + device placement |
| **Phase 2** | 3-4 | Basic electrical | Simple circuits working |
| **Phase 3** | 5 | Visual system | Real-time state visualization |
| **Phase 4** | 6 | User interaction | Complete edit-run cycle |
| **Phase 5** | 7-8 | Self-holding circuit | Advanced circuit resolution |
| **Phase 6** | 9-10 | Advanced features | Timer/Counter + file I/O |

### Daily Milestones / 日次マイルストーン

**Day 1**: Project setup + LogicElement + GridDeviceManager  
**Day 2**: Device placement + bidirectional linking + basic tests  
**Day 3**: ElectricalTracer + basic device evaluation  
**Day 4**: Simple circuits working + power visualization  
**Day 5**: Complete visual system + sprite integration  
**Day 6**: Mouse interaction + device editor + keyboard controls  
**Day 7**: Vertical connections + self-holding circuit logic  
**Day 8**: Self-holding circuit validation + edge case testing  
**Day 9**: Timer/Counter devices + configuration dialogs  
**Day 10**: File I/O + final testing + documentation  

---

## 🎉 Final Success Definition / 最終成功定義

### Quantitative Metrics / 定量的指標

1. **Code Quality / コード品質**
   - Main file: <150 lines / メインファイル150行以内
   - Test coverage: >90% / テストカバレッジ90%以上
   - Cyclomatic complexity: <10 per method / メソッド当たり循環的複雑度10未満

2. **Performance / 性能**
   - Frame rate: 60 FPS stable / 60FPS安定
   - Memory: <50MB for 100 devices / 100デバイスで50MB以内
   - Startup: <2 seconds / 起動2秒以内

3. **Functionality / 機能性**
   - Self-holding circuit: 100% correct operation / 自己保持回路100%正常動作
   - Device types: 10+ supported / 10種類以上デバイス対応
   - Grid size: Expandable to 20x20 / 20x20まで拡張可能

### Qualitative Success Criteria / 定性的成功基準

1. **User Experience / ユーザー体験**
   - Intuitive grid-based editing / 直感的グリッドベース編集
   - Real-time visual feedback / リアルタイム視覚フィードバック
   - Smooth learning curve / なめらかな学習曲線

2. **Developer Experience / 開発者体験**
   - Clear code structure / 明確なコード構造
   - Easy feature addition / 容易な機能追加
   - Comprehensive documentation / 包括的ドキュメント

3. **System Reliability / システム信頼性**
   - Stable operation under load / 負荷下安定動作
   - Graceful error handling / 優雅なエラー処理
   - Predictable behavior / 予測可能な動作

---

*Document Version: Final 1.0*  
*Last Updated: 2025-01-27*  
*Integration Source: Claude + Gemini + WindSurf Plans*  
*Target: PyPlc-v2 Complete Implementation*

---

**End of Final Plan / 最終プラン終了**
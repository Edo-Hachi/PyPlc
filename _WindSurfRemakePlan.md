# PyPlc Project Rebuild Plan / PyPlc プロジェクト再構築計画書

**Document Version**: 1.0  
**Created**: 2025-07-28  
**Target Audience**: AI Development Assistant  
**Language**: Japanese/English Bilingual  

---

## 🎯 Project Overview / プロジェクト概要

### English
This document outlines the complete rebuild plan for the PyPlc (PLC Ladder Diagram Simulator) project. The current codebase has become overly complex with dual-system architecture, requiring a simplified approach based on a pure grid-based system.

### Japanese
本ドキュメントは、PyPlc（PLCラダー図シミュレータ）プロジェクトの完全再構築計画を示します。現在のコードベースは二重システムアーキテクチャにより過度に複雑化しており、純粋なグリッドベースシステムによる簡素化アプローチが必要です。

---

## 📊 Current Problems / 現在の問題点

### English
- **Dual System Complexity**: Parallel grid-based + traditional PLC logic systems
- **Oversized Electrical System**: 902-line electrical_system.py with complex calculations
- **Overlapping Responsibilities**: Same functionality scattered across multiple classes
- **Incomplete Features**: WIRE_H/WIRE_V implementation half-finished
- **Maintenance Difficulty**: Complex interdependencies make debugging challenging

### Japanese
- **二重システムの複雑さ**: グリッドベース＋従来PLCロジックシステムの並行運用
- **巨大な電気システム**: 902行のelectrical_system.pyと複雑な計算
- **責任の重複**: 同一機能が複数クラスに分散
- **未完成機能**: WIRE_H/WIRE_V実装が中途半端
- **保守困難**: 複雑な相互依存関係によりデバッグが困難

---

## 🏗️ New Architecture / 新アーキテクチャ

### Core Data Structure / コアデータ構造

```python
class LogicElement:
    """Unified device representation / 統一デバイス表現"""
    # Basic Info / 基本情報
    id: str                    # "XXX_YYY" format (ROW_COL) / "XXX_YYY"形式
    name: str                  # User name (X001, Y001) / ユーザー名
    device_type: DeviceType    # Device type / デバイス種別
    grid_row: int             # Row coordinate (0-9) / 行座標
    grid_col: int             # Column coordinate (0-9) / 列座標
    
    # Connection / 接続
    left_dev: str             # Left device ID / 左デバイスID
    right_dev: str            # Right device ID / 右デバイスID
    
    # State / 状態
    powered: bool             # Power state / 通電状態
    active: bool              # Operation state / 動作状態
    
    # Device-specific / デバイス固有
    timer_preset: float       # Timer preset / タイマープリセット
    counter_preset: int       # Counter preset / カウンタープリセット
```

### DeviceType Enumeration / DeviceType列挙型

```python
class DeviceType(Enum):
    # Bus Systems / バスシステム
    L_SIDE = "L_SIDE"           # Power bus / 電源バス
    R_SIDE = "R_SIDE"           # Neutral bus / ニュートラルバス
    
    # Contacts / 接点
    CONTACT_A = "CONTACT_A"     # A contact (NO) / A接点（NO）
    CONTACT_B = "CONTACT_B"     # B contact (NC) / B接点（NC）
    
    # Coils / コイル
    COIL = "COIL"               # Output coil / 出力コイル
    INCOIL = "INCOIL"           # Input coil / 入力コイル
    OUTCOIL_REV = "OUTCOIL_REV" # Reverse coil / 反転コイル
    
    # Functions / 機能
    TIMER = "TIMER"             # Timer / タイマー
    COUNTER = "COUNTER"         # Counter / カウンター
    
    # Wiring / 配線
    WIRE_H = "WIRE_H"           # Horizontal wire / 水平配線
    WIRE_V = "WIRE_V"           # Vertical wire / 垂直配線
    LINK_UP = "LINK_UP"         # Up link / 上リンク
    LINK_DOWN = "LINK_DOWN"     # Down link / 下リンク
```

### Grid Management / グリッド管理

```python
class GridDeviceManager:
    """10x10 grid device management / 10x10グリッドデバイス管理"""
    GRID_ROWS: int = 10
    GRID_COLS: int = 10
    grid: List[List[Optional[LogicElement]]]
    
    def place_device(self, row: int, col: int, device_type: DeviceType, name: str) -> bool
    def remove_device(self, row: int, col: int) -> bool
    def get_device(self, row: int, col: int) -> Optional[LogicElement]
    def update_connections(self, row: int, col: int) -> None
```

---

## ⚡ Electrical System / 電気システム

### Simplified Power Tracing / 簡素化電力トレース

```python
class ElectricalTracer:
    """Simple left-to-right power tracing / シンプルな左→右電力トレース"""
    
    def trace_power_flow(self, grid_manager: GridDeviceManager) -> None:
        """Trace all rows / 全行トレース"""
        for row in range(GridDeviceManager.GRID_ROWS):
            self._trace_row(grid_manager, row)
    
    def _trace_row(self, grid_manager: GridDeviceManager, row: int) -> None:
        """Single row trace / 単一行トレース"""
        current_power = True  # Start from L_Side / L_Sideから開始
        
        for col in range(GridDeviceManager.GRID_COLS):
            device = grid_manager.get_device(row, col)
            if device:
                current_power = self._process_device(device, current_power)
                device.powered = current_power
```

### Device Processing Rules / デバイス処理ルール

| Device Type | English Rule | Japanese Rule |
|-------------|--------------|---------------|
| L_SIDE | Always provides power | 常に電力供給 |
| R_SIDE | Power sink | 電力吸収 |
| CONTACT_A | Pass if active | アクティブ時通過 |
| CONTACT_B | Pass if inactive | 非アクティブ時通過 |
| COIL | Energize and pass | 励磁して通過 |
| WIRE_H/V | Unconditional pass | 無条件通過 |

---

## 🎨 Visual System / 視覚システム

### Simplified Rendering / 簡素化描画

```python
class SimpleRenderer:
    """Grid rendering system / グリッド描画システム"""
    
    def render_grid(self, grid_manager: GridDeviceManager) -> None:
        """Render entire grid / 全グリッド描画"""
        for row in range(GridDeviceManager.GRID_ROWS):
            for col in range(GridDeviceManager.GRID_COLS):
                device = grid_manager.get_device(row, col)
                if device:
                    sprite_name = self._get_sprite_name(device)
                    self._draw_sprite(sprite_name, col * 16, row * 16)
    
    def _get_sprite_name(self, device: LogicElement) -> str:
        """State-based sprite selection / 状態ベーススプライト選択"""
        base_name = device.device_type.value
        state_suffix = "_ON" if device.active else "_OFF"
        return f"{base_name}{state_suffix}"
```

### Sprite Naming Convention / スプライト命名規則

Pattern: `{DEVICE_TYPE}_{STATE}` where STATE is "ON" or "OFF"  
パターン: `{DEVICE_TYPE}_{STATE}`、STATEは"ON"または"OFF"

---

## 🖱️ Interaction System / インタラクションシステム

### Device Editor / デバイスエディタ

```python
class DeviceEditor:
    """Device placement and editing / デバイス配置・編集"""
    
    def handle_mouse_click(self, mouse_x: int, mouse_y: int) -> None:
        """Mouse click handling / マウスクリック処理"""
        grid_x, grid_y = self._screen_to_grid(mouse_x, mouse_y)
        
        if self.selected_device_type:
            self._place_device(grid_x, grid_y)
        else:
            self._select_device(grid_x, grid_y)
    
    def _validate_placement(self, grid_x: int, grid_y: int, device_type: DeviceType) -> bool:
        """Placement rule validation / 配置ルール検証"""
        # Col=0 must be L_SIDE only / Col=0はL_SIDEのみ
        if grid_x == 0 and device_type != DeviceType.L_SIDE:
            return False
        # Col=9 must be R_SIDE only / Col=9はR_SIDEのみ
        if grid_x == 9 and device_type != DeviceType.R_SIDE:
            return False
        return True
```

---

## 📋 Implementation Phases / 実装フェーズ

### Phase 1: Core Architecture (1-2 days) / コアアーキテクチャ（1-2日）
1. ✅ LogicElement class / LogicElementクラス
2. ✅ GridDeviceManager class / GridDeviceManagerクラス
3. ✅ DeviceType enumeration / DeviceType列挙型
4. ✅ Basic grid operations / 基本グリッド操作
5. ✅ Bidirectional linking / 双方向リンク

### Phase 2: Electrical System (2-3 days) / 電気システム（2-3日）
1. ⚠️ ElectricalTracer class / ElectricalTracerクラス
2. ⚠️ Device power processing / デバイス電力処理
3. ⚠️ Contact logic / 接点論理
4. ⚠️ Coil logic / コイル論理
5. ⚠️ Power visualization / 電力可視化

### Phase 3: Visual System (1-2 days) / 視覚システム（1-2日）
1. ⚠️ SimpleRenderer class / SimpleRendererクラス
2. ⚠️ Sprite naming system / スプライト命名システム
3. ⚠️ State-based sprites / 状態ベーススプライト
4. ⚠️ Grid rendering / グリッド描画
5. ⚠️ Power flow colors / 電力フロー色

### Phase 4: Interaction (1 day) / インタラクション（1日）
1. 🔄 DeviceEditor class / DeviceEditorクラス
2. 🔄 Mouse handling / マウス処理
3. 🔄 Device palette / デバイスパレット
4. 🔄 Placement validation / 配置検証
5. 🔄 Device editing / デバイス編集

### Phase 5: Advanced Features (2-3 days) / 高度機能（2-3日）
1. 🔄 Timer functionality / タイマー機能
2. 🔄 Counter functionality / カウンター機能
3. 🔄 Vertical linking / 垂直リンク
4. 🔄 Wire devices / 配線デバイス
5. 🔄 Save/Load / 保存・読み込み

---

## 🎯 Success Criteria / 成功基準

### Functional / 機能要件
- ✅ 10x10 grid management / 10x10グリッド管理
- ⚠️ Left-to-right power tracing / 左→右電力トレース
- ⚠️ Real-time visualization / リアルタイム可視化
- 🔄 Mouse-based editing / マウスベース編集
- 🔄 Device support / デバイスサポート

### Performance / 性能要件
- 60 FPS simulation / 60FPSシミュレーション
- <16ms mouse response / <16msマウス応答
- <100MB memory usage / <100MBメモリ使用量
- <2s startup time / <2s起動時間

### Code Quality / コード品質
- Single-system architecture / 単一システムアーキテクチャ
- Clear responsibilities / 明確な責任
- Unit testable / ユニットテスト可能
- Easy extensibility / 容易な拡張性

---

## 📚 Reference Materials / 参考資料

- `ReMake_PlcSIm.txt`: Core requirements / コア要件
- `docs/SystemAndClass.md`: Current architecture / 現在のアーキテクチャ
- `docs/windsurf_refact.md`: Refactoring history / リファクタリング履歴
- `docs/● Update Todos.md`: Incomplete features / 未完成機能

---

## 🚀 Expected Benefits / 期待される効果

### Development / 開発効果
- **Reduced Complexity**: Single system eliminates confusion / 単一システムが混乱を排除
- **Faster Development**: Clear responsibilities speed implementation / 明確な責任が実装を加速
- **Easier Debugging**: Simplified logic reduces bugs / 簡素化論理がバグを削減
- **Better Maintenance**: Modular design supports long-term care / モジュラー設計が長期保守をサポート

### User / ユーザー効果
- **Intuitive Interface**: Grid matches real PLC diagrams / グリッドが実PLC図面と一致
- **Real-time Feedback**: Immediate visual response / 即座の視覚応答
- **Educational Value**: Clear power flow aids learning / 明確な電力フローが学習を支援
- **Reliability**: Simplified logic reduces unexpected behavior / 簡素化論理が予期しない動作を削減

---

## 📝 AI Implementation Notes / AI実装ノート

### Critical Points / 重要ポイント
1. **Grid Constraints**: Col=0 always L_SIDE, Col=9 always R_SIDE / グリッド制約
2. **Bidirectional Links**: Update both LEFT_DEV and RIGHT_DEV / 双方向リンク更新
3. **Power Direction**: Always left-to-right tracing / 常に左→右トレース
4. **State Separation**: Keep powered/active separate / 通電/動作状態分離
5. **Sprite Consistency**: Follow naming convention / 命名規則遵守

### Implementation Order / 実装順序
1. Start with LogicElement and GridDeviceManager / LogicElementとGridDeviceManagerから開始
2. Add basic electrical tracing / 基本電気トレース追加
3. Implement visual feedback / 視覚フィードバック実装
4. Add user interaction / ユーザーインタラクション追加
5. Extend with advanced features / 高度機能で拡張

---

**End of Document / ドキュメント終了**

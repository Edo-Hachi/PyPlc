# PyPlc Ver3 - タイマー・カウンター実装計画書

## 📋 **プロジェクト概要**
- **実装対象**: TON（Timer ON-Delay）・CTU（Counter UP）機能
- **PLC標準準拠**: 三菱PLC等実機と同等の動作・表示方式
- **推定総時間**: 5時間（6フェーズ構成）
- **品質基準**: WindSurf A+評価レベル維持

---


# ユーザー追加仕様（スプライトデータ）
# 以下スプライトを追加しました

   "72_0": {
      "x": 72,
      "y": 0,
      "NAME": "TIMER",
      "ACT_NAME": "TRUE"
    },
    "80_0": {
      "x": 80,
      "y": 0,
      "NAME": "TIMER",
      "ACT_NAME": "FALSE"
    },
    "88_0": {
      "x": 88,
      "y": 0,
      "NAME": "COUNTER",
      "ACT_NAME": "TRUE"
    },
    "96_0": {
      "x": 96,
      "y": 0,
      "NAME": "COUNTER",
      "ACT_NAME": "FALSE"
    }

# ------------------------------------


## 🎯 **6フェーズ実装計画**

### **Phase 1: データ構造・基盤拡張（推定45分）**

#### **1.1 PLCDeviceクラス拡張**
```python
# core/device_base.py 拡張予定
@dataclass
class PLCDevice:
    # 既存フィールド
    device_type: DeviceType
    position: tuple[int, int]  # (row, col)
    device_id: str
    is_energized: bool = False
    connections: Dict[str, tuple[int, int]] = field(default_factory=dict)
    
    # 新規追加フィールド
    preset_value: int = 0           # プリセット値（タイマー: 0.1秒単位、カウンター: 回数）
    current_value: int = 0          # 現在値
    timer_active: bool = False      # タイマー動作状態
    counter_previous_state: bool = False  # カウンター前回状態（エッジ検出用）
    last_update_time: float = 0.0   # 最終更新時刻（タイマー用）
```

#### **1.2 config.py更新**
```python
# DeviceType enum拡張
class DeviceType(Enum):
    # 既存デバイス
    CONTACT_A = "CONTACT_A"
    CONTACT_B = "CONTACT_B"
    COIL = "COIL"
    COIL_REV = "COIL_REV"
    LINK_HORZ = "LINK_HORZ"
    LINK_BRANCH = "LINK_BRANCH"
    LINK_VIRT = "LINK_VIRT"
    DEL = "DEL"
    
    # 新規追加
    TIMER_TON = "TIMER_TON"         # Timer ON-Delay
    COUNTER_CTU = "COUNTER_CTU"     # Counter UP

# タイマー・カウンター設定定数
class TimerCounterConfig:
    # タイマー仕様（PLC標準準拠）
    TIMER_MIN_VALUE: int = 0
    TIMER_MAX_VALUE: int = 32767    # 0-32767 (0.1秒単位)
    TIMER_UNIT: str = "0.1s"
    TIMER_DEFAULT_PRESET: int = 100  # デフォルト10.0秒
    
    # カウンター仕様（PLC標準準拠）
    COUNTER_MIN_VALUE: int = 0
    COUNTER_MAX_VALUE: int = 65535   # 0-65535 (回数)
    COUNTER_UNIT: str = "count"
    COUNTER_DEFAULT_PRESET: int = 10 # デフォルト10回
    
    # ID命名規則
    TIMER_ID_PREFIX: str = "T"       # T000-T255
    COUNTER_ID_PREFIX: str = "C"     # C000-C255
```

---

### **Phase 2: デバイスパレット統合（推定30分）**

#### **2.1 パレット定義更新**
```python
# config.py DEVICE_PALETTE_DEFINITIONS 更新
DEVICE_PALETTE_DEFINITIONS = [
    # 上段（既存）
    [
        PaletteDevice(DeviceType.CONTACT_A, "A-Contact", "1", 0),
        PaletteDevice(DeviceType.CONTACT_B, "B-Contact", "2", 0),
        PaletteDevice(DeviceType.COIL, "Coil", "3", 0),
        PaletteDevice(DeviceType.COIL_REV, "Rev-Coil", "4", 0),
        PaletteDevice(DeviceType.LINK_HORZ, "H-Link", "5", 0),
        PaletteDevice(DeviceType.LINK_BRANCH, "Branch", "6", 0),
        PaletteDevice(DeviceType.LINK_VIRT, "V-Link", "7", 0),
        PaletteDevice(DeviceType.DEL, "Delete", "8", 0),
        PaletteDevice(DeviceType.EMPTY, "", "9", 0),
        PaletteDevice(DeviceType.EMPTY, "", "0", 0)
    ],
    # 下段（新規有効化）
    [
        PaletteDevice(DeviceType.TIMER_TON, "Timer", "1", 1),
        PaletteDevice(DeviceType.COUNTER_CTU, "Counter", "2", 1),
        PaletteDevice(DeviceType.EMPTY, "", "3", 1),
        PaletteDevice(DeviceType.EMPTY, "", "4", 1),
        PaletteDevice(DeviceType.EMPTY, "", "5", 1),
        PaletteDevice(DeviceType.EMPTY, "", "6", 1),
        PaletteDevice(DeviceType.EMPTY, "", "7", 1),
        PaletteDevice(DeviceType.EMPTY, "", "8", 1),
        PaletteDevice(DeviceType.EMPTY, "", "9", 1),
        PaletteDevice(DeviceType.EMPTY, "", "0", 1)
    ]
]
```

#### **2.2 デバイス生成処理拡張**
```python
# main.py _create_device_with_default_id() 拡張
def _create_device_with_default_id(self, device_type: DeviceType, position: tuple[int, int]) -> PLCDevice:
    row, col = position
    
    if device_type == DeviceType.TIMER_TON:
        device_id = f"T{len([d for d in self.grid_system.get_all_devices() if d.device_type == DeviceType.TIMER_TON]):03d}"
        return PLCDevice(
            device_type=device_type,
            position=position,
            device_id=device_id,
            preset_value=TimerCounterConfig.TIMER_DEFAULT_PRESET
        )
    elif device_type == DeviceType.COUNTER_CTU:
        device_id = f"C{len([d for d in self.grid_system.get_all_devices() if d.device_type == DeviceType.COUNTER_CTU]):03d}"
        return PLCDevice(
            device_type=device_type,
            position=position,
            device_id=device_id,
            preset_value=TimerCounterConfig.COUNTER_DEFAULT_PRESET
        )
    # ... 既存処理
```

---

### **Phase 3: プリセット値編集ダイアログ拡張（推定60分）**

#### **3.1 DialogManager拡張**
```python
# dialogs/dialog_manager.py 拡張
class DialogManager:
    def show_device_edit_dialog(self, device: PLCDevice) -> Optional[Dict[str, any]]:
        """デバイス編集ダイアログ表示（ID + プリセット値対応）"""
        if device.device_type in [DeviceType.TIMER_TON, DeviceType.COUNTER_CTU]:
            return self._show_timer_counter_dialog(device)
        else:
            return self._show_device_id_dialog(device)
    
    def _show_timer_counter_dialog(self, device: PLCDevice) -> Optional[Dict[str, any]]:
        """タイマー・カウンター専用ダイアログ"""
        # ID編集 + プリセット値編集の統合ダイアログ
        pass
```

#### **3.2 バリデーション実装**
```python
# タイマープリセット値バリデーション
def _validate_timer_preset(self, value_str: str) -> tuple[bool, str, int]:
    """タイマープリセット値バリデーション (0-32767, 0.1秒単位)"""
    try:
        value = int(value_str)
        if TimerCounterConfig.TIMER_MIN_VALUE <= value <= TimerCounterConfig.TIMER_MAX_VALUE:
            return True, f"Set: {value * 0.1:.1f}s", value
        else:
            return False, f"Range: {TimerCounterConfig.TIMER_MIN_VALUE}-{TimerCounterConfig.TIMER_MAX_VALUE}", 0
    except ValueError:
        return False, "Input Error", 0

# カウンタープリセット値バリデーション  
def _validate_counter_preset(self, value_str: str) -> tuple[bool, str, int]:
    """カウンタープリセット値バリデーション (0-65535, 回数単位)"""
    try:
        value = int(value_str)
        if TimerCounterConfig.COUNTER_MIN_VALUE <= value <= TimerCounterConfig.COUNTER_MAX_VALUE:
            return True, f"Set: {value}count", value
        else:
            return False, f"Range: {TimerCounterConfig.COUNTER_MIN_VALUE}-{TimerCounterConfig.COUNTER_MAX_VALUE}", 0
    except ValueError:
        return False, "Input Error", 0
```

---

### **Phase 4: 回路解析エンジン統合（推定75分）**

#### **4.1 solve_ladder()拡張**
```python
# core/circuit_analyzer.py 拡張
class CircuitAnalyzer:
    def solve_ladder(self) -> None:
        """ラダー回路解析・実行（タイマー・カウンター対応）"""
        # 既存の回路解析処理
        self._analyze_basic_circuits()
        
        # 新規: タイマー・カウンター処理
        self._process_timers()
        self._process_counters()
        
        # 接点状態更新（タイマー・カウンター出力反映）
        self._update_contact_states_from_timers_counters()
    
    def _process_timers(self) -> None:
        """全タイマーの状態更新処理"""
        current_time = time.time()
        
        for device in self._get_devices_by_type(DeviceType.TIMER_TON):
            self._update_timer_ton(device, current_time)
    
    def _update_timer_ton(self, timer: PLCDevice, current_time: float) -> None:
        """TON（Timer ON-Delay）更新処理"""
        # 入力条件判定
        input_energized = self._is_timer_input_energized(timer)
        
        if input_energized and not timer.timer_active:
            # タイマー開始
            timer.timer_active = True
            timer.last_update_time = current_time
            timer.current_value = 0
            
        elif input_energized and timer.timer_active:
            # タイマー継続中
            elapsed_ms = int((current_time - timer.last_update_time) * 1000)
            elapsed_units = elapsed_ms // 100  # 0.1秒単位
            timer.current_value = min(elapsed_units, timer.preset_value)
            
            # プリセット値到達判定
            if timer.current_value >= timer.preset_value:
                timer.is_energized = True
            
        elif not input_energized:
            # タイマーリセット
            timer.timer_active = False
            timer.current_value = 0
            timer.is_energized = False
    
    def _process_counters(self) -> None:
        """全カウンターの状態更新処理"""
        for device in self._get_devices_by_type(DeviceType.COUNTER_CTU):
            self._update_counter_ctu(device)
    
    def _update_counter_ctu(self, counter: PLCDevice) -> None:
        """CTU（Counter UP）更新処理"""
        # 入力条件判定
        current_input = self._is_counter_input_energized(counter)
        
        # 立ち上がりエッジ検出
        if current_input and not counter.counter_previous_state:
            counter.current_value += 1
            
            # プリセット値到達判定
            if counter.current_value >= counter.preset_value:
                counter.is_energized = True
        
        # リセット条件判定
        if self._is_counter_reset_energized(counter):
            counter.current_value = 0
            counter.is_energized = False
        
        counter.counter_previous_state = current_input
```

#### **4.2 入力条件判定処理**
```python
def _is_timer_input_energized(self, timer: PLCDevice) -> bool:
    """タイマー入力条件判定"""
    # タイマーの左側接点チェーン解析
    return self._trace_input_conditions(timer.position)

def _is_counter_input_energized(self, counter: PLCDevice) -> bool:
    """カウンター入力条件判定"""
    # カウンターの左側接点チェーン解析
    return self._trace_input_conditions(counter.position)

def _is_counter_reset_energized(self, counter: PLCDevice) -> bool:
    """カウンターリセット条件判定"""
    # リセット入力の解析（将来拡張）
    return False
```

---

### **Phase 5: 現在値表示システム実装（推定45分）**

#### **5.1 デバイス描画拡張**
```python
# main.py draw()メソッド拡張
def _draw_timer_counter_overlay(self) -> None:
    """タイマー・カウンター現在値オーバーレイ表示"""
    for device in self.grid_system.get_all_devices():
        if device.device_type == DeviceType.TIMER_TON:
            self._draw_timer_overlay(device)
        elif device.device_type == DeviceType.COUNTER_CTU:
            self._draw_counter_overlay(device)

def _draw_timer_overlay(self, timer: PLCDevice) -> None:
    """タイマー現在値表示"""
    row, col = timer.position
    x = col * GridConfig.CELL_WIDTH + 2
    y = row * GridConfig.CELL_HEIGHT + 2
    
    # プリセット値 / 現在値表示
    preset_text = f"{timer.preset_value}"
    current_text = f"{timer.current_value}"
    
    # 背景矩形
    pyxel.rect(x, y, 28, 16, pyxel.COLOR_BLACK)
    pyxel.rectb(x, y, 28, 16, pyxel.COLOR_WHITE)
    
    # テキスト表示
    pyxel.text(x + 2, y + 2, f"T:{preset_text}", pyxel.COLOR_WHITE)
    pyxel.text(x + 2, y + 9, f"C:{current_text}", pyxel.COLOR_YELLOW if timer.timer_active else pyxel.COLOR_GRAY)

def _draw_counter_overlay(self, counter: PLCDevice) -> None:
    """カウンター現在値表示"""
    row, col = counter.position
    x = col * GridConfig.CELL_WIDTH + 2
    y = row * GridConfig.CELL_HEIGHT + 2
    
    # プリセット値 / 現在値表示
    preset_text = f"{counter.preset_value}"
    current_text = f"{counter.current_value}"
    
    # 背景矩形
    pyxel.rect(x, y, 28, 16, pyxel.COLOR_BLACK)
    pyxel.rectb(x, y, 28, 16, pyxel.COLOR_WHITE)
    
    # テキスト表示
    pyxel.text(x + 2, y + 2, f"P:{preset_text}", pyxel.COLOR_WHITE)
    pyxel.text(x + 2, y + 9, f"C:{current_text}", pyxel.COLOR_LIME if counter.is_energized else pyxel.COLOR_GRAY)
```

#### **5.2 ステータスバー拡張**
```python
def _draw_timer_counter_status(self) -> None:
    """タイマー・カウンター動作状態表示"""
    active_timers = [d for d in self.grid_system.get_all_devices() 
                    if d.device_type == DeviceType.TIMER_TON and d.timer_active]
    active_counters = [d for d in self.grid_system.get_all_devices() 
                      if d.device_type == DeviceType.COUNTER_CTU and d.current_value > 0]
    
    status_text = ""
    if active_timers:
        status_text += f"Timer Active: {len(active_timers)} "
    if active_counters:
        status_text += f"Counter Active: {len(active_counters)}"
    
    if status_text:
        pyxel.text(10, DisplayConfig.HEIGHT - 20, status_text, pyxel.COLOR_YELLOW)
```

---

### **Phase 6: 統合テスト・品質保証（推定45分）**

#### **6.1 基本動作テスト**
```python
# テストケース例
"""
基本タイマー回路テスト:
X000 --- [TON T000] --- Y000
         (10.0秒)

期待動作:
- X000 ON → 10秒後 → Y000 ON
- X000 OFF → 即座に → Y000 OFF, T000リセット
"""

"""
基本カウンター回路テスト:
X001 --- [CTU C000] --- Y001
         (5回)

期待動作:
- X001の5回目立ち上がり → Y001 ON
- リセット条件 → Y001 OFF, C000リセット
"""
```

#### **6.2 複合回路テスト**
```python
"""
複合回路テスト:
X000 --- [TON T000] --- [CTU C000] --- Y000
         (5.0秒)        (3回)

期待動作:
- X000 ON → 5秒後 → T000出力 → C000カウント開始
- T000出力の3回目立ち上がり → Y000 ON
"""
```

#### **6.3 パフォーマンス・品質確認**
- 30FPS維持確認
- メモリ使用量測定
- エラーハンドリング確認
- WindSurf A+評価レベル維持確認

---

## ✅ **実装完了チェックリスト**

### **Phase 1: データ構造・基盤拡張**
- [ ] PLCDeviceクラス拡張（preset_value, current_value等）
- [ ] config.py更新（TIMER_TON, COUNTER_CTU, TimerCounterConfig）

### **Phase 2: デバイスパレット統合**
- [ ] パレット定義更新（下段有効化）
- [ ] デバイス生成処理拡張

### **Phase 3: プリセット値編集ダイアログ拡張**
- [ ] DialogManager拡張（統合ダイアログ）
- [ ] タイマーバリデーション（0-32767, 0.1秒単位）
- [ ] カウンターバリデーション（0-65535, 回数単位）

### **Phase 4: 回路解析エンジン統合**
- [ ] solve_ladder()拡張（_process_timers, _process_counters）
- [ ] TON動作ロジック実装
- [ ] CTU動作ロジック実装（エッジ検出）
- [ ] 入力条件判定処理

### **Phase 5: 現在値表示システム**
- [ ] タイマー・カウンターオーバーレイ表示
- [ ] ステータスバー拡張

### **Phase 6: 統合テスト・品質保証**
- [ ] 基本動作テスト（タイマー・カウンター単体）
- [ ] 複合回路テスト
- [ ] パフォーマンス確認（30FPS維持）
- [ ] ドキュメント更新（CLAUDE.md）

---

## 🎯 **期待効果**

### **教育的価値向上**
- **実PLC準拠**: TON/CTU動作の正確な学習
- **時間制御学習**: 自動点滅、遅延動作の理解
- **シーケンス制御**: 生産ライン等の実用的制御学習

### **実用性向上**
- **自動化対応**: タイマーベース自動制御
- **生産管理**: カウンターによる数量管理
- **複合制御**: タイマー・カウンター組み合わせ回路

### **PLC完成度向上**
- **基本3要素完備**: 接点・コイル・タイマー/カウンター
- **商用レベル**: 実PLC環境への移行容易性
- **WindSurf A+評価**: 品質基準維持

---

**実装準備完了 - Phase 1開始承認をお待ちしております**

*作成日: 2025-08-07*  
*推定完了日: 2025-08-07 (同日完了予定)*  
*品質目標: WindSurf A+評価レベル維持*
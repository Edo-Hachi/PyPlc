# PyPlc Ver3 タイマー・カウンター実装プラン

## 📋 **プロジェクト概要**

**目標**: PLC標準準拠タイマー・カウンター機能の完全実装  
**アーキテクチャ**: 既存インフラ（DialogManager、DevicePalette、CircuitAnalyzer）を最大活用  
**効果**: PLC教育価値の大幅向上・実用レベル回路対応

---

## 🔍 **現状分析**

### **実装済みインフラ**
- ✅ **基本デバイスシステム**: PLCDevice、DeviceType.TIMER/COUNTER定義
- ✅ **ダイアログシステム**: DialogManager統合管理・デバイスID編集対応
- ✅ **デバイスパレット**: bottom_row準備済み（Shift+1/2キー待機状態）
- ✅ **回路解析エンジン**: CircuitAnalyzer.solve_ladder()・通電トレース完備
- ✅ **設定管理**: config.py内DEFAULT_TIMER_PRESET/COUNTER_PRESET定義済み

### **未実装要素**
- ⚠️ **タイマー・カウンター固有ロジック**: 時間制御・回数制御
- ⚠️ **デバイスパレット統合**: EMPTY状態からの有効化
- ⚠️ **プリセット値編集ダイアログ**: DialogManager拡張
- ⚠️ **現在値表示システム**: UI表示機能
- ⚠️ **回路解析統合**: solve_ladder()への組み込み

---

## 🎯 **実装戦略**

### **PLC標準準拠設計**
```python
# タイマー仕様（TON: Timer ON-Delay）
"""
入力条件: 起動接点（通電でタイマー開始）
動作: プリセット時間経過後、接点をONに変更
リセット: 起動接点OFF時、タイマー停止・現在値リセット
表示: T001 (現在値/プリセット値) 例: T001 (2.5/3.0)
"""

# カウンター仕様（CTU: Counter UP）
"""
入力条件: カウント接点（立ち上がりエッジでカウント）
動作: プリセット回数到達後、接点をONに変更  
リセット: リセット接点ON時、カウンター停止・現在値リセット
表示: C001 (現在値/プリセット値) 例: C001 (3/5)
"""
```

### **既存インフラ活用方針**
- **PLCDevice拡張**: 現在値・プリセット値・前回状態フィールド追加
- **DialogManager拡張**: プリセット値編集ダイアログ追加
- **CircuitAnalyzer統合**: solve_ladder()内でタイマー/カウンター更新処理追加
- **DevicePalette有効化**: bottom_row EMPTY → TIMER/COUNTER変更

---

## 📋 **6フェーズ実装プラン**

### **Phase 1: データ構造・基盤拡張（推定時間: 45分）**
**作業内容**:
- `core/device_base.py`拡張: PLCDevice にタイマー・カウンター専用フィールド追加
- `config.py`拡張: TimerConfig、CounterConfigクラス追加
- データ構造検証・基本テスト実施

**詳細仕様**:
```python
# PLCDevice拡張フィールド
@dataclass
class PLCDevice:
    # 既存フィールド + 以下を追加
    current_value: float = 0.0        # タイマー現在値(秒)/カウンター現在値(回数)
    preset_value: float = 0.0         # プリセット値  
    prev_input_state: bool = False    # 前回スキャン時の入力状態（エッジ検出用）
    is_timing: bool = False          # タイマー動作中フラグ
    last_update_time: float = 0.0    # 最終更新時刻（タイマー用）
```

### **Phase 2: デバイスパレット統合（推定時間: 30分）**
**作業内容**:
- `config.py`のDEVICE_PALETTE_DEFINITIONS更新
- `core/device_palette.py`でTIMER/COUNTER有効化
- Shift+1/2キー動作確認・テスト

**詳細仕様**:
```python
# config.py更新
"bottom_row": [
    (DeviceType.TIMER, "TIMER", 1, "Timer ON-Delay"),     # Shift+1
    (DeviceType.COUNTER, "COUNTR", 2, "Counter UP"),      # Shift+2
    (DeviceType.EMPTY, "", 3, "UNDEF"),
    # 以下同様...
]
```

### **Phase 3: プリセット値編集ダイアログ拡張（推定時間: 60分）**  
**作業内容**:
- `dialogs/device_id_dialog.py`拡張: プリセット値入力フィールド追加
- `dialogs/dialog_manager.py`拡張: タイマー/カウンター専用ダイアログ処理
- ダイアログUI改良・バリデーション強化

**詳細仕様**:
```python
# DeviceIDDialog拡張
class DeviceIDDialog:
    def __init__(self, device_type: DeviceType, current_id: str = "", preset_value: float = 0.0):
        # 既存初期化 + プリセット値フィールド追加
        self.preset_value = preset_value
        self.preset_input = str(preset_value)
        self.preset_field_rect = (x, y, width, height)  # プリセット値入力欄
        
    def _draw_preset_field(self):
        # プリセット値入力欄描画
        
    def _validate_preset_value(self):
        # タイマー: 0.1-999.9秒, カウンター: 1-9999回
```

### **Phase 4: 回路解析エンジン統合（推定時間: 75分）**
**作業内容**:
- `core/circuit_analyzer.py`拡張: タイマー・カウンター更新ロジック追加
- solve_ladder()内でのタイマー/カウンター処理統合
- 時間管理・エッジ検出・プリセット判定実装

**詳細仕様**:
```python
class CircuitAnalyzer:
    def solve_ladder(self) -> None:
        # 既存処理
        self._update_contact_states_from_coils()
        
        # 新規追加: タイマー・カウンター処理
        self._update_timers()
        self._update_counters()
        
    def _update_timers(self) -> None:
        """全タイマーデバイスの更新処理"""
        current_time = time.time()
        for device in self._get_timer_devices():
            # 入力条件確認・タイマー更新・プリセット判定
            
    def _update_counters(self) -> None:
        """全カウンターデバイスの更新処理"""
        for device in self._get_counter_devices():
            # 入力エッジ検出・カウント更新・プリセット判定
```

### **Phase 5: 現在値表示システム実装（推定時間: 45分）**
**作業内容**:
- `core/grid_system.py`拡張: タイマー・カウンター表示機能追加
- デバイス描画時の現在値/プリセット値表示
- UI表示の最適化・視認性向上

**詳細仕様**:
```python
# グリッド描画拡張
def _draw_timer_device(self, device: PLCDevice, x: int, y: int):
    # タイマーシンボル描画
    pyxel.rectb(x, y, 14, 14, pyxel.COLOR_CYAN)
    pyxel.text(x+2, y+2, "T", pyxel.COLOR_WHITE)
    
    # 現在値/プリセット値表示
    value_text = f"{device.current_value:.1f}/{device.preset_value:.1f}"
    pyxel.text(x, y-8, value_text, pyxel.COLOR_GRAY)
    
    # 動作状態表示（色分け）
    color = pyxel.COLOR_GREEN if device.state else pyxel.COLOR_GRAY
```

### **Phase 6: 統合テスト・品質保証（推定時間: 45分）**
**作業内容**:
- 全機能統合テスト・動作確認
- タイマー・カウンター基本回路テストケース作成
- パフォーマンス検証・最適化
- ドキュメント更新（CLAUDE.md）

**テストケース例**:
```
Test Case 1: 基本タイマー動作
- X000接点 → T001タイマー(3.0秒) → Y000コイル
- 期待動作: X000 ON後3秒でY000 ON

Test Case 2: 基本カウンター動作  
- X001接点 → C001カウンター(5回) → Y001コイル
- 期待動作: X001の5回目立ち上がりでY001 ON

Test Case 3: 複合回路
- タイマー・カウンター・接点・コイルの組み合わせ回路
```

---

## 🏗️ **詳細技術仕様**

### **PLCDevice拡張仕様**
```python
@dataclass
class PLCDevice:
    # 既存フィールド（変更なし）
    device_type: DeviceType
    position: Tuple[int, int]
    address: str
    state: bool = False
    is_energized: bool = False
    connections: Dict[str, Optional[Tuple[int, int]]] = field(default_factory=dict)
    
    # タイマー・カウンター専用フィールド（新規追加）
    current_value: float = 0.0        # 現在値（タイマー:秒、カウンター:回数）
    preset_value: float = 0.0         # プリセット値
    prev_input_state: bool = False    # 前回入力状態（エッジ検出用）
    is_timing: bool = False          # 動作中フラグ（タイマー専用）
    last_update_time: float = 0.0    # 最終更新時刻（タイマー専用）
```

### **タイマー動作アルゴリズム（TON: Timer ON-Delay）**
```python
def _update_timer(self, timer_device: PLCDevice, input_energized: bool) -> None:
    """タイマーデバイス更新処理"""
    current_time = time.time()
    
    if input_energized and not timer_device.prev_input_state:
        # 立ち上がりエッジ: タイマー開始
        timer_device.is_timing = True
        timer_device.current_value = 0.0
        timer_device.last_update_time = current_time
        
    elif input_energized and timer_device.is_timing:
        # タイマー動作中: 現在値更新
        elapsed = current_time - timer_device.last_update_time
        timer_device.current_value += elapsed
        timer_device.last_update_time = current_time
        
        # プリセット値到達判定
        if timer_device.current_value >= timer_device.preset_value:
            timer_device.state = True  # タイマー接点ON
            
    elif not input_energized:
        # 入力OFF: タイマーリセット
        timer_device.is_timing = False
        timer_device.current_value = 0.0
        timer_device.state = False
    
    timer_device.prev_input_state = input_energized
```

### **カウンター動作アルゴリズム（CTU: Counter UP）**
```python
def _update_counter(self, counter_device: PLCDevice, input_energized: bool, reset_energized: bool = False) -> None:
    """カウンターデバイス更新処理"""
    
    if reset_energized:
        # リセット入力: カウンター初期化
        counter_device.current_value = 0.0
        counter_device.state = False
        
    elif input_energized and not counter_device.prev_input_state:
        # 立ち上がりエッジ: カウントアップ
        counter_device.current_value += 1
        
        # プリセット値到達判定
        if counter_device.current_value >= counter_device.preset_value:
            counter_device.state = True  # カウンター接点ON
    
    counter_device.prev_input_state = input_energized
```

### **プリセット値編集ダイアログ拡張仕様**
```python
class DeviceIDDialog:
    def __init__(self, device_type: DeviceType, current_id: str = "", preset_value: float = 0.0):
        # 既存初期化
        self.device_type = device_type
        self.current_id = current_id
        
        # プリセット値関連（新規追加）
        self.preset_value = preset_value
        self.preset_input = str(preset_value) if preset_value > 0 else ""
        self.preset_cursor_pos = len(self.preset_input)
        
        # UI配置調整
        self.dialog_height = 180  # ダイアログ高さ拡張（プリセット値欄用）
        self.preset_field_rect = (self.dialog_x + 20, self.dialog_y + 100, 180, 20)
        
    def _draw_preset_field(self):
        """プリセット値入力フィールド描画"""
        if self.device_type in [DeviceType.TIMER, DeviceType.COUNTER]:
            # プリセット値ラベル
            label = "Preset Value:" if self.device_type == DeviceType.TIMER else "Preset Count:"
            pyxel.text(self.dialog_x + 10, self.dialog_y + 85, label, pyxel.COLOR_CYAN)
            
            # 入力フィールド背景・枠
            pyxel.rect(self.preset_field_rect[0], self.preset_field_rect[1], 
                      self.preset_field_rect[2], self.preset_field_rect[3], pyxel.COLOR_WHITE)
            pyxel.rectb(self.preset_field_rect[0], self.preset_field_rect[1], 
                       self.preset_field_rect[2], self.preset_field_rect[3], pyxel.COLOR_BLACK)
            
            # プリセット値テキスト・カーソル
            text_x = self.preset_field_rect[0] + 4
            text_y = self.preset_field_rect[1] + 6
            pyxel.text(text_x, text_y, self.preset_input, pyxel.COLOR_BLACK)
```

---

## 📊 **期待される効果**

### **PLC教育価値向上**
- **時間制御学習**: 実際のPLCと同等のタイマー動作体験
- **回数制御学習**: カウンター機能による反復動作理解
- **複合回路学習**: タイマー・カウンター組み合わせ回路対応

### **実用性向上**
```
実装後対応可能な基本回路例:
1. 自動点滅回路（タイマー + 自己保持）
2. 設備起動シーケンス（タイマー連鎖）
3. 生産個数カウンター（カウンター + リセット）
4. 異常検出タイマー（遅延動作検出）
5. バッチ処理制御（タイマー・カウンター複合）
```

### **技術的成果**
- **コード品質**: 既存A+評価基準維持・拡張
- **アーキテクチャ**: モジュール化設計・責任分離継続
- **パフォーマンス**: 30FPS安定動作維持（軽量実装）

---

## ⚠️ **リスク分析と対策**

### **潜在的リスク**
1. **時間管理の精度**: Pyxelフレームレート依存の時間計測精度
2. **メモリ使用量**: タイマー・カウンター専用フィールド追加によるメモリ増加
3. **UI複雑化**: プリセット値表示による画面レイアウトの複雑化

### **対策**
1. **高精度時間管理**: `time.time()`活用・フレームレート非依存実装
2. **メモリ最適化**: 必要時のみフィールド使用・効率的なデータ構造
3. **UI最適化**: コンパクトな表示・視認性重視のデザイン

---

## 🧪 **テスト戦略**

### **単体テスト**
- [ ] PLCDevice拡張フィールドの動作確認
- [ ] タイマー動作アルゴリズム精度検証
- [ ] カウンター動作アルゴリズム正確性確認
- [ ] プリセット値ダイアログ入力・バリデーション

### **統合テスト**
- [ ] デバイスパレット配置・プリセット設定・動作確認
- [ ] 回路解析エンジンとの統合動作
- [ ] 複合回路（タイマー+カウンター）動作確認

### **実用テスト**
- [ ] PLC標準回路パターン動作確認
- [ ] 長時間動作安定性確認
- [ ] UI/UX操作性確認

---

## 📈 **成功指標**

### **定量的指標**
- デバイスパレット有効化: bottom_row EMPTY 2個 → TIMER/COUNTER 2個
- ダイアログ機能拡張: プリセット値編集・バリデーション対応
- 回路解析統合: solve_ladder()へのタイマー・カウンター処理組み込み
- テスト成功率: 全テストケース100%成功

### **定性的指標**
- PLC標準動作完全準拠
- 実用回路パターン対応
- 教育効果大幅向上
- WindSurf A+評価基準維持

---

## ⏱️ **実装スケジュール**

| Phase | 作業内容 | 推定時間 | 累計時間 |
|-------|----------|----------|----------|
| Phase 1 | データ構造・基盤拡張 | 45分 | 45分 |
| Phase 2 | デバイスパレット統合 | 30分 | 1時間15分 |
| Phase 3 | プリセット値編集ダイアログ拡張 | 60分 | 2時間15分 |
| Phase 4 | 回路解析エンジン統合 | 75分 | 3時間30分 |
| Phase 5 | 現在値表示システム実装 | 45分 | 4時間15分 |
| Phase 6 | 統合テスト・品質保証 | 45分 | **5時間00分** |

**総実装時間**: 約5時間

---

## 🔄 **Ver3設計思想との整合性**

### **PLC標準準拠継続**
- タイマー・カウンター仕様は実PLC完全準拠
- デバイスアドレス体系（T001, C001等）維持
- 動作アルゴリズムは三菱PLC等と同等

### **シンプル・軽量維持** 
- 外部依存なし（Pyxelのみ）
- 既存インフラ最大活用
- 軽量データ構造・効率的アルゴリズム

### **教育価値最大化**
- 実PLC移行時の違和感なし
- 基本から応用まで段階的学習対応
- 視覚的理解促進（現在値表示・動作状態色分け）

---

## 📝 **実装準備完了**

このタイマー・カウンター実装プランは以下の状況で実行可能です：

- ✅ **詳細設計完了**: 全6フェーズの技術仕様確定
- ✅ **既存システム分析**: インフラ活用方針決定
- ✅ **リスク評価**: 対策・テスト戦略策定
- ✅ **品質保証**: WindSurf A+評価基準維持設計

---

**プラン作成日**: 2025-08-06  
**推定総実装時間**: 約5時間  
**実装準備**: 完了（詳細設計・技術仕様・テスト戦略確定）

---

## 🚀 **実行承認待ち**

このタイマー・カウンター実装プランをご確認ください。  
**承認をいただき次第、Phase 1から実装を開始します。**

または、プラン修正・他の優先課題への変更も承ります。
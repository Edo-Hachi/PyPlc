# Ver3 Edit/Run Mode Implementation Plan

**作成日**: 2025-08-03  
**基準分析**: Project Ver01/ Edit/Runモード実装の詳細分析  
**目標**: Ver3への高品質なEdit/Runモードシステム統合

---

## 📊 **Ver1実装分析結果**

### **実装されていた主要機能**

#### **1. モード管理システム (config.py)**
```python
class SimulatorMode(Enum):
    EDIT = "EDIT"        # 回路構築モード
    RUN = "RUN"          # シミュレーション実行モード
    DIALOG = "DIALOG"    # モーダルダイアログ有効

class PLCRunState(Enum):
    STOPPED = "STOPPED"  # 停止中
    RUNNING = "RUNNING"  # 実行中
```

#### **2. キー操作制御 (main.py 188-201行)**
```python
# TABキーでEDIT/RUN切り替え
if pyxel.btnp(pyxel.KEY_TAB):
    if self.current_mode == SimulatorMode.EDIT:
        self.current_mode = SimulatorMode.RUN
    elif self.current_mode == SimulatorMode.RUN:
        self.current_mode = SimulatorMode.EDIT

# F5キーでPLC実行制御（RUNモードのみ）
if pyxel.btnp(pyxel.KEY_F5) and self.current_mode == SimulatorMode.RUN:
    if self.plc_run_state == PLCRunState.STOPPED:
        self.plc_run_state = PLCRunState.RUNNING
    else:
        self.plc_run_state = PLCRunState.STOPPED
        self._reset_all_systems()
```

#### **3. マウス処理の分離 (main.py 147-174行)**
```python
# EDITモード: デバイス配置・設定
if self.current_mode == SimulatorMode.EDIT:
    mouse_result = self.mouse_handler.handle_mouse_input(...)
    # デバイス配置・設定ダイアログ表示

# RUNモード: デバイス操作のみ
elif self.current_mode == SimulatorMode.RUN:
    mouse_result = self.mouse_handler.handle_run_mode_input(...)
    # デバイス操作（A接点ON/OFF、PLCブレイク等）
```

#### **4. UI表示システム (ui_components.py 277-301行)**
```python
def draw_status_bar(self, current_mode: SimulatorMode, plc_run_state: PLCRunState):
    # モード表示（右端）
    mode_text = current_mode.value
    mode_color = Colors.MODE_EDIT if current_mode == SimulatorMode.EDIT else Colors.MODE_RUN
    
    # PLC実行状態表示（中央）
    if current_mode == SimulatorMode.RUN:
        plc_text = f"PLC: {plc_run_state.value}"
        plc_color = Colors.PLC_RUNNING if plc_run_state == PLCRunState.RUNNING else Colors.PLC_STOPPED
        
        # F5キーヒント表示
        hint_text = "F5:Start" if plc_run_state == PLCRunState.STOPPED else "F5:Stop"
```

#### **5. システムリセット機能 (main.py 306-322行)**
```python
def _reset_all_systems(self):
    """F5ストップ時の全システム初期化"""
    self.device_manager.reset_all_devices()
    self.grid_device_manager.reset_all_devices()
    self.electrical_system.reset_electrical_state()
    self.grid_device_manager.update_all_devices(self.device_manager)
```

---

## 🎯 **Ver3実装戦略**

### **実装アプローチ: 段階的統合**

#### **Phase 1: 基本モード管理システム**
**目標**: Edit/Runモード切り替えの基本機能実装

**Step 1**: `config.py`にモード定義追加
```python
# Ver3 config.py拡張
class SimulatorMode(Enum):
    EDIT = "EDIT"
    RUN = "RUN"

class PLCRunState(Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
```

**Step 2**: `main.py`にモード状態管理追加
```python
# PLCSimulator.__init__()に追加
self.current_mode = SimulatorMode.EDIT
self.plc_run_state = PLCRunState.STOPPED
```

**Step 3**: TABキーでのモード切り替え実装
```python
def _handle_keyboard_input(self):
    # TABキーでEDIT/RUN切り替え
    if pyxel.btnp(pyxel.KEY_TAB):
        if self.current_mode == SimulatorMode.EDIT:
            self.current_mode = SimulatorMode.RUN
        else:
            self.current_mode = SimulatorMode.EDIT
```

#### **Phase 2: UI表示システム統合**
**目標**: モード・実行状態の視覚的フィードバック

**Step 4**: ステータスバー描画機能実装
```python
def _draw_status_bar(self):
    """ステータスバー描画（画面下部）"""
    # モード表示（右端）
    mode_text = self.current_mode.value
    mode_color = pyxel.COLOR_YELLOW if self.current_mode == SimulatorMode.EDIT else pyxel.COLOR_LIME
    
    # PLC実行状態表示（中央）
    if self.current_mode == SimulatorMode.RUN:
        plc_text = f"PLC: {self.plc_run_state.value}"
        plc_color = pyxel.COLOR_LIME if self.plc_run_state == PLCRunState.RUNNING else pyxel.COLOR_RED
```

**Step 5**: `main.py draw()`にステータスバー統合

#### **Phase 3: F5実行制御システム**
**目標**: PLC実行・停止機能の実装

**Step 6**: F5キーでのPLC制御実装
```python
# RUNモード時のF5キー処理
if pyxel.btnp(pyxel.KEY_F5) and self.current_mode == SimulatorMode.RUN:
    if self.plc_run_state == PLCRunState.STOPPED:
        self.plc_run_state = PLCRunState.RUNNING
    else:
        self.plc_run_state = PLCRunState.STOPPED
        self._reset_all_systems()
```

**Step 7**: システムリセット機能実装
```python
def _reset_all_systems(self):
    """F5ストップ時の全デバイス・回路状態リセット"""
    # 回路解析エンジンリセット
    # グリッドシステムリセット
    # デバイス状態リセット
```

#### **Phase 4: モード別マウス処理**
**目標**: Edit/Runモードでの異なるマウス動作

**Step 8**: EDITモード処理
- デバイス配置・削除
- 右クリックでデバイス設定（将来機能）

**Step 9**: RUNモード処理  
- 左クリック無効化（配置禁止）
- 右クリックでデバイス操作（接点ON/OFF等）

#### **Phase 5: 回路実行制御統合**
**目標**: PLC実行状態での回路解析制御

**Step 10**: 実行状態別の処理分岐
```python
def update(self):
    # PLC実行中の場合のみ回路解析実行
    if (self.current_mode == SimulatorMode.RUN and 
        self.plc_run_state == PLCRunState.RUNNING):
        self.circuit_analyzer.solve_ladder()
    # EDITモードまたは停止中は解析停止
```

---

## 🔧 **Ver3実装上の考慮事項**

### **既存システムとの統合**

#### **現在のVer3アーキテクチャとの適合性**
- **core/input_handler.py**: モード別入力処理の統合
- **core/circuit_analyzer.py**: 実行状態による解析制御  
- **main.py**: モード管理の中央制御
- **config.py**: 定数・Enum定義の拡張

#### **Ver3の優位性を維持**
- **並列回路合流ロジック**: Ver1にない高度な回路解析
- **GEMINI設計**: PLCDevice + connections による優れたデータ構造
- **座標系統一**: Ver1の問題を解決済み
- **スプライトシステム**: 効率的な描画システム

### **実装時の注意点**

#### **1. 段階的実装**
- 既存機能を破綻させない慎重な統合
- 各フェーズでの動作確認必須

#### **2. UI設計**
- Ver3の30FPS・384x384画面での最適レイアウト
- 既存UIとの統合（デバイスパレット等）

#### **3. パフォーマンス**
- モード切り替え時の処理負荷最小化
- 実行状態による効率的な処理分岐

---

## 📋 **実装優先順位**

### **Phase 1: 基本モード管理（最優先）**
**期間**: 30-45分  
**リスク**: 低  
**効果**: 即座にEdit/Run概念を導入

### **Phase 2: UI表示システム（高優先）**
**期間**: 30-45分  
**リスク**: 低  
**効果**: ユーザビリティ大幅向上

### **Phase 3: F5実行制御（高優先）**  
**期間**: 45-60分  
**リスク**: 中（システムリセット実装）  
**効果**: 実用的なPLC操作感実現

### **Phase 4-5: 高度機能（中優先）**
**期間**: 60-90分  
**リスク**: 中  
**効果**: Ver1レベルの操作性達成

---

## 🎯 **期待される効果**

### **ユーザビリティ向上**
- **明確なモード分離**: 編集と実行の概念的分離
- **安全な操作**: 実行中の誤配置防止
- **直感的操作**: TAB/F5キーによる素早いモード切り替え

### **教育効果向上**
- **実PLC準拠**: 実際のPLCのEdit/Run概念と整合
- **段階的学習**: 回路構築→実行→デバッグの流れ
- **可視化強化**: モード・状態の明確な表示

### **開発継続性**
- **Ver1の優れた設計の継承**: 実証済みのモード管理システム
- **Ver3の技術的優位性維持**: 高度な回路解析＋優れたUI
- **将来拡張への基盤**: データ保存・読み込み等への発展

---

## 📝 **実装セッション計画**

### **Session 1: 基本システム実装**
1. **config.py拡張**: モード・状態定義追加
2. **main.py統合**: モード管理変数・TABキー処理
3. **基本動作確認**: モード切り替えテスト

### **Session 2: UI・制御システム**
1. **ステータスバー実装**: モード・状態表示
2. **F5キー制御**: PLC実行・停止機能
3. **統合テスト**: 全体動作確認

### **Session 3: 高度機能・最適化**
1. **モード別マウス処理**: Edit/Run分離
2. **システムリセット**: 完全な状態初期化
3. **品質保証**: パフォーマンス・安定性確認

---

## 🏆 **成功基準**

### **Phase 1完了基準**
- [x] TABキーでEdit/Run切り替え動作
- [x] 画面表示でモード確認可能
- [x] 既存機能の完全保持

### **最終完了基準**  
- [ ] Ver1と同等のEdit/Run操作感実現
- [ ] F5でのPLC実行制御完全動作
- [ ] 30FPS安定動作維持
- [ ] Ver3の技術的優位性保持

**Ver3は、Ver1の優れたUI設計とVer3の高度な技術を融合した、最高品質のPLCシミュレーターとなる。**

---

*最終更新: 2025-08-03*  
*次回更新: Edit/Runモード実装完了時*  
*参考実装: Project Ver01/ (main.py, ui_components.py, config.py)*
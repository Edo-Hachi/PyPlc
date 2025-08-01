# PyPlc Ver3 システム定義書
# 作成日: 2025-01-28
# 対象: AI開発支援・完全理解用定義

## 🎯 **Ver3の設計思想**

### **基本概念**
PyPlc Ver3は**PLC標準仕様完全準拠**を最優先とし、教育的価値と実用性を両立するラダー図シミュレーターです。

### **Ver1/Ver2からの進化**
- **Ver1**: プロトタイプ（内部データと表示の不整合問題）
- **Ver2**: モジュール化・安定化（INCOIL/OUTCOIL概念の混乱）
- **Ver3**: PLC標準準拠・教育効果最大化

---

## 📋 **1. デバイス体系定義**

### **1.1 PLC標準デバイス分類**

#### **接点系（入力条件表現）**
```python
# PLC標準記法準拠
class ContactDevice:
    """接点は入力条件を表現する"""
    
    # A接点（ノーマルオープン）
    TYPE_A: str = "TYPE_A"
    plc_notation: str = "-| |-"
    logic: str = "デバイス値True時に導通ON"
    
    # B接点（ノーマルクローズ）  
    TYPE_B: str = "TYPE_B"
    plc_notation: str = "-|/|-"
    logic: str = "デバイス値False時に導通ON（反転論理）"
```

#### **コイル系（出力結果表現）**
```python
# PLC標準記法準拠
class CoilDevice:
    """コイルは出力結果を表現する"""
    
    # 通常コイル
    COIL: str = "COIL"
    plc_notation: str = "-( )-"
    logic: str = "入力条件True時にコイル励磁"
    
    # 反転コイル
    COIL_REV: str = "COIL_REV"
    plc_notation: str = "-(/)-"
    logic: str = "入力条件True時にコイル非励磁（安全回路用）"
```

### **1.2 Ver2からの重要な概念変更**

#### **❌ Ver2の問題のある概念（廃止）**
```python
# Ver2で混乱を招いた概念 - Ver3では完全廃止
INCOIL = "INCOIL"          # ❌ 入力コイル（PLC標準にない概念）
OUTCOIL_NML = "OUTCOIL_NML" # ❌ 出力コイル（用語が不適切）
OUTCOIL_REV = "OUTCOIL_REV" # ❌ 反転出力コイル（概念混乱）

# 問題点:
# 1. 同一デバイス（Y001）が「入力コイル」と「出力コイル」の二重実体
# 2. PLC教育的観点から不適切な用語体系
# 3. 実PLC仕様との乖離による学習阻害
```

#### **✅ Ver3の正しい概念（新規実装）**
```python
# PLC標準準拠の正しい概念
class PLCStandardDevice:
    # 接点: 他のデバイスの状態を読み取る
    contact_y001 = ContactDevice(address="Y001", type="TYPE_A")  # Y001の状態を読む
    
    # コイル: デバイスの状態を設定する
    coil_y001 = CoilDevice(address="Y001", type="COIL")  # Y001の状態を設定
    
    # 論理関係:
    # if contact_y001.read() == True:  # Y001接点がONなら
    #     coil_y002.set(True)          # Y002コイルを励磁
```

---

## 📋 **2. 回路構造定義**

### **2.1 電気的継続性システム**

#### **Ver3の明示的配線システム**
```python
class CircuitConnection:
    """Ver3: すべての配線を明示的オブジェクト化"""
    
    # 水平配線（Ver3新機能）
    LINK_SIDE: str = "LINK_SIDE"
    purpose: str = "デバイス間の水平接続を明示的に表現"
    necessity: str = "自己保持回路の正確な動作に必須"
    
    # 垂直配線（Ver2から継承）
    LINK_UP: str = "LINK_UP"      # 上方向接続点
    LINK_DOWN: str = "LINK_DOWN"  # 下方向接続点
    pairing: str = "LINK_UP ↔ LINK_DOWN ペアで垂直接続形成"
```

#### **Ver2の問題点と解決**
```python
# ❌ Ver2の暗黙配線（自己保持回路が動作しない）
"""
[X001] ---- [Y001_INPUT] ---- [Y001_OUTPUT] ---- [X002]
   |                                                 |
   +----------- (暗黙の水平配線) -------------------+
   
問題: 暗黙配線のため電気的経路が認識されない
```

```python
# ✅ Ver3の明示的配線（自己保持回路が正確に動作）
"""
[X001]--[LINK_SIDE]--[Y001_COIL]--[LINK_SIDE]--[Y001_CONTACT]--[LINK_SIDE]--[X002]
   |                                                                              |
   +--[LINK_SIDE]--[LINK_SIDE]--[LINK_SIDE]--[LINK_SIDE]--[LINK_SIDE]--[LINK_SIDE]+
   
解決: 明示的LINK_SIDEにより電気的経路を完全にトレース可能
```

### **2.2 グリッド座標系（Ver1の教訓を活用）**

#### **Ver1の重大な問題（Ver3で完全解決）**
```python
# Ver1の問題: 内部データと表示データの齟齬
internal_data[row][col]  # 内部: [y座標][x座標]
display_pos(x, y)        # 表示: (x座標, y座標)
# → 座標変換でバグ多発

# Ver3の解決: 完全統一された座標系
grid[row][col]  # 常に [y座標][x座標] で統一
position: tuple[int, int]  # (row, col) = (y座標, x座標)
```

#### **Ver3座標系仕様**
```python
class GridSystem:
    """Ver3統一座標系"""
    GRID_ROWS: int = 15      # Y軸方向（行数）
    GRID_COLS: int = 20      # X軸方向（列数）
    
    # 制約条件（Ver2から継承・強化）
    LEFT_BUS_COL: int = 0    # L_SIDE（電源バス）
    RIGHT_BUS_COL: int = 19  # R_SIDE（ニュートラルバス）
    EDITABLE_COLS: range = range(1, 19)  # 編集可能領域
    
    # 座標表現の統一
    def get_device(self, row: int, col: int) -> Device:
        """grid[row][col] = [y座標][x座標] で統一"""
        return self.grid[row][col]  # [y座標][x座標]
```

---

## 📋 **3. アーキテクチャ定義**

### **3.1 モジュール構造（Ver2の良い部分を継承）**

#### **Ver2で成功したモジュール化**
```python
# ✅ Ver2の成功アーキテクチャ（Ver3で継承）
main.py                    # コーディネーター（196行 - 適切なサイズ）
config.py                  # 設定管理（定数ベース - Ver3でも継続）
core/
├── config_manager.py      # 設定管理システム
├── grid_manager.py        # グリッドデバイス管理
├── plc_controller.py      # PLC論理制御
├── renderer.py            # UI描画システム
└── input_handler.py       # 入力処理システム
```

#### **Ver3での改良点**
```python
# Ver3で改良・追加するモジュール
core/
├── device_factory.py     # 🆕 デバイス生成ファクトリー
├── circuit_analyzer.py   # 🆕 回路解析エンジン
├── connection_manager.py # 🆕 明示的配線管理
└── plc_standard.py       # 🆕 PLC標準仕様準拠チェック
```

### **3.2 データフロー設計**

#### **Ver3のクリーンなデータフロー**
```python
class Ver3DataFlow:
    """
    Ver3設計思想: Single Source of Truth
    """
    
    # 1. デバイス状態の単一管理
    device_state: dict[str, bool] = {}  # "X001" -> True/False
    
    # 2. グリッド配置の単一管理  
    grid_placement: dict[tuple[int, int], Device] = {}  # (row,col) -> Device
    
    # 3. 電気的接続の単一管理
    connections: list[Connection] = []  # 明示的配線リスト
    
    # 4. 論理演算の単一エンジン（Ver2から改良）
    def scan_cycle(self) -> None:
        """PLCスキャンサイクル（Ver2の成功パターンを継承）"""
        self.read_inputs()      # 入力読み取り
        self.solve_logic()      # 論理演算
        self.write_outputs()    # 出力書き込み
        self.update_display()   # 表示更新
```

---

## 📋 **4. UI/UX定義**

### **4.1 操作系統（Ver2の良い部分を継承・改良）**

#### **Ver2で成功したキー操作（Ver3で改良）**
```python
# Ver2の成功パターン（Ver3でも基本継承）
KEY_MAPPING = {
    1: "A接点",         # Ver2: TYPE_A（継承）
    2: "B接点",         # Ver2: TYPE_B（継承） 
    3: "水平配線",      # Ver3: LINK_SIDE（新規）
    4: "通常コイル",    # Ver3: COIL（Ver2のOUTCOIL_NMLから名称変更）
    5: "反転コイル",    # Ver3: COIL_REV（Ver2のOUTCOIL_REVから名称変更）
    6: "タイマー",      # Ver2: TIMER（継承・3状態システム維持）
    7: "カウンター",    # Ver2: COUNTER（継承・エッジ検出維持）
    8: "上向き接続",    # Ver2: LINK_UP（継承）
    9: "下向き接続",    # Ver2: LINK_DOWN（継承）
    0: "削除",          # Ver2: DEL（継承）
}
```

### **4.2 表示系統（Ver2の成功を継承）**

#### **Ver2で成功した表示仕様（Ver3で継承）**
```python
class DisplayConfig:
    """Ver2の成功した表示仕様をVer3で継续"""
    WINDOW_WIDTH: int = 384      # Ver2で最適化済み
    WINDOW_HEIGHT: int = 384     # Ver2で最適化済み
    GRID_CELL_SIZE: int = 16     # Ver2で最適化済み
    TARGET_FPS: int = 60         # Ver2で安定動作確認済み
    
    # Ver3で追加改良
    POWER_FLOW_COLORS = {
        "energized": 11,         # 緑色（通電中）
        "de_energized": 1,       # 灰色（非通電）
        "tracing": 10,           # 黄色（トレース中）
    }
```

---

## 📋 **5. 実装戦略**

### **5.1 Ver2の資産活用方針**

#### **✅ Ver2から継承する優良資産**
```python
# Ver2の成功要素（Ver3でそのまま活用）
1. モジュール化アーキテクチャ        # main.py 196行の適切な分割
2. 定数ベース設定管理システム        # config.py の簡潔な構造
3. グリッドベース座標系             # 内部データ表示統一の成功
4. リアルタイム電力フロー可視化      # 60FPS安定動作
5. マウス操作システム               # 直感的デバイス配置
6. タイマー3状態システム           # STANDBY/CNTUP/ON
7. カウンターエッジ検出システム      # 立ち上がりエッジ検出
8. LINK_UP/DOWN垂直接続システム    # 安定動作確認済み
```

#### **❌ Ver2から廃止する問題要素**
```python
# Ver2の問題要素（Ver3で完全廃止）
1. INCOIL/OUTCOIL概念              # PLC標準と乖離
2. 用語の不統一                    # 教育効果を阻害
3. 暗黙の水平配線                  # 自己保持回路未対応
4. スプライト名のタイポ            # TIMER_STANBY等
```

### **5.2 実装アプローチの選択**

#### **🎯 推奨: 段階的リファクタリング**
```python
# Ver2 → Ver3 段階的移行の利点
advantages = [
    "Ver2の安定動作を保持",
    "段階的な動作確認が可能",
    "低リスクでの仕様変更",
    "開発者の学習コスト削減",
]

# 段階的移行のフェーズ
Phase1: "用語統一・スプライト整備"      # 低リスク
Phase2: "デバイス概念変更"            # 中リスク  
Phase3: "水平配線システム実装"         # 高リスク
Phase4: "統合テスト・品質確保"         # 品質確保
```

#### **⚡ 代案: ゼロからクリーン実装**
```python
# クリーン実装の利点
advantages = [
    "PLC標準仕様の完全準拠",
    "技術的負債の完全解消",
    "最適化されたアーキテクチャ",
    "Ver3設計思想の純粋実装",
]

# クリーン実装のリスク
risks = [
    "Ver2の安定動作の再現コスト",
    "デバッグ・テスト工数の増大",
    "既存機能の一時的退行リスク",
    "開発期間の延長",
]
```

---

## 📋 **6. AIアシスタント向け開発ガイド**

### **6.1 重要な理解ポイント**

#### **PLC概念の正しい理解**
```python
# ✅ 正しいPLC概念（Ver3で実装）
"""
接点（Contact）:
- 他のデバイスの状態を「読み取る」素子
- 入力条件を表現
- -| |- (A接点), -|/|- (B接点)

コイル（Coil）:  
- デバイスの状態を「設定する」素子
- 出力結果を表現
- -( )- (通常), -(/)-（反転）
"""

# ❌ Ver2の誤った概念（理解のため記録）
"""
入力コイル/出力コイル:
- 同一デバイスの二重実体
- PLC標準にない概念
- 教育的に有害
"""
```

#### **座標系の完全理解**
```python
# Ver3統一座標系（必須理解事項）
grid[row][col]           # [y座標][x座標] で統一
position = (row, col)    # (y座標, x座標) で統一

# 配置制約の理解
L_SIDE: col = 0         # 左バス（電源）
R_SIDE: col = 19        # 右バス（ニュートラル）
EDITABLE: col = 1-18    # 編集可能領域

# Ver1の教訓: 内部データと表示データの完全統一が必須
```

### **6.2 開発時の注意事項**

#### **Ver2資産の慎重な活用**
```python
# Ver2の良い部分は積極的に継承
good_patterns = [
    "モジュール分割パターン",
    "config.py の定数管理", 
    "グリッド座標系",
    "電力フロー可視化",
]

# Ver2の問題部分は完全に廃止
bad_patterns = [
    "INCOIL/OUTCOIL概念",
    "用語の不統一",
    "暗黙配線システム",
]
```

#### **実装の優先順位**
```python
# 開発優先順位（リスク管理重要）
Priority1: "基本動作の確保"          # Ver2機能保持
Priority2: "概念の正しい実装"        # PLC標準準拠
Priority3: "新機能の追加"           # LINK_SIDE等
Priority4: "最適化・改良"           # パフォーマンス向上
```

---

## 📋 **7. 成功の定義**

### **7.1 Ver3成功基準**

#### **機能的成功**
- [ ] PLC教科書レベルの回路が100%動作
- [ ] 自己保持回路の完全動作
- [ ] 実PLC仕様との完全準拠
- [ ] Ver2の全機能継承

#### **品質的成功**
- [ ] 60FPS安定動作維持
- [ ] メモリリーク完全解消
- [ ] CPU使用率30%以下
- [ ] 1時間以上の無故障動作

#### **教育的成功**
- [ ] PLC学習者の混乱完全解消
- [ ] 実PLC移行時の違和感なし
- [ ] 正しいラダー図記法の習得支援
- [ ] 工場エンジニアの検証用途対応

### **7.2 Ver3の価値**

```python
# Ver3が実現する価値
educational_value = "PLC教育における標準ツール"
practical_value = "工場での実用的検証ツール"  
technical_value = "高品質なオープンソースシミュレーター"
```

---

**この定義書は、AIアシスタントがVer3開発を正確に理解し、適切な判断を行うための完全なガイドです。**

*作成日: 2025-08-01*  
*対象: AI開発支援・完全理解用*  
*更新: 開発進捗に応じて継続更新*
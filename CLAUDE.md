# PyPlc - PLC Ladder Simulator Project

## Overview
PyxelとPythonを使用したPLCラダー図シミュレーターの開発プロジェクト。
工場での検証用途と学習目的を兼ねた、リアルタイム動作可視化システム。

## Project Structure
```
PyPlc/
├── main.py                 # メインコーディネーター (196行) ✅
├── config.py               # 設定定数・レイアウト・Enum定義 (77行) ✅
├── grid_system.py          # グリッドベースデバイス管理 (99行) ✅
├── electrical_system.py    # 電気的継続性システム (197行) ✅
├── plc_logic.py            # 従来PLCロジック (184行) ✅
├── ui_components.py        # UI描画・マウス処理 (269行) ✅
├── pyxdlg.py               # モーダルダイアログシステム (559行) ✅
├── pyxdlg.txt              # pyxdlg.py使用マニュアル ✅
├── main_original.py        # 元のmain.py (1,109行) - バックアップ
├── SpriteManager.py        # スプライト管理システム  
├── SpriteDefiner.py        # ビジュアルスプライト定義ツール
├── sprites.json            # スプライト定義データ
├── my_resource.pyxres      # Pyxelリソースファイル
├── dialogs/                # JSONダイアログ定義ディレクトリ ✅
│   ├── device_settings.json    # デバイス設定ダイアログ
│   ├── timer_settings.json     # タイマー設定ダイアログ
│   └── text_input.json         # テキスト入力ダイアログ
├── docs/
│   └── plc_simulator_plan.md  # 開発計画書
└── venv/                   # Python仮想環境
```

## Development Progress (2025-01-24)

### Phase 1: Basic Framework ✅ COMPLETED
- [x] Pyxelの基本セットアップ (160x120解像度)
- [x] LogicElementベースクラス実装
- [x] 基本的なContact/Coilクラス実装  
- [x] 単純なAND回路のテスト実装

### Phase 2: Core Functions ✅ COMPLETED  
- [x] Timer/Counterクラス実装
- [x] デバイス管理システム（X、Y、M、T、C）拡張
- [x] スキャンサイクル実装
- [x] 複数テスト回路の追加

### Phase 3: Sprite Integration ✅ COMPLETED
- [x] SpriteManagerシステム統合
- [x] JSON-driven sprite management
- [x] A接点/B接点/ランプ用スプライト定義
- [x] 初期化時キャッシュパターン実装
- [x] スプライトテスト表示

### Phase 4: Grid-Based Electrical System ✅ COMPLETED
- [x] 16x16ピクセルグリッドシステム (10x10セル)
- [x] グリッド交点でのデバイス配置システム
- [x] 電気的継続性システムの実装
- [x] リアルタイム電力フロー可視化
- [x] マウスインターフェース統合

### Phase 5: Vertical Connection System ✅ COMPLETED
- [x] LINK_UP/LINK_DOWNスプライト統合
- [x] 縦方向電気接続システム実装
- [x] 上下ラング間での電力伝送機能
- [x] クリック配置とDEL削除機能実装

### Phase 6: Interactive Device Placement System ✅ COMPLETED
- [x] マウスクリック式デバイス配置システム実装
- [x] グリッド交点での正確な位置決め機能
- [x] リアルタイムプレビュー表示（配置可能性表示）
- [x] LINK_UP/LINK_DOWNスプライトのグリッド表示
- [x] DEL機能による削除システム完成
- [x] 自動デバイスアドレス生成システム
- [x] GridDeviceManagerによる交点ベースデバイス配置
- [x] デバイスパレット選択システム（1-8キー）
- [x] 電気的継続性システム（LadderRung）実装
- [x] リアルタイム電力フロー可視化
- [x] セグメント単位の配線色管理

### Phase 7: Code Modularization ✅ COMPLETED (2025-01-24)
- [x] main.py構造分析とモジュール分割計画策定
- [x] config.py作成（Layout, Colors, DeviceType, BusbarDirection）
- [x] grid_system.py作成（GridDevice, GridDeviceManager）
- [x] electrical_system.py作成（BusConnection, LadderRung, VerticalConnection, ElectricalSystem）
- [x] plc_logic.py作成（従来PLCロジック：PLCDevice, DeviceManager, LogicElement群）
- [x] ui_components.py作成（UI描画メソッド、マウス処理）
- [x] main.py縮小（PLCSimulatorをコーディネーター役に専念）
- [x] 全機能動作確認・バグ修正完了
- [x] グリッド座標オフセット修正
- [x] デバイスパレットスプライト表示修正
- [x] マウス処理統合・AttributeError修正

## Screen Layout & Display (Updated for 256x256)

### Current Screen Layout
```
┌─────────────────────────────────────────────────────────────┐
│ PLC Ladder Simulator                    │ Sprite Test Area   │
│                                         │ [A_ON][A_OFF]      │
│ Device Palette: [BUS][A][B][COIL][TMR][CNT][H][V]          │
│                 1   2  3  4    5   6   7  8               │
├─────────────────────────────────────────────────────────────┤
│ Grid-Based Ladder Display (16x16 Grid, 10x10 cells)       │
│ ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐                 │
│ │   │   │   │   │   │   │   │   │   │   │                 │
│ ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤                 │
│ │ L │   │ X │   │ X │   │   │   │ Y │   │ ← Real-time     │
│ │   │───│001│───│002│───│───│───│001│   │   power flow    │
│ ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤                 │
│ │   │   │   │   │   │   │   │   │   │   │                 │
│ └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘                 │
├─────────────────────────────────────────────────────────────┤
│ Device Status Monitor                                       │
│ X001: ON/OFF    Y001: ON/OFF    T001: 2.5s/3.0s           │
│ X002: ON/OFF    Y002: ON/OFF    C001: 2/3                  │
│ X003: ON/OFF    Y003: ON/OFF                               │
│ X004: ON/OFF                                               │
├─────────────────────────────────────────────────────────────┤
│ Controls: 1-8:Select Device  Shift+1-4:Toggle X001-X004  Q:Exit│
└─────────────────────────────────────────────────────────────┘
```

### Display Specifications
- **Screen Size**: 256x256 pixels (upgraded from 160x120)
- **Device Palette**: Y=16, 8 device types with 1-8 key selection
- **Grid System**: 16x16 pixel cells, 10x10 grid for device placement
- **Electrical Visualization**: Real-time power flow with color-coded segments
- **Device Status Area**: Y position starts at 160
- **Control Info**: Bottom at Y position 240

## Technical Architecture

### Modular Architecture (Phase 7 Refactoring)
```python
# config.py - 設定・定義モジュール ✅
class Layout:              # レイアウト定数
class Colors:              # 色定義
class DeviceType(Enum):    # デバイスタイプ定義
class BusbarDirection(Enum): # バスバー接続方向

# grid_system.py - グリッドベースシステム ✅
class GridDevice:          # グリッド交点配置デバイス
class GridDeviceManager:   # 10x10グリッド管理システム

# electrical_system.py - 電気的継続性システム ✅
class BusConnection:       # バスバー接続点管理
class LadderRung:          # 横ライン電気的管理
class VerticalConnection:  # 縦方向結線管理
class ElectricalSystem:    # 全体電気系統管理

# plc_logic.py - 従来PLCロジック (184行) ✅
class PLCDevice:           # PLCデバイス（X, Y, M, T, C）
class DeviceManager:       # デバイス管理システム
class LogicElement:        # 論理素子基底クラス
class LadderProgram:       # プログラム全体管理

# ui_components.py - UI・描画システム (269行) ✅
class UIRenderer:          # UI描画システム
class MouseHandler:        # マウス入力処理

# main.py - メインコーディネーター (196行) ✅
class PLCSimulator:        # システム統合・制御
```

### Device Types & Implementation Status
- **X**: 入力デバイス (X001-X004実装済み) - 範囲: X000-X377
- **Y**: 出力デバイス (Y001-Y003実装済み) - 範囲: Y000-Y377  
- **M**: 内部リレー - 範囲: M0-M7999
- **T**: タイマー (T001: 3秒プリセット実装済み) - 範囲: T0-T255
- **C**: カウンター (C001: 3回プリセット実装済み) - 範囲: C0-C255
- **D**: データレジスタ (未実装) - 範囲: D0-D7999

### Test Circuits Implemented
1. **Grid AND Circuit**: グリッド配置 - バスバー(0,2) → X001(2,2) → X002(4,2) → Y001(8,2)
2. **Traditional Timer Circuit**: X003 → T001(3秒) → Y002  
3. **Traditional Counter Circuit**: X004 → C001(3回) → Y003

### Grid-Based Electrical System
- **Real-time Power Flow**: セグメント単位の電力フロー可視化
- **Color-Coded Wiring**: 緑=通電、グレー=非通電の動的色変化
- **Intersection Placement**: 16x16ピクセルグリッドの交点配置
- **Electrical Continuity**: 左バスバー → デバイス → 右バスバーの連続性管理

## Sprite Management System

### JSON-Driven Architecture
ChromeBlazeプロジェクトから移植した高性能スプライト管理システム:

```python
# 初期化時キャッシュパターン
self.sprites = {
    "TYPE_A_ON": sprite_manager.get_sprite_by_name_and_tag("TYPE_A_ON"),
    "TYPE_A_OFF": sprite_manager.get_sprite_by_name_and_tag("TYPE_A_OFF"),
    "TYPE_B_ON": sprite_manager.get_sprite_by_name_and_tag("TYPE_B_ON"),
    "TYPE_B_OFF": sprite_manager.get_sprite_by_name_and_tag("TYPE_B_OFF"),
    "LAMP_ON": sprite_manager.get_sprite_by_name_and_tag("LAMP_ON"),
    "LAMP_OFF": sprite_manager.get_sprite_by_name_and_tag("LAMP_OFF")
}
```

### Current Sprites (sprites.json)
- **TYPE_A_ON/OFF**: A接点の通電/非通電状態
- **TYPE_B_ON/OFF**: B接点の通電/非通電状態  
- **LAMP_ON/OFF**: 出力ランプの点灯/消灯状態
- **TIMER_ON/OFF**: タイマーの動作/停止状態
- **COUNTER_DARK/LIGHT**: カウンターの非動作/動作状態
- **LINK_UP**: 上方向電気接続ポイント
- **LINK_DOWN**: 下方向電気接続ポイント
- **DEL**: デバイス削除用アイコン

### Performance Benefits
- **初期化時読み込み**: JSON検索は起動時のみ
- **実行時高速アクセス**: 辞書参照によるO(1)アクセス
- **メモリ効率**: 必要最小限のスプライトキャッシュ

## Controls

### Device Selection & Placement
- **1-8 keys**: デバイスタイプ選択（パレットから）
  - 1: A接点, 2: B接点, 3: コイル, 4: タイマー
  - 5: バスバー, 6: 上結線, 7: 下結線, 8: 削除
- **Mouse Click**: グリッド交点でのデバイス配置・削除
- **Visual Preview**: マウス位置でのデバイス配置プレビュー（黄色=配置可、赤色=上書き警告）
- **選択状態**: 黄色背景で現在選択デバイスを表示

### Device Operation
- **Shift+1**: Toggle X001 (グリッドAND回路入力1)
- **Shift+2**: Toggle X002 (グリッドAND回路入力2)  
- **Shift+3**: Toggle X003 (従来タイマー起動)
- **Shift+4**: Toggle X004 (従来カウンター入力)

### System Control
- **Q/ESC**: 終了

## Features Demonstrated

### Logic Operations
- **Grid-Based AND Logic**: グリッド交点配置での2入力AND回路
- **Electrical Continuity**: 左バスバーから右バスバーへの電気的連続性
- **Power Segment Management**: デバイス間配線の個別通電管理
- **Timer Operation**: 3秒遅延タイマー（従来システム）
- **Counter Operation**: 3回カウントアップ（従来システム）

### Visual Feedback
- **Grid-Based Display**: 16x16ピクセルグリッドでの交点配置表示
- **Real-time Power Flow**: セグメント単位の電力フロー可視化
- **Color-Coded Wiring**: 緑=通電、グレー=非通電の動的色変化
- **Vertical Connections**: LINK_UP/LINK_DOWNペアによる上下ラング間接続
- **Interactive Device Placement**: マウスクリックによる直感的デバイス配置
- **Visual Placement Preview**: 黄色=配置可、赤色=上書き警告の配置プレビュー
- **Device Palette**: 8種類のデバイスタイプ選択インターフェース
- **Device Status Panel**: リアルタイムデバイス状態表示
- **Sprite Integration**: 状態依存スプライト切り替え

### Interactive Placement System
- **Click-to-Place**: デバイスパレット選択後のワンクリック配置
- **Grid Intersection Targeting**: 16x16ピクセルグリッドの交点自動吸着
- **Visual Device Preview**: マウスホバー時のリアルタイム配置プレビュー
- **Automatic Address Generation**: 配置位置に基づく自動デバイスアドレス生成
- **DEL Device Functionality**: 削除デバイス選択による配置済みデバイス除去

### Vertical Connection System
- **LINK_UP/LINK_DOWN Pairing**: 同じX座標での上下デバイスペア形成
- **Multi-Rung Power Transfer**: 異なるラング間での電力伝送
- **Automatic Connection Detection**: 最も近い下方LINK_DOWNとの自動ペアリング
- **Visual Sprite Display**: グリッド交点でのLINK_UP/DOWNスプライト表示
- **Visual Wire Rendering**: 縦方向配線の色付き可視化

### Technical Excellence
- **Grid-Based Architecture**: 交点配置による直感的回路構築
- **Electrical System Modeling**: 実際のPLC電気的動作の忠実な再現
- **Dual System Integration**: グリッドシステムと従来システムの並行動作
- **Real-time Processing**: 60FPSでのリアルタイム状態更新
- **Object-Oriented Design**: クリーンなクラス設計と型安全性
- **Modular Architecture**: 機能別モジュール分離と拡張性

## Development Methodology

### AI-Assisted Development
- **TodoWrite Tool**: 段階的タスク管理による確実な進行
- **Phase-by-Phase Implementation**: リスク最小化アプローチ
- **Documentation-Driven**: 実装と並行した詳細記録

### Quality Assurance
- **Incremental Testing**: 各フェーズでの動作確認
- **Error Handling**: 堅牢なエラー処理実装
- **Performance Optimization**: ChromeBlazeのベストプラクティス適用

## Next Development Phase

### Phase 8: Advanced Circuit Functionality (Pending)
- [ ] 自己保持回路システム（SET/RST命令）
- [ ] 並列回路の電気的管理
- [ ] 分岐・合流回路対応
- [ ] カウンター/タイマーのグリッド統合

### Phase 9: Circuit Construction Enhancement (Pending)
- [ ] 回路保存・読み込み機能
- [ ] ラダー図エクスポート機能
- [ ] 複雑な論理回路パターン対応
- [ ] エラー検証システム実装

### Phase 10: User Experience Improvements (Pending)
- [ ] デバイス移動機能（ドラッグ&ドロップ）
- [ ] 回路コピー&ペースト機能
- [ ] アンドゥ・リドゥ機能
- [ ] デバイスアドレス編集システム

## Technical Debt & Future Improvements

### Code Modularization Achievements (Phase 7)
- **Dramatic Size Reduction**: main.py の1,109行から196行への82%削減
- **Perfect Modularity**: 6つのモジュールによる機能完全分離
- **Improved Maintainability**: 機能別モジュール分離による保守性向上
- **Enhanced Testability**: 各モジュールの独立テスト可能性
- **Better Separation of Concerns**: UI、ロジック、データの明確な分離
- **Easier Feature Development**: モジュール単位での機能追加・修正
- **Successful Migration**: 全機能の完全移行とバグ修正完了

### Architecture Enhancements
- **Vector2D Integration**: 位置計算の数学的抽象化
- **Configuration System**: 外部設定ファイル対応（config.py で部分実現）
- **State Machine**: より複雑な状態管理への対応

### Performance Optimizations
- **Sprite Batching**: 大量スプライト描画の最適化
- **Memory Management**: オブジェクトプールパターン適用
- **Rendering Pipeline**: 描画処理の効率化

## Technical Specifications & Design Details

### PLC Instruction Set (三菱PLC準拠)
- **LD/LDI**: 負荷/負荷反転
- **AND/ANI**: 論理積/論理積反転
- **OR/ORI**: 論理和/論理和反転
- **OUT**: 出力
- **SET/RST**: セット/リセット

### Class Design Details
```python
# デバイス管理
class PLCDevice:
    def __init__(self, address, device_type):
        self.address = address      # "X001", "Y010"等
        self.device_type = device_type  # 'X', 'Y', 'M', 'T', 'C'
        self.value = False/int
        
class DeviceManager:
    def __init__(self):
        self.devices = {}  # address -> PLCDevice

# 論理素子詳細設計
class ContactA(LogicElement):  # A接点（ノーマルオープン）
    def evaluate(self):
        return self.device.value

class ContactB(LogicElement):  # B接点（ノーマルクローズ）
    def evaluate(self):
        return not self.device.value

class Coil(LogicElement):      # 出力コイル
    def evaluate(self):
        result = self.inputs[0].evaluate() if self.inputs else False
        self.device.value = result
        return result

# ライン管理
class LadderLine:
    def __init__(self):
        self.elements = []     # 素子リスト（左→右順）
        self.power_flow = False
        
    def scan(self):
        # 左から右へトレース処理
        
class LadderProgram:
    def __init__(self):
        self.lines = []        # ライン リスト（上→下順）
        self.current_line = 0  # 現在処理中ライン
        
    def scan_cycle(self):
        # 全ライン順次実行
```

### Visual Design Specifications

#### Optimized Layout Design (256x256 Pyxel)
- **Improved Space Utilization**: 2.6x more display area (256x256 vs 160x120)
- **Better Text Spacing**: 12-pixel vertical spacing for device status
- **Dedicated Sprite Test Area**: Right side for sprite demonstration
- **Enhanced Readability**: Larger text areas and better positioning

#### Sprite Definitions (8x8 pixels)
```python
SPRITE_CONTACT_OPEN  = 0   # □ 開接点
SPRITE_CONTACT_CLOSE = 1   # ■ 閉接点
SPRITE_COIL_OFF      = 2   # ○ コイルOFF
SPRITE_COIL_ON       = 3   # ● コイルON
SPRITE_TIMER         = 4   # ⏱ タイマー
```

#### Color System
```python
COLOR_LINE_OFF = 1      # 灰色（通電なし）
COLOR_LINE_ON  = 11     # 緑色（通電中）
COLOR_TRACE    = 10     # 黄色（トレース中）
COLOR_BG       = 0      # 黒（背景）
```

### Implementation Priority Matrix

#### High Priority Features
1. 基本的なAND/OR回路
2. リアルタイム可視化
3. 手動入力操作

#### Medium Priority Features
1. タイマー機能
2. SET/RST命令
3. より複雑な回路パターン

#### Low Priority Features
1. ファイル入出力
2. 高度なデバッグ機能
3. パフォーマンス最適化

### Technical Challenges & Solutions

#### Challenge 1: Pyxel Resolution Limitations
- **Solution**: シンプルなスプライト設計、効率的な画面利用

#### Challenge 2: Complex Circuit Display
- **Solution**: スクロール機能、分割表示

#### Challenge 3: Real-time Performance
- **Solution**: 最適化されたスキャンアルゴリズム

### Scan Processing Implementation
- **Left-to-Right Trace**: 左から右へのトレース処理
- **Top-to-Bottom Execution**: 上から下へのライン実行順序
- **Real-time Current Flow**: リアルタイムでの電流フロー可視化

## References

### Source Projects
- **ChromeBlaze**: スプライト管理システムの参考実装

### External Resources
- **Pyxel Documentation**: https://github.com/kitao/pyxel
- **三菱PLC仕様**: デバイス体系とラダー命令の参考

## Running the Project
```bash
# 仮想環境での実行
./venv/bin/python main.py

# または直接実行 (pyxelインストール済み環境)
python main.py
```

## Development Environment & Setup

### Required Packages
```bash
pip install pyxel
```

### Recommended Environment
- **Python**: 3.8+
- **Pyxel**: 1.9.0+
- **IDE**: VSCode with Python extension (.vscode/launch.json設定済み)
- **Version Control**: Git対応

---

## Session Achievement Summary (2025-01-24)

### 🎉 Code Modularization - COMPLETED SUCCESSFULLY!

#### **Final Module Structure:**
- ✅ **`main.py`**: メインコーディネーター (196行) - 82%削減達成
- ✅ **`config.py`**: 設定定数・レイアウト・Enum定義 (77行)
- ✅ **`grid_system.py`**: GridDevice, GridDeviceManager (99行)
- ✅ **`electrical_system.py`**: 電気的継続性システム (197行)
- ✅ **`plc_logic.py`**: 従来PLCロジック (184行)
- ✅ **`ui_components.py`**: UI描画・マウス処理 (269行)
- ✅ **`main_original.py`**: 元のファイルバックアップ (1,109行)

#### **修正完了したバグ:**
1. **グリッド座標オフセット**: デバイス配置が交点上に正確に配置
2. **デバイスパレット**: スプライト表示とハイライト機能復旧
3. **マウス処理**: パレット選択とグリッド配置の統合処理
4. **AttributeError**: `selected_device_index`参照エラー修正

#### **品質保証:**
- **機能完全性**: 元のバージョンと同等の全機能動作確認済み
- **パフォーマンス**: 60FPSリアルタイム処理維持
- **拡張性**: モジュール単位での独立開発・テスト可能

### Modularization Impact
- **Dramatic Reduction**: 1,109行 → 196行 (82%削減)
- **Perfect Separation**: 6モジュールによる責任明確化
- **Future-Ready**: 次期開発フェーズの基盤完成

---

---

## Phase 8: EDIT/RUN Mode System (Planned - 2025-01-24 Afternoon)

### 🎯 **設計概要**
EDITモードと実行モードの分離により、より実用的なPLCシミュレーターを実現。

### **EDITモード機能**
- デバイス配置・削除・編集
- 回路構築・修正
- **デバイス番号入力システム** (M001, T001, X010等)
- グリッド編集機能

### **実行モード機能**  
- デバイス配置不可（編集ロック）
- 入力デバイス（X接点）のON/OFF操作
- リアルタイム回路シミュレーション
- 出力デバイス状態表示

### **SpriteDefiner参考実装要素**
**テキスト入力システム (322-347行)**:
```python
def _handle_text_input_common(self, input_text):
    # A-Z文字入力（SHIFT対応）
    for i in range(26):
        if pyxel.btnp(pyxel.KEY_A + i):
            if pyxel.btn(pyxel.KEY_SHIFT):
                input_text += chr(ord('A') + i)
            else:
                input_text += chr(ord('a') + i)
    # 0-9数字入力・バックスペース処理
```

**状態管理システム**:
```python
class AppState(Enum):
    VIEW = "view"
    EDIT = "edit" 
    COMMAND_INPUT = "command_input"
    LEGACY_INPUT = "legacy_input"
```

### **実装計画**
1. **モード管理システム**: `SimulatorMode(Enum)` 
2. **キー操作**: TABキーでモード切り替え
3. **デバイス番号入力**: ENTERキーで入力モード開始
4. **UI表示**: 画面上部にモード表示
5. **機能制限**: モード別の操作制限

### **PyPlc用実装仕様**
- **デバイス配置後番号入力**: デバイス配置→ENTER→番号入力モード
- **入力フォーマット**: "X001", "M100", "T050", "C020"等
- **バリデーション**: デバイスタイプと番号範囲チェック
- **UI表示**: 画面下部に入力プロンプト表示

### **開発優先順序**
1. モード切り替えシステム (TABキー)
2. デバイス番号入力システム
3. 実行モードでの操作システム  
4. UI表示統合

---

## Vertical Bus Line Implementation Fix (2025-01-25)

### 🔧 **Issue Resolution: Vertical Bus Line Connection Logic**

#### **Problem Identified**
- **Sprite Display vs Logic Mismatch**: Visual sprites and connection logic were reversed
- **Expected Behavior**: Upper line with LINK_DOWN (↓), lower line with LINK_UP (↑) should connect
- **Actual Behavior**: Connection logic was looking for opposite configuration

#### **Root Cause Analysis**
- `electrical_system.py`: Connection pair logic searched for LINK_UP followed by LINK_DOWN
- **Correct Logic**: Should search for LINK_DOWN (upper line) followed by LINK_UP (lower line)

#### **Implementation Fix**
1. **electrical_system.py**:
   - Modified `get_connected_pairs()`: Search LINK_DOWN → LINK_UP pairs
   - Updated `_process_vertical_connections()`: Power flows from LINK_DOWN to LINK_UP
   - Fixed `get_vertical_wire_segments()`: Correct drawing coordinates

2. **ui_components.py**:
   - Added clarifying comments for sprite placement logic
   - LINK_UP (↑): Place on lower line for upward connection
   - LINK_DOWN (↓): Place on upper line for downward connection

3. **main.py**:
   - Re-enabled BUSBAR in device palette (key 5)

#### **Visual Logic Clarification**
```
Upper Line: [DEVICE] ------ LINK_DOWN(↓) ------
                               |
                               | (Vertical Connection)
                               |
Lower Line: [DEVICE] ------ LINK_UP(↑) --------
```

### 📝 **Sprite Information Communication Methods**

#### **Challenge**: Communicating Visual Sprite Information to AI Assistant

#### **Effective Methods Discovered**

**1. Functional Description (Most Effective)**
- Describe **how sprites should behave** rather than how they look
- Example: "Upper line with ↓, lower line with ↑ should connect"
- More reliable than visual descriptions

**2. JSON Comment Enhancement**
```json
{
  "8_8": {
    "x": 8, "y": 8,
    "NAME": "LINK_UP",
    "desc": "Upward connection point"
  },
  "16_8": {
    "x": 16, "y": 8,
    "NAME": "LINK_DOWN", 
    "desc": "Downward connection point"
  }
}
```
- **Safe Implementation**: English comments avoid SpriteDefiner.py encoding issues
- **SpriteManager.py Compatibility**: `sprite.get("desc")` for safe retrieval
- **Consistent Naming**: `desc` field with capitalized descriptions

**3. ASCII Art + Context**
```
LINK_UP (8x8):     LINK_DOWN (8x8):
    ^^                 ||
    ||                 ||
    ||                 vv
```

**4. CLAUDE.md Documentation**
- Record sprite meaning and placement rules
- Visual behavior specifications
- Connection logic documentation

**5. Screenshot Reference**
- AI can read images using Read tool
- Most accurate for complex visual information

#### **Best Practice Guidelines**
1. **Primary**: Use functional/behavioral descriptions
2. **Secondary**: Add JSON `desc` fields in English
3. **Documentation**: Record in CLAUDE.md for future reference
4. **Validation**: Test SpriteDefiner.py compatibility before deployment

#### **Implementation Results**
- ✅ Vertical bus line connections working correctly
- ✅ Sprite display matches expected behavior  
- ✅ JSON comment system established
- ✅ Documentation methodology defined

---

---

## Dialog System Implementation (2025-01-25)

### 📦 **pyxdlg.py - Modal Dialog System**

#### **概要**
EDITモード拡張用のモーダルダイアログシステムを実装。デバイス設定、タイマー値、テキスト入力に対応した統合UI環境を提供。

#### **主要機能**
- **モーダルダイアログ**: 常にメイン画面上に表示される入力ダイアログ
- **入力タイプバリデーション**: TEXT/NUMBER/DEVICE_ADDRESS別の入力制限
- **JSONリソースファイル**: Windowsリソースファイル風のダイアログ定義
- **マウス・キーボード対応**: 直感的なUI操作
- **視認性改善**: マウスカーソル表示とボタンホバー効果

#### **技術仕様**
```python
# 従来API（シンプル）
result, text = pyxdlg.input_device_address("Device Settings", "X001")
result, text = pyxdlg.input_number("Timer Settings", "Timer value:", "3")
result, text = pyxdlg.input_text("Name Input", "Enter name:", "")

# JSONリソースAPI（高度）
result, values = pyxdlg.JsonDialogBuilder.show_json_dialog("dialogs/device_settings.json")
```

#### **JSONダイアログ定義システム**
```json
{
  "title": "Device Settings",
  "width": 220, "height": 140,
  "controls": [
    {
      "type": "label",
      "x": 10, "y": 20,
      "text": "Configure Device Properties",
      "color": "white"
    },
    {
      "type": "textinput",
      "x": 10, "y": 55,
      "width": 120, "height": 20,
      "input_type": "device_address",
      "placeholder": "X001"
    }
  ]
}
```

#### **実装されたコンポーネント**
- **PyxDialog**: メインダイアログクラス
- **DialogLabel**: 色付きテキストラベル
- **JsonDialogBuilder**: JSON定義からの動的ダイアログ生成
- **InputType**: TEXT/NUMBER/DEVICE_ADDRESS入力タイプ定義
- **マウスカーソル描画**: ダイアログ上での視認性確保

#### **ファイル構成**
- `pyxdlg.py` (559行): メインモジュール
- `pyxdlg.txt`: 詳細使用マニュアル・テストコード集
- `dialogs/device_settings.json`: デバイス設定ダイアログ定義
- `dialogs/timer_settings.json`: タイマー設定ダイアログ定義
- `dialogs/text_input.json`: テキスト入力ダイアログ定義

#### **PyPlc統合準備**
- EDITモードでのデバイス設定ダイアログ表示
- ENTERキーでのデバイスアドレス入力
- タイマー・カウンター値設定ダイアログ
- 回路保存・読み込み時の名前入力

#### **品質保証**
- **完全なテストスイート**: 基本機能・JSON・エラーハンドリング・統合テスト
- **エラーハンドリング**: FileNotFoundError、JSON解析エラー対応
- **パフォーマンス最適化**: 効率的な背景暗転効果、マウスカーソル描画
- **使用マニュアル**: 豊富なコード例とトラブルシューティング

---

*Project Status: ✅ Dialog System Implementation COMPLETED*  
*Last Updated: 2025-01-25*  
*Latest Achievement: モーダルダイアログシステム + JSONリソースファイル実装完了*  
*Current Status: Phase 8 (EDIT/RUN Mode System) 実装待機中*  
*Next Session: pyxdlg.pyをPyPlc main.pyに統合・EDITモード拡張*
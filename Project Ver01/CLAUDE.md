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

## Phase 8: EDIT/RUN/STOP Mode System Implementation Plan (2025-01-25)

### 🎯 **Next Development Phase Analysis**

#### **Current Challenge Analysis**
Based on `todo_plan.md` requirements:

1. **Mode State Management Issue**
   - TAB切り替え後、デフォルトでRUN状態になる問題
   - **Required**: EDIT → STOP (デフォルト) → F5でRUN開始

2. **Output Coil Sprite Gap**
   - コイル `<Y01>` に対する出力表示 `|Y01|` スプライト未実装
   - Y接点の視覚的状態表示不足

#### **Technical Implementation Strategy**

### **Phase 8a: Mode Management System**
```python
# config.py 拡張
class SimulatorMode(Enum):
    EDIT = "EDIT"      # デバイス配置・編集可能
    STOP = "STOP"      # 実行停止中（デフォルト状態）
    RUN = "RUN"        # 回路実行中
    
# main.py 統合
class PLCSimulator:
    def __init__(self):
        self.mode = SimulatorMode.EDIT  # 起動時はEDITモード
        self.execution_state = SimulatorMode.STOP  # RUNモード時の実行状態
```

### **Key Operation Mapping**
- **TAB**: EDIT ↔ STOP モード切り替え
- **F5**: STOP → RUN (実行開始)
- **F6/ESC**: RUN → STOP (実行停止)
- **ENTER**: EDITモードでデバイス設定ダイアログ表示

### **Phase 8b: Output Coil Visual System**

#### **Missing Sprite Implementation**
```python
# sprites.json 追加予定
"COIL_ON": {        # |Y01| 通電時表示
    "x": pos_x, "y": pos_y,
    "desc": "Energized output coil display"
},
"COIL_OFF": {       # |Y01| 非通電時表示  
    "x": pos_x, "y": pos_y,
    "desc": "De-energized output coil display"
}
```

#### **PLC Logic Enhancement**
1. **コイル→Y接点連動**: コイル通電時、対応するY接点をON状態に
2. **視覚的フィードバック**: グリッド上でのコイル状態リアルタイム表示
3. **デバイス状態パネル**: Y接点状態の詳細表示強化

### **Implementation Priority & Dependencies**

#### **Priority 1: Mode State Management**
- TAB切り替え時のデフォルト動作修正
- F5実行開始機能の実装
- モード表示UI追加（画面上部）

#### **Priority 2: Coil Sprite System**
- SpriteDefiner.pyでCOIL_ON/OFF作成
- sprites.json更新
- GridDeviceManagerでのコイル表示統合
- 電気的継続性システムとの連携

#### **Priority 3: Dialog Integration**
- pyxdlg.py統合
- ENTERキーでのデバイス設定ダイアログ
- タイマー/カウンター値設定機能

### **Expected User Workflow**
```
1. 起動 → EDITモード
2. デバイス配置・回路構築
3. TAB → STOPモード（編集ロック）
4. F5 → RUN開始（回路シミュレーション）
5. Shift+1-4 → X接点操作でテスト
6. F6 → STOP（シミュレーション停止）
7. TAB → EDIT（回路編集に戻る）
```

### **Technical Challenges & Solutions**

#### **Challenge 1: Mode State Persistence**
- **Solution**: config.pyでのモード状態管理
- モード変更時の状態保存・復元機能

#### **Challenge 2: Coil-Contact Synchronization**
- **Solution**: electrical_system.pyでのコイル→Y接点自動連動
- リアルタイム状態同期システム

#### **Challenge 3: UI Space Constraints**
- **Solution**: 既存256x256レイアウトでのモード表示最適化
- 右上エリア活用によるモード状態表示

### **Development Session Structure**
```python
# Session 1: Mode Management
1. SimulatorMode enum追加
2. TAB/F5/F6キー処理実装
3. UI表示システム統合

# Session 2: Coil Sprite System  
1. SpriteDefiner.pyでスプライト作成
2. GridDeviceManager統合
3. 電気系統連動テスト

# Session 3: Dialog Integration
1. pyxdlg.py統合
2. デバイス設定機能実装
3. 全体動作テスト・品質保証
```

---

## Major Device System Refactoring (2025-01-25)

### 🎉 **Complete Device System Overhaul - COMPLETED**

#### **Refactoring Phase Summary**
大規模なスプライト仕様統一とデバイスシステム拡張を5フェーズで完全実装。

### **Phase 1: Sprite Name Unification ✅ COMPLETED**
- [x] sprites.json typo修正 (TIMR_STNBY → TIMER_STANBY)
- [x] main.py スプライト名統一 (CDEV → OUTCOIL_NML)
- [x] grid_system.py スプライト参照統一
- [x] デバイスパレット表示名修正

### **Phase 2: INCOIL (Input Coil) Implementation ✅ COMPLETED**
- [x] config.py にINCOILデバイスタイプ追加
- [x] main.py にINCOILスプライトキャッシュ追加
- [x] grid_system.py にINCOILスプライト参照・状態更新追加
- [x] electrical_system.py にINCOIL電気的動作実装
- [x] デバイスパレット統合 (3キー: Input Coil)

### **Phase 3: TIMER Three-State System ✅ COMPLETED**
- [x] main.py に3状態スプライト追加 (TIMER_STANBY/CNTUP/ON)
- [x] grid_system.py にtimer_state フィールド・3状態切り替え実装
- [x] electrical_system.py にタイマー状態遷移処理実装
- [x] _process_timer_logic() による精密な時間管理
- [x] デバイスパレット更新 (6キー: Timer)

### **Phase 4: OUTCOIL_REV (Reverse Output Coil) ✅ COMPLETED**
- [x] config.py にOUTCOIL_REVデバイスタイプ追加
- [x] grid_system.py にOUTCOIL_REVスプライト参照・状態更新追加
- [x] electrical_system.py に反転動作実装 (device.coil_energized = not power_state)
- [x] デバイス同期システム拡張
- [x] デバイスパレット統合 (5キー: Rev Output)

### **Phase 5: COUNTER System Enhancement ✅ COMPLETED**
- [x] main.py にCOUNTER_ON/OFFスプライトキャッシュ追加
- [x] grid_system.py にcounter_state フィールド・専用スプライト実装
- [x] electrical_system.py にエッジ検出カウンターロジック実装
- [x] _process_counter_logic() による立ち上がりエッジ検出
- [x] デバイスパレット統合 (7キー: Counter)
- [x] キー操作1-0対応（0キーは10番目のDEL）

### **Final Device Palette Configuration**
```
完全版デバイスパレット (1-0キー):
1: A Contact     (TYPE_A)
2: B Contact     (TYPE_B)  
3: Input Coil    (INCOIL)
4: Output Coil   (OUTCOIL_NML)
5: Rev Output    (OUTCOIL_REV)
6: Timer         (TIMER - 3状態)
7: Counter       (COUNTER - エッジ検出)
8: Link Up       (LINK_UP)
9: Link Down     (LINK_DOWN)
0: Delete        (DEL)
```

### **Technical Achievements**

#### **Device System Completeness**
- **10デバイス完全対応**: 全PLC基本機能実装完了
- **sprites.json完全統合**: CSV仕様書準拠の統一実装
- **状態管理システム**: デバイス別専用状態フィールド
- **電気系統統合**: 全デバイスの電力フロー・同期処理

#### **Advanced Logic Implementation**
- **TIMER 3状態**: STANBY → CNTUP → ON の精密状態遷移
- **COUNTER エッジ検出**: 立ち上がりエッジでのカウントアップ
- **OUTCOIL_REV 反転動作**: 電力状態反転による安全回路対応
- **INCOIL 内部処理**: M接点対応の中間結果保存

#### **Quality Assurance**
- **段階的実装**: 5フェーズによるリスク最小化
- **機能完全性**: 既存機能の完全保持
- **拡張性確保**: モジュール化による将来対応
- **パフォーマンス維持**: 60FPSリアルタイム処理継続

### **Development Methodology Excellence**
- **ステップバイステップ**: 段階的な安全実装
- **Git管理**: 各フェーズでのコミット対応
- **仕様準拠**: CSV/JSON仕様書の完全実装
- **AI協調開発**: 効率的なチームワーク実現

---

## 水平・垂直配線システム実装計画 (2025-01-27)

### 🎯 **自己保持回路問題の解決方針**

#### **現在の課題**
`SimIssue/PLC Sim Plan.txt`で特定された自己保持回路の動作不良：
- X001 → Y01入力コイル → Y01出力コイル → X002 → (バスライン) → Y01入力コイル
- **問題**: 水平配線が明示的オブジェクト化されていないため、電気的接続が認識されない

#### **解決アプローチ: 明示的配線システム**
```
従来: [X001] (暗黙接続) [Y01入力] (暗黙接続) [Y01出力]
新方式: [X001]---[WIRE_H]---[Y01入力]---[WIRE_V]---[Y01出力]---[WIRE_H]---[X002]
```

### 📋 **実装ステップバイステップ計画**

#### **Phase 1: アイコン・スプライト基盤 (ユーザー作業 + システム統合)**
**Step 1**: ユーザーによる水平・垂直配線アイコン作成 (8x8ピクセル)
- `WIRE_H`: 水平配線 `[---]`
- `WIRE_V`: 垂直配線 `[|]`

**Step 2**: `config.py`にWIRE_H、WIRE_Vデバイスタイプ追加
**Step 3**: `sprites.json`に新しい配線アイコンエントリ追加
**Step 4**: `main.py`スプライトキャッシュに配線スプライト追加

#### **Phase 2: UI・操作系拡張 (3段パレットシステム)**
**Step 5**: デバイスパレット3段化（現在10個→15個対応）
- 上段5個・中段5個・下段5個の構成
- Page Up/Downキーでパレット段切り替え

**Step 6**: UIRendererでの3段パレット表示対応
**Step 7**: キーボード操作拡張（Page Up/Downまたは追加キー）

#### **Phase 3: 配線オブジェクト実装**
**Step 8**: GridDeviceに配線専用フィールド追加
- `wire_direction`: "H"/"V"方向指定
- `connected_devices`: 接続デバイスリスト

**Step 9**: マウスハンドラーに配線配置・削除機能追加

#### **Phase 4: 電気系統配線トレース**
**Step 10**: electrical_systemに配線トレース機能実装
- 配線経由の電気的経路追跡
- デバイス→配線→デバイスの連続性管理

**Step 11**: 自己保持回路での動作テスト・検証
**Step 12**: 複雑配線回路での電気的継続性テスト

### 🔧 **技術仕様詳細**

#### **配線オブジェクト設計**
```python
class WireDevice(GridDevice):
    def __init__(self, direction: str):
        self.direction = direction        # "H" or "V"
        self.connected_terminals = []     # 接続端子リスト
        self.wire_energized = False       # 配線通電状態
        
    def update_power_flow(self):
        # 接続デバイスから電力状態を判定・伝送
        pass
```

#### **電気的ネットワーク構築**
```python
class ElectricalNetwork:
    def trace_power_path(self, start_node, end_node):
        """配線を含む電力経路をトレース"""
        pass
        
    def build_circuit_graph(self):
        """デバイス+配線の接続グラフを構築"""
        pass
```

### 🎯 **期待される効果**

#### **自己保持回路の完全動作**
```
[X001]---[WIRE_H]---[Y01入力]
                         |
                    [WIRE_V]
                         |
[Y01出力]---[X002]---[WIRE_H]---[WIRE_V]
```
**完全な電気的経路追跡** → **正しい自己保持動作**

#### **設計意図の明確化**
- 配線を意識的に配置 → 回路構造の理解向上
- 視覚的な回路表現 → デバッグの容易性
- 実PLC図面との整合性 → 学習効果の向上

### ⏱ **作業時間見積もり**
- **Phase 1 (Step 1-4)**: 約30分
- **Phase 2 (Step 5-7)**: 約1時間  
- **Phase 3 (Step 8-9)**: 約45分
- **Phase 4 (Step 10-12)**: 約1時間
**合計**: 約3時間15分で完全実装予定

### 📝 **実装優先度**
1. **最優先**: 水平配線システム（自己保持回路の動作に直結）
2. **高優先**: 3段パレットUI（操作性向上）
3. **中優先**: 垂直配線システム（現LINK_UP/DOWNからの移行）
4. **低優先**: 高度な配線機能（交差点、分岐等）

### 🔄 **段階的移行戦略**
1. **現在システム維持**: LINK_UP/DOWNシステムを保持
2. **配線システム併用**: 新旧システムの並行動作
3. **段階的移行**: ユーザビリティテスト後に最適解を決定

---

## Current Session Work Status (2025-01-27)

### 🔍 **Session Analysis & Implemented Fixes**

#### **F5 Reset System Enhancement ✅ COMPLETED**
- **Issue**: F5 stop functionality needed to reset all devices to initial state
- **Implementation**: 
  - Added `_reset_all_systems()` method in main.py calling all subsystem resets
  - Enhanced `DeviceManager.reset_all_devices()` for X,Y,M,T,C device state reset
  - Enhanced `GridDeviceManager.reset_all_devices()` with reverse coil initial state handling
  - Enhanced `ElectricalSystem.reset_electrical_state()` for complete electrical reset
- **Result**: F5 now properly resets entire system to clean initial state

#### **Grid Column Placement Fix ✅ COMPLETED**
- **Issue**: Devices could only be placed in columns 1-8, not column 9
- **Root Cause**: Overly restrictive grid validation in ui_components.py
- **Fix**: Modified mouse input validation from `grid_x != 0 and grid_x != Layout.GRID_COLS - 1` to `grid_x != 0`
- **Result**: Devices can now be placed in columns 1-9 as intended

#### **Display State Synchronization Fix ✅ COMPLETED**
- **Issue**: Device sprites remained lit after F5 stop despite reset system
- **Root Cause**: Sprite display not updating after device reset
- **Fix**: Added `self.grid_device_manager.update_all_devices(self.device_manager)` after reset
- **Result**: All device sprites properly turn off when system is reset

#### **Edit Mode Bus Connection Display Fix ✅ COMPLETED**
- **Issue**: Vertical bus connection display disappeared in EDIT mode after reset changes
- **Root Cause**: Full electrical updates were disabled during STOPPED state
- **Solution**: Implemented `update_structure_only()` method for STOPPED state
- **Result**: LINK_UP/DOWN sprites display correctly in EDIT mode without full simulation

#### **Same-Address Coil Synchronization ✅ COMPLETED**
- **Implementation**: Input coil (Y01) automatically synchronizes with output coils of same address
- **Features**:
  - Input coil ON → Output coil ON
  - Input coil ON → Reverse coil OFF
  - Automatic device manager synchronization
  - Reset state handling for reverse coils (ON when power off)

### 📋 **Self-Holding Circuit Analysis**

#### **Problem Identified**
From `SimIssue/PLC Sim Plan.txt` analysis:
- Self-holding circuit: X001 → Y01 input coil → Y01 output coil → X002 → (busline) → Y01 input coil
- **Current Issue**: Horizontal wiring connections are implicit, preventing proper electrical continuity recognition
- **Expected**: When X001 turns OFF, circuit should maintain through Y01 output → X002 → busline connection back to Y01 input

#### **Root Cause: Implicit Wiring System**
```
Current: [X001] (implicit) [Y01入力] (implicit) [Y01出力] (implicit) [X002]
Problem: No explicit horizontal wire objects to trace electrical paths
```

#### **Proposed Solution: Explicit Wire Objects**
```
New System: [X001]---[WIRE_H]---[Y01入力]---[WIRE_H]---[Y01出力]---[WIRE_H]---[X002]
                                      |                                            |
                                 [WIRE_V]                                     [WIRE_V]
                                      |                                            |
                                   [BUSLINE]---[WIRE_H]---[WIRE_H]---[WIRE_H]---
```

### 🎯 **Implementation Plan: Wire Object System**

#### **12-Step Implementation Strategy**

**Phase 1: Icon & Sprite Foundation (User Task + System Integration)**
1. ⏳ **User Task**: Create horizontal & vertical wire icons (8x8 pixels)
2. 📝 **Add Device Types**: Update config.py with WIRE_H, WIRE_V enums
3. 📝 **Update Sprites**: Add wire sprites to sprites.json
4. 📝 **Cache Integration**: Add wire sprites to main.py sprite cache

**Phase 2: UI & Interaction System (3-Tier Palette)**
5. 📝 **Expand Palette**: Upgrade to 3-tier device palette (15 devices total)
6. 📝 **UI Rendering**: Update UIRenderer for 3-tier display
7. 📝 **Key Controls**: Add Page Up/Down or extended key controls

**Phase 3: Wire Object Implementation**
8. 📝 **Grid Enhancement**: Add wire-specific fields to GridDevice
9. 📝 **Mouse Handling**: Implement wire placement/deletion in mouse handler

**Phase 4: Electrical System Integration**
10. 📝 **Wire Tracing**: Implement wire-based electrical path tracing
11. 🧪 **Self-Hold Test**: Verify self-holding circuit operation
12. 🔬 **Complex Circuits**: Test advanced circuit configurations

#### **Technical Architecture**
```python
# Wire Object Design
class GridDevice:
    # Enhanced for wire support
    def __init__(self):
        self.wire_direction = None      # "H"/"V" for wire objects
        self.wire_energized = False     # Wire power state
        self.connected_terminals = []   # Connected device list

# Electrical Network Tracing
class ElectricalSystem:
    def trace_wire_path(self, start_node, end_node):
        """Trace electrical path through wire objects"""
        
    def build_circuit_graph(self):
        """Build device+wire connection graph"""
```

#### **Expected Benefits**
- ✅ **Self-Holding Circuits**: Proper electrical continuity recognition
- ✅ **Visual Clarity**: Explicit wire placement shows circuit intention
- ✅ **Real PLC Alignment**: Matches actual PLC ladder diagram conventions
- ✅ **Educational Value**: Users learn proper circuit construction principles

### 📊 **Current Technical Status**

#### **System Architecture (Post-Refactoring)**
- **main.py**: 309 lines (coordinator)
- **config.py**: 106 lines (constants & enums) 
- **grid_system.py**: 197 lines (grid device management)
- **electrical_system.py**: 415 lines (electrical continuity)
- **plc_logic.py**: 184 lines (traditional PLC logic)
- **ui_components.py**: 269 lines (UI rendering & mouse)

#### **Device System Completeness**
- ✅ **10 Device Types**: A/B contacts, input/output/reverse coils, timer, counter, vertical links, delete
- ✅ **Advanced Logic**: 3-state timers, edge-detection counters, reverse coil operation
- ✅ **Real-time Simulation**: 60fps electrical flow visualization
- ✅ **Mode System**: EDIT/RUN/STOP states with F5 control

### 🚀 **Next Development Session**

#### **Immediate Priority**
1. **Wait for User**: Wire icon creation completion
2. **Step 2**: Begin config.py wire device type addition
3. **Progressive Implementation**: Follow 12-step plan systematically

#### **Session Continuation Strategy**
- User explicitly requested step-by-step implementation following the plan
- All preparation work completed - ready for immediate Phase 1 execution
- No outstanding technical debt or blocking issues identified

---

*Project Status: 🎯 Ready for Wire System Implementation*  
*Last Updated: 2025-01-27*  
*Latest Achievement: Complete session analysis & self-holding circuit solution design*  
*Current Status: Awaiting wire icon completion → Phase 1 Step 2 ready to begin*  
*Next Session: Progressive 12-step wire object system implementation*
# PyPlc - PLC Ladder Simulator Project

## Overview
PyxelとPythonを使用したPLCラダー図シミュレーターの開発プロジェクト。
工場での検証用途と学習目的を兼ねた、リアルタイム動作可視化システム。

## Project Structure
```
PyPlc/
├── main.py                 # メインシミュレーター
├── SpriteManager.py        # スプライト管理システム  
├── SpriteDefiner.py        # ビジュアルスプライト定義ツール
├── sprites.json            # スプライト定義データ
├── my_resource.pyxres      # Pyxelリソースファイル
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
- [x] 16x16ピクセルグリッド（10x10）実装
- [x] GridDeviceManagerによる交点ベースデバイス配置
- [x] デバイスパレット選択システム（1-8キー）
- [x] 電気的継続性システム（LadderRung）実装
- [x] リアルタイム電力フロー可視化
- [x] セグメント単位の配線色管理

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

### Core Classes
```python
# グリッドベースデバイス管理
class GridDevice:          # グリッド交点配置デバイス
class GridDeviceManager:   # 10x10グリッド管理システム
class DeviceType(Enum):    # デバイスタイプ定義

# 電気的継続性システム
class LadderRung:          # 横ライン電気的管理
class BusConnection:       # バスバー接続点管理
class ElectricalSystem:    # 全体電気系統管理

# 従来システム（互換性維持）
class PLCDevice:           # PLCデバイス（X, Y, M, T, C）
class DeviceManager:       # デバイス管理システム
class LogicElement:        # 論理素子基底クラス
class LadderProgram:       # プログラム全体管理
class PLCSimulator:        # メインシミュレーター
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

### Performance Benefits
- **初期化時読み込み**: JSON検索は起動時のみ
- **実行時高速アクセス**: 辞書参照によるO(1)アクセス
- **メモリ効率**: 必要最小限のスプライトキャッシュ

## Controls

### Device Selection & Placement
- **1-8 keys**: デバイスタイプ選択（パレットから）
  - 1: バスバー, 2: A接点, 3: B接点, 4: コイル
  - 5: タイマー, 6: カウンター, 7: 横線, 8: 縦線
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
- **Device Palette**: 8種類のデバイスタイプ選択インターフェース
- **Device Status Panel**: リアルタイムデバイス状態表示
- **Sprite Integration**: 状態依存スプライト切り替え

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

## Next Development Phase (Pending)

### Phase 5: Interactive Device Placement
- [ ] マウスクリックによるグリッド配置機能
- [ ] デバイス削除・移動機能
- [ ] 複数ライン回路の構築
- [ ] デバイスアドレス入力システム

### Phase 6: Advanced Electrical System
- [ ] 縦バスバー（ジャンプ線）実装
- [ ] 分岐・合流回路対応
- [ ] 自己保持回路システム
- [ ] 並列回路の電気的管理

### Phase 7: Circuit Construction Enhancement
- [ ] 回路保存・読み込み機能
- [ ] ラダー図エクスポート
- [ ] 複雑な論理回路パターン
- [ ] エラー検証システム

## Technical Debt & Future Improvements

### Architecture Enhancements
- **Vector2D Integration**: 位置計算の数学的抽象化
- **Configuration System**: 外部設定ファイル対応
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

*Project Status: Active Development*  
*Last Updated: 2025-01-24*  
*Latest Achievement: Grid-based electrical system with real-time power flow visualization*  
*Next Session: Interactive device placement with mouse operation*
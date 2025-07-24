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

## Screen Layout & Display (Updated for 256x256)

### Current Screen Layout
```
┌─────────────────────────────────────────────────────────────┐
│ PLC Ladder Simulator                    │ Sprite Test Area   │
│                                         │ [A_ON][A_OFF]      │
│                                         │ [B_ON][B_OFF]      │
│                                         │ [LAMP_ON][LAMP_OFF]│
├─────────────────────────────────────────┴───────────────────┤
│ Ladder Diagram Display Area                                 │
│ ├─[X001]─[M001]─(Y001) (AND Circuit)                      │
│ ├─[X003]─[T001]─(Y002) (Timer Circuit)                    │
│ ├─[X004]─[C001]─(Y003) (Counter Circuit)                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Device Status Monitor                                       │
│ X001: ON/OFF    Y001: ON/OFF    T001: 2.5s/3.0s           │
│ X002: ON/OFF    Y002: ON/OFF    C001: 2/3                  │
│ X003: ON/OFF    Y003: ON/OFF                               │
│ X004: ON/OFF                                               │
├─────────────────────────────────────────────────────────────┤
│ Controls: 1:X001 2:X002 3:X003(Timer) 4:X004(Counter) Q:Exit│
└─────────────────────────────────────────────────────────────┘
```

### Display Specifications
- **Screen Size**: 256x256 pixels (upgraded from 160x120)
- **Title Position**: (10, 5)
- **Ladder Diagram Area**: Y position starts at 50
- **Device Status Area**: Y position starts at 160
- **Control Info**: Bottom at Y position 240
- **Sprite Test Area**: Right side starting at (160, 10)

## Technical Architecture

### Core Classes
```python
# デバイス管理
class PLCDevice:           # PLCデバイス（X, Y, M, T, C）
class DeviceManager:       # デバイス管理システム

# 論理素子  
class LogicElement:        # 論理素子基底クラス
class ContactA:            # A接点（ノーマルオープン）
class ContactB:            # B接点（ノーマルクローズ）
class Coil:               # 出力コイル
class Timer:              # タイマー（TON）
class Counter:            # カウンター（CTU）

# ラダープログラム
class LadderLine:         # ラダー図の1行
class LadderProgram:      # プログラム全体管理
class PLCSimulator:       # メインシミュレーター
```

### Device Types & Implementation Status
- **X**: 入力デバイス (X001-X004実装済み) - 範囲: X000-X377
- **Y**: 出力デバイス (Y001-Y003実装済み) - 範囲: Y000-Y377  
- **M**: 内部リレー - 範囲: M0-M7999
- **T**: タイマー (T001: 3秒プリセット実装済み) - 範囲: T0-T255
- **C**: カウンター (C001: 3回プリセット実装済み) - 範囲: C0-C255
- **D**: データレジスタ (未実装) - 範囲: D0-D7999

### Test Circuits Implemented
1. **AND Circuit**: X001 AND X002 → Y001
2. **Timer Circuit**: X003 → T001(3秒) → Y002  
3. **Counter Circuit**: X004 → C001(3回) → Y003

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
- **1 key**: Toggle X001 (AND回路入力1)
- **2 key**: Toggle X002 (AND回路入力2)  
- **3 key**: Toggle X003 (タイマー起動)
- **4 key**: Toggle X004 (カウンター入力)
- **Q/ESC**: 終了

## Features Demonstrated

### Logic Operations
- **AND Logic**: 2入力AND回路の動作
- **Timer Operation**: 3秒遅延タイマー
- **Counter Operation**: 3回カウントアップ

### Visual Feedback
- **Real-time Ladder Display**: ラダー図の動的表示
- **Current Flow Visualization**: 通電状態の色表示（緑=ON, 灰=OFF）
- **Device Status Panel**: リアルタイムデバイス状態表示
- **Sprite Test Display**: 画面上部のスプライト表示テスト

### Technical Excellence
- **Scan Cycle**: 左→右、上→下の忠実なPLCスキャン再現
- **Object-Oriented Design**: クリーンなクラス設計
- **Type Safety**: 型ヒント付きPythonコード
- **Modular Architecture**: 機能別モジュール分離

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

### Phase 4: Sprite-Based Ladder Display
- [ ] ラダー図の素子をスプライト表示に置き換え
- [ ] ContactA/ContactBの状態依存スプライト切り替え
- [ ] Coilのアニメーション表示
- [ ] Timer/Counterの専用スプライト追加

### Phase 5: Advanced Visualization  
- [ ] 電流フローアニメーション
- [ ] スキャン順序の可視化
- [ ] より複雑な回路パターン対応
- [ ] デバッグ情報表示の拡充

### Phase 6: User Interaction Enhancement
- [ ] マウス操作対応
- [ ] 入力デバイス操作UI
- [ ] 設定保存/読み込み機能
- [ ] ラダー図ローダー実装

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
*Next Session: Sprite-based ladder display implementation*
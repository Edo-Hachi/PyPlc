# PLC Simulator Project Plan

## プロジェクト概要
PyxelとPythonを使用したPLCラダー図シミュレーターの開発。
工場での検証用途と学習目的を兼ねた、リアルタイム動作可視化システム。

## 技術スタック
- **言語**: Python 3.x
- **グラフィック**: Pyxel (160x120 解像度)
- **アーキテクチャ**: オブジェクト指向設計

## 設計コンセプト

### 1. スキャン処理の忠実な再現
- 左から右へのトレース処理
- 上から下へのライン実行順序
- リアルタイムでの電流フロー可視化

### 2. オブジェクト指向による論理回路実装
```python
# 基本設計パターン
class LogicElement:
    - inputs: List[LogicElement]
    - output: bool
    - evaluate(): bool

class Contact(LogicElement):  # 接点
class Coil(LogicElement):     # コイル
class Timer(LogicElement):    # タイマー
```

## 開発フェーズ

### Phase 1: 基本フレームワーク
- [ ] Pyxelの基本セットアップ
- [ ] LogicElementベースクラス実装
- [ ] 基本的なContact/Coilクラス
- [ ] 単純なAND回路のテスト

### Phase 2: コア機能実装
- [ ] LadderLineクラス（ライン管理）
- [ ] LadderProgramクラス（全体制御）
- [ ] スキャンサイクル実装
- [ ] デバイス管理システム（X、Y、M、T、C）

### Phase 3: 視覚化システム
- [ ] ラダー図描画エンジン
- [ ] 電流フロー表示（色変更）
- [ ] 素子状態アニメーション
- [ ] スキャン順序可視化

### Phase 4: インタラクション
- [ ] マウス/キーボード入力
- [ ] 入力デバイス操作UI
- [ ] リアルタイムデバイス監視
- [ ] デバッグ情報表示

### Phase 5: 拡張機能
- [ ] タイマー・カウンター実装
- [ ] SET/RST命令
- [ ] 基本的なラダー図ローダー
- [ ] 設定保存/読み込み

## クラス設計

### デバイス管理
```python
class PLCDevice:
    def __init__(self, address, device_type):
        self.address = address      # "X001", "Y010"等
        self.device_type = device_type  # 'X', 'Y', 'M', 'T', 'C'
        self.value = False/int
        
class DeviceManager:
    def __init__(self):
        self.devices = {}  # address -> PLCDevice
```

### 論理素子
```python
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
```

### ライン管理
```python
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

## Pyxel実装仕様

### 画面レイアウト
```
┌─────────────────────────────────────────┐
│ ラダー図表示エリア          │ デバイス  │
│ ├─[X001]─[M001]─(Y001)    │ 監視      │
│ ├─[X002]─[T001]─(Y002)    │ X001: ON  │
│ ├─[M001]───────(M002)     │ Y001: OFF │
│ │                         │ T001: 5.2s│
│ └─────────────────────────┘           │
│ 入力操作パネル                          │
│ [X001] [X002] [X003] ...              │
└─────────────────────────────────────────┘
```

### スプライト定義
```python
# 8x8ピクセルスプライト
SPRITE_CONTACT_OPEN  = 0   # □ 開接点
SPRITE_CONTACT_CLOSE = 1   # ■ 閉接点
SPRITE_COIL_OFF      = 2   # ○ コイルOFF
SPRITE_COIL_ON       = 3   # ● コイルON
SPRITE_TIMER         = 4   # ⏱ タイマー
```

### 色定義
```python
COLOR_LINE_OFF = 1      # 灰色（通電なし）
COLOR_LINE_ON  = 11     # 緑色（通電中）
COLOR_TRACE    = 10     # 黄色（トレース中）
COLOR_BG       = 0      # 黒（背景）
```

## 実装優先度

### 高優先度
1. 基本的なAND/OR回路
2. リアルタイム可視化
3. 手動入力操作

### 中優先度
1. タイマー機能
2. SET/RST命令
3. より複雑な回路パターン

### 低優先度
1. ファイル入出力
2. 高度なデバッグ機能
3. パフォーマンス最適化

## 想定される課題と対策

### 課題1: Pyxelの解像度制限
- **対策**: シンプルなスプライト設計、効率的な画面利用

### 課題2: 複雑な回路の表示
- **対策**: スクロール機能、分割表示

### 課題3: リアルタイム性能
- **対策**: 最適化されたスキャンアルゴリズム

## 参考情報

### 三菱PLCデバイス仕様
- **X**: 入力デバイス (X000-X377 等)
- **Y**: 出力デバイス (Y000-Y377 等)  
- **M**: 内部リレー (M0-M7999 等)
- **T**: タイマー (T0-T255 等)
- **C**: カウンター (C0-C255 等)
- **D**: データレジスタ (D0-D7999 等)

### 基本命令セット
- **LD/LDI**: 負荷/負荷反転
- **AND/ANI**: 論理積/論理積反転
- **OR/ORI**: 論理和/論理和反転
- **OUT**: 出力
- **SET/RST**: セット/リセット

## 開発環境

### 必要パッケージ
```bash
pip install pyxel
```

### 推奨開発環境
- Python 3.8+
- VSCode with Python extension
- Git for version control

## Next Steps

1. **Phase 1から順次実装開始**
2. **Claude CLIを活用した効率的な開発**
3. **継続的な動作テストとデバッグ**
4. **実際のラダー図での検証**

---

*このドキュメントは開発進行に合わせて更新していく*
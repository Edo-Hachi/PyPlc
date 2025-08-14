# PyPlc データレジスタ（Dデバイス）実装プラン - Claude版

## 1. 実装概要

### 1.1 プロジェクト目標
PyPlcシミュレーターに三菱PLC互換のデータレジスタ（Dデバイス）機能を追加し、数値データの保存・操作・演算機能を実現する。

### 1.2 調査結果サマリー

#### **三菱シーケンサ仕様（Web調査結果）**
- **データ容量**: 16ビット符号付き整数（-32,768～+32,767）
- **32ビット対応**: 上位ワード自動占有（例: D110指定→D111も占有）
- **分類**:
  - 一般用: D0～D199（電源OFF時クリア）
  - 停電保持用: D200～D511（電源OFF時保持）
  - 停電保持専用: D512～D799（専用エリア）
- **基本操作**: MOV命令による転送・読み書き
- **応用機能**: 比較演算・算術演算・論理演算対応

#### **既存PyPlcアーキテクチャ分析**
- **デバイス管理**: PLCDevice + DeviceManagerによる統一管理
- **現在対応**: X, Y, M, T, Cデバイス（Dは未実装）
- **統合システム**: grid_system, electrical_system, plc_logicの3層アーキテクチャ
- **UI統合**: 3段パレットシステム（15デバイス対応）

## 2. 技術設計仕様

### 2.1 データレジスタ管理クラス設計

```python
# plc_logic.py 拡張
class DataRegister:
    """データレジスタ（Dデバイス）管理クラス"""
    def __init__(self, address: str):
        self.address = address              # "D100"形式
        self.value = 0                      # 16ビット符号付き整数
        self.is_32bit = False              # 32ビットモードフラグ
        self.upper_register = None          # 32ビット時の上位レジスタ参照
        self.retain_power_off = False       # 停電保持フラグ
    
    def set_value(self, value: int, is_32bit: bool = False) -> bool:
        """値設定（範囲チェック付き）"""
        if is_32bit:
            # 32ビット範囲: -2,147,483,648 ～ 2,147,483,647
            if -2147483648 <= value <= 2147483647:
                self.value = value & 0xFFFF          # 下位16ビット
                if self.upper_register:
                    self.upper_register.value = (value >> 16) & 0xFFFF  # 上位16ビット
                return True
        else:
            # 16ビット範囲: -32,768 ～ 32,767
            if -32768 <= value <= 32767:
                self.value = value
                return True
        return False
    
    def get_value(self, is_32bit: bool = False) -> int:
        """値取得"""
        if is_32bit and self.upper_register:
            # 32ビット復元: 上位16ビット << 16 + 下位16ビット
            return (self.upper_register.value << 16) | (self.value & 0xFFFF)
        return self.value

class DataRegisterManager:
    """データレジスタ統合管理システム"""
    def __init__(self):
        self.registers = {}                 # address -> DataRegister
        self.register_ranges = {
            "general": (0, 199),           # 一般用D0-D199
            "retain": (200, 511),          # 停電保持D200-D511
            "retain_dedicated": (512, 799)  # 停電保持専用D512-D799
        }
    
    def get_register(self, address: str) -> DataRegister:
        """レジスタ取得（存在しない場合は作成）"""
        if address not in self.registers:
            register_num = int(address[1:])  # "D100" -> 100
            register = DataRegister(address)
            
            # 停電保持設定
            if 200 <= register_num <= 799:
                register.retain_power_off = True
            
            self.registers[address] = register
        return self.registers[address]
    
    def set_register_value(self, address: str, value: int, is_32bit: bool = False) -> bool:
        """レジスタ値設定"""
        register = self.get_register(address)
        
        # 32ビットモードの場合、上位レジスタも確保
        if is_32bit:
            upper_address = f"D{int(address[1:]) + 1}"
            upper_register = self.get_register(upper_address)
            register.upper_register = upper_register
            upper_register.is_32bit = True
        
        return register.set_value(value, is_32bit)
    
    def reset_general_registers(self):
        """一般用レジスタをリセット（停電保持は除く）"""
        for address, register in self.registers.items():
            if not register.retain_power_off:
                register.value = 0
```

### 2.2 PLCDevice拡張

```python
# plc_logic.py PLCDevice拡張
class PLCDevice:
    def __init__(self, address: str, device_type: str):
        self.address = address
        self.device_type = device_type
        if device_type in ['X', 'Y', 'M']:
            self.value = False
        elif device_type in ['T', 'C']:
            self.value = 0
            self.preset_value = 0
            self.current_value = 0
            self.coil_state = False
        elif device_type == 'D':  # 🆕 データレジスタ対応
            self.value = 0
            self.is_32bit = False
            self.retain_power_off = False
        else:
            self.value = 0
```

### 2.3 DeviceManager統合

```python
# plc_logic.py DeviceManager拡張
class DeviceManager:
    def __init__(self):
        self.devices = {}
        self.data_register_manager = DataRegisterManager()  # 🆕 データレジスタ管理追加
    
    def get_device(self, address: str) -> PLCDevice:
        """デバイス取得（データレジスタ対応）"""
        if address not in self.devices:
            device_type = address[0]
            self.devices[address] = PLCDevice(address, device_type)
            
            # データレジスタの場合、専用マネージャーと連動
            if device_type == 'D':
                register = self.data_register_manager.get_register(address)
                self.devices[address].value = register.value
                self.devices[address].retain_power_off = register.retain_power_off
        
        return self.devices[address]
    
    def set_data_register(self, address: str, value: int, is_32bit: bool = False) -> bool:
        """データレジスタ専用設定メソッド"""
        if address.startswith('D'):
            success = self.data_register_manager.set_register_value(address, value, is_32bit)
            if success:
                # PLCDeviceと同期
                device = self.get_device(address)
                register = self.data_register_manager.get_register(address)
                device.value = register.value
                device.is_32bit = is_32bit
            return success
        return False
    
    def get_data_register(self, address: str, is_32bit: bool = False) -> int:
        """データレジスタ値取得"""
        if address.startswith('D'):
            register = self.data_register_manager.get_register(address)
            return register.get_value(is_32bit)
        return 0
```

## 3. 評価式実装アーキテクチャ

### 3.1 DataLogicElement階層設計（推奨実装）

#### **既存LogicElementアーキテクチャ分析**
```python
# 現在のLogicElement設計パターン
class LogicElement(ABC):
    def evaluate(self, device_manager: DeviceManager) -> bool
    # 👆 bool返却型：接点・コイル論理向け
```

#### **データレジスタ特殊要件**
- **数値データ処理**: bool → int/数値演算
- **条件付き実行**: パルス実行（MOVP）対応が重要
- **多様な操作**: 転送・演算・比較・論理演算
- **エラーハンドリング**: オーバーフロー・ゼロ除算検出

### 3.2 DataLogicElement基底クラス設計

```python
# plc_logic.py 拡張
class DataLogicElement(LogicElement):
    """データ処理用論理素子基底クラス"""
    def __init__(self, device_address: str = None):
        super().__init__(device_address)
        self.pulse_mode = False         # パルス実行モード
        self.last_trigger_state = False # 前回トリガー状態
        self.execution_enabled = False   # 実行可能フラグ
        self.error_flag = False         # エラー状態フラグ
    
    @abstractmethod
    def evaluate_data(self, device_manager: DeviceManager) -> bool:
        """データ処理専用評価メソッド"""
        pass
    
    def evaluate(self, device_manager: DeviceManager) -> bool:
        """既存LogicElementインターフェース維持"""
        current_trigger = self.inputs[0].evaluate(device_manager) if self.inputs else True
        
        # パルス実行判定
        if self.pulse_mode:
            self.execution_enabled = current_trigger and not self.last_trigger_state
        else:
            self.execution_enabled = current_trigger
        
        self.last_trigger_state = current_trigger
        
        # データ処理実行
        if self.execution_enabled:
            try:
                result = self.evaluate_data(device_manager)
                self.error_flag = False
                return result
            except Exception as e:
                # エラーフラグ設定（三菱PLC準拠）
                device_manager.set_device_value("M8020", True)  # 演算エラー
                self.error_flag = True
                return False
        return False
    
    def _get_value(self, device_manager: DeviceManager, address: str, is_32bit: bool = False) -> int:
        """アドレスまたは即値から値を取得"""
        if address.isdigit() or address.startswith('-'):
            return int(address)
        elif address.startswith('D'):
            return device_manager.get_data_register(address, is_32bit)
        else:
            # 他のデバイスタイプ（X, Y, M等）
            device = device_manager.get_device(address)
            return int(device.value) if isinstance(device.value, bool) else device.value
```

### 3.3 基本命令セット実装

#### **MOV命令（データ転送）**

```python
class MOVInstruction(DataLogicElement):
    """MOV命令: データ転送（MOVP対応）"""
    def __init__(self, source_address: str, dest_address: str, is_32bit: bool = False, pulse_mode: bool = True):
        super().__init__()
        self.source_address = source_address
        self.dest_address = dest_address
        self.is_32bit = is_32bit
        self.pulse_mode = pulse_mode  # デフォルトパルス実行（MOVP）
    
    def evaluate_data(self, device_manager: DeviceManager) -> bool:
        """MOV実行: source → dest"""
        source_value = self._get_value(device_manager, self.source_address, self.is_32bit)
        success = device_manager.set_data_register(self.dest_address, source_value, self.is_32bit)
        return success

class ADDInstruction(DataLogicElement):
    """ADD命令: 加算"""
    def __init__(self, operand1: str, operand2: str, result: str, is_32bit: bool = False):
        super().__init__()
        self.operand1 = operand1
        self.operand2 = operand2
        self.result = result
        self.is_32bit = is_32bit
        self.pulse_mode = True  # 算術演算はパルス実行推奨
    
    def evaluate_data(self, device_manager: DeviceManager) -> bool:
        """ADD実行: operand1 + operand2 → result"""
        val1 = self._get_value(device_manager, self.operand1, self.is_32bit)
        val2 = self._get_value(device_manager, self.operand2, self.is_32bit)
        
        result_value = val1 + val2
        
        # オーバーフロー検出
        max_val = 2147483647 if self.is_32bit else 32767
        min_val = -2147483648 if self.is_32bit else -32768
        
        if min_val <= result_value <= max_val:
            return device_manager.set_data_register(self.result, result_value, self.is_32bit)
        else:
            # オーバーフローエラー
            raise OverflowError(f"ADD result overflow: {result_value}")

class CMPInstruction(DataLogicElement):
    """CMP命令: 比較（比較結果をbool返却）"""
    def __init__(self, operand1: str, operand2: str, comparison_type: str = "EQ"):
        super().__init__()
        self.operand1 = operand1
        self.operand2 = operand2
        self.comparison_type = comparison_type
        self.pulse_mode = False  # 比較は連続実行
    
    def evaluate_data(self, device_manager: DeviceManager) -> bool:
        """CMP実行: 比較結果をboolで返す"""
        val1 = self._get_value(device_manager, self.operand1, False)
        val2 = self._get_value(device_manager, self.operand2, False)
        
        if self.comparison_type == "EQ":
            return val1 == val2
        elif self.comparison_type == "GT":
            return val1 > val2
        elif self.comparison_type == "LT":
            return val1 < val2
        elif self.comparison_type == "GE":
            return val1 >= val2
        elif self.comparison_type == "LE":
            return val1 <= val2
        elif self.comparison_type == "NE":
            return val1 != val2
        return False
```

### 3.4 実装統合のメリット

#### **1. 既存システムとの完全互換性**
```python
# 既存LadderLineとシームレス統合
ladder_line = LadderLine()
ladder_line.add_element(ContactA("X001"))                    # 実行条件
ladder_line.add_element(MOVInstruction("K100", "D0"))        # データ転送
ladder_line.add_element(Coil("M001"))                        # 完了フラグ
```

#### **2. パルス実行の自動管理**
```python
# 使用例
X0 ── MOVP K100 D0    # X0立ち上がりエッジで1回のみ実行
X1 ── MOV D0 D10      # X1がONの間、毎スキャン実行（非推奨）
```

#### **3. 三菱PLC準拠エラーハンドリング**
```python
# エラー検出例
ADD D0 D1 D2          # 加算実行
M8020                 # 演算エラーフラグ（システム提供）
── SET M100           # エラー表示ランプ点灯
```

### 3.5 ラダー図統合実例

#### **温度制御システム例**
```python
# ライン1: 測定開始
line1 = LadderLine()
line1.add_element(ContactA("X001"))                          # 測定開始ボタン
line1.add_element(MOVInstruction("D100", "D0"))             # 現在温度 → 作業用
line1.add_element(Coil("M001"))                             # 測定完了フラグ

# ライン2: 温度判定・制御
line2 = LadderLine()
line2.add_element(ContactA("M001"))                          # 測定完了時
line2.add_element(CMPInstruction("D0", "D101", "GT"))       # 現在温度 > 設定温度
line2.add_element(Coil("Y001"))                             # 冷却装置ON

# ライン3: 統計更新
line3 = LadderLine()
line3.add_element(ContactA("M001"))                          # 測定完了時
line3.add_element(ADDInstruction("D200", "K1", "D200"))     # 測定回数カウンタ
line3.add_element(Coil("M002"))                             # 統計更新完了
```

### 3.6 推奨実装戦略

#### **Phase 1: DataLogicElement基盤構築**
- DataLogicElement基底クラス実装
- パルス実行システム統合
- 三菱PLC準拠エラーハンドリング

#### **Phase 2: 基本命令実装**
- MOVInstruction（パルス・連続両対応）
- CMPInstruction（比較結果→接点化）
- ADD/SUBInstruction（算術演算）

#### **Phase 3: 高度機能**
- INC/DEC（インクリメント・デクリメント）
- MUL/DIV（乗算・除算）
- 論理演算（AND/OR/XOR）

この階層設計により、**実PLC準拠のデータレジスタ処理**を**既存PyPlcアーキテクチャ**に**最小限の影響**で統合し、**高い拡張性**と**エラー安全性**を実現できます。

## 4. UI統合設計

### 4.1 config.py拡張

```python
# config.py 追加
class DeviceType(Enum):
    # ... 既存デバイス ...
    DATA_REGISTER = "DATA_REGISTER"    # 🆕 データレジスタ

# データレジスタアドレス範囲定義
class DeviceAddressRanges:
    DATA_REGISTER = {
        "prefix": "D",
        "min": 0,
        "max": 7999,
        "ranges": {
            "general": (0, 199),           # 一般用
            "retain": (200, 511),          # 停電保持
            "retain_dedicated": (512, 799), # 停電保持専用
            "extended": (800, 7999)        # 拡張エリア
        }
    }
```

### 4.2 デバイスパレット統合

```python
# main.py _setup_device_palette() 拡張
def _setup_device_palette(self):
    """デバイスパレットの定義（データレジスタ追加）"""
    self.device_palette = [
        # ... 既存11デバイス ...
        {"type": DeviceType.DATA_REGISTER, "name": "Data Reg", "sprite": "DATA_REG_ICON"},  # 🆕
    ]
```

### 4.3 データレジスタUI表示

```python
# ui_components.py UIRenderer拡張
class UIRenderer:
    def render_data_register_panel(self, data_register_manager: DataRegisterManager, x: int, y: int):
        """データレジスタ監視パネル表示"""
        pyxel.text(x, y, "Data Registers:", Colors.TEXT)
        
        # 使用中レジスタのみ表示（最大10個）
        display_count = 0
        for address in sorted(data_register_manager.registers.keys()):
            if display_count >= 10:
                break
                
            register = data_register_manager.registers[address]
            if register.value != 0 or register.retain_power_off:  # 値が設定されているものを表示
                display_text = f"{address}: {register.value}"
                if register.is_32bit:
                    display_text += " (32bit)"
                pyxel.text(x, y + 10 + (display_count * 8), display_text, Colors.TEXT)
                display_count += 1
```

## 5. 段階的実装計画

### Phase 1: 基盤システム構築（1週間）

#### **Step 1.1: データレジスタ基本クラス実装**
- [ ] DataRegister, DataRegisterManager クラス作成
- [ ] 16ビット/32ビット値管理システム
- [ ] 停電保持機能実装

#### **Step 1.2: PLCDevice統合**
- [ ] PLCDevice に Dデバイス対応追加
- [ ] DeviceManager にデータレジスタ管理統合
- [ ] リセット機能拡張（停電保持考慮）

#### **Step 1.3: 単体テスト**
- [ ] データレジスタ作成・値設定・取得テスト
- [ ] 32ビットモード動作テスト
- [ ] 範囲チェック・オーバーフロー検出テスト

### Phase 2: 基本命令実装（1週間）

#### **Step 2.1: DataLogicElement基盤実装**
- [ ] DataLogicElement基底クラス作成
- [ ] パルス実行システム実装
- [ ] 三菱PLC準拠エラーハンドリング（M8020演算エラーフラグ）
- [ ] 汎用値取得メソッド（即値・Dレジスタ・他デバイス対応）

#### **Step 2.2: MOV命令実装**
- [ ] MOVInstruction クラス作成（DataLogicElement継承）
- [ ] 即値→レジスタ転送
- [ ] レジスタ→レジスタ転送
- [ ] 16ビット/32ビット対応
- [ ] デフォルトパルス実行（MOVP）対応

#### **Step 2.3: 算術・比較命令実装**
- [ ] ADDInstruction（加算）命令
- [ ] SUBInstruction（減算）命令
- [ ] CMPInstruction（比較）命令
- [ ] オーバーフロー検出・例外処理
- [ ] 比較結果の接点化

### Phase 3: UI統合（1週間）

#### **Step 3.1: デバイスパレット拡張**
- [ ] config.py にDATA_REGISTERタイプ追加
- [ ] スプライト定義（データレジスタアイコン）
- [ ] 3段パレットシステム統合

#### **Step 3.2: データレジスタ表示パネル**
- [ ] UIRenderer にデータレジスタ表示機能追加
- [ ] アクティブレジスタ一覧表示
- [ ] 値の実時間更新

#### **Step 3.3: 設定ダイアログ統合**
- [ ] pyxdlg.py を使用したレジスタ設定ダイアログ
- [ ] アドレス・初期値・32ビットモード設定
- [ ] バリデーション機能

### Phase 4: 高度機能・テスト（1週間）

#### **Step 4.1: 論理演算命令**
- [ ] AND（論理積）命令
- [ ] OR（論理和）命令
- [ ] XOR（排他論理和）命令
- [ ] シフト演算（SHL/SHR）

#### **Step 4.2: 統合テスト**
- [ ] タイマー・カウンターとの連携テスト
- [ ] 複合回路でのデータレジスタ動作確認
- [ ] パフォーマンステスト（大量レジスタ操作）

#### **Step 4.3: ドキュメント整備**
- [ ] 使用マニュアル作成
- [ ] サンプル回路集
- [ ] トラブルシューティングガイド

## 6. 技術的課題と解決策

### 6.1 メモリ効率化

**課題**: 8000個のレジスタ領域を効率的に管理
**解決策**: 
- 疎な辞書型による実使用レジスタのみメモリ確保
- 遅延初期化パターンによるメモリ使用量最適化

### 6.2 32ビット演算対応

**課題**: 16ビットレジスタでの32ビット値管理
**解決策**:
- 上位・下位レジスタの自動ペア管理
- 32ビット演算時の自動レジスタ確保
- オーバーフロー検出とエラーハンドリング

### 6.3 既存システムとの統合

**課題**: 既存のX,Y,M,T,Cデバイス管理との整合性
**解決策**:
- PLCDeviceクラスの統一インターフェース維持
- DeviceManagerの段階的拡張
- 既存機能への影響最小化

## 7. 期待される効果

### 7.1 機能向上
- **数値データ処理**: 測定値・設定値・計算結果の保存
- **レシピ機能**: 製品別パラメータセットの切り替え
- **データロギング**: 履歴データの蓄積・参照

### 7.2 教育効果
- **実PLC準拠**: 三菱シーケンサとの高い互換性
- **実践的学習**: 数値処理を伴う制御プログラム作成体験
- **デバッグ支援**: データレジスタ値の可視化によるトラブルシューティング

### 7.3 応用可能性
- **HMI連携**: 外部システムとのデータ交換基盤
- **ファイルI/O**: レジスタデータの保存・復元機能
- **通信機能**: ネットワーク経由でのデータ共有

## 8. リスク管理

| リスク要因 | 影響度 | 発生確率 | 対応策 |
|-----------|--------|----------|--------|
| 既存機能への影響 | 高 | 低 | 段階的実装・包括的回帰テスト |
| パフォーマンス低下 | 中 | 中 | プロファイリング・最適化実装 |
| メモリ使用量増加 | 中 | 高 | 疎なデータ構造・メモリ監視 |
| 32ビット演算複雑性 | 高 | 中 | 十分な単体テスト・エラーハンドリング |

## 9. 参考情報

### 9.1 三菱電機PLC仕様準拠項目
- **データ形式**: 16ビット符号付き整数基本、32ビット拡張対応
- **アドレス範囲**: D0-D7999（実装対象: D0-D799）
- **停電保持**: D200-D799エリアでの状態保持
- **基本命令**: MOV, ADD, SUB, CMP命令の互換実装

### 9.2 PyPlcアーキテクチャ活用
- **モジュラー設計**: 既存の3層アーキテクチャとの整合性
- **スプライト統合**: 統一されたビジュアル表現
- **ダイアログシステム**: pyxdlg.pyによる設定UI

### 9.3 実用例・学習リソース

#### **おすすめ学習サイト（詳細調査結果）**

**🥇 電気設計人.com（最重要リソース）**
- **データレジスタ基礎**: https://denkisekkeijin.com/ladder/data-register/
- **MOV命令詳解**: https://denkisekkeijin.com/ladder/mitsubishi_fx/fx-mov/
- **実践プログラム**: https://denkisekkeijin.com/ladder/mitsubishi_fx/fx-dregister-use/
- **数値計算実例**: https://denkisekkeijin.com/ladder/lad_knowhow_easy/khe_fx_inc_dec/

**🥈 実践的プログラミング**
- **GX Work3講座**: https://www.niwakafa.com/entry/2019/03/28/【入門編】GX_Work3によるプログラム講座016
- **PLC制御技術**: https://plckouza.com/st3/st3_2.html

#### **データレジスタ実用パターン集**

**基本パターン1: 定数転送**
```
X0 ON → MOV K325 D0    # 定数325をD0に転送
X1 ON → MOV K0 D0      # D0をクリア（0転送）
```

**基本パターン2: レジスタ間転送**
```
X0 ON → MOV D0 D10     # D0の値をD10にコピー
X1 ON → BMOV D0 D10 K5 # D0-D4をD10-D14に一括転送
```

**数値演算パターン1: 加算・減算**
```
X0 ON → ADD D0 K10 D1  # D0 + 10 → D1
X1 ON → SUB D0 K5 D1   # D0 - 5 → D1
X2 ON → INC D0         # D0を+1（インクリメント）
X3 ON → DEC D0         # D0を-1（デクリメント）
```

**数値演算パターン2: 比較処理**
```
CMP D0 K100 M0 M1 M2   # D0と100を比較
                       # M0: D0 < 100
                       # M1: D0 = 100  
                       # M2: D0 > 100
```

**実用アプリケーション例**

**1. 工程管理システム**
```
D0: 現在工程番号（0-99）
D1: 各工程の実行時間カウンタ
D2: エラーコード格納エリア
D10-D19: 工程別設定時間（レシピデータ）
```

**2. 温度制御システム**
```
D100: 現在温度値（-999〜9999）
D101: 設定温度値
D102: 温度差分（設定-現在）
D103: 制御出力値（0-100%）
```

**3. カウンター・統計管理**
```
D200: 生産カウンタ（停電保持）
D201: 不良品カウンタ（停電保持）
D202: 今日の生産目標
D203: 生産効率（%表示）
```

#### **32ビットデータの実用例**

**大きな数値の処理**
```
DMOV K100000 D0       # 100,000をD0-D1に32ビット転送
DADD D0 K50000 D2     # D0-D1 + 50,000 → D2-D3
```

**時間管理（ミリ秒単位）**
```
D0-D1: システム稼働時間（ms）
D2-D3: 前回メンテナンス日時
D4-D5: 次回メンテナンス予定日時
```

#### **パルス実行の重要性**

**問題のあるプログラム（連続実行）**
```
X0 ── MOV K100 D0     # X0がONの間、毎スキャン実行される
```

**推奨プログラム（パルス実行）**
```
X0 ── MOVP K100 D0    # X0がONした瞬間のみ1回実行
```

#### **エラーハンドリング例**

**オーバーフロー検出**
```
ADD D0 D1 D2
M8020                 # 演算エラーフラグ
── SET M100           # エラー表示ランプ点灯
```

**ゼロ除算対策**
```
CMP D1 K0 M0 M1 M2
M1                    # D1 = 0の場合
── SET M101           # ゼロ除算エラーフラグ
M2                    # D1 > 0の場合
── DIV D0 D1 D2       # 除算実行
```

#### **デバッグ・監視のベストプラクティス**

**デバイス監視項目**
- 使用中レジスタの一覧表示
- 値の変化履歴
- 設定値との比較
- 異常値の検出・警告

**テスト時の確認ポイント**
- 境界値での動作（-32768, 32767）
- オーバーフロー時の処理
- 停電保持レジスタの動作確認
- 32ビット演算の正確性

## 10. 比較演算子アイコンシステム設計

### 10.1 視覚的ラダー図表現

#### **比較演算専用アイコンシステム**
```
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│ X01 │ === │ [=] │ === │ === │ === │ Y01 │
│     │     │K100 │     │     │     │     │
│     │     │ D0  │     │     │     │     │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┘
回路の意味: X01がON かつ D0=K100 なら Y01をON
```

#### **比較演算子アイコン種類**
```
[=] : 等価比較 (EQ)    D0 = K100
[>] : より大きい (GT)   D0 > K100  
[<] : より小さい (LT)   D0 < K100
[≥] : 以上 (GE)        D0 ≥ K100
[≤] : 以下 (LE)        D0 ≤ K100
[≠] : 不等価 (NE)      D0 ≠ K100
```

#### **情報表示レイアウト**
```
┌─────┐
│ [=] │ ← 8x8比較アイコン
│K100 │ ← 比較値1（定数・デバイス）
│ D0  │ ← 比較値2（デバイス）
└─────┘
```

### 10.2 統一アイコンシステム設計

#### **デバイス分類とアイコン対応**
```
データ保持系:
- [D] : データレジスタ（値保持）
- [T] : タイマー（時間管理）  
- [C] : カウンター（回数管理）

データ処理系:
- [MOV] : データ転送
- [ADD] : 加算演算
- [SUB] : 減算演算
- [MUL] : 乗算演算
- [DIV] : 除算演算

比較判定系:
- [=] : 等価比較
- [>] : 大小比較（大）
- [<] : 大小比較（小）
- [≥] : 以上比較
- [≤] : 以下比較  
- [≠] : 不等価比較
```

### 10.3 実装統合メリット

#### **1. 直感的回路理解**
```
従来: X01 ── CMP D0 K100 EQ ── Y01
新方式: X01 ── [=] K100 D0 ── Y01
       読みやすさ大幅向上！
```

#### **2. 教育効果向上**
- 視覚的にロジックが理解できる
- 実PLC操作への移行が容易
- デバッグ時の状態把握が簡単

#### **3. 国際対応**
- 数学記号は言語に依存しない
- グローバルな理解しやすさ

### 10.4 スプライト実装仕様

#### **実装済みスプライト定義**
```json
// sprites.json 実装済み
{
  "136_0": {
    "x": 136,
    "y": 0,
    "NAME": "D_DEV",
    "ACT_NAME": "TRUE"
  },
  "144_0": {
    "x": 144,
    "y": 0,
    "NAME": "D_DEV",
    "ACT_NAME": "FALSE"
  },
  "152_0": {
    "x": 152,
    "y": 0,
    "NAME": "CMP",
    "ACT_NAME": "TRUE"
  },
  "160_0": {
    "x": 160,
    "y": 0,
    "NAME": "CMP",
    "ACT_NAME": "FALSE"
  }
}
```

#### **スプライト使用方法**
```python
# main.py スプライトキャッシュ追加
def _initialize_sprites(self):
    """スプライトキャッシュ初期化"""
    self.sprites = {
        # ... 既存スプライト ...
        
        # データレジスタスプライト
        "D_DEV_ON": sprite_manager.get_sprite_by_name_and_tag("D_DEV", "TRUE"),
        "D_DEV_OFF": sprite_manager.get_sprite_by_name_and_tag("D_DEV", "FALSE"),
        
        # 比較演算子スプライト
        "CMP_ON": sprite_manager.get_sprite_by_name_and_tag("CMP", "TRUE"),
        "CMP_OFF": sprite_manager.get_sprite_by_name_and_tag("CMP", "FALSE"),
    }
```

#### **デバイスパレット実装**
```python
# main.py _setup_device_palette() 拡張
self.device_palette = [
    # ... 既存11デバイス ...
    {"type": DeviceType.DATA_REGISTER, "name": "Data Reg", "sprite": "D_DEV_OFF"},
    {"type": DeviceType.COMPARE_DEVICE, "name": "Compare", "sprite": "CMP_OFF"},
]
```

#### **GridDevice状態別スプライト表示**
```python
# grid_system.py 表示ロジック
def get_sprite_name(self):
    """デバイス状態に応じたスプライト名を返す"""
    if self.device_type == DeviceType.DATA_REGISTER:
        # データレジスタの場合、値の有無で判定
        return "D_DEV_ON" if self.current_value != 0 else "D_DEV_OFF"
    
    elif self.device_type == DeviceType.COMPARE_DEVICE:
        # 比較デバイスの場合、比較結果で判定
        return "CMP_ON" if self.comparison_result else "CMP_OFF"
    
    # ... 他のデバイスタイプ ...
```

#### **横一列表示UI設計**

##### **レイアウト仕様**
```
データレジスタ: [D📶] D100:325
比較演算子:     [=📶] =K100
```

##### **表示幅計算**
```
スプライト: 8ピクセル
スペース:   2ピクセル  
テキスト:   約30ピクセル（5文字×6ピクセル）
総幅:       約40ピクセル
```

##### **右端オフセット対応**
```python
# ui_components.py 最適化表示
def render_data_device(self, device, x, y):
    """データデバイス横一列表示"""
    # 状態別スプライト取得
    sprite_name = device.get_sprite_name()
    sprite_data = self.sprites.get(sprite_name)
    
    # 右端判定・オフセット計算
    text_width = self._calculate_text_width(device)
    if x + 8 + 2 + text_width > Layout.GRID_START_X + (Layout.GRID_COLS * Layout.GRID_SIZE):
        # 右端の場合、左にオフセット
        text_x = x - text_width - 2
        sprite_x = x
    else:
        # 通常配置
        sprite_x = x
        text_x = x + 8 + 2
    
    # スプライト描画
    if sprite_data:
        pyxel.blt(sprite_x, y, 0, sprite_data["x"], sprite_data["y"], 8, 8, Colors.TRANSPARENT)
    
    # 情報テキスト描画（横一列）
    info_text = self._generate_info_text(device)
    pyxel.text(text_x, y, info_text, Colors.TEXT)

def _calculate_text_width(self, device):
    """テキスト幅計算"""
    info_text = self._generate_info_text(device)
    return len(info_text) * 4  # 1文字約4ピクセル

def _generate_info_text(self, device):
    """情報テキスト生成"""
    if device.device_type == DeviceType.DATA_REGISTER:
        if device.device_address and device.current_value != 0:
            return f"{device.device_address}:{device.current_value}"  # "D100:325"
        elif device.device_address:
            return device.device_address  # "D100"
        else:
            return "D???"
    
    elif device.device_type == DeviceType.COMPARE_DEVICE:
        symbol = device.comparison_symbol or "="
        param = device.param_summary or "K100"
        return f"{symbol}{param}"  # "=K100", ">80"
    
    return ""
```

##### **配置パターン例**

**通常配置（左・中央）:**
```
[D📶] D100:325    [=📶] =K100    [タイマー]
 ↑      ↑          ↑     ↑
スプライト テキスト   スプライト テキスト
```

**右端配置（自動オフセット）:**
```
D100:325 [D📶]    =K100 [=📶]    [タイマー]
   ↑        ↑        ↑      ↑
 テキスト  スプライト テキスト  スプライト
```

##### **色分け表示**
```python
# 状態別色分け
def get_text_color(self, device):
    """デバイス状態に応じた文字色"""
    if device.device_type == DeviceType.DATA_REGISTER:
        if device.current_value != 0:
            return Colors.VALUE_ACTIVE  # 値有り: 明るい色
        else:
            return Colors.VALUE_INACTIVE  # 値無し: 暗い色
    
    elif device.device_type == DeviceType.COMPARE_DEVICE:
        if device.comparison_result:
            return Colors.COMPARE_TRUE   # 比較TRUE: 緑色
        else:
            return Colors.COMPARE_FALSE  # 比較FALSE: 赤色
    
    return Colors.TEXT
```

### 10.5 実用回路例

#### **温度監視システム**
```
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│ X01 │ === │ [>] │ === │ === │ === │ Y01 │ ← 冷却装置
│     │     │ 80  │     │     │     │     │
│     │     │D100 │     │     │     │     │
├─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│ X01 │ === │ [<] │ === │ === │ === │ Y02 │ ← 加熱装置
│     │     │ 20  │     │     │     │     │
│     │     │D100 │     │     │     │     │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┘
意味: D100(温度) > 80°C → 冷却ON
     D100(温度) < 20°C → 加熱ON
```

#### **生産カウンター管理**
```
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│ X02 │ === │ [≥] │ === │ === │ === │ Y03 │ ← 目標達成ランプ
│     │     │1000 │     │     │     │     │
│     │     │D200 │     │     │     │     │
├─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│ X03 │ === │ [=] │ === │ === │ === │ Y04 │ ← アラームランプ  
│     │     │ 0   │     │     │     │     │
│     │     │D201 │     │     │     │     │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┘
意味: D200(生産数) ≥ 1000 → 目標達成
     D201(不良数) = 0 → 品質良好
```

## 11. 今後の拡張計画

### 10.1 Phase 5以降の機能
- **浮動小数点演算**: 実数値処理対応
- **インデックスレジスタ**: Z, Vデバイス実装
- **ファイルレジスタ**: 外部ファイルとの連携
- **ネットワーク機能**: PLC間通信シミュレーション

### 10.2 高度なデバッグ機能
- **ウォッチ機能**: 特定レジスタの監視・履歴表示
- **ブレークポイント**: レジスタ値条件でのシミュレーション停止
- **データ変更履歴**: レジスタ値変更のトレーサビリティ

---

**実装開始予定**: 2025年1月
**完成目標**: 2025年2月
**責任者**: Claude + Human Developer
**プロジェクト管理**: TodoWriteツールによる段階的実装管理

*本プランは三菱電機PLC仕様とPyPlc既存アーキテクチャの詳細調査に基づいて作成され、実用的で教育効果の高いデータレジスタシステムの実現を目指します。*
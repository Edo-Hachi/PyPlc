# PyPlc Ver3 縦方向接続改修プラン
## AI開発支援用詳細設計書

**作成日**: 2025-08-05  
**対象**: 縦方向接続アーキテクチャの根本的改修  
**目的**: LINK_TO_UP/LINK_FROM_DOWN問題の解決とPLC標準準拠の実現  

---

## 📋 **現状問題分析**

### **発見された課題**
```python
# 問題1: 複雑すぎる上下伝播ロジック
if device.device_type == DeviceType.LINK_TO_UP:
    self._trace_power_flow(device.connections.get('up'), visited)  # 上方向のみ

if device.device_type == DeviceType.LINK_FROM_DOWN:
    self._handle_parallel_convergence(device, visited)  # 複雑な合流処理
```

### **根本的問題**
- **実装複雑性**: `_handle_parallel_convergence()` 125行の複雑ロジック
- **概念理解困難**: 上下方向伝播の直感性欠如
- **PLC標準乖離**: 実PLCの物理的分岐・合流との不整合
- **保守性低下**: デバッグが困難な複雑条件分岐

### **影響範囲**
- `config.py`: Line 144-146 (DeviceType定義)
- `core/circuit_analyzer.py`: Line 57-125 (電力トレースロジック)
- `core/device_palette.py`: パレット定義との連携

---

## 🎯 **新概念設計**

### **設計原則**
1. **物理モデル準拠**: 実PLCの電気的分岐・合流を忠実に再現
2. **シンプル第一**: 理解しやすく保守しやすい実装
3. **直感的操作**: ユーザーが予想できる動作
4. **PLC標準準拠**: 教育効果の最大化

### **新デバイス定義**

#### **BRANCH_POINT（分岐点）**
```python
BRANCH_POINT = "BRANCH_POINT"  # 電力を全方向に分配する分岐点
```
**機能仕様**:
- **電力分配**: 入力電力を4方向（上下左右）に同時分配
- **導通条件**: 常時導通（配線と同様）
- **表示記号**: `┼` または `+` （十字分岐）
- **PLCアナロジー**: 電気的分岐ボックス

#### **LINK_VIRT（垂直配線）- 強化版**
```python
LINK_VIRT = "LINK_VIRT"  # 上下方向の物理的配線（双方向）
```
**機能仕様**:
- **双方向伝播**: 上下両方向に電力伝播
- **導通条件**: 常時導通（水平配線と同様）
- **表示記号**: `│` （垂直線）
- **PLCアナロジー**: 物理的垂直配線

---

## 🔧 **実装仕様**

### **新しい電力トレースロジック**
```python
def _trace_power_flow(self, start_pos: Optional[Tuple[int, int]], visited: Optional[Set[Tuple[int, int]]] = None) -> None:
    """新しいシンプルな電力トレースロジック"""
    # ... 基本処理（既存と同じ） ...
    
    # --- 新しいシンプルな分岐処理 ---
    if device.device_type == DeviceType.BRANCH_POINT:
        # 全方向に電力分配（シンプルかつ直感的）
        for direction in ['up', 'down', 'left', 'right']:
            self._trace_power_flow(device.connections.get(direction), visited)
    
    elif device.device_type == DeviceType.LINK_VIRT:
        # 上下双方向に電力伝播（物理配線モデル）
        self._trace_power_flow(device.connections.get('up'), visited)
        self._trace_power_flow(device.connections.get('down'), visited)
    
    else:
        # 既存デバイスロジック維持（互換性確保）
        self._trace_power_flow(device.connections.get('right'), visited)
```

### **導通判定の更新**
```python
def _is_conductive(self, device: PLCDevice) -> bool:
    """導通判定ロジックの更新"""
    # ... 既存ロジック ...
    
    # 新デバイスは常時導通（配線系と同様）
    if device.device_type in [DeviceType.BRANCH_POINT, DeviceType.LINK_VIRT]:
        return True
    
    # 既存ロジック維持
    # ...
```

---

## 📁 **ファイル変更計画**

### **Phase 1: 基盤準備**

#### **1. config.py 更新**
```python
# Line 120 DeviceType定義に追加
class DeviceType(Enum):
    # ... 既存定義 ...
    
    # 新概念追加
    BRANCH_POINT = "BRANCH_POINT"     # 分岐点（全方向分配）
    
    # 既存LINK_VIRT強化（実装は変更なし、コメント明確化）
    LINK_VIRT = "LINK_VIRT"           # 垂直配線（上下双方向）
    
    # 廃止予定（後方互換性で当面残存）
    LINK_TO_UP = "LINK_TO_UP"         # 廃止予定
    LINK_FROM_DOWN = "LINK_FROM_DOWN" # 廃止予定
```

#### **2. パレット定義更新**
```python
# Line 172 DEVICE_PALETTE_DEFINITIONS更新
"top_row": [
    # ... 既存定義 ...
    (DeviceType.BRANCH_POINT, "BRANCH", 6, "分岐点"),      # 新規追加
    (DeviceType.LINK_VIRT, "LINK |", 7, "垂直配線"),       # 位置変更
    # ... 残りの定義 ...
],
```

### **Phase 2: コア実装**

#### **3. core/circuit_analyzer.py 改修**
```python
# _trace_power_flow メソッド更新
# Line 57-67 の LINK_TO_UP/LINK_FROM_DOWN 処理を新ロジックで置換

# _handle_parallel_convergence メソッド削除予定
# Line 86-125 の複雑ロジックを新シンプルロジックで置換

# _is_conductive メソッド更新
# Line 76 に新デバイス追加
```

#### **4. デバイス表示更新**
```python
# main.py または renderer関連
# BRANCH_POINT: "┼" または "+" 記号で表示
# LINK_VIRT: "│" 記号で表示（既存から変更なし）
```

### **Phase 3: 統合・テスト**

#### **5. テストケース作成**
```python
# 新しい縦方向接続パターンのテスト
test_patterns = [
    "simple_branch",      # BRANCH_POINT単体テスト
    "vertical_link",      # LINK_VIRT双方向テスト
    "complex_parallel",   # BRANCH_POINT + LINK_VIRT組み合わせ
    "backward_compat",    # 旧LINK_TO_UP/FROM_DOWN併存テスト
]
```

---

## 🚀 **段階的実装手順**

### **Step 1: 準備作業**
1. **config.py更新**: BRANCH_POINT追加、コメント整理
2. **パレット統合**: 新デバイスをUI上で選択可能に
3. **表示機能**: 新デバイスの視覚的表現実装

### **Step 2: コアロジック実装**
1. **電力トレース更新**: 新デバイス対応ロジック追加
2. **導通判定更新**: 新デバイス導通条件追加
3. **並行テスト**: 旧ロジックと新ロジックの併存確認

### **Step 3: 検証・移行**
1. **回路テスト**: 複雑な並列回路での動作確認
2. **性能測定**: 処理速度・安定性の評価
3. **段階的移行**: 旧概念の段階的廃止

### **Step 4: 完全移行**
1. **旧コード削除**: LINK_TO_UP/LINK_FROM_DOWN完全除去
2. **ドキュメント更新**: コメント・設計書更新
3. **最終検証**: 全機能統合テスト

---

## 📊 **期待される効果**

### **技術的改善**
- **コード削減**: 125行の複雑ロジック → 10行のシンプルロジック
- **理解容易性**: 物理モデルベースの直感的動作
- **保守性向上**: デバッグ・拡張の容易化
- **処理効率**: 不要な条件判定の除去

### **ユーザー体験向上**
- **操作予測性**: 期待通りに動作する縦方向接続
- **学習効果**: 実PLCとの完全一致による教育価値向上
- **回路設計**: より柔軟で直感的な並列回路構築

### **プロジェクト品質向上**
- **PLC標準準拠**: 実PLC設計思想との完全一致
- **コード品質**: WindSurf A+評価基準の維持・向上
- **長期保守性**: 将来機能拡張への対応力強化

---

## ⚠️ **実装時の注意事項**

### **後方互換性**
- 既存のLINK_TO_UP/LINK_FROM_DOWNは当面併存
- 段階的移行により既存回路の動作保証
- 移行期間中の動作テスト必須

### **テスト戦略**
- 新機能単体テスト
- 既存機能回帰テスト  
- 複雑回路統合テスト
- 性能・安定性テスト

### **品質基準**
- WindSurf A+評価レベルの実装品質維持
- PLC標準準拠の厳格な遵守
- コメント・ドキュメントの充実

---

## 📝 **実装優先順位**

### **High Priority**
1. config.py更新（BRANCH_POINT追加）
2. circuit_analyzer.py新ロジック実装
3. 基本テストケース作成・検証

### **Medium Priority**
1. パレット統合（UI対応）
2. 表示機能実装（新デバイス記号）
3. 既存回路での互換性確認

### **Low Priority**
1. 旧概念の完全削除
2. ドキュメント・コメント更新
3. 最終統合テスト

---

**このプランに基づき、段階的かつ安全に縦方向接続の改修を実行する。**  
**各ステップでの動作確認と品質維持を最優先とし、PLC標準準拠を厳格に遵守する。**

---
*作成者: Claude (Sonnet 4)*  
*最終更新: 2025-08-05*  
*次回更新: Phase 1実装完了時*
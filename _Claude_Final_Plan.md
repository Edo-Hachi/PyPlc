# PyPlc Ver3 縦方向接続改修 - 最終実装プラン
## ユーザー要件反映版・AI開発支援用完全設計書

**作成日**: 2025-08-05  
**基準プラン**: 統合プラン + ユーザー修正指示  
**目的**: 矛盾点解決済み・実装レベル完全プラン  

---

## 🎯 **確定仕様（ユーザー決定事項）**

### **1. デバイス名統一**
```python
# 確定: LINK_BRANCH で統一
DeviceType.LINK_BRANCH = "LINK_BRANCH"  # 分岐点デバイス
```
- **概念名**: BRANCH_POINT → **LINK_BRANCH** に変更
- **スプライト名**: "LINK_BRNCH" → **"LINK_BRANCH"** に統一
- **理由**: 実装との整合性確保、命名規則統一

### **2. 電力分配仕様確定**
```python
# 確定: 上・下・右の3方向分配（左には戻らない）
for direction in ['right', 'up', 'down']:  # 左を除外
    next_pos = device.connections.get(direction)
    if next_pos and next_pos not in visited:
        self._trace_power_flow(next_pos, visited)
```
- **分配方向**: 右・上・下の3方向のみ
- **除外方向**: 左（電力の逆流防止）
- **理由**: PLCラダー図の電力フロー原則準拠

---

## 📋 **修正された問題分析**

### **解決済み矛盾点**
1. ✅ **デバイス名不整合**: LINK_BRANCH で統一確定
2. ✅ **電力分配論理**: 3方向分配（右・上・下）で確定
3. ✅ **仕様曖昧性**: ユーザー決定により明確化

### **継続課題**
- **実装複雑性**: `_handle_parallel_convergence()` 125行の複雑ロジック
- **概念理解困難**: LINK_TO_UP/LINK_FROM_DOWN の直感性欠如  
- **PLC標準乖離**: 実PLC物理モデルとの不整合

---

## 🏗️ **確定アーキテクチャ設計**

### **新デバイス定義**
```python
# config.py 確定実装仕様
class DeviceType(Enum):
    # ... 既存定義 ...
    
    # 新デバイス（確定）
    LINK_BRANCH = "LINK_BRANCH"    # 分岐点（右・上・下分配）
    LINK_VIRT = "LINK_VIRT"        # 垂直配線（上下双方向）
    
    # 段階的廃止対象（後方互換性保持）
    LINK_TO_UP = "LINK_TO_UP"         # Phase 4で削除予定
    LINK_FROM_DOWN = "LINK_FROM_DOWN" # Phase 4で削除予定
```



### **確定電力トレースロジック**
```python
def _trace_power_flow(self, start_pos: Optional[Tuple[int, int]], visited: Optional[Set[Tuple[int, int]]] = None) -> None:
    """確定版：新電力トレースロジック"""
    if visited is None:
        visited = set()
    
    if start_pos is None or start_pos in visited:
        return
    
    visited.add(start_pos)
    device = self.grid.get_device(start_pos[0], start_pos[1])
    if not device:
        return
    
    # 通電マーク
    device.is_energized = True
    
    # 導通チェック
    if not self._is_conductive(device):
        return
    
    # 確定仕様：デバイス別電力分配処理
    if device.device_type == DeviceType.LINK_BRANCH:
        # 3方向分配：右・上・下（左除外）
        for direction in ['right', 'up', 'down']:
            next_pos = device.connections.get(direction)
            if next_pos and next_pos not in visited:
                self._trace_power_flow(next_pos, visited)
    
    elif device.device_type == DeviceType.LINK_VIRT:
        # 上下双方向伝播
        for direction in ['up', 'down']:
            next_pos = device.connections.get(direction)
            if next_pos and next_pos not in visited:
                self._trace_power_flow(next_pos, visited)
    
    else:
        # 標準デバイス（右方向のみ）
        next_pos = device.connections.get('right')
        if next_pos and next_pos not in visited:
            self._trace_power_flow(next_pos, visited)

def _is_conductive(self, device: PLCDevice) -> bool:
    """確定版：導通判定ロジック"""
    # ... 既存ロジック ...
    
    # 新デバイス導通条件（確定）
    if device.device_type in [DeviceType.LINK_BRANCH, DeviceType.LINK_VIRT]:
        return True
    
    # 既存ロジック維持
    # ...
```

---

## 📁 **段階的実装計画**

### **Phase 1: 基盤準備（2日間）**
**期間**: 2025-08-05 ～ 2025-08-07  
**目標**: 新デバイス定義とスプライト統合

#### **Task 1.1: config.py更新**
```python
# 確定実装内容
class DeviceType(Enum):
    # ... 既存定義 ...
    LINK_BRANCH = "LINK_BRANCH"    # 新規追加（確定名）
    # 旧概念は Phase 4 まで併存

# パレット定義更新
DEVICE_PALETTE_DEFINITIONS = {
    "top_row": [
        # ... 既存 ...
        (DeviceType.LINK_BRANCH, "BRANCH", 6, "分岐点"),  # 新規（確定）
        (DeviceType.LINK_VIRT, "LINK |", 7, "垂直配線"),   # 既存強化
        # ...
    ]
}
```

#### **Task 1.2: スプライト定義統一**
```python
# sprites.json 確定更新内容
# ユーザー提供スプライト座標を使用
"LINK_BRANCH": {
    "ON": {"x": 72, "y": 8, "w": 16, "h": 16},   # TRUE状態
    "OFF": {"x": 80, "y": 8, "w": 16, "h": 16}   # FALSE状態
}

# LINK_VIRT は既存のまま使用
```

#### **Task 1.3: デバイスパレット統合**
- core/device_palette.py に LINK_BRANCH 追加
- UI表示名: "BRANCH" 
- キーバインド: 6番キー
- ツールチップ: "分岐点"

#### **Phase 1 完了条件**
- [ ] DeviceType.LINK_BRANCH 定義完了
- [ ] スプライト座標統一完了  
- [ ] パレットからLINK_BRANCH選択可能
- [ ] グリッドへの基本配置動作確認

### **Phase 2: コアロジック実装（3日間）**
**期間**: 2025-08-07 ～ 2025-08-10  
**目標**: 電力トレースロジック完全書き換え

#### **Task 2.1: circuit_analyzer.py 改修**
```python
# 実装対象メソッド
def _trace_power_flow(self, start_pos, visited=None):
    # 上記確定ロジック実装

def _is_conductive(self, device):
    # LINK_BRANCH, LINK_VIRT を常時導通に追加

# 削除対象
def _handle_parallel_convergence(self, device, visited):
    # Phase 2 で完全削除（125行削減）
```

#### **Task 2.2: 接続管理システム対応**
- grid_system.py: LINK_BRANCH の4方向接続管理
- 配置時の自動接続判定ロジック
- 接続情報の保存・復元機能

#### **Task 2.3: 基本動作テスト**
```python
# 最小テストケース
test_link_branch_basic = """
ROW,COL,DEVICE_TYPE,ADDRESS,STATE
0,1,CONTACT_A,X001,False
0,2,LINK_BRANCH,,False
0,3,CONTACT_B,X002,False
1,2,LINK_VIRT,,False
2,2,CONTACT_A,X003,False
"""
```

#### **Phase 2 完了条件**
- [ ] _trace_power_flow() 新ロジック実装完了
- [ ] _handle_parallel_convergence() 削除完了
- [ ] LINK_BRANCH 基本分岐動作確認
- [ ] 既存機能への影響なし確認

### **Phase 3: 包括的テスト・検証（3日間）**
**期間**: 2025-08-10 ～ 2025-08-13  
**目標**: 全パターン動作検証と性能確認

#### **Task 3.1: テストケース作成**
```python
# 新規テストファイル
test_files = [
    "test_link_branch_basic.csv",      # 基本3方向分岐
    "test_link_branch_multi.csv",      # 複数行跨ぎ分岐  
    "test_branch_virt_combined.csv",   # BRANCH + VIRT 組み合わせ
    "test_complex_parallel.csv",       # 複雑並列回路
    "test_backward_compatibility.csv", # 旧デバイス併存テスト
]
```

#### **Task 3.2: 性能・品質検証**
- 30FPS安定動作維持確認
- メモリ使用量測定（増加なし目標）
- 複雑回路での応答速度測定
- WindSurf A+品質基準維持確認

#### **Task 3.3: 回帰テスト**
- 既存テストケース全通過確認
- 自己保持回路動作確認
- 基本直列・並列回路動作確認

#### **Phase 3 完了条件**
- [ ] 全新規テストケース通過
- [ ] 性能劣化なし確認
- [ ] 既存機能100%動作確認
- [ ] 品質基準維持確認

### **Phase 4: 完全移行・クリーンアップ（2日間）**
**期間**: 2025-08-13 ～ 2025-08-15  
**目標**: 旧システム完全除去と最終検証

#### **Task 4.1: 旧概念完全削除**
```python
# config.py から削除
# LINK_TO_UP = "LINK_TO_UP"         # 削除
# LINK_FROM_DOWN = "LINK_FROM_DOWN" # 削除

# circuit_analyzer.py から削除
# 旧LINK_TO_UP/LINK_FROM_DOWN処理ロジック完全除去
```

# User 追記 --------------------------------------
config.py の以下2つを削除する

        (DeviceType.LINK_FROM_DOWN, "LINK v", 6, "下から合流"),
        (DeviceType.LINK_TO_UP, "LINK ^", 7, "上へ分岐"),

以下のように変更です

>>      (DeviceType.LINK_BRANCH, "BRANCH", 6, "リンクブランチポイント"),
>>      (DeviceType.EMPTY, "", 7, "未定義"),




#### **Task 4.2: テストケース書き換え**
```python
# 書き換え対象
existing_tests = [
    "test_link_direct.csv",     # LINK_BRANCH版に書き換え
    "test_link_virt_1row.csv",  # LINK_BRANCH版に書き換え  
    "test_link_virt_2row.csv",  # LINK_BRANCH版に書き換え
]
```

#### **Task 4.3: ドキュメント更新**
- CLAUDE.md の開発記録更新
- コード内コメント整理
- 技術文書の更新

#### **Phase 4 完了条件**
- [ ] 旧概念完全削除完了
- [ ] 全テストファイル新形式対応
- [ ] ドキュメント完全更新
- [ ] 最終品質確認完了

---

## ⚠️ **リスク管理と軽減策**

### **高リスク項目**
| リスク | 影響度 | 発生確率 | 軽減策 |
|--------|--------|----------|--------|
| 既存並列回路の動作停止 | 高 | 中 | Phase 2での段階的移行、バックアップ保持 |
| 接続管理ロジックのバグ | 高 | 中 | Phase 2での集中テスト、単体テスト充実 |
| 性能劣化 | 中 | 低 | Phase 3での性能測定、最適化実装 |
| UI操作性の悪化 | 中 | 中 | Phase 1でのUI検証、ユーザビリティテスト |

### **品質保証戦略**
- **段階的実装**: 各Phase完了時の動作確認必須
- **バックアップ保持**: 各Phase開始前のコミット必須
- **自動テスト**: 可能な限りの自動化実装
- **即座ロールバック**: 問題発生時の復旧手順準備

---

## 📊 **期待される効果**

### **技術的改善**
- **コード削減**: 125行複雑ロジック → 15行シンプルロジック（88%削減）
- **処理効率**: 不要な条件分岐・合流判定の除去
- **保守性**: 直感的で理解しやすい電力フロー
- **拡張性**: 新機能追加時の影響範囲最小化

### **ユーザー体験向上**
- **直感性**: 実PLC分岐点モデルに準拠した操作感
- **予測性**: 期待通りに動作する縦方向接続
- **学習効果**: PLC教育価値の最大化
- **操作効率**: シンプルな分岐点配置による回路構築効率化

### **プロジェクト品質向上**
- **PLC標準準拠**: 実PLC設計思想との完全一致
- **コード品質**: WindSurf A+評価基準の維持・向上
- **長期保守性**: 将来機能拡張への対応力強化
- **教育価値**: 実用PLCへの移行時違和感なし

---

## 🎯 **成功指標**

### **定量的指標**
- [ ] LINK_BRANCH基本動作成功率: 100%
- [ ] 複数行跨ぎ接続成功率: 100%  
- [ ] 30FPS安定動作維持: 100%
- [ ] メモリ使用量増加: 0%
- [ ] コード行数削減: 88%以上
- [ ] テストケース通過率: 100%

### **定性的指標**
- [ ] コード可読性の向上
- [ ] デバッグ容易性の向上
- [ ] PLC標準準拠度の完全達成
- [ ] ユーザー操作の直感性向上
- [ ] 教育効果の最大化

---

## 📝 **実装チェックリスト**

### **Phase 1: 基盤準備**
- [ ] `DeviceType.LINK_BRANCH` 定義追加
- [ ] スプライト座標統一（72,8 / 80,8）
- [ ] パレット定義更新（6番キー、"BRANCH"）
- [ ] 基本配置機能動作確認

### **Phase 2: コアロジック**
- [ ] `_trace_power_flow()` 新ロジック実装
- [ ] `_handle_parallel_convergence()` 完全削除
- [ ] `_is_conductive()` LINK_BRANCH対応
- [ ] 基本3方向分岐動作確認

### **Phase 3: テスト・検証**
- [ ] 5つの新規テストケース作成・実行
- [ ] 性能テスト（30FPS維持）実施
- [ ] 既存機能回帰テスト実施
- [ ] 品質基準維持確認

### **Phase 4: 完全移行**
- [ ] LINK_TO_UP/LINK_FROM_DOWN完全削除
- [ ] 既存テストケース3件書き換え
- [ ] ドキュメント完全更新
- [ ] 最終品質確認

---

## 💡 **実装時の重要注意事項**

### **コーディング開始前の必須確認**
1. **Phase順序厳守**: 各Phase完了まで次に進まない
2. **バックアップ必須**: 各Phase開始前のコミット
3. **テスト優先**: 実装よりテストケース作成を優先
4. **品質基準**: WindSurf A+レベルの実装品質維持

### **実装品質基準**
```python
# 必須遵守事項
- PLC標準準拠の厳格な実装
- 日本語コメントの充実
- 型宣言の完全実装
- ステップバイステップ確認
- git コミットでの進捗管理
```

---

## 🚀 **実装開始準備完了**

このプランに基づき、以下の順序で実装を進めます：

1. **Phase 1開始**: config.py更新からスタート
2. **段階的検証**: 各Task完了時の動作確認
3. **品質維持**: WindSurf A+基準の厳格な遵守
4. **PLC準拠**: 実PLC設計思想の完全実装

**全ての矛盾点が解決され、ユーザー要件が完全に反映された実装レベル完全プランです。このプランに従って段階的かつ安全に縦方向接続の根本的改修を実行し、PyPlc Ver3をより高い品質レベルに押し上げます。**

---
*最終作成者: Claude (Sonnet 4)*  
*ユーザー要件反映: LINK_BRANCH統一、3方向分配確定*  
*最終更新: 2025-08-05*  
*実装開始準備: 完了*
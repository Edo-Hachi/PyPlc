# PyPlc Ver3 - デバイスグリッド配置処理 作業プラン

**作成日**: 2025-08-02  
**作成者**: Claude AI Assistant  
**対象**: デバイスグリッドへの配置処理（描画＋内部データ）完成

---

## 🎯 **デバイスグリッド配置処理 - 作業プラン**

### **📊 現在の実装状況評価**

#### ✅ **既に完了している素晴らしい機能**
- **SpriteManager統合**: grid_system.pyに正常に組み込み済み
- **基本スプライト描画**: `pyxel.blt()`を使用した描画ロジック実装
- **COIL_REV追加**: sprites.jsonにCOIL_REV TRUE/FALSE追加済み
- **EMPTY対応**: SpriteManagerでEMPTY処理追加
- **座標計算**: グリッド座標→描画座標の変換完成

#### 🚧 **改善が必要な部分**
- バスバーが旧描画方式（rect）のまま
- フォールバック描画でデバッグ情報不足
- 通電状態計算との完全統合が未完了

---

## 📋 **Todo リスト**

### **Phase 1: 基本動作確認（高優先度）**

#### **Todo 1: 現在の描画システム動作確認・テスト実行** ⭐⭐⭐⭐⭐
**目標**: 現在のスプライト描画システムが正常に動作することを確認
**作業内容**:
- main.pyを実行してスプライト描画動作確認
- CONTACT_A, CONTACT_B, COIL_STD, LINK系の正常表示確認
- エラーログ・警告メッセージのチェック
- 座標計算の正確性確認

#### **Todo 2: バスバー（L_SIDE/R_SIDE）のスプライト描画対応** ⭐⭐⭐⭐⭐
**目標**: バスバーをスプライト描画方式に統一
**作業内容**:
```json
# sprites.jsonに追加が必要
"72_0": {"x": 72, "y": 0, "NAME": "L_SIDE", "ACT_NAME": "TRUE"},
"80_0": {"x": 80, "y": 0, "NAME": "R_SIDE", "ACT_NAME": "TRUE"}
```
- my_resource.pyxresにバスバースプライト追加
- grid_system.pyの旧描画方式削除
- 新しいスプライト描画ロジック実装

#### **Todo 3: デバイス配置時の通電状態計算ロジック統合** ⭐⭐⭐⭐⭐
**目標**: デバイス配置後の即座な通電状態反映
**作業内容**:
- `place_device()`実行後の`circuit_analyzer`連携
- 新規配置デバイスの通電状態即座反映
- リアルタイム回路解析との統合
- 自己保持回路での動作確認

---

### **Phase 2: 品質向上（中優先度）**

#### **Todo 4: フォールバック描画（PINK矩形）の改善・デバッグ情報追加** ⭐⭐⭐
**目標**: スプライトが見つからない場合の適切な対応
**作業内容**:
```python
# より詳細なエラー表示
else:
    print(f"警告: {device.device_type.name} のスプライトが見つかりません")
    # 視覚的にわかりやすいフォールバック描画
    pyxel.rect(draw_x, draw_y, sprite_size, sprite_size, pyxel.COLOR_PINK)
    pyxel.text(draw_x, draw_y, "?", pyxel.COLOR_WHITE)
```

#### **Todo 5: main.pyのテスト描画コード削除・統合完了** ⭐⭐⭐
**目標**: テスト用コードを削除して本格統合完了
**作業内容**:
- `_draw_sprite_manager_test()`メソッド削除
- テスト用のSpriteManager読み込み処理削除
- `draw()`メソッドからテスト呼び出し削除

#### **Todo 6: circuit_analyzer.pyとの通電状態連携確認** ⭐⭐⭐
**目標**: 回路解析結果の正確なスプライト反映確認
**作業内容**:
- 回路解析結果がスプライト表示に正確に反映されているか確認
- 自己保持回路での通電状態変化の表示確認
- 複雑回路での動作テスト

---

### **Phase 3: 最適化（低優先度）**

#### **Todo 7: パフォーマンス最適化・描画効率化** ⭐⭐
**目標**: 描画処理の高速化
**作業内容**:
- スプライト座標取得のキャッシュ化
- 不要な描画処理の削減
- 30FPS安定動作の確保

#### **Todo 8: エラーハンドリング強化・ログ出力改善** ⭐
**目標**: デバッグ効率の向上
**作業内容**:
- より詳細な警告メッセージ
- デバッグモード実装
- エラー回復機能の追加

---

## 🚀 **推奨実行順序**

### **Week 1: Phase 1完了目標**
1. **Todo 1**: 現在のシステム動作確認 → **最優先**
2. **Todo 2**: バスバースプライト対応 → **即座実装**
3. **Todo 3**: 通電状態計算統合 → **システム統合**

### **Week 1完了後の成功基準**
- [ ] 全デバイスがスプライト表示される
- [ ] バスバーがスプライト描画で統一される
- [ ] デバイス配置後の通電状態が即座に反映される
- [ ] 30FPS安定動作が維持される

### **Week 2: Phase 2-3実装**
4. **Todo 4-6**: 品質向上（中優先度）
5. **Todo 7-8**: 最適化（低優先度）

---

## 📊 **技術仕様詳細**

### **スプライト描画統合仕様**

#### **現在の実装状況（grid_system.py:141-143）**
```python
# デバイスのスプライト描画
coords = sprite_manager.get_sprite_coords(device.device_type, device.is_energized)
if coords:
    pyxel.blt(draw_x, draw_y, 0, coords[0], coords[1], sprite_size, sprite_size, 0)
```

#### **座標計算ロジック（grid_system.py:126-127）**
```python
draw_x = self.origin_x + c * self.cell_size - sprite_size // 2
draw_y = self.origin_y + r * self.cell_size - sprite_size // 2
```

#### **必要なsprites.json拡張**
```json
{
  "sprites": {
    // 既存スプライト + 追加が必要
    "72_0": {"x": 72, "y": 0, "NAME": "L_SIDE", "ACT_NAME": "TRUE"},
    "80_0": {"x": 80, "y": 0, "NAME": "R_SIDE", "ACT_NAME": "TRUE"}
  }
}
```

### **通電状態連携仕様**

#### **デバイス配置フロー**
1. `place_device()` → デバイス配置
2. `_update_connections()` → 接続更新
3. `circuit_analyzer.analyze()` → 通電計算
4. `draw()` → スプライト描画（通電状態反映）

#### **通電状態判定**
```python
# device.is_energized の値に基づいてスプライト選択
sprite_coords = sprite_manager.get_sprite_coords(device_type, is_energized)
# TRUE → 通電時スプライト, FALSE → 非通電時スプライト
```

---

## 🎯 **期待される効果**

### **完成時の達成目標**
- **統一されたスプライト描画**: 全デバイスが美しいスプライト表示
- **リアルタイム通電表示**: デバイス配置と同時に通電状態反映
- **PLC標準準拠**: 実際のPLCと同等の視覚的表現
- **30FPS安定動作**: パフォーマンス最適化による快適操作

### **教育的価値の向上**
- **実PLC移行時の違和感なし**: 標準的なラダー図表示
- **視覚的理解促進**: 通電状態の明確な表現
- **デバッグ効率向上**: 問題箇所の即座特定

---

## 📝 **実装時の注意点**

### **既存機能の保護**
- 現在動作している機能を破壊しない
- 段階的実装により安全性確保
- 各Todo完了後の動作確認必須

### **設計思想の維持**
- PLC標準準拠の徹底継続
- シンプル・可読性重視の維持
- Ver3のモジュール統合方針継続

### **テスト項目**
- 各デバイスタイプの正常表示
- 通電状態変化の正確反映
- 複雑回路での動作確認
- パフォーマンス目標の達成確認

---

**このClaude作業プランにより、デバイスグリッド配置処理を完全に仕上げ、Ver3の完成度を大幅に向上させます。**

*最終更新: 2025-08-02*  
*作成者: Claude AI Assistant*  
*次回更新: Phase 1完了時*
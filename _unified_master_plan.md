# PyPlc Ver3 - 統合マスタープラン（最終版）

**作成日**: 2025-08-02  
**統合者**: Claude AI Assistant  
**統合元**: Gemini Plan + WindSurf Plan + Claude Plan  
**目標**: デバイス配置機能 + スプライト描画システムの完全統合

---

## 🎯 **統合プラン概要**

3つのAI提案を分析・統合し、**最も効率的で実用的な実装順序**を決定しました。

### **📊 プラン分析結果**

#### **Geminiプランの優位性**
- ✅ **ユーザー操作重視**: 実際の使用シーンを考慮
- ✅ **段階的実装**: データ更新→解析→描画の論理的順序
- ✅ **プレビュー機能**: ゴーストスプライト提案が秀逸

#### **WindSurfプランの優位性**
- ✅ **操作仕様明確**: キーボードショートカット詳細定義
- ✅ **ファイル構成整理**: 修正対象ファイルの明確化
- ✅ **制約テスト重視**: バスバー配置禁止等の実用性

#### **Claudeプランの優位性**
- ✅ **現状分析詳細**: 既存実装の正確な把握
- ✅ **技術仕様具体的**: 実装コード例とエラー対応
- ✅ **パフォーマンス重視**: 30FPS維持を明確に目標設定

---

## 🚀 **統合マスタープラン - 実装順序**

### **Phase 1: 基盤システム検証・修正** ⭐⭐⭐⭐⭐

#### **1.1 現在のシステム動作確認** 
**優先度**: 最高 / **工数**: 1-2時間
- **目標**: スプライト描画システムの完全動作確認
- **作業**:
  - main.py実行テスト
  - 全スプライト表示確認（CONTACT_A/B, COIL_STD/REV, LINK系）
  - エラーログ詳細分析
  - my_resource.pyxres読み込み確認


### **Phase 2: デバイス配置システム実装** ⭐⭐⭐⭐⭐


#### **2.2 マウス配置処理（Gemini案ベース）**
**優先度**: 最高 / **工数**: 3-4時間
- **目標**: データ更新ロジック実装
- **作業**:
  ```python
  def _handle_device_placement(self):
      if not self.mouse_state.hovered_pos or not self.mouse_state.on_editable_area:
          return
          
      row, col = self.mouse_state.hovered_pos
      selected_device = self.device_palette.get_selected_device_type()
      
      if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
          if selected_device == DeviceType.DEL:
              self.grid_system.remove_device(row, col)
          else:
              address = f\"DEV_{row}_{col}\"
              self.grid_system.place_device(row, col, selected_device, address)
      
      elif pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
          device = self.grid_system.get_device(row, col)
          if device:
              device.state = not device.state  # 状態トグル
  ```

#### **2.3 通電状態計算統合**
**優先度**: 最高 / **工数**: 2-3時間
- **目標**: リアルタイム回路解析
- **作業**:
  - 配置/削除後の`circuit_analyzer.solve_ladder()`実行
  - 新規デバイスの通電状態即座反映
  - 自己保持回路動作確認

---

### **Phase 3: 視覚的UX向上** ⭐⭐⭐⭐

#### **3.1 プレビュー機能（Gemini案採用）**
## Pyxelには半透明機能がないが、マウスカーソルのグリッドポイントにスプライトを表示するのはありだと思います
**優先度**: 高 / **工数**: 2-3時間
- **目標**: ゴーストスプライト実装
- **作業**:
  ```python
  def _draw_placement_preview(self):
      if not self.mouse_state.hovered_pos or not self.mouse_state.on_editable_area:
          return
          
      row, col = self.mouse_state.hovered_pos
      selected_device = self.device_palette.get_selected_device_type()
      
      if selected_device != DeviceType.DEL:
          coords = sprite_manager.get_sprite_coords(selected_device, True)
          if coords:
              draw_x = self.grid_system.origin_x + col * self.grid_system.cell_size - 4
              draw_y = self.grid_system.origin_y + row * self.grid_system.cell_size - 4
              # 半透明ゴースト描画
              pyxel.blt(draw_x, draw_y, 0, coords[0], coords[1], 8, 8, 0)
  ```

#### **3.2 配置制約チェック（WindSurf案採用）**
**優先度**: 高 / **工数**: 2時間
- **目標**: 無効配置の防止
- **作業**:
  - バスバー列への配置禁止
  - グリッド範囲外チェック
  - 制約違反時の視覚的警告

#### **3.3 エラーハンドリング強化（Claude案採用）**
**優先度**: 中 / **工数**: 1-2時間
- **目標**: デバッグ効率向上
- **作業**:
  ```python
  # 詳細ログ出力
  if not coords:
      print(f\"警告: {device.device_type.name} のスプライトが見つかりません\")
      pyxel.rect(draw_x, draw_y, 8, 8, pyxel.COLOR_PINK)
      pyxel.text(draw_x, draw_y, \"?\", pyxel.COLOR_WHITE)
  ```

---

### **Phase 4: 最終統合・最適化** ⭐⭐⭐

#### **4.1 統合テスト**
**優先度**: 中 / **工数**: 2-3時間
- 全デバイスタイプ配置テスト
- 削除機能完全テスト
- 複雑回路での通電テスト
- 30FPS維持確認

#### **4.2 パフォーマンス最適化**
**優先度**: 低 / **工数**: 1-2時間
- 描画処理効率化
- 不要な座標計算削減
- メモリ使用量最適化

---

## 📊 **実装仕様詳細**

### **操作仕様（最終決定版）**

#### **マウス操作**
```
左クリック: 選択中デバイスを配置（DEL選択時は削除）
右クリック: デバイス状態トグル（テスト用）
ホバー: 配置プレビュー表示（ゴーストスプライト）
```

### **配置制約ルール**
1. **バスバー列（0列, 19列）**: 配置禁止
3. **グリッド範囲外**: 自動的に無視
4. **編集不可領域**: ホバー時に警告表示

### **通電計算統合**
```python
# 配置/削除処理後の即座実行
def _update_circuit_after_placement(self):
    self.grid_system.reset_all_energized_states()
    self.circuit_analyzer.solve_ladder()
    # 描画は次のフレームで自動更新
```

---

## 🎯 **成功基準**

### **Phase 1完了基準**
- [ ] 全スプライト正常表示
- [ ] バスバー描画統一完了
- [ ] エラーメッセージゼロ

### **Phase 2完了基準**
- [ ] キーボードデバイス選択動作
- [ ] マウス配置/削除動作
- [ ] 通電状態即座反映

### **Phase 3完了基準**
- [ ] プレビュー機能完全動作
- [ ] 制約チェック完全動作
- [ ] エラーハンドリング完成

### **Phase 4完了基準**
- [ ] 全機能統合テスト完了
- [ ] 30FPS安定動作確認
- [ ] PLC標準準拠完成

---

## 📁 **修正対象ファイル優先順位**

### **最優先修正ファイル**
1. **main.py**: デバイス配置処理、キーボード入力
2. **core/grid_system.py**: バスバー描画修正
3. **sprites.json**: バスバー定義追加

### **次優先修正ファイル**
4. **core/device_palette.py**: キーボード選択統合
5. **core/input_handler.py**: 制約チェック統合

### **最終修正ファイル**
6. **config.py**: 制約ルール定義
7. **my_resource.pyxres**: スプライト画像追加

---

## 🚀 **実装開始推奨**

**推奨開始**: **Phase 1.1 現在のシステム動作確認**

まず現在のスプライト描画システムを実行し、どの部分が動作してどの部分に問題があるかを正確に把握してから、段階的に改善していくことを強く推奨します。

---

## 💡 **実装時の重要な注意点**

### **既存機能保護**
- Ver3の既存動作機能を絶対に破壊しない
- 段階的実装で各Phase完了後に動作確認必須

### **設計思想維持**
- PLC標準準拠の徹底継続
- 30FPS安定動作の維持
- シンプル・可読性重視の継続

### **統合品質確保**
- 3つのAI案の優位性を最大限活用
- 教育的価値とユーザビリティの両立
- 実PLC移行時の違和感なし

---

**この統合マスタープランにより、PyPlc Ver3のデバイス配置機能を最高品質で完成させ、PLC教育ツールとしての完成度を飛躍的に向上させます。**

*最終更新: 2025-08-02*  
*統合者: Claude AI Assistant（Gemini + WindSurf + Claude統合版）*  
*次回更新: Phase 1完了時*

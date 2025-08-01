# 🎯 **デバイス配置機能実装プラン**

## 📊 **現在の実装状況**
- ✅ SpriteManager統合完了
- ✅ sprites.json拡張（COIL_REV, EMPTY追加）
- ✅ グリッド描画システム完成
- ✅ デバイス描画機能実装済み

## 📋 **デバイス配置機能実装TODO**

### **Phase 1: 配置インターフェース設計**

#### 1. **デバイス選択システム**
- キーボードショートカット（1=CONTACT_A, 2=CONTACT_B, 3=COIL_STD等）
- 現在選択中デバイスの表示
- デバイスパレット表示の改善

#### 2. **マウス配置処理**
- 左クリック：デバイス配置
- 右クリック：デバイス削除
- グリッド交点への正確な配置

### **Phase 2: データ構造更新**

#### 3. **GridSystem拡張**
- `place_device(row, col, device_type)` メソッド
- `remove_device(row, col)` メソッド
- 配置制約チェック（バスバー列への配置禁止等）

#### 4. **デバイス状態管理**
- 新規配置デバイスの初期状態設定
- 通電状態の適切な初期化

### **Phase 3: 描画更新システム**

#### 5. **リアルタイム描画更新**
- 配置後の即座な描画更新
- マウスホバー時のプレビュー表示
- 配置可能位置のハイライト

#### 6. **視覚フィードバック**
- 配置成功/失敗の視覚的フィードバック
- 無効な配置位置の警告表示

### **Phase 4: 統合テスト**

#### 7. **機能テスト**
- 各デバイスタイプの配置テスト
- 削除機能のテスト
- 描画更新の確認

#### 8. **制約テスト**
- バスバー列への配置禁止確認
- グリッド範囲外配置の防止確認

## 🔧 **実装優先順位**

### **最優先（今すぐ実装）:**
- デバイス選択システム（キーボードショートカット）
- 基本的なマウス配置処理

### **次優先:**
- GridSystemの配置/削除メソッド
- リアルタイム描画更新

### **最後:**
- 視覚フィードバックの改善
- 詳細なテスト

## 💡 **実装方針**

1. **段階的実装**: 基本機能から始めて徐々に拡張
2. **既存コード活用**: 現在のGridSystemとSpriteManagerを最大限活用
3. **ユーザビリティ重視**: 直感的な操作感を重視

## 🎮 **操作仕様（予定）**

### **キーボードショートカット**
```
1: CONTACT_A (A接点)
2: CONTACT_B (B接点)
3: COIL_STD (標準コイル)
4: COIL_REV (反転コイル)
5: TIMER (タイマー)
6: COUNTER (カウンター)
D: DEL (削除モード)
E: EMPTY (空白モード)
```

### **マウス操作**
```
左クリック: 選択中デバイスを配置
右クリック: デバイス削除
ホバー: 配置プレビュー表示
```

## 📁 **関連ファイル**

### **修正対象ファイル**
- `main.py` - キーボード入力処理、メインループ
- `core/grid_system.py` - デバイス配置/削除メソッド
- `core/input_handler.py` - マウス/キーボード入力処理
- `core/device_palette.py` - デバイス選択UI

### **参照ファイル**
- `sprites.json` - スプライト定義
- `config.py` - DeviceType定義、制約設定

## 🚀 **次のアクション**

**選択肢:**
- A) デバイス選択システム（キーボードショートカット）
- B) マウス配置処理
- C) GridSystem拡張メソッド
- D) 全体的な実装方針の詳細検討

---

**作成日時**: 2025-08-02T22:01:14+09:00  
**プロジェクト**: PyPlc Ver3 - PLC Ladder Diagram Simulator  
**フェーズ**: SpriteManager統合完了 → デバイス配置機能実装

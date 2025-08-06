# PyPlc Ver3 デバイスID入力・編集機能実装プラン

## 📋 **実装概要**

**目標**: エディットモードでのデバイス右クリック→ID入力ダイアログ表示機能の実装  
**アーキテクチャ**: Ver3設計思想に合致したシンプルなモーダルダイアログシステム  
**操作方法**: マウス右クリック → デバイスID編集ダイアログ表示

---

## 🎯 **Phase 1: コアダイアログシステム実装**

### **Task 1.1: DeviceIDDialog基本クラス作成**
**ファイル**: `core/device_id_dialog.py`（新規作成）  
**推定時間**: 45分

**実装内容**:
```python
class DeviceIDDialog:
    """Ver3専用デバイスID編集ダイアログ"""
    
    def __init__(self, device_type: DeviceType, current_id: str = ""):
        self.device_type = device_type
        self.current_id = current_id
        self.input_text = current_id
        self.is_active = False
        self.dialog_result = None  # True: OK, False: Cancel
        
    def show_modal(self) -> tuple[bool, str]:
        """モーダル表示・入力処理（Pyxelループ統合）"""
        
    def update(self):
        """キーボード・マウス入力処理"""
        
    def draw(self):
        """ダイアログUI描画"""
        
    def _validate_device_id(self, device_id: str) -> bool:
        """PLC標準準拠デバイスIDバリデーション"""
```

**機能仕様**:
- モーダルウィンドウ表示（中央配置）
- テキスト入力機能（英数字のみ）
- OK/Cancelボタン（マウス・キー対応）
- 背景暗転効果（モーダル感の演出）

### **Task 1.2: PLC標準バリデーション実装**
**推定時間**: 30分

**バリデーション仕様**:
```python
# デバイスタイプ別ID形式
CONTACT_A/B: X000-X377 (8進数)
COIL/COIL_REV: Y000-Y377, M000-M7999
TIMER: T000-T255
COUNTER: C000-C255
LINK系: IDなし（バリデーションスキップ）
```

**実装詳細**:
- デバイスタイプ別のID形式チェック
- 数値範囲バリデーション（8進数・10進数対応）
- エラーメッセージ表示機能

---

## 🎯 **Phase 2: Ver3統合実装**

### **Task 2.1: main.py右クリック処理拡張**
**ファイル**: `main.py`  
**推定時間**: 20分

**変更箇所**: `_handle_device_placement()`メソッド

**実装内容**:
```python
# 既存の右クリック処理を拡張
if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
    device = self.grid_system.get_device(row, col)
    if device and self.current_mode == SimulatorMode.EDIT:
        # デバイスID編集ダイアログ表示
        self._show_device_id_dialog(device, row, col)
    # 既存のRUNモード処理は保持
```

**新規メソッド**:
- `_show_device_id_dialog()`: ダイアログ表示・結果処理
- ダイアログ結果に基づくデバイスID更新処理

### **Task 2.2: GridSystem連携実装**
**ファイル**: `core/grid_system.py`  
**推定時間**: 15分

**実装内容**:
- `update_device_id(row, col, new_id)`: デバイスID更新メソッド
- ID変更後の画面更新処理
- デバイスアドレス管理の統合

---

## 🎯 **Phase 3: UI/UX最適化**

### **Task 3.1: ダイアログUI設計実装**
**推定時間**: 30分

**UI仕様**:
```
┌─────────────────────────────┐
│     Device ID Editor        │
├─────────────────────────────┤
│ Device Type: CONTACT_A      │
│ Current ID:  [X001_____]    │
│                             │
│ Valid Format: X000-X377     │
│ Example: X001, X010, X100   │
│                             │
│   [  OK  ]     [Cancel]     │
└─────────────────────────────┘
```

**描画仕様**:
- ダイアログサイズ: 200x120ピクセル
- 中央配置計算（384x384画面基準）
- 背景暗転: 50%透明度
- ボタンホバー効果

### **Task 3.2: キーボード操作最適化**
**推定時間**: 15分

**操作仕様**:
- 英数字キー: テキスト入力
- Backspace: 文字削除
- Enter: OK確定
- Escape: Cancel
- Tab: OK/Cancel間フォーカス移動

---

## 🎯 **Phase 4: テスト・品質保証**

### **Task 4.1: 機能テスト**
**推定時間**: 20分

**テスト項目**:
- 各デバイスタイプでの右クリック動作確認
- バリデーション機能（正常・異常入力）
- モード切り替え時の動作確認
- キーボード・マウス操作の統合テスト

### **Task 4.2: 統合テスト・バグ修正**
**推定時間**: 20分

**確認項目**:
- 既存機能への影響なし
- パフォーマンス（30FPS維持）
- メモリリーク・リソース管理
- エラーハンドリング

---

## 📊 **実装スケジュール**

| Phase | 作業内容 | 推定時間 | 累計時間 |
|-------|----------|----------|----------|
| Phase 1 | コアダイアログシステム | 1時間15分 | 1時間15分 |
| Phase 2 | Ver3統合実装 | 35分 | 1時間50分 |
| Phase 3 | UI/UX最適化 | 45分 | 2時間35分 |
| Phase 4 | テスト・品質保証 | 40分 | **3時間15分** |

**総実装時間**: 約3時間15分

---

## 🔧 **技術仕様詳細**

### **デバイスIDフォーマット仕様**
```python
# PLC標準準拠ID形式
DEVICE_ID_FORMATS = {
    DeviceType.CONTACT_A: r"X[0-3][0-7][0-7]",     # X000-X377 (8進数)
    DeviceType.CONTACT_B: r"X[0-3][0-7][0-7]",     # X000-X377 (8進数)
    DeviceType.COIL: r"(Y[0-3][0-7][0-7]|M[0-7][0-9]{3})", # Y000-Y377, M0000-M7999
    DeviceType.COIL_REV: r"(Y[0-3][0-7][0-7]|M[0-7][0-9]{3})",
    DeviceType.TIMER: r"T[0-2][0-5][0-5]",         # T000-T255
    DeviceType.COUNTER: r"C[0-2][0-5][0-5]",       # C000-C255
    # LINK系は ID入力対象外
}
```

### **ダイアログ状態管理**
```python
class DialogState(Enum):
    INACTIVE = "inactive"    # ダイアログ非表示
    EDITING = "editing"      # テキスト入力中
    WAITING = "waiting"      # OK/Cancel待ち
```

### **統合インターフェース**
```python
# main.py での使用例
dialog = DeviceIDDialog(device.device_type, device.address)
result, new_id = dialog.show_modal()
if result:  # OK押下
    self.grid_system.update_device_id(row, col, new_id)
```

---

## ⚠️ **実装時注意点**

### **既存機能への影響最小化**
- 右クリック処理の拡張（RUNモードでの状態切り替えは保持）
- main.pyの既存コード構造維持
- パフォーマンスへの影響なし

### **Ver3設計思想準拠**
- シンプル・軽量実装
- モジュール化による拡張性確保
- PLC標準準拠の教育価値重視

### **エラーハンドリング**
- 不正入力時の適切なフィードバック
- ダイアログ表示中の例外処理
- メモリリーク防止

---

## 🎯 **実装完了後の期待効果**

1. **ユーザビリティ向上**: 直感的なデバイスID編集操作
2. **PLC標準準拠**: 実際のPLCと同等のアドレス体系
3. **教育効果**: 正しいデバイスアドレス命名の学習
4. **Ver3品質維持**: シンプル設計思想に合致した実装

---

**プラン作成日**: 2025-08-06  
**推定総実装時間**: 約3時間15分  
**実装準備**: 完了（詳細設計・技術仕様確定済み）

---

## 📝 **承認待ち**

このプランの確認をお願いします。  
**OKをいただき次第、Phase 1からコーディングを開始します。**
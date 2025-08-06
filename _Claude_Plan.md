# PyPlc Ver3 ダイアログシステム リファクタリングプラン

## 📋 **プロジェクト概要**

**目標**: main.pyの肥大化解消とダイアログシステムの独立モジュール化  
**アーキテクチャ**: ダイアログ関連コードを`dialogs/`ディレクトリに分離  
**効果**: コードの保守性・拡張性・可読性の大幅向上

---

## 🔍 **現状分析**

### **問題点**
- **main.py肥大化**: 705行（ダイアログ関連65行が含まれる）
- **責任分散**: UIロジック、ダイアログ処理、アプリ制御が混在
- **拡張困難**: 新しいダイアログ追加時にmain.pyを修正が必要

### **ダイアログ関連ファイル現状**
```python
# 現在の構成
core/device_id_dialog.py     # ダイアログクラス（343行）
config.py                    # DialogConfig設定クラス
main.py                      # ダイアログ統合処理（65行）
├── _show_device_id_dialog()      # 22行
├── _generate_default_device_id()  # 20行  
└── _draw_background_for_dialog()  # 23行
```

---

## 🎯 **リファクタリング戦略**

### **新しいアーキテクチャ設計**
```
PyPlc/
├── dialogs/                 # ダイアログシステム独立ディレクトリ
│   ├── __init__.py         # ダイアログシステムエクスポート
│   ├── device_id_dialog.py # デバイスID編集ダイアログ
│   ├── dialog_manager.py   # ダイアログ統合管理クラス
│   └── dialog_base.py      # 将来拡張用ベースクラス
├── core/                   # コアシステム（ダイアログ除外）
├── main.py                 # 640行に削減（65行減少）
└── config.py              # DialogConfig維持
```

### **責任分離設計**
```python
# dialogs/dialog_manager.py
class DialogManager:
    """ダイアログシステム統合管理"""
    def show_device_id_dialog(device, row, col, background_func)
    def generate_default_device_id(device_type, row, col)
    
# main.py（簡素化後）
class PyPlcVer3:
    def __init__(self):
        self.dialog_manager = DialogManager()  # ダイアログ管理委譲
    
    def _handle_device_placement(self):
        # 右クリック時
        self.dialog_manager.show_device_id_dialog(
            device, row, col, self._draw_background_for_dialog
        )
```

---

## 📋 **5フェーズ実装プラン**

### **Phase 1: ディレクトリ構造作成**
**推定時間**: 15分  
**作業内容**:
- `dialogs/` ディレクトリ作成
- `dialogs/__init__.py` 作成（エクスポート定義）
- `core/device_id_dialog.py` → `dialogs/device_id_dialog.py` 移動

### **Phase 2: DialogManager作成**
**推定時間**: 30分  
**作業内容**:
- `dialogs/dialog_manager.py` 新規作成
- main.pyからダイアログ関連メソッド移動
  - `_show_device_id_dialog()` → `DialogManager.show_device_id_dialog()`
  - `_generate_default_device_id()` → `DialogManager.generate_default_device_id()`
- グリッドシステム連携機能実装

### **Phase 3: main.py統合修正**
**推定時間**: 20分  
**作業内容**:
- DialogManager インポート・インスタンス化
- 右クリック処理の委譲実装
- `_draw_background_for_dialog()` の引き継ぎ

### **Phase 4: インポート参照更新**
**推定時間**: 15分  
**作業内容**:
- 全ファイルのインポート文修正
- `from core.device_id_dialog` → `from dialogs`
- パッケージ間依存関係の整理

### **Phase 5: 統合テスト・品質保証**
**推定時間**: 30分  
**作業内容**:
- 全機能動作確認
- ダイアログ表示・バリデーション・ID更新テスト
- パフォーマンス確認（背景暗転改善効果維持）

---

## 🏗️ **詳細実装仕様**

### **DialogManager クラス設計**
```python
from typing import Callable, Optional, Tuple
from config import DeviceType
from .device_id_dialog import DeviceIDDialog

class DialogManager:
    """
    ダイアログシステム統合管理クラス
    main.pyからダイアログ関連処理を完全分離
    """
    
    def show_device_id_dialog(
        self, 
        device, 
        row: int, 
        col: int, 
        background_draw_func: Callable[[], None],
        grid_system
    ) -> bool:
        """デバイスID編集ダイアログ統合処理"""
        
    def generate_default_device_id(
        self, 
        device_type: DeviceType, 
        row: int, 
        col: int
    ) -> str:
        """デバイスタイプ別デフォルトID生成"""
        
    def validate_device_for_id_edit(self, device) -> bool:
        """ID編集可能デバイス判定"""
```

### **dialogs/__init__.py 設計**
```python
"""
PyPlc Ver3 ダイアログシステム
統合ダイアログ管理とデバイスID編集機能
"""

from .dialog_manager import DialogManager
from .device_id_dialog import DeviceIDDialog, DialogState

__all__ = [
    'DialogManager',
    'DeviceIDDialog', 
    'DialogState'
]
```

### **main.py 簡素化後**
```python
# インポート簡素化
from dialogs import DialogManager

class PyPlcVer3:
    def __init__(self):
        # ダイアログシステム初期化
        self.dialog_manager = DialogManager()
    
    def _handle_device_placement(self):
        # 右クリック処理（大幅簡素化）
        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            device = self.grid_system.get_device(row, col)
            if device:
                self.dialog_manager.show_device_id_dialog(
                    device, row, col, 
                    self._draw_background_for_dialog,
                    self.grid_system
                )
```

---

## 📊 **期待される効果**

### **コード品質向上**
```
main.py行数: 705行 → 640行（9%削減）
責任分離: アプリ制御 vs ダイアログ管理の明確化
保守性: ダイアログ機能の独立開発・テスト可能
```

### **拡張性確保**
```python
# 将来の機能拡張例
dialogs/
├── device_id_dialog.py      # 既存
├── file_save_dialog.py      # 新規
├── settings_dialog.py       # 新規
└── confirmation_dialog.py   # 新規
```

### **開発効率向上**
- **ダイアログ開発**: 独立したモジュールでの集中開発
- **テスト効率**: ダイアログ機能の単体テスト容易化
- **デバッグ効率**: 機能別の問題切り分けが明確化

---

## ⚠️ **リスク分析と対策**

### **潜在的リスク**
1. **インポート循環参照**: dialogs ↔ core間の依存関係
2. **機能分離の複雑化**: grid_system連携の複雑性
3. **既存機能への影響**: リファクタリング時の機能劣化

### **対策**
1. **依存関係設計**: dialog_manager → core（単方向依存）
2. **インターフェース明確化**: 最小限の引数での連携
3. **段階的移行**: フェーズごとの動作確認実施

---

## 🧪 **テスト戦略**

### **機能テスト**
- [ ] デバイス右クリック→ダイアログ表示
- [ ] ID入力・バリデーション・更新
- [ ] ESCキャンセル・F12終了動作
- [ ] 背景暗転効果（改善版）

### **品質テスト**  
- [ ] パフォーマンス（30FPS維持）
- [ ] メモリリーク確認
- [ ] エラーハンドリング

### **統合テスト**
- [ ] EDIT/RUNモード動作
- [ ] 全デバイスタイプ対応確認
- [ ] CSV保存・読み込み連携

---

## 📈 **成功指標**

### **定量的指標**
- main.py行数: 705行 → 640行（9%削減）
- ダイアログ関連行数: 65行 → 5行（92%削減）
- テスト成功率: 100%

### **定性的指標**
- コードの可読性向上
- 新規ダイアログ追加の容易性
- 開発チーム生産性向上

---

## ⏱️ **実装スケジュール**

| Phase | 作業内容 | 推定時間 | 累計時間 |
|-------|----------|----------|----------|
| Phase 1 | ディレクトリ構造作成 | 15分 | 15分 |
| Phase 2 | DialogManager作成 | 30分 | 45分 |
| Phase 3 | main.py統合修正 | 20分 | 1時間5分 |
| Phase 4 | インポート参照更新 | 15分 | 1時間20分 |
| Phase 5 | 統合テスト・品質保証 | 30分 | **1時間50分** |

**総実装時間**: 約1時間50分

---

## 🔄 **Ver3設計思想との整合性**

### **シンプル・軽量維持**
- 外部依存なし（Pyxelのみ）
- モジュール単位での軽量化
- 明確な責任分離

### **教育価値向上**
- コードアーキテクチャの学習効果
- モジュール設計パターンの実践
- 保守性重視の開発手法

### **PLC標準準拠継続**
- デバイスID仕様の完全維持
- バリデーション機能の継承
- 操作性の一貫性確保

---

**プラン作成日**: 2025-08-06  
**推定総実装時間**: 約1時間50分  
**実装準備**: 完了（詳細設計・リスク分析済み）

---

## 📝 **承認待ち**

このリファクタリングプランをご確認ください。  
**OKをいただき次第、Phase 1からリファクタリングを開始します。**
# PyPlc main.py リファクタリング提案

## 現状分析

### 現在のmain.pyの状況
- **ファイルサイズ**: 451行、22.5KB
- **主要クラス**: PyPlcSimulatorクラスに全機能が集約
- **メソッド数**: 31個のアウトライン項目
- **問題点**: 責務が混在し、保守性・可読性が低下

### 現在の責務分析
1. **描画系**: `_draw_*`メソッド群（12個）
   - `_draw_grid()`: グリッド線描画
   - `_draw_devices()`: デバイス描画
   - `_draw_mouse_cursor()`: マウスカーソル描画
   - `_draw_controls()`: 操作情報描画
   - `_draw_status_bar()`: ステータスバー描画
   - その他描画支援メソッド

2. **入力系**: マウス・キーボード処理（4個）
   - `_update_mouse()`: マウス状態更新
   - `_screen_to_grid()`: 座標変換（最適化済み）
   - `_is_editable_position()`: 編集可能性判定
   - `update()`: キーボード入力処理

3. **PLCロジック系**: スキャン制御（3個）
   - `_execute_plc_scan()`: PLCスキャン実行
   - `_set_scan_time()`: スキャンタイム設定
   - スキャンタイム管理変数

4. **メインループ**: 統合制御（2個）
   - `__init__()`: 初期化
   - `draw()`: 描画統合

## リファクタリング提案

### 分割方針

#### 1. 描画系の分離 → `core/renderer.py`
**責務**: 全ての描画処理を統合管理
```python
class PyPlcRenderer:
    def __init__(self, config: PyPlcConfig)
    def draw_all(self, grid_manager, mouse_state, plc_state)
    def draw_grid(self)
    def draw_devices(self, devices)
    def draw_mouse_cursor(self, mouse_state)
    def draw_ui_elements(self, plc_state)
    def draw_status_bar(self, mouse_state, snap_mode)
```

**移動対象メソッド**:
- `_draw_grid()`
- `_draw_devices()`
- `_draw_single_device()`
- `_draw_mouse_cursor()`
- `_draw_controls()`
- `_draw_status_bar()`
- `_draw_device_*()` 系列
- `_get_device_*()` 系列
- `_calculate_device_rect()`

#### 2. 入力系の分離 → `core/input_handler.py`
**責務**: マウス・キーボード入力処理と座標変換
```python
class PyPlcInputHandler:
    def __init__(self, config: PyPlcConfig)
    def update_mouse(self) -> MouseState
    def screen_to_grid(self, screen_x, screen_y) -> tuple[int, int] | None
    def is_editable_position(self, row, col) -> bool
    def handle_keyboard_input(self) -> InputEvents
```

**移動対象メソッド**:
- `_update_mouse()`
- `_screen_to_grid()` (最適化済み)
- `_old_screen_to_grid()` (参考用)
- `_is_editable_position()`
- キーボード入力処理部分

#### 3. PLCロジック系の分離 → `core/plc_controller.py`
**責務**: PLCスキャン制御とタイミング管理
```python
class PyPlcController:
    def __init__(self, config: PyPlcConfig)
    def update_scan_timing(self) -> bool  # スキャン実行判定
    def execute_plc_scan(self, grid_manager)
    def set_scan_time(self, scan_time_ms: int)
    def get_scan_status(self) -> ScanStatus
```

**移動対象メソッド**:
- `_execute_plc_scan()`
- `_set_scan_time()`
- スキャンタイム管理ロジック

#### 4. メインクラスの簡素化 → `main.py`
**責務**: 各モジュールの統合・調整のみ
```python
class PyPlcSimulator:
    def __init__(self)
    def update(self)  # 各ハンドラーの呼び出しのみ
    def draw(self)    # レンダラーの呼び出しのみ
```

### 期待される効果

#### コード品質向上
- **main.py**: 451行 → 約150行（66%削減）
- **責務分離**: 各クラスが単一責任を持つ
- **保守性向上**: 機能別にファイルが分かれ、変更影響範囲が明確
- **テスタビリティ**: 各モジュールを独立してテスト可能

#### 開発効率向上
- **並行開発**: 描画・入力・ロジックを独立して開発可能
- **デバッグ容易性**: 問題の発生箇所を特定しやすい
- **機能拡張**: 新機能追加時の影響範囲を限定

## 実装手順

### Phase 1: 描画系分離
1. `core/renderer.py`作成
2. 描画関連メソッドの移動
3. `main.py`での呼び出し統合
4. 動作確認・テスト

### Phase 2: 入力系分離
1. `core/input_handler.py`作成
2. 入力処理メソッドの移動
3. マウス状態管理の統合
4. 動作確認・テスト

### Phase 3: PLCロジック系分離
1. `core/plc_controller.py`作成
2. スキャン制御ロジックの移動
3. タイミング管理の統合
4. 動作確認・テスト

### Phase 4: 最終統合・最適化
1. `main.py`の最終簡素化
2. インターフェース統一
3. パフォーマンス確認
4. ドキュメント更新

## 技術的考慮事項

### データ共有方式
- **設定**: `PyPlcConfig`を各モジュールで共有
- **状態管理**: 必要に応じてデータクラスで状態を管理
- **イベント**: 入力イベントは専用クラスで管理

### 既存機能の保持
- **パフォーマンス最適化**: `_screen_to_grid()`のO(1)最適化を保持
- **スキャンタイム制御**: 動的変更機能を保持
- **マウススナップ**: CTRL+スナップ機能を保持
- **グリッド描画**: はみ出し修正済みの描画ロジックを保持

### 互換性保証
- **外部インターフェース**: `PyPlcSimulator`の公開メソッドは変更しない
- **設定ファイル**: `PyPlc.json`の構造は維持
- **動作仕様**: 既存の動作は完全に保持

## 次期ステップ

リファクタリング完了後は、以下の機能実装に進む予定：

1. **デバイス配置機能**
   - ContactA/B、Coil、Timer等の配置
   - キーボードでのデバイス種別選択
   - マウスクリックでの配置・削除

2. **配線システム**
   - 水平配線（WIRE_H）
   - 垂直配線（WIRE_V）
   - 双方向リンク実装

3. **電力トレースシステム**
   - 左→右電力伝播
   - 自己保持回路対応

---

**作成日時**: 2025-07-28T22:56:35+09:00  
**対象バージョン**: PyPlc v2  
**main.py現在サイズ**: 451行、22.5KB
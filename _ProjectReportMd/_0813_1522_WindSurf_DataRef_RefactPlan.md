# DialogManager リファクタリング計画書

## 1. 概要

このドキュメントは、PyPlc Ver3のDialogManagerコンポーネントのレビューと今後の改善計画をまとめたものです。

## 2. 現状の評価

### 2.1 優れている点

1. **モジュール化と関心の分離**
   - 各コンポーネントの責務が明確に分離されている
   - 疎結合な設計により、保守性・拡張性が高い

2. **イベント駆動アーキテクチャ**
   - 疎結合なイベントシステムの採用
   - コンポーネント間の依存関係が最小限に抑えられている

3. **コード品質**
   - 型ヒントが適切に使用されている
   - ドキュメンテーションが充実している
   - 命名規則が一貫している

4. **柔軟性**
   - JSON駆動のUI構成
   - デバイス種別に応じた動的なダイアログ表示

## 3. 改善提案

### 3.1 依存関係の管理

**現状**:
- 各ダイアログクラスが直接インポートされている

**改善案**:
```python
def _get_dialog_class(dialog_type: str):
    """動的にダイアログクラスを取得"""
    if dialog_type == "data_register":
        from .dialogs.data_register_dialog import DataRegisterDialog
        return DataRegisterDialog
    # 他のダイアログタイプも同様に
```

### 3.2 エラーハンドリングの強化

**現状**:
- 一部のメソッドでエラーハンドリングが最小限

**改善案**:
```python
def show_device_edit_dialog(self, device, row: int, col: int, background_draw_func: Callable[[], None], grid_system) -> None:
    try:
        if not hasattr(device, 'device_type'):
            raise ValueError("無効なデバイスオブジェクトです")
            
        # 既存の分岐処理
        if device.device_type in [DeviceType.TIMER_TON, DeviceType.COUNTER_CTU]:
            self._show_timer_counter_dialog(device, row, col, grid_system)
        # ...
    except Exception as e:
        logger.error(f"ダイアログ表示中にエラーが発生しました: {str(e)}")
        # ユーザーへのフィードバック
        self._show_error_dialog("エラー", "ダイアログの表示に失敗しました")
```

### 3.3 設定の外部化

**現状**:
- ダイアログのサイズや色などがハードコードされている可能性

**改善案**:
- `config.py` やJSON設定ファイルに移動して一元管理
- テーマ機能の追加を検討

### 3.4 テスト容易性の向上

**改善案**:
```python
# tests/test_dialog_manager.py
def test_show_device_edit_dialog():
    """デバイス編集ダイアログのテスト"""
    manager = DialogManager()
    mock_device = Mock(device_type=DeviceType.DATA_REGISTER, address="D0")
    
    # モックを使用してテスト
    with patch.object(manager, '_show_data_register_dialog') as mock_show:
        manager.show_device_edit_dialog(mock_device, 0, 0, None, None)
        mock_show.assert_called_once()
```

### 3.5 パフォーマンス最適化

**改善案**:
```python
class BaseDialog:
    def __init__(self, ...):
        self.needs_redraw = True  # 再描画フラグ
        
    def update(self):
        if not self.needs_redraw:
            return
            
        # 描画処理
        self._draw()
        self.needs_redraw = False
        
    def invalidate(self):
        """再描画を要求"""
        self.needs_redraw = True
```

## 4. 実装計画

### フェーズ1: 依存関係の見直し（1日）
- 動的インポートの実装
- 依存関係の整理

### フェーズ2: エラーハンドリング強化（2日）
- 例外処理の追加
- エラーログの実装
- ユーザー向けエラーメッセージの整備

### フェーズ3: 設定の外部化（1日）
- 設定ファイルの作成
- テーマサポートの追加

### フェーズ4: テストの追加（2日）
- ユニットテストの作成
- 統合テストの作成
- カバレッジレポートの生成

### フェーズ5: パフォーマンス最適化（1日）
- 不要な再描画の削減
- メモリ使用量の最適化

## 5. 期待される効果

1. **保守性の向上**
   - 依存関係が明確になり、変更に強い構造に
   - テストカバレッジの向上による品質向上

2. **拡張性の向上**
   - 新しいダイアログの追加が容易に
   - 設定の変更が柔軟に

3. **パフォーマンスの向上**
   - 不要な再描画の削減
   - メモリ使用量の最適化

## 6. リスクと対策

| リスク | 影響度 | 発生確率 | 対策 |
|--------|--------|----------|------|
| 既存機能への影響 | 高 | 中 | 十分なテストの実施 |
| パフォーマンス低下 | 中 | 低 | プロファイリングの実施 |
| 互換性の問題 | 高 | 低 | 段階的なリリース |

## 7. 参考資料

- DialogManager ソースコード
- Pyxel ドキュメント
- 既存のテストケース

---

*このドキュメントは2025年8月13日に作成されました。*

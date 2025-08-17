# pyDialogManager - ダイアログシステム開発記録

## プロジェクト概要
pyxelを使った日本語対応ダイアログシステム。JSON駆動のレイアウト、ウィジェットベースUI、ファイルシステム連携機能を実装。

## 主要な技術的概念

### 1. Python動的属性システム (hasattr パターン)
プロジェクトの核となる技術。イベントハンドラーの動的追加により疎結合な設計を実現。

#### 基本パターン
```python
# ウィジェット側 (widgets.py)
if hasattr(self, 'on_item_activated'):
    self.on_item_activated(self.selected_index)

# コントローラー側 (file_open_dialog.py)  
listbox.on_item_activated = self.handle_file_activation
```

#### 学習教材
- `_study_hasattr.md`: 7段階のカリキュラム文書
- `python_attributes_tutorial.py`: 実行可能チュートリアル

### 2. 重要ファイル構成

#### widgets.py
- `ListBoxWidget`: 高度なスクロールボタン付きリスト
  - 4ボタンスクロールシステム (1行/5行 x 上下)
  - pyxel.tri()による三角形グラフィック
  - シングル/ダブルクリックモード対応
  - 動的イベントハンドラー: `on_item_activated`, `on_selection_changed`

#### file_open_dialog.py
- `FileOpenDialogController`: MVC パターンでファイルダイアログ制御
- リアルファイルシステム連携
- クリックモード動的切り替え

#### system_settings.py
- シングルトンパターンでグローバル設定管理
- シングル/ダブルクリックモード切り替え

### 3. 設計原則 (DESIGN.md準拠)
- pyxel.COLOR_xxx 定数使用必須
- ASCII文字のみ表示対応
- 日本語コメント推奨

### 4. 開発済み機能
✅ TextBoxWidget (入力/編集/カーソル/readonly対応)
✅ ファイルオープンダイアログ (完全なファイルシステム連携)
✅ クリックモードシステム (TABキー切り替え)
✅ 高度なスクロールボタン (グラフィック表示)
✅ 動的属性システム学習教材

### 5. 次回開発予定
SaveDialog の実装

### 6. 重要な技術的洞察

#### イベントハンドラーパターンの利点
- **疎結合**: ウィジェットとコントローラーが独立
- **再利用性**: 同じウィジェットを異なるコントローラーで使用可能
- **柔軟性**: 実行時にイベントハンドラーを変更可能
- **拡張性**: 新しいイベントを簡単に追加可能

#### 学習の進行
1. 基本的な属性操作 (hasattr, getattr, setattr)
2. 関数の動的追加
3. イベントハンドラーパターン
4. 複数ハンドラー管理
5. 実際のプロジェクトでの応用

この知識により、Python の動的な性質を活用した柔軟で保守性の高いダイアログシステムを構築できた。
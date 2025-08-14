# TextBoxControl責任統一リファクタリング計画

**作成日時**: 2025-08-14 20:20  
**目的**: TextBoxControlに適切な責任を集約し、FileLoadDialogを簡略化する  
**背景**: 現在、ファイル名編集とキーボード入力処理が複数のクラスに分散している問題を解決

## 🔍 調査結果

### 現在の問題箇所

**1. ファイル名設定の重複（2箇所）**:
- `_on_file_selected()` (340行目): マウスクリック時
- `_move_selection()` (432行目): キーボード選択時  
- 両方とも低レベル操作: `self.controls['filename_input']['text'] = selected.name`

**2. キーボード入力処理の複雑性（30行）**:
- `show_load_dialog()` (690-719行目): 英字・数字・記号の変換処理
- 22個のキーマッピング辞書
- FileLoadDialog側で文字変換を実行

**3. TextBoxControlの不完全性**:
- `on_key()`: 特殊キーのみ（文字変換なし）
- ファイル選択との連携機能なし
- 高レベルAPI不足

## 📋 Phase F: TextBoxControl責任統一リファクタリング

### **Phase F1: キーボード入力処理移行** 🟡 中程度: 1-2時間
**作業内容**:
- FileLoadDialogの30行キーボード処理→TextBoxControl.on_key()へ移行
- 22個のキーマッピング辞書の移植
- 英字・数字・記号変換ロジックの統合
- Shift状態判定の統合

**難易度理由**: 
- 複雑なキーマッピング移植が必要
- 既存の特殊キー処理との統合
- Pyxelキー定数の正確な対応

**実装ポイント**:
```python
class TextBoxControl:
    def on_key(self, key: int) -> bool:
        # 既存の特殊キー処理 + 新規文字変換処理
        if key in self._get_character_keys():
            char = self._convert_key_to_char(key)
            if self._is_character_allowed(char):
                return self.on_text(char)
        # 既存の特殊キー処理...
```

**リスク**: 
- 既存動作の変更可能性
- キーマッピング不整合

### **Phase F2: ファイル名選択連携機能追加** 🟢 簡単: 30分
**作業内容**:
- `set_filename_from_selection(file_info: FileInfo) -> bool` 実装
- `get_edited_filename() -> Optional[str]` 実装  
- `suggest_filename(base_name: str, extension: str = "") -> None` 実装

**実装例**:
```python
def set_filename_from_selection(self, file_info: FileInfo) -> bool:
    """ファイル・フォルダ選択からファイル名を設定"""
    if file_info.file_type == FileType.FILE:
        self.text = file_info.name
        return True
    elif file_info.file_type == FileType.DIRECTORY:
        self.text = ""  # フォルダ選択時はクリア
        return False

def get_edited_filename(self) -> Optional[str]:
    """編集されたファイル名を取得（バリデーション付き）"""
    if not self.text.strip():
        return None
    # 拡張子チェック、長さチェック等
    return self.text.strip()
```

**リスク**: ほとんどなし

### **Phase F3: FileLoadDialog簡略化リファクタリング** 🟢 簡単: 30分
**作業内容**:
- 重複したファイル名設定ロジック削除
- 複雑なキーボード入力処理削除
- TextBoxControl高レベルAPIへの移行

**変更前**:
```python
# _on_file_selected() と _move_selection() の両方に重複
if 'filename_input' in self.controls and selected.file_type == FileType.FILE:
    self.controls['filename_input']['text'] = selected.name

# 30行の複雑なキーボード処理
key_mappings = { ... }
for key, (normal_char, shift_char) in key_mappings.items(): ...
```

**変更後**:
```python
# シンプルな高レベル操作
self.filename_textbox.set_filename_from_selection(selected)

# キーボード処理は完全削除（TextBoxControlに移管）
```

**リスク**: 低（既存機能の高レベル化のみ）

### **Phase F4: ファイル名編集統合テスト** 🟢 簡単: 30分
**作業内容**:
- ファイル選択→編集→取得の一連動作確認
- 各入力フィルターモードでのテスト
- FileLoadDialog統合動作確認

**テストケース**:
```python
def test_filename_editing_workflow():
    # 1. ファイル選択
    file_info = FileInfo("test.csv", FileType.FILE)
    result = textbox.set_filename_from_selection(file_info)
    
    # 2. 編集操作
    textbox.on_text('_')  # test_.csv
    textbox.on_text('2')  # test_2.csv
    
    # 3. 結果取得
    final_name = textbox.get_edited_filename()
    assert final_name == "test_2.csv"
```

**リスク**: ほとんどなし

## 📊 作業難易度サマリー

| Phase | 難易度 | 予定時間 | リスク | 優先度 |
|-------|--------|----------|--------|--------|
| F1 | 🟡 中程度 | 1-2時間 | 中 | 高 |
| F2 | 🟢 簡単 | 30分 | 低 | 中 |
| F3 | 🟢 簡単 | 30分 | 低 | 中 |
| F4 | 🟢 簡単 | 30分 | 低 | 低 |

**総作業時間**: 2.5-3時間  
**最高難易度**: 🟡 中程度（Phase F1のみ）

## 🎯 期待される効果

### **設計品質向上**
- **単一責任原則**: TextBoxControlが文字入力のすべてを管理
- **再利用性**: 他のダイアログでも同じTextBoxControlを使用可能
- **保守性**: 1箇所でキーボード処理を管理

### **コード品質向上**
- **FileLoadDialog**: 30行削減（キーボード処理削除）
- **重複排除**: ファイル名設定ロジックの統一化
- **可読性**: 高レベルAPIによる意図の明確化

### **機能的改善**
- **意味的操作**: ファイル名編集の意図が明確
- **バリデーション**: 不正なファイル名の防止  
- **拡張性**: 将来の機能（自動補完等）追加が容易

## 🚀 推奨実行戦略

1. **Phase F1を最優先**: 最も複雑で影響範囲が大きい
2. **段階的検証**: 各Phase完了後に動作確認
3. **後方互換性**: 既存のFileLoadDialog動作を保持
4. **テスト重視**: 各段階でテストケース実行

## ✅ 完了基準

- [ ] Phase F1: TextBoxControlでキーボード入力が正常動作
- [ ] Phase F2: ファイル選択連携APIが正常動作  
- [ ] Phase F3: FileLoadDialogが簡略化されても同じ動作
- [ ] Phase F4: 統合テストが100%成功
- [ ] 既存のファイルダイアログ機能が完全に保持されている

---

**次回アクション**: Phase F1の実装から開始
**担当者確認**: 各Phaseの実装前にユーザー承認を求める
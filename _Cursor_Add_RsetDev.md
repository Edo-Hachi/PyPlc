# RST 追加 開発ノート（Mitsubishi準拠）

作成日: 2025-08-09  
対象: PyPlc Ver3（RST 基本実装 Phase 1）

---

## 背景・目的
- 三菱PLC準拠のRST（Reset）命令を導入し、カウンター/タイマーの即時リセットを教育的に正しく再現する。
- UI/解析/スプライト/CSVと一貫した体験を提供する。

---

## 設計方針（サマリ）
- **採用方式**: 三菱RST命令（X入力で[RST T/C]を駆動 → 対象の現在値0・出力OFF）
- **対象デバイス（Phase 1）**: `TIMER_TON`, `COUNTER_CTU` のみ
- **実行順序（1スキャン）**:
  1) 電力フローDFS  2) タイマ/カウンタ更新  3) RST処理  4) 接点状態の一括反映
- **UI/パレット**: 下段（Shift+3）に`RESET`を配置
- **スプライト**: `RESET TRUE:(104,0) / FALSE:(112,0)` を使用（TIMER/COUNTERは既存）
- **アドレス編集**: 既存DeviceIDダイアログを流用し、RST時のみ `T/C` かつ `0-255` に制限
- **CSV**: 既存拡張CSVに従い、RSTデバイスも他デバイス同様に保存/復元

---

## 実装詳細
- 仕様反映のポイント
  - RST通電中は、同一アドレスの `TIMER_TON`/`COUNTER_CTU` を即時リセット
  - タイマー: `current_value=0`, `state=False`, `timer_active=False`
  - カウンタ: `current_value=0`, `state=False`, `last_input_state` を現在入力で更新（誤カウント防止）
  - 大文字正規化（`address.upper()`）で比較

- スキャン内の実行順序（重要）
  - `電力フロー → タイマ/カウンタ更新 → RST → 接点状態更新`

---

## 変更ファイルと要点
- `config.py`
  - `DeviceType.RST` 追加
  - パレット下段 `Shift+3` に `(DeviceType.RST, "RESET", 3, ...)` を追加
- `core/SpriteManager.py`
  - スプライト名マッピング `RST -> RESET` を追加
- `sprites.json`
  - `RESET` スプライトを登録（TRUE: `(104,0)`, FALSE: `(112,0)`）
- `DialogManager/device_id_dialog_json.py`
  - RST選択時のみ、ID入力を `^(T|C)(\d{1,3})$` かつ `0-255` に制限
- `core/circuit_analyzer.py`
  - `solve_ladder()` に `_process_rst_commands()` を追加
  - RSTターゲット（通電中 + addressあり）を収集 → T/C一致デバイスを即時リセット
- `main.py`
  - Todo更新（Timer/Counterアドレス編集・RST Phase 1 完了）

---

## 動作確認（手動テスト）
- 回路A（CTU + RST）
  - `X001 ─┤├── CTU C0 (K=3)` / 別回路 `X002 ─┤├── RST C0`
  - X001で3回カウント→出力ON、X002 ONで即時 `ACC=0`・出力OFF
- 回路B（TON + RST）
  - `X001 ─┤├── TON T1 (K=1000ms)` / 別回路 `X002 ─┤├── RST T1`
  - 動作中にX002 ONで即時 0クリア・停止・出力OFF
- アドレス未設定RST: 通電しても無動作（エラーにしない）
- 複数RST（同一/異なるターゲット）: 冪等動作
- CSV保存/読込: RST含む構成が正しく往復

---

## 開発レビュー（所感）
- 良かった点
  - 最小限の変更で三菱RSTの教育的な効果を実現（スキャン順制御が効いている）
  - 既存のDialog/Validation基盤を再利用し、RST特有制約のみ薄く追加
  - スプライト連携（RST→RESET）により、UIの一貫性が高い
- パフォーマンス
  - RST処理はフルグリッド走査だが、15×20規模では十分軽量（30FPS維持）
  - アドレス比較は大小文字差を吸収（`upper()`）
- 可読性/保守性
  - RST処理は `_process_rst_commands()` に集約し、責務が明確
  - 実行順のコメント明記で誤改変のリスク低減

---

## 気になっていること・改善候補
- 既定アドレス生成（RST）
  - 現状は配置時アドレス空文字→右クリック編集想定。将来的に `T000` 等の初期値付与を検討
- RSTの対象範囲
  - Phase 1では T/C のみ。将来的に `Y/M` 等への拡張（メーカー流儀に合わせて慎重に）
- タイマーのフレーム刻み
  - 現行は約33ms/フレーム加算 + `FRAME_THRESHOLD` で近似。将来は実測/設定切替の検討余地
- カウンタ `last_input_state` の更新タイミング
  - RST直後の誤カウント防止策は実装済みだが、複雑回路での境界条件を追加検証
- 複数RSTの競合
  - 仕様上は冪等だが、将来のZRSTや範囲指定導入時は優先度/競合解決ポリシー要検討
- UI/UX
  - ステータスバーにRST対象のヒント表示、RST動作時の一時的な視覚効果（薄いフラッシュなど）

---

## 今後の拡張（Phase 2/3想定）
- Phase 2
  - ZRST（範囲リセット）/ 複数指定対応
  - RST対象候補のUI補助（同一アドレス一覧の簡易プレビュー）
  - エラーメッセージ/ログの整備（無効アドレス・未配置等）
- Phase 3
  - デバッグ表示の強化（RSTトリガログ、対象デバイス数、処理時間）
  - 教材用サンプル回路追加とドキュメント拡充

---

## 参考（スプライト座標）
- TIMER: TRUE `(72,0)`, FALSE `(80,0)`
- COUNTER: TRUE `(88,0)`, FALSE `(96,0)`
- RESET: TRUE `(104,0)`, FALSE `(112,0)`

---

以上、RST（Mitsubishi準拠）Phase 1 の設計・実装・レビュー・懸念点の記録。
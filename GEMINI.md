# GEMINI提案: PLC回路の接続情報と通電解析アーキテクチャ

## 概要

`Ver3_Definition.md`の「明示的配線システム」と「自己保持回路の動作」という目標を達成するための、デバイス接続情報の保持方法と、通電解析（結線）アルゴリズムに関する設計プラン。

## 1. データ構造：デバイス自身が接続情報を持つ

PLC回路を一種の「グラフ」として捉え、各デバイス（ノード）が隣接デバイス（エッジ）への接続情報を持つ構造を採用する。

### `PLCDevice`クラスの拡張案

`core/device_base.py`で定義する`PLCDevice`クラスに、四方の接続情報を保持するフィールドを追加する。

```python
# core/device_base.py の拡張イメージ

from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional
from config import DeviceType

@dataclass
class PLCDevice:
    """PLCデバイスの基本データ構造（接続情報を含む）""" 
    device_type: DeviceType
    position: Tuple[int, int]  # グリッド座標 (row, col)
    address: str
    state: bool = False
    
    # --- 接続情報 ---
    # key: "up", "down", "left", "right"
    # value: 接続先デバイスのユニークID（例: "row_col"文字列やオブジェクト参照）
    connections: Dict[str, Optional[str]] = field(default_factory=dict)
    
    # --- 回路解析用 ---
    is_energized: bool = False # このデバイスが通電しているか
```

### このデータ構造の利点

1.  **明示的な接続:** 各デバイスが上下左右のどのデバイスに接続されているかを明確に保持する。これにより、「暗黙の配線」問題を完全に解決する。
2.  **柔軟性と統一性:** `LINK_UP`/`LINK_DOWN`による垂直接続も、`LINK_SIDE`による水平接続も、すべてこの`connections`辞書で統一的に表現できる。
3.  **解析の容易性:** あるデバイスから`connections`をたどることで、回路網のトレースが容易になる。これは次の結線アルゴ-リズムの基礎となる。

## 2. 結線アルゴリズム：回路解析エンジンによる走査

デバイスの配置・削除が行われるたびに、`GridSystem`がそのデバイスと周囲のデバイスの`connections`情報を更新する。これにより、データとして常に最新の回路網が維持される。

この回路網の「通電状態」を計算するのが、**回路解析エンジン** (`core/circuit_analyzer.py`) の役割となる。これはPLCの「スキャン」動作を模倣する。

### 通電ロジックの計算手順 (`solve_logic`)

1.  **リセット:**
    *   まず、バスバー以外のすべてのデバイスの`is_energized`フラグを`False`にリセットする。

2.  **走査の開始点:**
    *   グリッドの左端にあるすべての`L_SIDE`（電源バス）を探す。これらが電力の供給源であり、常に`is_energized = True`となる。ここが走査のスタート地点になる。

3.  **深さ優先探索 (DFS) による通電トレース:**
    *   各`L_SIDE`から、接続されている右隣のデバイスに向かって、再帰的に通電をトレースする。
    *   **トレース関数 `trace_power(device)` の処理概要:**
        a.  現在の`device`を「訪問済み」としてマークする（自己保持回路のようなループでの無限再帰を防ぐため）。
        b.  現在の`device`の`is_energized`を`True`にする。
        c.  現在の`device`のロジックを評価し、通電が継続するか判断する。
            *   **開いた接点** (`CONTACT_A`で`state`が`False`など) に到達した場合、そこで通電はストップする。
            *   **コイル** (`COIL`) に到達した場合、そのコイルの`state`を`True`に更新する。
            *   **配線や閉じた接点**の場合、通電は継続する。
        d.  通電が継続する場合、`device.connections`をたどり、まだ「訪問済み」でない隣接デバイスに対して、再帰的に`trace_power()`を呼び出す。

4.  **結果の反映:**
    *   このトレース処理が完了すると、`L_SIDE`から電気的に到達可能なすべてのデバイスの`is_energized`フラグが`True`になる。
    *   描画処理では、この`is_energized`フラグを参照して、通電している配線やデバイスの色を変化させる。

## 結論

このアーキテクチャにより、複雑な自己保持回路や並列回路であっても、その接続状態と通電状態を正確にシミュレートすることが可能になる。

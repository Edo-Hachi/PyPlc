"""
PyPlc Ver3 Device Base Module
作成日: 2025-01-29
目標: 論理基盤の確立（Claude案 Phase 1-Stage 3 / Gemini案）

すべてのPLCデバイスの基底となるデータ構造を定義する。
"""

from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional

# config.pyからDeviceType Enumをインポート
from config import DeviceType

@dataclass
class PLCDevice:
    """
    PLCデバイスの基本データ構造。
    回路上のすべての要素（接点、コイル、配線など）を表す。
    GEMINI.mdで定義された設計に基づいています。
    """
    
    # --- 基本情報 ---
    device_type: DeviceType
    """デバイスの種類 (A接点、コイルなど)"""
    
    position: Tuple[int, int]
    """グリッド上の位置 (row, col)。[y座標][x座標]の順序。"""
    
    address: str
    """デバイスアドレス ('X001', 'Y002', 'T001'など)"""
    
    # --- 状態 ---
    state: bool = False
    """
    デバイスの論理的な状態 (ON/OFF)。
    - 接点の場合: 関連付けられたデバイス(X, Y, Mなど)がONかOFFか。
    - コイルの場合: 演算結果としてONになったかOFFになったか。
    """
    
    is_energized: bool = False
    """
    デバイスが電気的に通電しているかどうかの状態。
    回路解析エンジンによって毎スキャン更新される。
    描画時の色分けなどに使用する。
    """
    
    # --- 接続情報 ---
    # key: "up", "down", "left", "right"
    # value: 接続先デバイスの座標 (row, col)
    connections: Dict[str, Optional[Tuple[int, int]]] = field(default_factory=dict)
    """
    四方のデバイスへの接続情報を保持する辞書。
    値には接続先のデバイスのpositionタプルを格納する。
    接続がない方向のキーは存在しないか、値がNoneになる。
    """

    def __post_init__(self):
        """データクラス初期化後の追加処理"""
        # positionがタプルで、要素が2つであることを簡易的にチェック
        if not isinstance(self.position, tuple) or len(self.position) != 2:
            raise TypeError("position must be a tuple of (row, col)")

    def get_id(self) -> str:
        """
        デバイスのユニークIDを位置情報から生成して返す。
        GridSystemでのデバイス管理に使用できる。
        """
        row, col = self.position
        return f"{row:03d}_{col:03d}"

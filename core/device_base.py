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
    
    # --- タイマー・カウンター専用フィールド ---
    preset_value: int = 0
    """
    プリセット値（設定値）
    - タイマー: 設定時間（0.1秒単位、0-32767）
    - カウンター: 設定回数（0-65535）
    - その他のデバイス: 未使用（常に0）
    """
    
    current_value: int = 0
    """
    現在値
    - タイマー: 経過時間（0.1秒単位）
    - カウンター: 現在のカウント値
    - その他のデバイス: 未使用（常に0）
    """
    
    timer_active: bool = False
    """
    タイマー動作状態
    - True: タイマー実行中（カウントアップ中）
    - False: タイマー停止中またはタイムアップ済み
    - カウンター・その他: 未使用
    """
    
    last_input_state: bool = False
    """
    前回スキャン時の入力状態（エッジ検出用）
    - カウンター: 立ち上がりエッジ検出に使用
    - タイマー: リセット検出に使用
    - その他: 未使用
    """
    
    # --- データレジスタ演算機能フィールド（Phase 1拡張）---
    operation_type: str = "MOV"
    """
    データレジスタの演算種別
    - "MOV": データ転送（デフォルト）
    - "ADD": 加算
    - "SUB": 減算  
    - "MUL": 乗算
    - "DIV": 除算
    - その他のデバイス: 未使用
    """
    
    operand_value: int = 0
    """
    演算オペランド値（-32768 to 32767）
    - MOV: 転送元データ値
    - ADD/SUB/MUL/DIV: 演算対象値
    - その他のデバイス: 未使用
    """
    
    execution_enabled: bool = False
    """
    演算実行許可フラグ
    - True: 入力条件がONの時に演算実行
    - False: 演算無効
    - その他のデバイス: 未使用
    """
    
    error_state: str = ""
    """
    演算エラー状態文字列（WindSurf提案）
    - "": エラーなし
    - "OVERFLOW": 値オーバーフロー
    - "UNDERFLOW": 値アンダーフロー
    - "DIV_BY_ZERO": ゼロ除算
    - "INVALID_OPERAND": 無効なオペランド
    """
    
    # --- 比較デバイス専用フィールド（Compare Device Phase）---
    compare_left: str = ""
    """
    比較式の左辺値（例: "D0", "T001", "C005"）
    - COMPARE_DEVICE: 比較対象のデバイス名
    - その他のデバイス: 未使用
    """
    
    compare_operator: str = ""
    """
    比較演算子（例: "=", "<", ">", "<=", ">=", "<>"）
    - COMPARE_DEVICE: 比較演算子
    - その他のデバイス: 未使用
    """
    
    compare_right: str = ""
    """
    比較式の右辺値（例: "10", "D1", "T002"）
    - COMPARE_DEVICE: 比較対象の値またはデバイス名
    - その他のデバイス: 未使用
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

"""
PyPlc Ver3 Circuit Analyzer Module
作成日: 2025-01-29
目標: 通電ロジックの実装と自己保持回路の実現
"""

from typing import Set, Tuple, Optional
from core.grid_system import GridSystem
from core.device_base import PLCDevice
from config import DeviceType

class CircuitAnalyzer:
    """ラダー図の回路を解析し、各デバイスの通電状態を決定するエンジン"""

    def __init__(self, grid_system: GridSystem):
        """CircuitAnalyzerの初期化"""
        self.grid = grid_system

    def solve_ladder(self) -> None:
        """ラダー図全体の通電解析を実行する（1スキャンに相当）"""
        # 1. GridSystemに依頼して、全デバイスの通電状態を正しくリセットする
        self.grid.reset_all_energized_states()

        # 2. 各行の左バスから電力のトレースを開始
        for r in range(self.grid.rows):
            left_bus = self.grid.get_device(r, 0)
            # L_SIDEはリセット処理で既を通電済みのはず
            if left_bus and left_bus.is_energized:
                # 右隣のデバイスからトレースを開始
                self._trace_power_flow(left_bus.connections.get('right'))

    def _trace_power_flow(self, start_pos: Optional[Tuple[int, int]], visited: Optional[Set[Tuple[int, int]]] = None) -> None:
        """指定された位置から電力の流れを再帰的にトレースする（深さ優先探索）"""
        if visited is None:
            visited = set()

        if start_pos is None or start_pos in visited:
            return

        visited.add(start_pos)
        device = self.grid.get_device(start_pos[0], start_pos[1])
        if not device:
            return

        # このデバイスは通電しているとマーク
        device.is_energized = True

        # デバイスが電力を通すか（導通性があるか）チェック
        if not self._is_conductive(device):
            return # 通さないなら、この先のトレースは行わない

        # --- 次に電力を流す先を決定 ---
        # LINK_TO_UP は上の行に電力を送る特殊なデバイス
        if device.device_type == DeviceType.LINK_TO_UP:
            self._trace_power_flow(device.connections.get('up'), visited)
        # それ以外のデバイスは、原則として右に流す
        else:
            self._trace_power_flow(device.connections.get('right'), visited)

            # LINK_FROM_DOWN は下の行からも電力を受け取る
            if device.device_type == DeviceType.LINK_FROM_DOWN:
                # TODO: 並列回路の合流ロジックをここに追加する
                pass

    def _is_conductive(self, device: PLCDevice) -> bool:
        """デバイスが現在、電気を通す状態にあるかを判定する"""
        if device.device_type == DeviceType.CONTACT_A:
            return device.state  # ON状態なら通す
        if device.device_type == DeviceType.CONTACT_B:
            return not device.state  # OFF状態なら通す
        
        # 配線系は常時通す
        if device.device_type in [DeviceType.LINK_SIDE, DeviceType.LINK_FROM_DOWN, DeviceType.LINK_TO_UP]:
            return True

        # L_SIDE（左バス）は電源なので常時導通
        if device.device_type == DeviceType.L_SIDE:
            return True

        # R_SIDE（右バス）とコイルは電力の終端なので、電気を通さない
        return False

    # 不要でバグの原因となっていたプライベートメソッドは完全に削除
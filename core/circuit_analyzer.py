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

        # 3. PLC標準動作: 励磁されたコイルの同一アドレス接点を自動的にON状態に更新
        self._update_contact_states_from_coils()

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
        # 新アーキテクチャ: LINK_BRANCH による3方向分配（右・上・下）
        if device.device_type == DeviceType.LINK_BRANCH:
            # 確定仕様: 右・上・下の3方向に電力分配（左は除外）
            for direction in ['right', 'up', 'down']:
                next_pos = device.connections.get(direction)
                if next_pos and next_pos not in visited:
                    self._trace_power_flow(next_pos, visited)
        
        elif device.device_type == DeviceType.LINK_VIRT:
            # 上下双方向に電力伝播
            for direction in ['up', 'down']:
                next_pos = device.connections.get(direction)
                if next_pos and next_pos not in visited:
                    self._trace_power_flow(next_pos, visited)
        
        # 旧システム（Phase 4で削除予定）
        elif device.device_type == DeviceType.LINK_TO_UP:
            self._trace_power_flow(device.connections.get('up'), visited)
        
        # 標準デバイス（右方向のみ）
        else:
            self._trace_power_flow(device.connections.get('right'), visited)

            # 旧システム（Phase 4で削除予定）
            if device.device_type == DeviceType.LINK_FROM_DOWN:
                # 下の行からの電力供給をチェック
                self._handle_parallel_convergence(device, visited)

    def _is_conductive(self, device: PLCDevice) -> bool:
        """デバイスが現在、電気を通す状態にあるかを判定する"""
        if device.device_type == DeviceType.CONTACT_A:
            return device.state  # ON状態なら通す
        if device.device_type == DeviceType.CONTACT_B:
            return not device.state  # OFF状態なら通す
        
        # 配線系は常時通す
        if device.device_type in [DeviceType.LINK_HORZ, DeviceType.LINK_BRANCH, DeviceType.LINK_VIRT, 
                                  DeviceType.LINK_FROM_DOWN, DeviceType.LINK_TO_UP]:  # 旧システム併存
            return True

        # L_SIDE（左バス）は電源なので常時導通
        if device.device_type == DeviceType.L_SIDE:
            return True

        # R_SIDE（右バス）とコイルは電力の終端なので、電気を通さない
        return False

    # 旧_handle_parallel_convergence()メソッドは削除済み
    # LINK_BRANCHアーキテクチャにより、複雑な合流ロジックは不要になりました

    def _update_contact_states_from_coils(self) -> None:
        """
        PLC標準動作の実装: コイル状態に応じて同一アドレス接点を自動更新
        
        実PLC動作原理:
        - コイル Y001 が励磁されると、すべての Y001 接点が自動的にON状態になる
        - コイル Y001 が非励磁になると、すべての Y001 接点が自動的にOFF状態になる
        - これにより自己保持回路やSTOP動作が正常に動作する
        """
        # 1. 全コイルアドレスと励磁状態を取得
        all_coil_addresses = set()
        energized_coil_addresses = set()
        
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                device = self.grid.get_device(row, col)
                if (device and 
                    device.device_type in [DeviceType.COIL_STD, DeviceType.COIL_REV] and
                    device.address and
                    device.address != "WIRE"):  # アドレス指定されたコイルのみ
                    all_coil_addresses.add(device.address)
                    if device.is_energized:
                        energized_coil_addresses.add(device.address)
        
        # 2. 全コイルアドレスについて対応する接点の状態を更新
        for coil_address in all_coil_addresses:
            is_coil_energized = coil_address in energized_coil_addresses
            
            for row in range(self.grid.rows):
                for col in range(self.grid.cols):
                    device = self.grid.get_device(row, col)
                    if (device and 
                        device.device_type in [DeviceType.CONTACT_A, DeviceType.CONTACT_B] and
                        device.address == coil_address):
                        # PLC標準: コイル状態に応じて同一アドレス接点を自動更新
                        old_state = device.state
                        device.state = is_coil_energized
                        
                        if old_state != device.state:
                            status = "activated" if device.state else "deactivated"
                            print(f"  📍 Contact [{row}][{col}] {device.address} auto-{status} (coil energized: {is_coil_energized})")
        
        if energized_coil_addresses:
            print(f"🔗 PLC Standard Operation: Energized coils: {energized_coil_addresses}")
        
        # 非励磁になったコイルがある場合の情報出力
        de_energized_coils = all_coil_addresses - energized_coil_addresses
        if de_energized_coils:
            print(f"🔗 PLC Standard Operation: De-energized coils: {de_energized_coils}")

    # 不要でバグの原因となっていたプライベートメソッドは完全に削除
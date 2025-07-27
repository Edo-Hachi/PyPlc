"""
PyPlc Electrical System Module

ラダー図の電気的継続性システムを管理するモジュール。
- BusConnection: バスバー接続点の管理
- LadderRung: 単一ラング（横ライン）の電気的管理
- VerticalConnection: 縦方向結線の管理
- ElectricalSystem: 全体電気系統の管理
- CircuitTopologyManager: 完全回路継続性管理（新機能）
"""

import logging
from typing import List, Tuple, Dict, Optional
from config import DeviceType, Colors
from circuit_topology import CircuitTopologyManager

# デバッグログ設定
debug_logger = logging.getLogger('PyPlc_Debug')
debug_logger.setLevel(logging.DEBUG)
debug_handler = logging.FileHandler('debug.log', mode='w', encoding='utf-8')
debug_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
debug_handler.setFormatter(debug_formatter)
debug_logger.addHandler(debug_handler)
debug_logger.propagate = False  # コンソール出力を防ぐ


class BusConnection:
    """バスバー接続点の管理（縦バスバー対応準備）"""
    def __init__(self, grid_x: int, grid_y: int):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.is_energized = False
        self.connected_rungs = []  # 接続されているラング
        self.bus_type = "LEFT"     # LEFT/RIGHT/MIDDLE（将来の縦バス用）


class LadderRung:
    """ラダー図の1ライン（ラング）を電気的に管理"""
    def __init__(self, grid_y: int, grid_cols: int = 10, grid_manager=None):
        self.grid_y = grid_y
        self.grid_cols = grid_cols
        self.grid_manager = grid_manager  # グリッドマネージャーの参照を保持
        self.devices = []           # このライン上のデバイス（左→右順）
        self.power_segments = []    # 電力セグメント
        self.left_bus_connection = BusConnection(0, grid_y)   # 左バスバー接続
        self.right_bus_connection = BusConnection(grid_cols-1, grid_y)  # 右バスバー接続
        self.is_energized = False   # ライン全体の通電状態
        
    def add_device_at_position(self, grid_x: int, device):
        """指定位置にデバイスを追加"""
        # デバイスを位置順でソート挿入
        inserted = False
        for i, (pos, dev) in enumerate(self.devices):
            if grid_x < pos:
                self.devices.insert(i, (grid_x, device))
                inserted = True
                break
        if not inserted:
            self.devices.append((grid_x, device))
    
    def calculate_power_flow(self) -> bool:
        """左から右への電力フロー計算（ワイヤー対応）"""
        if not self.left_bus_connection.is_energized:
            return False
            
        # 左バスバーからスタート
        power_state = True
        
        # ワイヤー経由の接続を考慮した電力フロー計算
        power_state = self._calculate_wire_aware_power_flow()
        
        self.is_energized = power_state
        self.right_bus_connection.is_energized = power_state
        return power_state
    
    def _calculate_wire_aware_power_flow(self) -> bool:
        """ワイヤーを考慮した電力フロー計算（並列パス対応）"""
        if not self.devices:
            return True  # デバイスがない場合は通電
        
        # 並列パスを検出して処理
        power_state = self._process_parallel_paths()
        
        return power_state
    
    def _process_parallel_paths(self) -> bool:
        """並列パスを処理して電力状態を計算（ワイヤー依存）"""
        if len(self.devices) == 0:
            return True
        elif len(self.devices) == 1:
            # 単独デバイスの場合、左バスバーからの直接接続をチェック
            grid_x, device = self.devices[0]
            return self._check_single_device_connection(grid_x, device)
        
        # 複数デバイスの場合、デバイス間のワイヤー接続を確認
        return self._check_multi_device_wire_connection()
    
    def _check_single_device_connection(self, grid_x: int, device) -> bool:
        """単独デバイスの左バスバーからの接続をチェック"""
        # 左バスバー(0)から当該デバイスまでの経路にワイヤーがあるかチェック
        for check_x in range(1, grid_x):
            check_device = self.grid_manager.get_device(check_x, device.grid_y)
            if not check_device or check_device.device_type != DeviceType.WIRE_H:
                # ワイヤーが欠けている場合は接続なし
                return False
        
        # デバイス自体の状態を評価
        device_result = self._evaluate_device_state(device)
        
        # 全デバイスの表示状態を更新
        if device.device_type in [DeviceType.COIL, DeviceType.INCOIL, DeviceType.OUTCOIL_REV, 
                                 DeviceType.TIMER, DeviceType.COUNTER]:
            self._update_single_device_state(device, device_result)
        elif device.device_type in [DeviceType.TYPE_A, DeviceType.TYPE_B]:
            # 接点の表示状態を電気的継続性に基づいて設定
            device.active = device_result
        
        return device_result
    
    def _update_single_device_state(self, device, power_state: bool):
        """単独デバイスの状態を更新"""
        if device.device_type == DeviceType.COIL:
            device.coil_energized = power_state
            device.active = power_state
        elif device.device_type == DeviceType.INCOIL:
            device.coil_energized = power_state
            device.active = power_state
        elif device.device_type == DeviceType.OUTCOIL_REV:
            device.coil_energized = not power_state
            device.active = not power_state
        elif device.device_type == DeviceType.TIMER:
            self._process_timer_logic(device, power_state)
        elif device.device_type == DeviceType.COUNTER:
            self._process_counter_logic(device, power_state)
    
    def _check_multi_device_wire_connection(self) -> bool:
        """複数デバイス間のワイヤー接続をチェック"""
        power_state = True
        
        # 各デバイス間にワイヤーが存在するかチェック
        for i in range(len(self.devices) - 1):
            current_x, current_device = self.devices[i]
            next_x, next_device = self.devices[i + 1]
            
            # 現在のデバイスの状態を評価
            device_result = self._evaluate_device_state(current_device)
            power_state = power_state and device_result
            
            # 接点デバイスの表示状態を更新
            if current_device.device_type in [DeviceType.TYPE_A, DeviceType.TYPE_B]:
                current_device.active = device_result
            
            if not power_state:
                break
            
            # デバイス間のワイヤー接続をチェック
            if not self._check_wire_connection_between_devices(current_x, next_x, current_device.grid_y):
                power_state = False
                break
        
        # 最後のデバイスの状態も評価
        if power_state and self.devices:
            _, last_device = self.devices[-1]
            device_result = self._evaluate_device_state(last_device)
            power_state = power_state and device_result
            
            # 最後のデバイスの表示状態も更新
            if last_device.device_type in [DeviceType.TYPE_A, DeviceType.TYPE_B]:
                last_device.active = device_result
            
            # コイルデバイスの状態を更新
            self._update_coil_states(power_state)
        
        return power_state
    
    def _update_coil_states(self, final_power_state: bool):
        """ラング内のコイルデバイスの状態を更新"""
        for grid_x, device in self.devices:
            if device.device_type == DeviceType.COIL:
                # 出力コイル：最終電力状態で励磁
                device.coil_energized = final_power_state
                device.active = final_power_state
            elif device.device_type == DeviceType.INCOIL:
                # 入力コイル：最終電力状態で励磁
                device.coil_energized = final_power_state
                device.active = final_power_state
            elif device.device_type == DeviceType.OUTCOIL_REV:
                # 反転出力コイル：最終電力状態を反転して励磁
                device.coil_energized = not final_power_state
                device.active = not final_power_state
            elif device.device_type == DeviceType.TIMER:
                # タイマー：電力状態に応じて状態遷移
                self._process_timer_logic(device, final_power_state)
            elif device.device_type == DeviceType.COUNTER:
                # カウンター：電力状態に応じてカウント動作
                self._process_counter_logic(device, final_power_state)
    
    def _evaluate_device_state(self, device) -> bool:
        """デバイスの状態を評価（電源側・負荷側チェック含む）"""
        if device.device_type == DeviceType.TYPE_A:
            # A接点：左側に電源接続 AND 右側に負荷 AND 接点論理状態
            has_power = self._has_power_on_left_side(device.grid_x, device.grid_y)
            has_load = self._has_load_on_right_side(device.grid_x, device.grid_y)
            return device.contact_state and has_power and has_load
        elif device.device_type == DeviceType.TYPE_B:
            # B接点：左側に電源接続 AND 右側に負荷 AND 接点反転論理状態
            has_power = self._has_power_on_left_side(device.grid_x, device.grid_y)
            has_load = self._has_load_on_right_side(device.grid_x, device.grid_y)
            return (not device.contact_state) and has_power and has_load
        elif device.device_type in [DeviceType.COIL, DeviceType.INCOIL, DeviceType.OUTCOIL_REV]:
            # コイル：左側に電源接続 AND 右側にコールド接続が必要
            has_power = self._has_power_on_left_side(device.grid_x, device.grid_y)
            has_cold_connection = self._has_cold_connection_on_right_side(device.grid_x, device.grid_y)
            return has_power and has_cold_connection
        elif device.device_type in [DeviceType.TIMER, DeviceType.COUNTER]:
            # タイマー・カウンター：左側に電源接続 AND 右側にコールド接続が必要
            has_power = self._has_power_on_left_side(device.grid_x, device.grid_y)
            has_cold_connection = self._has_cold_connection_on_right_side(device.grid_x, device.grid_y)
            return has_power and has_cold_connection
        return True
    
    def _has_power_on_left_side(self, contact_x: int, contact_y: int) -> bool:
        """接点の左側（上流）にHOT側電力源が存在するかをチェック"""
        # 新方式：列0=HOT決め打ち
        hot_col = 0  # HOT列は決め打ち
        
        debug_logger.debug(f"HOT(列{hot_col})→接点({contact_x},{contact_y})接続チェック開始")
        
        # 接点が列1にある場合は、HOT（列0）に直接隣接しているので接続済み
        if contact_x == 1:
            debug_logger.debug(f"接点({contact_x},{contact_y})はHOTに直接隣接、接続OK")
            return True
        
        # 接点が列2以降にある場合は、HOTから接点まで完全にワイヤーで接続が必要
        for check_x in range(hot_col + 1, contact_x):
            device = self.grid_manager.get_device(check_x, contact_y)
            if not device or device.device_type != DeviceType.WIRE_H:
                debug_logger.debug(f"位置({check_x},{contact_y})にワイヤーなし - HOT接続失敗")
                return False
            debug_logger.debug(f"位置({check_x},{contact_y})にワイヤー確認OK")
        
        debug_logger.debug(f"HOT→接点({contact_x},{contact_y})完全接続確認")
        return True
    
    def _has_load_on_right_side(self, contact_x: int, contact_y: int) -> bool:
        """接点の右側（下流）に負荷デバイスが存在するかをチェック"""
        # 接点の右側から右バスバーまでの範囲で負荷デバイスを探索
        for check_x in range(contact_x + 1, self.grid_manager.grid_cols):
            device = self.grid_manager.get_device(check_x, contact_y)
            if not device or device.device_type == DeviceType.EMPTY:
                continue
                
            # 負荷デバイス（電力を消費するデバイス）をチェック
            if device.device_type in [DeviceType.COIL, DeviceType.INCOIL, DeviceType.OUTCOIL_REV,
                                     DeviceType.TIMER, DeviceType.COUNTER]:
                # 負荷デバイスが見つかった場合、そこまでの経路をチェック
                return self._check_wire_path_to_load(contact_x, check_x, contact_y)
            elif device.device_type == DeviceType.WIRE_H:
                # ワイヤーは通過可能、継続探索
                continue
            elif device.device_type in [DeviceType.TYPE_A, DeviceType.TYPE_B]:
                # 他の接点がある場合、その先に負荷があるかを再帰的にチェック
                if self._has_load_on_right_side(check_x, contact_y):
                    # その接点の先に負荷がある場合、経路をチェック
                    return self._check_wire_path_to_load(contact_x, check_x, contact_y)
        
        # 右バスバーまで到達した場合も負荷とみなす（右バスバーへの出力）
        return self._check_wire_path_to_load(contact_x, self.grid_manager.grid_cols - 1, contact_y)
    
    def _has_cold_connection_on_right_side(self, coil_x: int, coil_y: int) -> bool:
        """コイルの右側（下流）にCOLD側接続が存在するかをチェック"""
        # 新方式：列9=COLD決め打ち
        cold_col = 9  # COLD列は決め打ち
        
        debug_logger.debug(f"コイル({coil_x},{coil_y})→COLD(列{cold_col})接続チェック開始")
        
        # コイルが列8にある場合は、COLD（列9）に直接隣接しているので接続済み
        if coil_x == 8:
            debug_logger.debug(f"コイル({coil_x},{coil_y})はCOLDに直接隣接、接続OK")
            return True
        
        # コイルから列9まで、すべての位置にワイヤーが必要
        for check_x in range(coil_x + 1, cold_col):
            device = self.grid_manager.get_device(check_x, coil_y)
            if not device or device.device_type != DeviceType.WIRE_H:
                debug_logger.debug(f"位置({check_x},{coil_y})にワイヤーなし - COLD接続失敗")
                return False
            debug_logger.debug(f"位置({check_x},{coil_y})にワイヤー確認OK")
        
        debug_logger.debug(f"コイル({coil_x},{coil_y})→COLD完全接続確認")
        return True
    
    def _check_wire_path_to_load(self, start_x: int, end_x: int, grid_y: int) -> bool:
        """指定範囲にワイヤー経路が存在するかをチェック"""
        # start_x + 1 から end_x - 1 までの範囲にワイヤーが必要
        for check_x in range(start_x + 1, end_x):
            device = self.grid_manager.get_device(check_x, grid_y)
            if not device or device.device_type != DeviceType.WIRE_H:
                return False  # ワイヤーが欠けている場合は接続なし
        return True
    
    def _check_wire_connection_between_devices(self, start_x: int, end_x: int, grid_y: int) -> bool:
        """デバイス間のワイヤー接続をチェック"""
        # start_x + 1 から end_x - 1 までの範囲にワイヤーが必要
        for check_x in range(start_x + 1, end_x):
            device = self.grid_manager.get_device(check_x, grid_y)
            if not device or device.device_type != DeviceType.WIRE_H:
                # ワイヤーが欠けている場合は接続なし
                return False
        return True
    
    def _legacy_process_devices(self):
        """レガシーデバイス処理（従来のロジック）"""
        power_state = True
        
        # デバイスを左から右に処理（AND直列論理）
        for grid_x, device in self.devices:
            if device.device_type == DeviceType.TYPE_A:
                # A接点：デバイスがONの時に通電継続
                power_state = power_state and device.active
            elif device.device_type == DeviceType.TYPE_B:
                # B接点：デバイスがOFFの時に通電継続
                power_state = power_state and (not device.contact_state)
            elif device.device_type == DeviceType.COIL:
                # 出力コイル：電力状態を受け取って励磁
                device.coil_energized = power_state
                device.active = power_state
            elif device.device_type == DeviceType.INCOIL:
                # 入力コイル：電力状態を受け取って励磁（内部処理用）
                device.coil_energized = power_state
                device.active = power_state
            elif device.device_type == DeviceType.OUTCOIL_REV:
                # 反転出力コイル：電力状態を反転して励磁（反転動作）
                device.coil_energized = not power_state  # 反転！
                device.active = not power_state
            elif device.device_type == DeviceType.TIMER:
                # タイマー：電力状態に応じて状態遷移とタイマー動作
                self._process_timer_logic(device, power_state)
            elif device.device_type == DeviceType.COUNTER:
                # カウンター：電力状態に応じてカウント動作
                self._process_counter_logic(device, power_state)
            elif device.device_type in [DeviceType.WIRE_H, DeviceType.WIRE_V]:
                # ワイヤー：電力状態を伝達
                device.wire_energized = power_state
                device.active = power_state
                # ワイヤーは電力を通すだけなので、power_stateはそのまま継続
            # 他のデバイスタイプも必要に応じて追加
        
        self.is_energized = power_state
        self.right_bus_connection.is_energized = power_state
        return power_state
    
    def get_power_segments(self) -> List[Tuple[int, int, bool]]:
        """電力セグメント情報を取得（描画用）"""
        segments = []
        if not self.devices:
            return segments
            
        # 左バスバーから最初のデバイスまで
        if self.devices:
            first_x = self.devices[0][0]
            segments.append((0, first_x, self.left_bus_connection.is_energized))
        
        # デバイス間のセグメント
        current_power = self.left_bus_connection.is_energized
        for i, (grid_x, device) in enumerate(self.devices):
            # デバイス通過後の電力状態を計算
            if device.device_type == DeviceType.TYPE_A:
                current_power = current_power and device.active
            elif device.device_type == DeviceType.TYPE_B:
                current_power = current_power and (not device.contact_state)
            
            # 次のデバイスまでのセグメント
            if i < len(self.devices) - 1:
                next_x = self.devices[i + 1][0]
                segments.append((grid_x, next_x, current_power))
            else:
                # 最後のデバイスから右バスバーまで
                segments.append((grid_x, self.grid_cols - 1, current_power))
        
        return segments


class VerticalConnection:
    """縦方向結線を管理するクラス"""
    def __init__(self, grid_x: int):
        self.grid_x = grid_x
        self.connection_points = []  # (grid_y, DeviceType) のリスト
        self.is_energized = False
    
    def add_connection_point(self, grid_y: int, device_type: DeviceType):
        """結線点を追加"""
        if (grid_y, device_type) not in self.connection_points:
            self.connection_points.append((grid_y, device_type))
            self.connection_points.sort()  # Y座標でソート
    
    def remove_connection_point(self, grid_y: int):
        """結線点を削除"""
        self.connection_points = [(y, t) for y, t in self.connection_points if y != grid_y]
    
    def get_connected_pairs(self) -> List[Tuple[int, int]]:
        """縦方向接続ペアを取得
        上のラインにLINK_DOWN（↓）、下のラインにLINK_UP（↑）が配置されたときに接続
        """
        pairs = []
        link_ups = [y for y, t in self.connection_points if t == DeviceType.LINK_UP]
        link_downs = [y for y, t in self.connection_points if t == DeviceType.LINK_DOWN]
        
        # LINK_DOWN（上のラインの↓）とLINK_UP（下のラインの↑）のペアを作成
        for down_y in link_downs:
            # down_yより下にあるLINK_UPを探す
            compatible_ups = [up_y for up_y in link_ups if up_y > down_y]
            if compatible_ups:
                closest_up = min(compatible_ups)
                pairs.append((down_y, closest_up))  # (LINK_DOWNのY, LINK_UPのY)
        
        return pairs


class ElectricalSystem:
    """ラダー図全体の電気系統を管理"""
    def __init__(self, grid_device_manager):
        self.grid_manager = grid_device_manager
        self.rungs: Dict[int, LadderRung] = {}  # grid_y -> LadderRung
        self.left_bus_energized = True   # 左バスバー通電状態
        self.right_bus_energized = False # 右バスバー通電状態
        
        # 縦方向結線管理
        self.vertical_connections: Dict[int, VerticalConnection] = {}  # grid_x -> VerticalConnection
        
        # 新しい回路トポロジー管理システム
        self.circuit_topology = CircuitTopologyManager(grid_device_manager)
        self.use_topology_system = False  # 新システム使用フラグ（デバッグ用）
        
    def get_or_create_rung(self, grid_y: int) -> LadderRung:
        """指定行のラングを取得（なければ作成）"""
        if grid_y not in self.rungs:
            self.rungs[grid_y] = LadderRung(grid_y, self.grid_manager.grid_cols, self.grid_manager)
        return self.rungs[grid_y]
    
    def update_electrical_state(self):
        """全体の電気状態を更新"""
        if self.use_topology_system:
            # 新しい回路トポロジーシステムを使用
            self._update_with_topology_system()
        else:
            # 従来のシステムを使用
            self._update_with_legacy_system()
    
    def _update_with_topology_system(self):
        """新しい回路トポロジーシステムで電気状態を更新"""
        print("Using new topology system...")
        # 回路トポロジーを構築
        self.circuit_topology.build_circuit_topology()
        
        # 全回路の継続性を検証
        validation_results = self.circuit_topology.validate_all_circuits()
        
        # エラーがある場合は警告表示（将来的にUIに表示）
        errors = self.circuit_topology.get_circuit_errors()
        if errors:
            print("Circuit Errors:")
            for error in errors:
                print(f"  {error}")
        
        # デバッグ: 実際に構築された回路チェーンを表示
        print("Constructed circuit chains:")
        for grid_y, chain in self.circuit_topology.circuit_chains.items():
            print(f"  Row {grid_y}: {len(chain.elements)} elements")
            for element in chain.elements:
                print(f"    {element.element_type.value} at X={element.grid_x}")
        
        # 全デバイスの通電状態をリセット
        self.circuit_topology.reset_all_energized_states()
        
        # 有効な回路のみ通電状態を更新
        self.circuit_topology.update_energized_states()
        
        # 縦方向結線の処理（既存システムを併用）
        self._process_vertical_connections()
        
        # コイル状態とY接点デバイスの自動連動処理
        self._update_coil_device_synchronization()
    
    def _update_with_legacy_system(self):
        """従来のシステムで電気状態を更新"""
        # 既存のラングデバイス情報をクリア
        for rung in self.rungs.values():
            rung.devices.clear()
        
        # 縦方向結線情報をクリア
        self.vertical_connections.clear()
        
        # 各ラングにデバイス情報を同期 & 縦方向結線を検出
        for row in self.grid_manager.grid:
            for device in row:
                if device.device_type != DeviceType.EMPTY:
                    rung = self.get_or_create_rung(device.grid_y)
                    rung.add_device_at_position(device.grid_x, device)
                    
                    # 縦方向結線点を登録
                    if device.device_type in [DeviceType.LINK_UP, DeviceType.LINK_DOWN]:
                        if device.grid_x not in self.vertical_connections:
                            self.vertical_connections[device.grid_x] = VerticalConnection(device.grid_x)
                        self.vertical_connections[device.grid_x].add_connection_point(device.grid_y, device.device_type)
        
        # 左バスバーを通電
        for rung in self.rungs.values():
            rung.left_bus_connection.is_energized = self.left_bus_energized
        
        # 各ラングの電力フロー計算
        for rung in self.rungs.values():
            rung.calculate_power_flow()
        
        # 縦方向結線の電力伝達を処理
        self._process_vertical_connections()
        
        # コイル状態とY接点デバイスの自動連動処理
        self._update_coil_device_synchronization()
        
        # ワイヤーの電気状態を更新
        self.update_wire_electrical_state()
        
        # 自己保持回路対応：複数回スキャンして安定状態を求める
        self._stabilize_electrical_state()
    
    def update_structure_only(self):
        """構造のみ更新（電力フロー計算なし）"""
        # 既存のラングデバイス情報をクリア
        for rung in self.rungs.values():
            rung.devices.clear()
        
        # 縦方向結線情報をクリア
        self.vertical_connections.clear()
        
        # 各ラングにデバイス情報を同期 & 縦方向結線を検出
        for row in self.grid_manager.grid:
            for device in row:
                if device.device_type != DeviceType.EMPTY:
                    rung = self.get_or_create_rung(device.grid_y)
                    rung.add_device_at_position(device.grid_x, device)
                    
                    # 縦方向結線点を登録
                    if device.device_type in [DeviceType.LINK_UP, DeviceType.LINK_DOWN]:
                        if device.grid_x not in self.vertical_connections:
                            self.vertical_connections[device.grid_x] = VerticalConnection(device.grid_x)
                        self.vertical_connections[device.grid_x].add_connection_point(device.grid_y, device.device_type)
    
    def get_wire_color(self, grid_x: int, grid_y: int) -> int:
        """指定位置の配線色を取得"""
        if grid_y in self.rungs:
            rung = self.rungs[grid_y]
            segments = rung.get_power_segments()
            
            for start_x, end_x, is_energized in segments:
                if start_x <= grid_x <= end_x:
                    return Colors.WIRE_ON if is_energized else Colors.WIRE_OFF
        
        return Colors.WIRE_OFF
    
    def _process_vertical_connections(self):
        """縦方向結線による電力伝達を処理"""
        for connection in self.vertical_connections.values():
            pairs = connection.get_connected_pairs()
            
            for down_y, up_y in pairs:
                # LINK_DOWNがあるラング（上のライン）の電力状態を取得
                if down_y in self.rungs:
                    down_rung = self.rungs[down_y]
                    # LINK_DOWNの位置での電力状態を計算
                    down_power = self._get_power_at_position(down_rung, connection.grid_x)
                    
                    # LINK_UPがあるラング（下のライン）に電力を伝達
                    if up_y in self.rungs and down_power:
                        up_rung = self.rungs[up_y]
                        # LINK_UP位置から左バスバーに電力を注入
                        up_rung.left_bus_connection.is_energized = True
                        # ラング全体を再計算
                        up_rung.calculate_power_flow()
    
    def _get_power_at_position(self, rung: LadderRung, grid_x: int) -> bool:
        """指定位置での電力状態を取得"""
        segments = rung.get_power_segments()
        for start_x, end_x, is_energized in segments:
            if start_x <= grid_x <= end_x:
                return is_energized
        return False
    
    def get_vertical_wire_segments(self) -> List[Tuple[int, int, int, bool]]:
        """縦方向配線セグメントを取得（描画用）"""
        segments = []
        for connection in self.vertical_connections.values():
            pairs = connection.get_connected_pairs()
            for down_y, up_y in pairs:
                # 電力状態を判定（LINK_DOWNがあるラングの電力状態）
                is_energized = False
                if down_y in self.rungs:
                    down_rung = self.rungs[down_y]
                    is_energized = self._get_power_at_position(down_rung, connection.grid_x)
                
                segments.append((connection.grid_x, down_y, up_y, is_energized))
        
        return segments
    
    def _update_coil_device_synchronization(self):
        """コイル状態とY接点デバイスの自動連動処理
        
        コイルが通電状態になった場合、対応するY接点デバイスを自動的にON状態にする。
        PLC動作の基本原理：出力コイル励磁 → 対応する出力接点導通
        """
        # デバイスマネージャーへの参照を取得する必要があるため、
        # 実際の連動処理はmain.pyから呼び出される専用メソッドで実行
        pass
    
    def synchronize_coil_to_device(self, device_manager):
        """コイル状態をデバイスマネージャーのY接点と同期
        
        Args:
            device_manager: PLCデバイスマネージャー（plc_logic.py）
        """
        # 全グリッドデバイスをスキャンしてコイルを検出
        for row in self.grid_manager.grid:
            for device in row:
                if device.device_type in [DeviceType.COIL, DeviceType.INCOIL, DeviceType.OUTCOIL_REV] and device.device_address:
                    # コイルのデバイスアドレス（例: Y001, M001）から対応デバイスを更新
                    plc_device = device_manager.get_device(device.device_address)
                    if plc_device:
                        # コイルの励磁状態をデバイスに反映
                        plc_device.value = device.coil_energized
                        
                        # Y接点の場合は、グリッド上の他のY接点（TYPE_A/TYPE_B）も同期
                        if device.device_address.startswith('Y'):
                            self._synchronize_y_contacts(device.device_address, device.coil_energized)
    
    def _synchronize_y_contacts(self, y_address: str, energized_state: bool):
        """指定Yアドレスに対応するグリッド上のY接点を同期
        
        Args:
            y_address: Yデバイスアドレス（例: "Y001"）
            energized_state: コイルの励磁状態
        """
        # 全グリッドデバイスをスキャンして同じYアドレスのTYPE_A/TYPE_B接点を更新
        for row in self.grid_manager.grid:
            for device in row:
                if (device.device_address == y_address and 
                    device.device_type in [DeviceType.TYPE_A, DeviceType.TYPE_B]):
                    
                    # Y接点の状態を更新
                    if device.device_type == DeviceType.TYPE_A:
                        # A接点：コイル励磁時にON
                        device.contact_state = energized_state
                        device.active = energized_state
                    elif device.device_type == DeviceType.TYPE_B:
                        # B接点：コイル励磁時にOFF（反転動作）
                        device.contact_state = energized_state
                        device.active = not energized_state
    
    def synchronize_same_address_coils(self, device_manager):
        """同名アドレスのコイル連動処理（Input→Output/Reverse連動）"""
        # 処理済みアドレスを記録（重複処理防止）
        processed_addresses = set()
        
        # 全グリッドデバイスをスキャンしてInputCoilを検出
        for row in self.grid_manager.grid:
            for device in row:
                if (device.device_type == DeviceType.INCOIL and 
                    device.device_address and 
                    device.device_address not in processed_addresses):
                    
                    # 同名デバイス関係を取得
                    relationships = self.grid_manager.get_coil_relationships(device.device_address)
                    
                    # InputCoilの状態を取得
                    input_energized = device.coil_energized
                    
                    # 同名OutputCoilと連動（InputCoil ON → OutputCoil ON）
                    for output_coil in relationships['output_coils']:
                        output_coil.coil_energized = input_energized
                        output_coil.active = input_energized
                    
                    # 同名ReverseCoilと反転連動（InputCoil ON → ReverseCoil OFF）
                    for reverse_coil in relationships['reverse_coils']:
                        reverse_coil.coil_energized = not input_energized
                        reverse_coil.active = not input_energized
                    
                    # PLCデバイスマネージャーと同期
                    plc_device = device_manager.get_device(device.device_address)
                    if plc_device:
                        plc_device.value = input_energized
                    
                    # 処理済みとしてマーク
                    processed_addresses.add(device.device_address)
    
    def _process_timer_logic(self, timer_device, power_input: bool):
        """タイマーデバイスの状態遷移処理
        
        Args:
            timer_device: タイマーデバイス
            power_input: 入力電力状態
        """
        # プリセット値がない場合はデフォルト値を設定
        if timer_device.timer_preset <= 0:
            timer_device.timer_preset = 3.0  # デフォルト3秒
        
        if power_input:
            # 電力入力あり：タイマー開始または継続
            if timer_device.timer_state == "STANBY":
                # 待機中 → カウントアップ開始
                timer_device.timer_state = "CNTUP"
                timer_device.timer_current = 0.0
                timer_device.active = False  # カウント中は出力OFF
            elif timer_device.timer_state == "CNTUP":
                # カウントアップ中：時間進行
                timer_device.timer_current += 1.0/60.0  # 60FPS想定で1/60秒進行
                if timer_device.timer_current >= timer_device.timer_preset:
                    # プリセット時間到達 → 出力ON
                    timer_device.timer_state = "ON"
                    timer_device.active = True
                else:
                    timer_device.active = False
            elif timer_device.timer_state == "ON":
                # 出力中：継続
                timer_device.active = True
        else:
            # 電力入力なし：リセット
            timer_device.timer_state = "STANBY"
            timer_device.timer_current = 0.0
            timer_device.active = False
    
    def _process_counter_logic(self, counter_device, power_input: bool):
        """カウンターデバイスの動作処理
        
        Args:
            counter_device: カウンターデバイス
            power_input: 入力電力状態
        """
        # プリセット値がない場合はデフォルト値を設定
        if counter_device.counter_preset <= 0:
            counter_device.counter_preset = 3  # デフォルト3回
        
        # エッジ検出用の前回状態を記録（簡易実装）
        if not hasattr(counter_device, '_prev_power_input'):
            counter_device._prev_power_input = False
        
        # 立ち上がりエッジ検出（OFF→ONの瞬間）
        rising_edge = power_input and not counter_device._prev_power_input
        
        if rising_edge:
            # カウントアップ
            counter_device.counter_current += 1
            
            # プリセット値到達チェック
            if counter_device.counter_current >= counter_device.counter_preset:
                counter_device.counter_state = "ON"
                counter_device.active = True
            else:
                counter_device.counter_state = "OFF"
                counter_device.active = False
        
        # 前回状態を更新
        counter_device._prev_power_input = power_input
        
        # リセット条件（電力が完全に切れた場合）
        if not power_input:
            # 通常、カウンターは電力が切れてもカウント値は保持される
            # ただし、特定の条件でリセットする場合はここに実装
            pass
    
    def reset_electrical_state(self):
        """電気系統を初期状態にリセット"""
        # バスバー状態をリセット
        self.left_bus_energized = True   # 左バスバーは常に通電
        self.right_bus_energized = False
        
        # 全ラングの電力状態をリセット
        for rung in self.rungs.values():
            rung.left_bus_connection.is_energized = self.left_bus_energized
            rung.right_bus_connection.is_energized = False
            rung.is_energized = False
            
            # ラング内の全デバイスの電力状態をリセット
            for grid_x, device in rung.devices:
                device.wire_energized = False
                if hasattr(device, 'coil_energized'):
                    device.coil_energized = False
                if hasattr(device, 'active'):
                    device.active = False
        
        # 縦方向結線の状態をリセット
        for connection in self.vertical_connections.values():
            # 接続ポイントの電力状態をリセット
            connection.connection_points = {}  # 接続ポイントをクリア
    
    def trace_wire_path(self, start_x: int, start_y: int, target_x: int, target_y: int) -> bool:
        """ワイヤーを経由した電気経路をトレース
        
        Args:
            start_x: 開始X座標
            start_y: 開始Y座標  
            target_x: 目標X座標
            target_y: 目標Y座標
            
        Returns:
            bool: 電気的接続があるかどうか
        """
        # 境界チェック
        if (start_x < 0 or start_x >= self.grid_manager.grid_cols or
            start_y < 0 or start_y >= self.grid_manager.grid_rows or
            target_x < 0 or target_x >= self.grid_manager.grid_cols or
            target_y < 0 or target_y >= self.grid_manager.grid_rows):
            return False
        
        visited = set()
        return self._trace_recursive(start_x, start_y, target_x, target_y, visited)
    
    def _trace_recursive(self, current_x: int, current_y: int, target_x: int, target_y: int, visited: set) -> bool:
        """再帰的な経路探索
        
        Args:
            current_x: 現在のX座標
            current_y: 現在のY座標
            target_x: 目標X座標
            target_y: 目標Y座標
            visited: 訪問済み座標のセット
            
        Returns:
            bool: 目標に到達できるかどうか
        """
        # 座標が範囲外または既に訪問済み
        if (current_x < 0 or current_x >= self.grid_manager.grid_cols or
            current_y < 0 or current_y >= self.grid_manager.grid_rows or
            (current_x, current_y) in visited):
            return False
        
        # 目標座標に到達
        if current_x == target_x and current_y == target_y:
            return True
        
        visited.add((current_x, current_y))
        
        # 現在位置のデバイスを取得
        current_device = self.grid_manager.get_device(current_x, current_y)
        if not current_device:
            return False
        
        # ワイヤーでない場合は探索終了
        if current_device.device_type not in [DeviceType.WIRE_H, DeviceType.WIRE_V]:
            return False
        
        # ワイヤーの方向に応じて隣接セルを探索
        if current_device.device_type == DeviceType.WIRE_H:
            # 水平ワイヤー：左右に探索
            return (self._trace_recursive(current_x - 1, current_y, target_x, target_y, visited.copy()) or
                   self._trace_recursive(current_x + 1, current_y, target_x, target_y, visited.copy()))
        elif current_device.device_type == DeviceType.WIRE_V:
            # 垂直ワイヤー：上下に探索
            return (self._trace_recursive(current_x, current_y - 1, target_x, target_y, visited.copy()) or
                   self._trace_recursive(current_x, current_y + 1, target_x, target_y, visited.copy()))
        
        return False
    
    def update_wire_electrical_state(self):
        """ワイヤーの電気状態を個別に更新（手動配置対応）"""
        # 全ワイヤーの通電状態をリセット
        for row in range(self.grid_manager.grid_rows):
            for col in range(self.grid_manager.grid_cols):
                device = self.grid_manager.get_device(col, row)
                if device and device.device_type in [DeviceType.WIRE_H, DeviceType.WIRE_V]:
                    device.wire_energized = False
        
        # 左から右に順番にワイヤーの状態を判定（依存関係解決）
        for row in range(self.grid_manager.grid_rows):
            for col in range(1, self.grid_manager.grid_cols):  # 左バスバー(0)は除く
                device = self.grid_manager.get_device(col, row)
                if device and device.device_type == DeviceType.WIRE_H:
                    # 横方向ワイヤーの個別接続判定
                    device.wire_energized = self._check_horizontal_wire_connection(col, row)
    
    def _stabilize_electrical_state(self):
        """自己保持回路のため反復スキャンで安定状態を求める"""
        max_iterations = 5  # 最大反復回数
        
        for iteration in range(max_iterations):
            # 現在の状態を保存
            previous_states = {}
            for rung in self.rungs.values():
                for grid_x, device in rung.devices:
                    if device.device_type in [DeviceType.COIL, DeviceType.INCOIL, DeviceType.OUTCOIL_REV]:
                        previous_states[(grid_x, rung.grid_y)] = device.coil_energized
            
            # 1回のスキャンサイクルを実行
            self._single_scan_cycle()
            
            # 状態変化をチェック
            state_changed = False
            for rung in self.rungs.values():
                for grid_x, device in rung.devices:
                    if device.device_type in [DeviceType.COIL, DeviceType.INCOIL, DeviceType.OUTCOIL_REV]:
                        current_state = device.coil_energized
                        previous_state = previous_states.get((grid_x, rung.grid_y), False)
                        if current_state != previous_state:
                            state_changed = True
                            break
                if state_changed:
                    break
            
            # 安定状態に到達
            if not state_changed:
                break
    
    def _single_scan_cycle(self):
        """1回のスキャンサイクルを実行"""
        # コイル状態とデバイス状態の同期
        self._update_coil_device_synchronization()
        
        # 各ラングの電力フロー再計算
        for rung in self.rungs.values():
            rung.left_bus_connection.is_energized = self.left_bus_energized
            rung.calculate_power_flow()
        
        # 縦方向結線の電力伝達を処理
        self._process_vertical_connections()
        
        # ワイヤーの電気状態を更新
        self.update_wire_electrical_state()
    
    def _check_horizontal_wire_connection(self, wire_x: int, wire_y: int) -> bool:
        """横方向ワイヤーの接続状態をチェック
        
        Args:
            wire_x: ワイヤーのX座標
            wire_y: ワイヤーのY座標
            
        Returns:
            bool: ワイヤーが通電状態かどうか
        """
        # 左側（前方）にホット源があるかチェック
        has_hot_source = self._check_left_side_connection(wire_x, wire_y)
        
        # 右側（後方）に負荷があるかチェック
        has_load = self._check_right_side_connection(wire_x, wire_y)
        
        # 両方向に接続があり、ホット源がある場合のみ通電
        return has_hot_source and has_load
    
    def _check_left_side_connection(self, wire_x: int, wire_y: int) -> bool:
        """ワイヤーの左側（ホット側）接続をチェック"""
        # 直接隣接する左側のセルをチェック
        left_x = wire_x - 1
        if left_x < 0:
            return False
            
        if left_x == 0:
            # 左バスバー（ホット源）に直接接続
            return True
            
        device = self.grid_manager.get_device(left_x, wire_y)
        if not device or device.device_type == DeviceType.EMPTY:
            return False
            
        if device.device_type == DeviceType.WIRE_H:
            # 左隣のワイヤーが通電していればOK（既に処理済みのはず）
            return device.wire_energized
        elif device.device_type == DeviceType.LINK_DOWN:
            # LINK_DOWNがある場合、ペアのLINK_UPからの接続をチェック
            return self._check_linkup_left_connection_from_linkdown(left_x, wire_y)
        elif device.device_type in [DeviceType.TYPE_A, DeviceType.TYPE_B, 
                                   DeviceType.INCOIL, DeviceType.COIL, 
                                   DeviceType.OUTCOIL_REV, DeviceType.TIMER, 
                                   DeviceType.COUNTER]:
            # デバイスの場合、そのデバイスが通電していればOK
            return device.active
            
        return False
    
    def _check_right_side_connection(self, wire_x: int, wire_y: int) -> bool:
        """ワイヤーの右側（負荷側）接続をチェック"""
        # 直接隣接する右側のセルをチェック
        right_x = wire_x + 1
        if right_x >= self.grid_manager.grid_cols:
            return False
            
        if right_x == self.grid_manager.grid_cols - 1:
            # 右バスバー（負荷側）に直接接続
            return True
            
        device = self.grid_manager.get_device(right_x, wire_y)
        if not device or device.device_type == DeviceType.EMPTY:
            return False
            
        if device.device_type == DeviceType.WIRE_H:
            # 右隣にワイヤーがある場合は接続とみなす
            return True
        elif device.device_type == DeviceType.LINK_DOWN:
            # LINK_DOWNがある場合、ペアのLINK_UPとの接続をチェック
            return self._check_linkdown_pair_connection(right_x, wire_y)
        elif device.device_type in [DeviceType.TYPE_A, DeviceType.TYPE_B, 
                                   DeviceType.INCOIL, DeviceType.COIL, 
                                   DeviceType.OUTCOIL_REV, DeviceType.TIMER, 
                                   DeviceType.COUNTER]:
            # デバイスがあれば負荷として認識
            return True
            
        return False
    
    def _check_linkdown_pair_connection(self, linkdown_x: int, linkdown_y: int) -> bool:
        """LINK_DOWNのペアLINK_UPとの接続をチェック
        
        Args:
            linkdown_x: LINK_DOWNのX座標
            linkdown_y: LINK_DOWNのY座標
            
        Returns:
            bool: ペアのLINK_UPが存在し、接続可能かどうか
        """
        # 同じX座標の下方向にLINK_UPを探索
        for search_y in range(linkdown_y + 1, self.grid_manager.grid_rows):
            device = self.grid_manager.get_device(linkdown_x, search_y)
            if device and device.device_type == DeviceType.LINK_UP:
                # ペアのLINK_UPが見つかった場合、そのLINK_UPの後方接続をチェック
                return self._check_linkup_right_connection(linkdown_x, search_y)
                
        return False
    
    def _check_linkup_right_connection(self, linkup_x: int, linkup_y: int) -> bool:
        """LINK_UPの後方（右側）接続をチェック
        
        Args:
            linkup_x: LINK_UPのX座標
            linkup_y: LINK_UPのY座標
            
        Returns:
            bool: LINK_UPの右側に接続があるかどうか
        """
        # 右隣のセルをチェック
        right_x = linkup_x + 1
        if right_x >= self.grid_manager.grid_cols:
            return False
            
        if right_x == self.grid_manager.grid_cols - 1:
            # 右バスバー（負荷側）に直接接続
            return True
            
        device = self.grid_manager.get_device(right_x, linkup_y)
        if not device or device.device_type == DeviceType.EMPTY:
            return False
            
        if device.device_type in [DeviceType.WIRE_H, DeviceType.TYPE_A, DeviceType.TYPE_B, 
                                 DeviceType.INCOIL, DeviceType.COIL, 
                                 DeviceType.OUTCOIL_REV, DeviceType.TIMER, 
                                 DeviceType.COUNTER]:
            # ワイヤーまたはデバイスがあれば接続とみなす
            return True
            
        return False
    
    def _check_linkup_left_connection_from_linkdown(self, linkdown_x: int, linkdown_y: int) -> bool:
        """LINK_DOWNのペアLINK_UPの左側接続をチェック
        
        Args:
            linkdown_x: LINK_DOWNのX座標
            linkdown_y: LINK_DOWNのY座標
            
        Returns:
            bool: ペアのLINK_UPの左側に接続があるかどうか
        """
        # 同じX座標の下方向にLINK_UPを探索
        for search_y in range(linkdown_y + 1, self.grid_manager.grid_rows):
            device = self.grid_manager.get_device(linkdown_x, search_y)
            if device and device.device_type == DeviceType.LINK_UP:
                # ペアのLINK_UPが見つかった場合、そのLINK_UPの左側接続をチェック
                return self._check_linkup_left_connection(linkdown_x, search_y)
                
        return False
    
    def _check_linkup_left_connection(self, linkup_x: int, linkup_y: int) -> bool:
        """LINK_UPの左側（前方）接続をチェック
        
        Args:
            linkup_x: LINK_UPのX座標
            linkup_y: LINK_UPのY座標
            
        Returns:
            bool: LINK_UPの左側に接続があるかどうか
        """
        # 左隣のセルをチェック
        left_x = linkup_x - 1
        if left_x < 0:
            return False
            
        if left_x == 0:
            # 左バスバー（ホット源）に直接接続
            return True
            
        device = self.grid_manager.get_device(left_x, linkup_y)
        if not device or device.device_type == DeviceType.EMPTY:
            return False
            
        if device.device_type == DeviceType.WIRE_H:
            # 左隣のワイヤーが通電していればOK
            return device.wire_energized
        elif device.device_type == DeviceType.LINK_DOWN:
            # ペアのLINK_DOWNがある場合、再帰的にチェック
            return self._check_linkup_left_connection_from_linkdown(left_x, linkup_y)
        elif device.device_type in [DeviceType.TYPE_A, DeviceType.TYPE_B, 
                                   DeviceType.INCOIL, DeviceType.COIL, 
                                   DeviceType.OUTCOIL_REV, DeviceType.TIMER, 
                                   DeviceType.COUNTER]:
            # デバイスが通電していればOK
            return device.active
            
        return False
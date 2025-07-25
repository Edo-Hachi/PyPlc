"""
PyPlc Electrical System Module

ラダー図の電気的継続性システムを管理するモジュール。
- BusConnection: バスバー接続点の管理
- LadderRung: 単一ラング（横ライン）の電気的管理
- VerticalConnection: 縦方向結線の管理
- ElectricalSystem: 全体電気系統の管理
"""

from typing import List, Tuple, Dict, Optional
from config import DeviceType, Colors


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
    def __init__(self, grid_y: int, grid_cols: int = 10):
        self.grid_y = grid_y
        self.grid_cols = grid_cols
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
        """左から右への電力フロー計算"""
        if not self.left_bus_connection.is_energized:
            return False
            
        # 左バスバーからスタート
        power_state = True
        
        # 各デバイスの論理演算（左→右）
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
        
    def get_or_create_rung(self, grid_y: int) -> LadderRung:
        """指定行のラングを取得（なければ作成）"""
        if grid_y not in self.rungs:
            self.rungs[grid_y] = LadderRung(grid_y, self.grid_manager.grid_cols)
        return self.rungs[grid_y]
    
    def update_electrical_state(self):
        """全体の電気状態を更新"""
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
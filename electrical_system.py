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
                # コイル：電力状態を受け取って励磁
                device.coil_energized = power_state
                device.active = power_state
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
        """LINK_UPとLINK_DOWNのペアを取得"""
        pairs = []
        link_ups = [y for y, t in self.connection_points if t == DeviceType.LINK_UP]
        link_downs = [y for y, t in self.connection_points if t == DeviceType.LINK_DOWN]
        
        # 最も近いペアを作成
        for up_y in link_ups:
            # up_yより下にあるLINK_DOWNを探す
            compatible_downs = [down_y for down_y in link_downs if down_y > up_y]
            if compatible_downs:
                closest_down = min(compatible_downs)
                pairs.append((up_y, closest_down))
        
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
            
            for up_y, down_y in pairs:
                # LINK_UPがあるラングの電力状態を取得
                if up_y in self.rungs:
                    up_rung = self.rungs[up_y]
                    # LINK_UPの位置での電力状態を計算
                    up_power = self._get_power_at_position(up_rung, connection.grid_x)
                    
                    # LINK_DOWNがあるラングに電力を伝達
                    if down_y in self.rungs and up_power:
                        down_rung = self.rungs[down_y]
                        # LINK_DOWN位置から左バスバーに電力を注入
                        down_rung.left_bus_connection.is_energized = True
                        # ラング全体を再計算
                        down_rung.calculate_power_flow()
    
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
            for up_y, down_y in pairs:
                # 電力状態を判定
                is_energized = False
                if up_y in self.rungs:
                    up_rung = self.rungs[up_y]
                    is_energized = self._get_power_at_position(up_rung, connection.grid_x)
                
                segments.append((connection.grid_x, up_y, down_y, is_energized))
        
        return segments
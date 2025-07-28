"""
PyPlc Circuit Topology Module

ホット→コールド回路継続性を管理するリンクリスト構造システム。
完全な電気的継続性チェックと回路エラー検出を提供。
"""

import logging
from typing import List, Optional, Set, Tuple, Dict
from enum import Enum
from config import DeviceType

# デバッグログ設定（electrical_system.pyと同じloggerを使用）
debug_logger = logging.getLogger('PyPlc_Debug')


class ElementType(Enum):
    """回路要素タイプ"""
    HOT_BUS = "HOT_BUS"           # ホットバスバー（左バスバー）
    COLD_BUS = "COLD_BUS"         # コールドバスバー（右バスバー）
    WIRE = "WIRE"                 # 水平ワイヤー
    CONTACT = "CONTACT"           # 接点（A/B接点）
    COIL = "COIL"                 # コイル（負荷デバイス）
    TIMER = "TIMER"               # タイマー（負荷デバイス）
    COUNTER = "COUNTER"           # カウンター（負荷デバイス）


class CircuitElement:
    """回路要素の基底クラス"""
    def __init__(self, element_type: ElementType, grid_x: int, grid_y: int, device=None):
        self.element_type = element_type
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.device = device  # GridDeviceの参照
        
        # リンクリスト構造
        self.left_connections: List['CircuitElement'] = []   # 左側接続要素リスト
        self.right_connections: List['CircuitElement'] = []  # 右側接続要素リスト
        
        # 電気的状態
        self.is_energized = False      # 通電状態
        self.can_conduct = True        # 導通可能性
        self.is_validated = False      # 回路検証済みフラグ
        
    def add_left_connection(self, element: 'CircuitElement'):
        """左側接続要素を追加"""
        if element not in self.left_connections:
            self.left_connections.append(element)
            
    def add_right_connection(self, element: 'CircuitElement'):
        """右側接続要素を追加"""
        if element not in self.right_connections:
            self.right_connections.append(element)
    
    def get_conduction_state(self) -> bool:
        """要素の導通状態を取得"""
        if self.element_type == ElementType.HOT_BUS:
            return True  # ホットバスバーは常に導通
        elif self.element_type == ElementType.COLD_BUS:
            return True  # コールドバスバーは常に導通
        elif self.element_type == ElementType.WIRE:
            return True  # ワイヤーは常に導通
        elif self.element_type == ElementType.CONTACT:
            # 接点：論理状態に依存
            if self.device:
                if self.device.device_type == DeviceType.TYPE_A:
                    return self.device.contact_state  # A接点
                elif self.device.device_type == DeviceType.TYPE_B:
                    return not self.device.contact_state  # B接点
        elif self.element_type in [ElementType.COIL, ElementType.TIMER, ElementType.COUNTER]:
            return True  # 負荷デバイスは常に導通（電力を消費）
        
        return False
    
    def __repr__(self):
        return f"CircuitElement({self.element_type.value}, {self.grid_x}, {self.grid_y})"


class HotBusElement(CircuitElement):
    """ホットバスバー要素（X=0固定）"""
    def __init__(self, grid_y: int):
        super().__init__(ElementType.HOT_BUS, 0, grid_y)
        # ホットバスバーは常にX=0、右方向にのみ接続可能


class ColdBusElement(CircuitElement):
    """コールドバスバー要素（X=grid_cols-1固定）"""
    def __init__(self, grid_y: int, grid_cols: int):
        super().__init__(ElementType.COLD_BUS, grid_cols - 1, grid_y)
        # コールドバスバーは常にX=grid_cols-1、左方向からのみ接続可能


class CircuitChain:
    """完全な回路チェーンを管理"""
    def __init__(self, grid_y: int, grid_cols: int):
        self.grid_y = grid_y
        self.grid_cols = grid_cols
        self.elements: List[CircuitElement] = []
        self.hot_bus = HotBusElement(grid_y)
        self.cold_bus = ColdBusElement(grid_y, grid_cols)
        self.has_complete_path = False
        self.circuit_errors: List[str] = []
    
    def add_element(self, element: CircuitElement):
        """回路要素を追加"""
        self.elements.append(element)
        
    def build_connections(self):
        """要素間の接続を構築"""
        # 実際に配置されている要素のみをソート（バスバー除く）
        circuit_elements = sorted(self.elements, key=lambda e: e.grid_x)
        
        debug_logger.debug(f"Row {self.grid_y}: Building connections with {len(circuit_elements)} elements")
        for element in circuit_elements:
            debug_logger.debug(f"  Element: {element.element_type.value} at X={element.grid_x}")
        
        if not circuit_elements:
            debug_logger.debug(f"Row {self.grid_y}: No elements found, skipping connection building")
            return  # 要素がない場合は何もしない
        
        # ホットバスバー（X=0）を最初の要素に直接接続
        first_element = circuit_elements[0]
        self.hot_bus.add_right_connection(first_element)
        first_element.add_left_connection(self.hot_bus)
        
        # 中間要素間の接続を構築（隣接する実在要素のみ）
        for i in range(len(circuit_elements) - 1):
            current = circuit_elements[i]
            next_element = circuit_elements[i + 1]
            
            # 連続した位置にある場合のみ直接接続
            if next_element.grid_x == current.grid_x + 1:
                current.add_right_connection(next_element)
                next_element.add_left_connection(current)
            else:
                # 間にワイヤーが必要な場合のチェック（将来拡張）
                # 現在は間にワイヤーがある前提で接続
                has_wire_path = self._check_wire_path_between(current.grid_x, next_element.grid_x)
                if has_wire_path:
                    current.add_right_connection(next_element)
                    next_element.add_left_connection(current)
        
        # 最後の要素をコールドバスバー（X=grid_cols-1）に直接接続
        last_element = circuit_elements[-1]
        last_element.add_right_connection(self.cold_bus)
        self.cold_bus.add_left_connection(last_element)
        
        debug_logger.debug(f"Row {self.grid_y}: Connected HOT_BUS(X=0) -> {first_element.element_type.value}(X={first_element.grid_x}) -> ... -> {last_element.element_type.value}(X={last_element.grid_x}) -> COLD_BUS(X={self.cold_bus.grid_x})")
    
    def _check_wire_path_between(self, start_x: int, end_x: int) -> bool:
        """要素間のワイヤー経路をチェック"""
        # start_x + 1 から end_x - 1 までの範囲にワイヤーが必要
        for check_x in range(start_x + 1, end_x):
            # 対応するワイヤー要素が存在するかチェック
            wire_found = any(
                element.grid_x == check_x and element.element_type == ElementType.WIRE
                for element in self.elements
            )
            if not wire_found:
                return False  # ワイヤーが欠けている
        return True
    
    def validate_complete_circuit(self) -> bool:
        """ホット→コールド完全経路チェック"""
        self.circuit_errors.clear()
        
        # DFS（深度優先探索）でホット→コールド経路を探索
        visited: Set[CircuitElement] = set()
        path_found = self._dfs_path_search(self.hot_bus, visited)
        
        if not path_found:
            self.circuit_errors.append(f"Row {self.grid_y}: ホット→コールド完全経路が存在しません")
        
        # 導通チェック
        conduction_valid = self._validate_conduction_path()
        if not conduction_valid:
            self.circuit_errors.append(f"Row {self.grid_y}: 導通経路に問題があります")
            
        self.has_complete_path = path_found and conduction_valid
        return self.has_complete_path
    
    def _dfs_path_search(self, current: CircuitElement, visited: Set[CircuitElement]) -> bool:
        """深度優先探索でコールドバスバーまでの経路を探索"""
        if current in visited:
            return False
            
        visited.add(current)
        
        # デバッグ情報
        debug_logger.debug(f"  DFS visiting: {current.element_type.value} at ({current.grid_x}, {current.grid_y})")
        
        # コールドバスバーに到達した場合
        if current.element_type == ElementType.COLD_BUS:
            debug_logger.debug(f"  Found path to COLD_BUS!")
            return True
        
        # 最後の実要素（右端のデバイス）に到達した場合もコールド到達とみなす
        # これにより列8で終わる回路でも完全経路として認識される
        if (len(current.right_connections) == 1 and 
            current.right_connections[0].element_type == ElementType.COLD_BUS):
            debug_logger.debug(f"  Found path to last real element connected to COLD_BUS!")
            return True
            
        # 右側接続要素を探索
        for right_element in current.right_connections:
            if self._dfs_path_search(right_element, visited.copy()):
                return True
                
        return False
    
    def _validate_conduction_path(self) -> bool:
        """導通経路の妥当性をチェック"""
        # ホットバスバーから開始して、各要素の導通状態をチェック
        return self._check_conduction_recursive(self.hot_bus, set())
    
    def _check_conduction_recursive(self, current: CircuitElement, visited: Set[CircuitElement]) -> bool:
        """再帰的に導通状態をチェック"""
        if current in visited:
            return False
            
        visited.add(current)
        
        # 現在要素の導通状態をチェック
        if not current.get_conduction_state():
            return False
            
        # コールドバスバーに到達した場合
        if current.element_type == ElementType.COLD_BUS:
            return True
            
        # 右側接続要素をチェック
        for right_element in current.right_connections:
            if self._check_conduction_recursive(right_element, visited.copy()):
                return True
                
        return False
    
    def get_energized_elements(self) -> List[CircuitElement]:
        """通電している要素のリストを取得"""
        if not self.has_complete_path:
            return []
            
        energized = []
        visited = set()
        self._mark_energized_recursive(self.hot_bus, visited, energized)
        return energized
    
    def _mark_energized_recursive(self, current: CircuitElement, visited: Set[CircuitElement], energized: List[CircuitElement]):
        """再帰的に通電要素をマーク"""
        if current in visited or not current.get_conduction_state():
            return
            
        visited.add(current)
        energized.append(current)
        current.is_energized = True
        
        # 右側接続要素を処理
        for right_element in current.right_connections:
            self._mark_energized_recursive(right_element, visited, energized)


class CircuitTopologyManager:
    """回路トポロジー全体を管理"""
    def __init__(self, grid_manager):
        self.grid_manager = grid_manager
        self.circuit_chains: Dict[int, CircuitChain] = {}  # grid_y -> CircuitChain
        
    def build_circuit_topology(self):
        """グリッドデバイスから回路トポロジーを構築"""
        self.circuit_chains.clear()
        
        # 各行について回路チェーンを構築
        for row_idx, row in enumerate(self.grid_manager.grid):
            # デバイスが存在する行のみチェーンを作成
            has_devices = any(device.device_type != DeviceType.EMPTY for device in row)
            
            if has_devices:
                chain = CircuitChain(row_idx, self.grid_manager.grid_cols)
                
                for device in row:
                    if device.device_type != DeviceType.EMPTY:
                        element = self._create_circuit_element(device)
                        if element:
                            chain.add_element(element)
                
                # 接続を構築
                chain.build_connections()
                self.circuit_chains[row_idx] = chain
            else:
                debug_logger.debug(f"Row {row_idx}: No devices found, skipping circuit chain creation")
    
    def _create_circuit_element(self, device) -> Optional[CircuitElement]:
        """GridDeviceからCircuitElementを作成"""
        if device.device_type == DeviceType.WIRE_H:
            return CircuitElement(ElementType.WIRE, device.grid_x, device.grid_y, device)
        elif device.device_type in [DeviceType.TYPE_A, DeviceType.TYPE_B]:
            return CircuitElement(ElementType.CONTACT, device.grid_x, device.grid_y, device)
        elif device.device_type in [DeviceType.COIL, DeviceType.INCOIL, DeviceType.OUTCOIL_REV]:
            return CircuitElement(ElementType.COIL, device.grid_x, device.grid_y, device)
        elif device.device_type == DeviceType.TIMER:
            return CircuitElement(ElementType.TIMER, device.grid_x, device.grid_y, device)
        elif device.device_type == DeviceType.COUNTER:
            return CircuitElement(ElementType.COUNTER, device.grid_x, device.grid_y, device)
        
        return None
    
    def validate_all_circuits(self) -> Dict[int, bool]:
        """全回路の継続性を検証"""
        validation_results = {}
        
        for grid_y, chain in self.circuit_chains.items():
            is_valid = chain.validate_complete_circuit()
            validation_results[grid_y] = is_valid
            
        return validation_results
    
    def get_circuit_errors(self) -> List[str]:
        """全回路のエラーメッセージを取得"""
        all_errors = []
        for chain in self.circuit_chains.values():
            all_errors.extend(chain.circuit_errors)
        return all_errors
    
    def update_energized_states(self):
        """全回路の通電状態を更新"""
        for chain in self.circuit_chains.values():
            energized_elements = chain.get_energized_elements()
            
            # GridDeviceの表示状態を更新
            for element in energized_elements:
                if element.device and hasattr(element.device, 'active'):
                    element.device.active = True
    
    def reset_all_energized_states(self):
        """全デバイスの通電状態をリセット"""
        for row in self.grid_manager.grid:
            for device in row:
                if hasattr(device, 'active'):
                    device.active = False
                if hasattr(device, 'is_energized'):
                    device.is_energized = False
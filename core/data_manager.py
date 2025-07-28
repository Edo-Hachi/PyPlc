"""
PyPlc Data Manager Module
データ管理システムを分離したモジュール

Phase 4 リファクタリング: 設定・データ管理分離
- テストデータ・回路データ管理
- 回路セットアップ・初期化
- デバイス配置データ管理
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from core.constants import DeviceType


@dataclass
class DeviceData:
    """デバイス配置データ"""
    row: int
    col: int
    device_type: DeviceType
    device_id: str
    active: bool = False
    preset_value: Optional[float] = None


@dataclass
class CircuitData:
    """回路データ"""
    name: str
    description: str
    devices: List[DeviceData]


class PyPlcDataManager:
    """PyPlc データ管理システム"""
    
    def __init__(self):
        """データ管理システム初期化"""
        self._test_circuits: Dict[str, CircuitData] = {}
        self._current_circuit: Optional[str] = None
        self._initialize_test_circuits()
    
    def _initialize_test_circuits(self) -> None:
        """テスト回路データ初期化"""
        
        # 基本テスト回路（現在のmain.pyと同じ）
        basic_test = CircuitData(
            name="basic_test",
            description="基本テスト回路 - データと表示の整合性確認",
            devices=[
                DeviceData(
                    row=5, col=5, 
                    device_type=DeviceType.CONTACT_A, 
                    device_id="X001",
                    active=False
                )
            ]
        )
        
        # 複合テスト回路（コメントアウトされていたもの）
        complex_test = CircuitData(
            name="complex_test",
            description="複合テスト回路 - 複数デバイステスト",
            devices=[
                DeviceData(
                    row=5, col=5, 
                    device_type=DeviceType.CONTACT_A, 
                    device_id="X001",
                    active=False
                ),
                DeviceData(
                    row=2, col=4, 
                    device_type=DeviceType.CONTACT_B, 
                    device_id="X002",
                    active=False
                ),
                DeviceData(
                    row=2, col=7, 
                    device_type=DeviceType.COIL, 
                    device_id="Y001",
                    active=False
                ),
                DeviceData(
                    row=4, col=3, 
                    device_type=DeviceType.TIMER, 
                    device_id="T001",
                    active=False,
                    preset_value=3.0
                )
            ]
        )
        
        # 空回路（デバイスなし）
        empty_circuit = CircuitData(
            name="empty",
            description="空回路 - デバイス配置なし",
            devices=[]
        )
        
        # テスト回路登録
        self._test_circuits["basic_test"] = basic_test
        self._test_circuits["complex_test"] = complex_test
        self._test_circuits["empty"] = empty_circuit
        
        # デフォルト回路設定
        self._current_circuit = "basic_test"
    
    def get_available_circuits(self) -> List[str]:
        """利用可能な回路名一覧取得"""
        return list(self._test_circuits.keys())
    
    def get_circuit_info(self, circuit_name: str) -> Optional[CircuitData]:
        """回路情報取得"""
        return self._test_circuits.get(circuit_name)
    
    def set_current_circuit(self, circuit_name: str) -> bool:
        """現在の回路設定"""
        if circuit_name in self._test_circuits:
            self._current_circuit = circuit_name
            return True
        return False
    
    def get_current_circuit(self) -> Optional[CircuitData]:
        """現在の回路データ取得"""
        if self._current_circuit:
            return self._test_circuits.get(self._current_circuit)
        return None
    
    def get_current_circuit_name(self) -> Optional[str]:
        """現在の回路名取得"""
        return self._current_circuit
    
    def setup_circuit_on_grid(self, grid_manager, circuit_name: Optional[str] = None) -> bool:
        """
        グリッドマネージャーに回路をセットアップ
        
        Args:
            grid_manager: グリッドマネージャーインスタンス
            circuit_name: 回路名（Noneの場合は現在の回路）
            
        Returns:
            bool: セットアップ成功の場合True
        """
        # 回路データ取得
        if circuit_name:
            circuit_data = self.get_circuit_info(circuit_name)
        else:
            circuit_data = self.get_current_circuit()
        
        if not circuit_data:
            print(f"回路データが見つかりません: {circuit_name or self._current_circuit}")
            return False
        
        # デバイス配置実行
        success_count = 0
        total_devices = len(circuit_data.devices)
        
        print(f"回路セットアップ開始: {circuit_data.name} ({circuit_data.description})")
        
        for device_data in circuit_data.devices:
            try:
                # デバイス配置
                result = grid_manager.place_device(
                    device_data.row,
                    device_data.col,
                    device_data.device_type,
                    device_data.device_id
                )
                
                if result:
                    # デバイス状態設定
                    device = grid_manager.get_device(device_data.row, device_data.col)
                    if device:
                        device.active = device_data.active
                        if device_data.preset_value is not None:
                            # プリセット値設定（タイマー・カウンター用）
                            if hasattr(device, 'preset_value'):
                                device.preset_value = device_data.preset_value
                    
                    success_count += 1
                    print(f"デバイス配置成功: {device_data.device_id} at ({device_data.row},{device_data.col})")
                else:
                    print(f"デバイス配置失敗: {device_data.device_id} at ({device_data.row},{device_data.col})")
                    
            except Exception as e:
                print(f"デバイス配置エラー: {device_data.device_id} - {e}")
        
        print(f"回路セットアップ完了: {success_count}/{total_devices} デバイス配置成功")
        
        # 配置結果確認
        total_grid_devices = len(grid_manager.get_all_devices())
        print(f"グリッド総デバイス数: {total_grid_devices}")
        
        # 配置確認（最初のデバイスのみ）
        if circuit_data.devices:
            first_device = circuit_data.devices[0]
            placed_device = grid_manager.get_device(first_device.row, first_device.col)
            if placed_device:
                print(f"配置確認: {placed_device}")
        
        return success_count > 0
    
    def add_custom_circuit(self, circuit_data: CircuitData) -> bool:
        """カスタム回路追加"""
        if circuit_data.name in self._test_circuits:
            print(f"回路名が重複しています: {circuit_data.name}")
            return False
        
        self._test_circuits[circuit_data.name] = circuit_data
        print(f"カスタム回路追加: {circuit_data.name}")
        return True
    
    def remove_circuit(self, circuit_name: str) -> bool:
        """回路削除"""
        if circuit_name not in self._test_circuits:
            return False
        
        # 現在の回路の場合はemptyに変更
        if self._current_circuit == circuit_name:
            self._current_circuit = "empty"
        
        del self._test_circuits[circuit_name]
        print(f"回路削除: {circuit_name}")
        return True
    
    def get_circuit_summary(self) -> Dict[str, Dict]:
        """全回路サマリー取得"""
        summary = {}
        for name, circuit in self._test_circuits.items():
            summary[name] = {
                'description': circuit.description,
                'device_count': len(circuit.devices),
                'devices': [
                    {
                        'position': f"({d.row},{d.col})",
                        'type': d.device_type.value,
                        'id': d.device_id,
                        'active': d.active
                    }
                    for d in circuit.devices
                ],
                'is_current': name == self._current_circuit
            }
        return summary
    
    def validate_circuit_data(self, circuit_data: CircuitData, grid_cols: int) -> List[str]:
        """回路データ妥当性チェック"""
        errors = []
        
        # デバイス位置チェック
        for device in circuit_data.devices:
            # グリッド範囲チェック
            if not (0 <= device.row < 10):  # 仮の範囲
                errors.append(f"行が範囲外: {device.device_id} row={device.row}")
            
            if not (0 <= device.col < grid_cols):
                errors.append(f"列が範囲外: {device.device_id} col={device.col}")
            
            # 編集可能位置チェック（バスデバイス以外）
            if device.device_type not in [DeviceType.L_SIDE, DeviceType.R_SIDE]:
                if not (1 <= device.col <= grid_cols - 2):
                    errors.append(f"編集不可位置: {device.device_id} at ({device.row},{device.col})")
        
        # 重複位置チェック
        positions = [(d.row, d.col) for d in circuit_data.devices]
        if len(positions) != len(set(positions)):
            errors.append("デバイス位置が重複しています")
        
        # デバイスID重複チェック
        device_ids = [d.device_id for d in circuit_data.devices]
        if len(device_ids) != len(set(device_ids)):
            errors.append("デバイスIDが重複しています")
        
        return errors

import pyxel
import time
from typing import List, Optional, Dict, Tuple
from abc import ABC, abstractmethod
from enum import Enum
from SpriteManager import sprite_manager

WIDTH = 256
HEIGHT = 256

# レイアウト定数
class Layout:
    # 基本配置
    TITLE_X = 10
    TITLE_Y = 5
    
    # デバイスパレット
    PALETTE_Y = 16
    PALETTE_START_X = 20
    PALETTE_DEVICE_WIDTH = 24
    PALETTE_NUMBER_OFFSET_Y = -8
    
    # グリッド設定
    GRID_SIZE = 16
    GRID_COLS = 10
    GRID_ROWS = 10
    GRID_START_X = 16
    GRID_START_Y = 32
    
    # デバイス状態表示
    DEVICE_STATUS_Y = 160
    DEVICE_STATUS_X = 10
    DEVICE_STATUS_SPACING = 12
    DEVICE_STATUS_X2 = 90
    TIMER_COUNTER_X = 170
    
    # 操作説明
    CONTROLS_Y = 240
    CONTROLS_X = 10
    
    # スプライトテスト（右上）
    SPRITE_TEST_X = 160
    SPRITE_TEST_Y = 10

# 色定数
class Colors:
    GRID_LINE = 1        # ダークグレイ
    WIRE_OFF = 1         # グレイ（通電なし）
    WIRE_ON = 11         # 緑（通電中）
    SELECTED_BG = 6      # 黄色（選択背景）
    TEXT = 7             # 白
    BUSBAR = 7           # 白
    BLACK = 0            # 黒

# デバイスタイプ定義
class DeviceType(Enum):
    EMPTY = "EMPTY"          # 空のグリッド
    BUSBAR = "BUSBAR"        # バスバー
    TYPE_A = "TYPE_A"        # A接点
    TYPE_B = "TYPE_B"        # B接点
    COIL = "COIL"            # コイル
    TIMER = "TIMER"          # タイマー
    COUNTER = "COUNTER"      # カウンター
    WIRE_H = "WIRE_H"        # 横配線
    WIRE_V = "WIRE_V"        # 縦配線

# バスバー接続方向
class BusbarDirection(Enum):
    NONE = 0
    UP = 1
    DOWN = 2
    BOTH = 3

class GridDevice:
    """グリッド上に配置されるロジックデバイス"""
    def __init__(self, device_type: DeviceType = DeviceType.EMPTY, grid_x: int = 0, grid_y: int = 0):
        self.device_type = device_type
        self.grid_x = grid_x
        self.grid_y = grid_y
        
        # デバイス共通状態
        self.active = False          # 動作状態（通電状態）
        self.device_address = None   # デバイスアドレス（X001, Y001等）
        
        # デバイス固有の状態
        self.timer_preset = 0.0      # タイマープリセット値
        self.timer_current = 0.0     # タイマー現在値
        self.counter_preset = 0      # カウンタープリセット値
        self.counter_current = 0     # カウンター現在値
        self.contact_state = False   # 接点状態（A/B接点用）
        self.coil_energized = False  # コイル励磁状態
        
        # バスバー専用
        self.busbar_direction = BusbarDirection.NONE  # 接続方向
        
        # 配線専用
        self.wire_energized = False  # 配線通電状態
    
    def get_sprite_name(self) -> Optional[str]:
        """デバイスタイプと状態に応じたスプライト名を返す"""
        if self.device_type == DeviceType.TYPE_A:
            return "TYPE_A_ON" if self.active else "TYPE_A_OFF"
        elif self.device_type == DeviceType.TYPE_B:
            return "TYPE_B_ON" if self.active else "TYPE_B_OFF"
        elif self.device_type == DeviceType.COIL:
            return "LAMP_ON" if self.coil_energized else "LAMP_OFF"
        elif self.device_type == DeviceType.TIMER:
            return "TYPE_A_ON" if self.active else "TYPE_A_OFF"  # 仮のスプライト
        elif self.device_type == DeviceType.COUNTER:
            return "TYPE_A_ON" if self.active else "TYPE_A_OFF"  # 仮のスプライト
        return None
    
    def update_state(self, device_manager):
        """デバイス状態を更新"""
        if self.device_address and self.device_type in [DeviceType.TYPE_A, DeviceType.TYPE_B]:
            plc_device = device_manager.get_device(self.device_address)
            if self.device_type == DeviceType.TYPE_A:
                self.contact_state = plc_device.value
                self.active = self.contact_state
            elif self.device_type == DeviceType.TYPE_B:
                self.contact_state = plc_device.value
                self.active = not self.contact_state  # B接点は反転
        elif self.device_address and self.device_type == DeviceType.COIL:
            plc_device = device_manager.get_device(self.device_address)
            self.coil_energized = plc_device.value
            self.active = self.coil_energized

class GridDeviceManager:
    """グリッド上のデバイス配置を管理するクラス"""
    def __init__(self, grid_cols: int = 10, grid_rows: int = 10):
        self.grid_cols = grid_cols
        self.grid_rows = grid_rows
        # 2次元配列でグリッドデバイスを管理
        self.grid: List[List[GridDevice]] = []
        
        # グリッドを初期化
        for row in range(grid_rows):
            grid_row = []
            for col in range(grid_cols):
                grid_row.append(GridDevice(DeviceType.EMPTY, col, row))
            self.grid.append(grid_row)
    
    def place_device(self, grid_x: int, grid_y: int, device_type: DeviceType, device_address: str = None) -> bool:
        """指定位置にデバイスを配置"""
        if 0 <= grid_x < self.grid_cols and 0 <= grid_y < self.grid_rows:
            device = self.grid[grid_y][grid_x]
            device.device_type = device_type
            device.device_address = device_address
            device.grid_x = grid_x
            device.grid_y = grid_y
            return True
        return False
    
    def get_device(self, grid_x: int, grid_y: int) -> Optional[GridDevice]:
        """指定位置のデバイスを取得"""
        if 0 <= grid_x < self.grid_cols and 0 <= grid_y < self.grid_rows:
            return self.grid[grid_y][grid_x]
        return None
    
    def remove_device(self, grid_x: int, grid_y: int) -> bool:
        """指定位置のデバイスを削除"""
        if 0 <= grid_x < self.grid_cols and 0 <= grid_y < self.grid_rows:
            device = self.grid[grid_y][grid_x]
            device.device_type = DeviceType.EMPTY
            device.device_address = None
            device.active = False
            return True
        return False
    
    def update_all_devices(self, device_manager):
        """全デバイスの状態を更新"""
        for row in self.grid:
            for device in row:
                if device.device_type != DeviceType.EMPTY:
                    device.update_state(device_manager)


class PLCDevice:
    """PLCデバイス（X, Y, M, T, C等）を表現するクラス"""
    def __init__(self, address: str, device_type: str):
        self.address = address
        self.device_type = device_type
        if device_type in ['X', 'Y', 'M']:
            self.value = False
        elif device_type in ['T', 'C']:
            self.value = 0
            self.preset_value = 0
            self.current_value = 0
            self.coil_state = False
        else:
            self.value = 0


class DeviceManager:
    """PLCデバイスを管理するクラス"""
    def __init__(self):
        self.devices = {}
        
    def get_device(self, address: str) -> PLCDevice:
        """デバイスを取得（存在しない場合は作成）"""
        if address not in self.devices:
            device_type = address[0]
            self.devices[address] = PLCDevice(address, device_type)
        return self.devices[address]
    
    def set_device_value(self, address: str, value):
        """デバイス値を設定"""
        device = self.get_device(address)
        device.value = value


class LogicElement(ABC):
    """論理素子の基底クラス"""
    def __init__(self, device_address: str = None):
        self.inputs: List[LogicElement] = []
        self.device_address = device_address
        self.device = None
        self.last_result = False
        
    def add_input(self, element: 'LogicElement'):
        """入力素子を追加"""
        self.inputs.append(element)
        
    @abstractmethod
    def evaluate(self, device_manager: DeviceManager) -> bool:
        """論理演算を実行"""
        pass


class ContactA(LogicElement):
    """A接点（ノーマルオープン）"""
    def __init__(self, device_address: str):
        super().__init__(device_address)
        
    def evaluate(self, device_manager: DeviceManager) -> bool:
        device = device_manager.get_device(self.device_address)
        self.last_result = bool(device.value)
        return self.last_result


class ContactB(LogicElement):
    """B接点（ノーマルクローズ）"""
    def __init__(self, device_address: str):
        super().__init__(device_address)
        
    def evaluate(self, device_manager: DeviceManager) -> bool:
        device = device_manager.get_device(self.device_address)
        self.last_result = not bool(device.value)
        return self.last_result


class Coil(LogicElement):
    """出力コイル"""
    def __init__(self, device_address: str):
        super().__init__(device_address)
        
    def evaluate(self, device_manager: DeviceManager) -> bool:
        result = self.inputs[0].evaluate(device_manager) if self.inputs else False
        device_manager.set_device_value(self.device_address, result)
        self.last_result = result
        return result


class Timer(LogicElement):
    """タイマー（TON: タイマーオン）"""
    def __init__(self, device_address: str, preset_time: float = 5.0):
        super().__init__(device_address)
        self.preset_time = preset_time
        self.start_time = None
        self.is_timing = False
        
    def evaluate(self, device_manager: DeviceManager) -> bool:
        input_state = self.inputs[0].evaluate(device_manager) if self.inputs else False
        device = device_manager.get_device(self.device_address)
        
        current_time = time.time()
        
        if input_state and not self.is_timing:
            self.start_time = current_time
            self.is_timing = True
            device.current_value = 0
            device.coil_state = False
            
        elif not input_state:
            self.is_timing = False
            self.start_time = None
            device.current_value = 0
            device.coil_state = False
            
        if self.is_timing:
            elapsed = current_time - self.start_time
            device.current_value = elapsed
            
            if elapsed >= self.preset_time:
                device.coil_state = True
            else:
                device.coil_state = False
        
        device.preset_value = self.preset_time
        self.last_result = device.coil_state
        return device.coil_state


class Counter(LogicElement):
    """カウンター（CTU: カウントアップ）"""
    def __init__(self, device_address: str, preset_count: int = 5):
        super().__init__(device_address)
        self.preset_count = preset_count
        self.last_input_state = False
        
    def evaluate(self, device_manager: DeviceManager) -> bool:
        input_state = self.inputs[0].evaluate(device_manager) if self.inputs else False
        device = device_manager.get_device(self.device_address)
        
        if input_state and not self.last_input_state:
            device.current_value += 1
            
        if device.current_value >= self.preset_count:
            device.coil_state = True
        else:
            device.coil_state = False
            
        device.preset_value = self.preset_count
        self.last_input_state = input_state
        self.last_result = device.coil_state
        return device.coil_state


class LadderLine:
    """ラダー図の1行を表現するクラス"""
    def __init__(self):
        self.elements: List[LogicElement] = []
        self.power_flow = False
        
    def add_element(self, element: LogicElement):
        """素子を追加（左から右の順序）"""
        if self.elements:
            element.add_input(self.elements[-1])
        self.elements.append(element)
        
    def scan(self, device_manager: DeviceManager):
        """ライン実行（左から右へ）"""
        if self.elements:
            self.power_flow = self.elements[-1].evaluate(device_manager)


class LadderProgram:
    """ラダープログラム全体を管理するクラス"""
    def __init__(self):
        self.lines: List[LadderLine] = []
        self.current_line = 0
        
    def add_line(self, line: LadderLine):
        """ラインを追加"""
        self.lines.append(line)
        
    def scan_cycle(self, device_manager: DeviceManager):
        """スキャンサイクル実行（上から下へ）"""
        for i, line in enumerate(self.lines):
            self.current_line = i
            line.scan(device_manager)


class PLCSimulator:
    """PLCシミュレーターのメインクラス"""
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="PLC Ladder Simulator")
        pyxel.load("my_resource.pyxres")
        
        self.device_manager = DeviceManager()
        self.ladder_program = LadderProgram()
        
        # グリッドデバイス管理システム
        self.grid_device_manager = GridDeviceManager(Layout.GRID_COLS, Layout.GRID_ROWS)
        
        # スプライトキャッシュ（初期化時に一括取得）
        self.sprites = {
            "TYPE_A_ON": sprite_manager.get_sprite_by_name_and_tag("TYPE_A_ON"),
            "TYPE_A_OFF": sprite_manager.get_sprite_by_name_and_tag("TYPE_A_OFF"),
            "TYPE_B_ON": sprite_manager.get_sprite_by_name_and_tag("TYPE_B_ON"),
            "TYPE_B_OFF": sprite_manager.get_sprite_by_name_and_tag("TYPE_B_OFF"),
            "LAMP_ON": sprite_manager.get_sprite_by_name_and_tag("LAMP_ON"),
            "LAMP_OFF": sprite_manager.get_sprite_by_name_and_tag("LAMP_OFF")
        }
        
        # デバイス選択システム
        self.selected_device_type = DeviceType.TYPE_A  # 現在選択中のデバイスタイプ
        self.device_palette = [
            {"type": DeviceType.BUSBAR, "name": "バスバー", "sprite": None},
            {"type": DeviceType.TYPE_A, "name": "A接点", "sprite": "TYPE_A_OFF"},
            {"type": DeviceType.TYPE_B, "name": "B接点", "sprite": "TYPE_B_OFF"},
            {"type": DeviceType.COIL, "name": "コイル", "sprite": "LAMP_OFF"},
            {"type": DeviceType.TIMER, "name": "タイマー", "sprite": "TYPE_A_OFF"},
            {"type": DeviceType.COUNTER, "name": "カウンタ", "sprite": "TYPE_A_OFF"},
            {"type": DeviceType.WIRE_H, "name": "横線", "sprite": None},
            {"type": DeviceType.WIRE_V, "name": "縦線", "sprite": None}
        ]
        
        # テスト用にグリッドにデバイスを配置
        self._setup_test_grid_devices()
        
        # テスト用AND回路を作成: X001 AND X002 -> Y001
        line1 = LadderLine()
        line1.add_element(ContactA("X001"))
        line1.add_element(ContactA("X002"))  
        line1.add_element(Coil("Y001"))
        self.ladder_program.add_line(line1)
        
        # タイマーテスト回路: X003 -> T001(3秒) -> Y002
        line2 = LadderLine()
        line2.add_element(ContactA("X003"))
        line2.add_element(Timer("T001", 3.0))
        line2.add_element(Coil("Y002"))
        self.ladder_program.add_line(line2)
        
        # カウンタテスト回路: X004 -> C001(3回) -> Y003
        line3 = LadderLine()
        line3.add_element(ContactA("X004"))
        line3.add_element(Counter("C001", 3))
        line3.add_element(Coil("Y003"))
        self.ladder_program.add_line(line3)
        
        # 初期値設定
        self.device_manager.set_device_value("X001", False)
        self.device_manager.set_device_value("X002", False)
        self.device_manager.set_device_value("X003", False)
        self.device_manager.set_device_value("X004", False)
        
        pyxel.run(self.update, self.draw)
    
    def _setup_test_grid_devices(self):
        """テスト用グリッドデバイス配置"""
        # ライン1: バスバー -> X001 -> X002 -> Y001
        self.grid_device_manager.place_device(0, 2, DeviceType.BUSBAR)
        self.grid_device_manager.place_device(2, 2, DeviceType.TYPE_A, "X001")
        self.grid_device_manager.place_device(4, 2, DeviceType.TYPE_A, "X002")
        self.grid_device_manager.place_device(8, 2, DeviceType.COIL, "Y001")
        
    def update(self):
        """フレーム更新処理"""
        # ESCキーでアプリケーションを終了
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
            
        # デバイスパレット選択（1-8キー）
        device_keys = [pyxel.KEY_1, pyxel.KEY_2, pyxel.KEY_3, pyxel.KEY_4, 
                      pyxel.KEY_5, pyxel.KEY_6, pyxel.KEY_7, pyxel.KEY_8]
        
        for i, key in enumerate(device_keys):
            if pyxel.btnp(key) and i < len(self.device_palette):
                if pyxel.btn(pyxel.KEY_SHIFT):
                    # Shift+数字キー: デバイス手動操作
                    if i == 0:  # Shift+1: X001
                        current = self.device_manager.get_device("X001").value
                        self.device_manager.set_device_value("X001", not current)
                    elif i == 1:  # Shift+2: X002
                        current = self.device_manager.get_device("X002").value
                        self.device_manager.set_device_value("X002", not current)
                    elif i == 2:  # Shift+3: X003
                        current = self.device_manager.get_device("X003").value
                        self.device_manager.set_device_value("X003", not current)
                    elif i == 3:  # Shift+4: X004
                        current = self.device_manager.get_device("X004").value
                        self.device_manager.set_device_value("X004", not current)
                else:
                    # 数字キーのみ: デバイス選択
                    self.selected_device_type = self.device_palette[i]["type"]
            
        # スキャンサイクル実行
        self.ladder_program.scan_cycle(self.device_manager)
        
        # グリッドデバイス状態更新
        self.grid_device_manager.update_all_devices(self.device_manager)
        
    def draw(self):
        """画面描画処理"""
        pyxel.cls(0)  # 背景をクリア
        
        # タイトル
        pyxel.text(Layout.TITLE_X, Layout.TITLE_Y, "PLC Ladder Simulator", Colors.TEXT)
        
        # PLCデバイスパレット表示（Y=16ライン）
        self._draw_device_palette()
        
        # PLCデバイス配置用グリッド表示
        self._draw_device_grid()
        
        # スプライトテスト表示（画面上部）
        self._draw_sprite_test()
        
        # ラダー図描画
        y_pos = 50
        for line in self.ladder_program.lines:
            x_pos = 10
            
            # 左バスバー
            pyxel.line(x_pos, y_pos, x_pos, y_pos + 8, 7)
            x_pos += 5
            
            for element in line.elements:
                # 素子の描画
                if isinstance(element, ContactA):
                    color = 11 if element.last_result else 1
                    pyxel.rect(x_pos, y_pos, 8, 8, color)
                    pyxel.text(x_pos + 1, y_pos + 2, "A", 0)
                    # デバイス名表示
                    pyxel.text(x_pos, y_pos - 8, element.device_address, 7)
                    
                elif isinstance(element, ContactB):
                    color = 11 if element.last_result else 1
                    pyxel.rect(x_pos, y_pos, 8, 8, color)
                    pyxel.text(x_pos + 1, y_pos + 2, "B", 0)
                    pyxel.text(x_pos, y_pos - 8, element.device_address, 7)
                    
                elif isinstance(element, Coil):
                    color = 11 if element.last_result else 1
                    pyxel.circ(x_pos + 4, y_pos + 4, 3, color)
                    pyxel.text(x_pos, y_pos - 8, element.device_address, 7)
                    
                elif isinstance(element, Timer):
                    color = 11 if element.last_result else 1
                    pyxel.rect(x_pos, y_pos, 10, 8, color)
                    pyxel.text(x_pos + 1, y_pos + 2, "T", 0)
                    pyxel.text(x_pos, y_pos - 8, element.device_address, 7)
                    
                elif isinstance(element, Counter):
                    color = 11 if element.last_result else 1
                    pyxel.rect(x_pos, y_pos, 10, 8, color)
                    pyxel.text(x_pos + 1, y_pos + 2, "C", 0)
                    pyxel.text(x_pos, y_pos - 8, element.device_address, 7)
                
                # 接続線
                if x_pos > 15:  # 最初の素子でない場合
                    line_color = 11 if element.last_result else 1
                    pyxel.line(x_pos - 5, y_pos + 4, x_pos, y_pos + 4, line_color)
                
                x_pos += 15
                
            y_pos += 20
            
        # デバイス状態表示
        pyxel.text(Layout.DEVICE_STATUS_X, Layout.DEVICE_STATUS_Y, "Device Status:", Colors.TEXT)
        y_offset = Layout.DEVICE_STATUS_Y + 10
        
        # 入力デバイス
        for i, addr in enumerate(['X001', 'X002', 'X003', 'X004']):
            device = self.device_manager.get_device(addr)
            pyxel.text(Layout.DEVICE_STATUS_X, y_offset + i * Layout.DEVICE_STATUS_SPACING, f"{addr}: {'ON' if device.value else 'OFF'}", Colors.TEXT)
            
        # 出力デバイス
        for i, addr in enumerate(['Y001', 'Y002', 'Y003']):
            device = self.device_manager.get_device(addr)
            pyxel.text(Layout.DEVICE_STATUS_X2, y_offset + i * Layout.DEVICE_STATUS_SPACING, f"{addr}: {'ON' if device.value else 'OFF'}", Colors.TEXT)
            
        # タイマー・カウンター状態
        timer_device = self.device_manager.get_device('T001')
        counter_device = self.device_manager.get_device('C001')
        
        pyxel.text(Layout.TIMER_COUNTER_X, y_offset, f"T001: {timer_device.current_value:.1f}s/{timer_device.preset_value:.1f}s", Colors.TEXT)
        pyxel.text(Layout.TIMER_COUNTER_X, y_offset + Layout.DEVICE_STATUS_SPACING, f"C001: {counter_device.current_value}/{counter_device.preset_value}", Colors.TEXT)
        
        # 操作説明
        pyxel.text(Layout.CONTROLS_X, Layout.CONTROLS_Y, "1-8:Select Device  Shift+1-4:Toggle X001-X004  Q:Exit", Colors.TEXT)
        
    def _draw_sprite_test(self):
        """スプライトテスト表示"""
        # スプライトテスト - 右上に配置
        start_x = Layout.SPRITE_TEST_X
        start_y = Layout.SPRITE_TEST_Y
        
        # TYPE_A ON/OFF スプライト
        sprite_a_on = self.sprites["TYPE_A_ON"]
        sprite_a_off = self.sprites["TYPE_A_OFF"]
        pyxel.blt(start_x, start_y, 0, sprite_a_on.x, sprite_a_on.y, 8, 8, 0)
        pyxel.blt(start_x + 15, start_y, 0, sprite_a_off.x, sprite_a_off.y, 8, 8, 0)
        pyxel.text(start_x - 2, start_y + 10, "A_ON", Colors.TEXT)
        pyxel.text(start_x + 13, start_y + 10, "A_OFF", Colors.TEXT)
        
        # TYPE_B ON/OFF スプライト
        sprite_b_on = self.sprites["TYPE_B_ON"]
        sprite_b_off = self.sprites["TYPE_B_OFF"]
        pyxel.blt(start_x + 35, start_y, 0, sprite_b_on.x, sprite_b_on.y, 8, 8, 0)
        pyxel.blt(start_x + 50, start_y, 0, sprite_b_off.x, sprite_b_off.y, 8, 8, 0)
        pyxel.text(start_x + 33, start_y + 10, "B_ON", Colors.TEXT)
        pyxel.text(start_x + 48, start_y + 10, "B_OFF", Colors.TEXT)
        
        # LAMP ON/OFF スプライト
        sprite_lamp_on = self.sprites["LAMP_ON"]
        sprite_lamp_off = self.sprites["LAMP_OFF"]
        pyxel.blt(start_x + 10, start_y + 25, 0, sprite_lamp_on.x, sprite_lamp_on.y, 8, 8, 0)
        pyxel.blt(start_x + 25, start_y + 25, 0, sprite_lamp_off.x, sprite_lamp_off.y, 8, 8, 0)
        pyxel.text(start_x + 5, start_y + 35, "LAMP_ON", Colors.TEXT)
        pyxel.text(start_x + 20, start_y + 35, "LAMP_OFF", Colors.TEXT)

    def _draw_grid_devices(self):
        """グリッド配置されたデバイスを描画"""
        for row in self.grid_device_manager.grid:
            for device in row:
                if device.device_type != DeviceType.EMPTY:
                    # グリッド座標をピクセル座標に変換
                    px = self.grid_start_x + device.grid_x * self.grid_size
                    py = self.grid_start_y + device.grid_y * self.grid_size
                    
                    # デバイスタイプに応じて描画
                    if device.device_type == DeviceType.BUSBAR:
                        pyxel.rect(px - 2, py - 6, 4, 12, Colors.BUSBAR)
                        pyxel.text(px - 8, py + 8, "L", Colors.TEXT)
                    elif device.device_type in [DeviceType.TYPE_A, DeviceType.TYPE_B, DeviceType.COIL]:
                        sprite_name = device.get_sprite_name()
                        if sprite_name and sprite_name in self.sprites:
                            sprite = self.sprites[sprite_name]
                            pyxel.blt(px - 4, py - 4, 0, sprite.x, sprite.y, 8, 8, 0)
                        
                        # デバイスアドレス表示
                        if device.device_address:
                            pyxel.text(px - 8, py + 8, device.device_address, Colors.TEXT)
                    elif device.device_type == DeviceType.WIRE_H:
                        color = Colors.WIRE_ON if device.wire_energized else Colors.WIRE_OFF
                        pyxel.line(px - 8, py, px + 8, py, color)
                    elif device.device_type == DeviceType.WIRE_V:
                        color = Colors.WIRE_ON if device.wire_energized else Colors.WIRE_OFF
                        pyxel.line(px, py - 8, px, py + 8, color)

    def _draw_device_palette(self):
        """Y=16ラインにPLCデバイスパレットを表示"""
        
        for i, device in enumerate(self.device_palette):
            x_pos = Layout.PALETTE_START_X + i * Layout.PALETTE_DEVICE_WIDTH
            
            # 選択中のデバイスは背景を明るく
            if device["type"] == self.selected_device_type:
                pyxel.rect(x_pos - 2, Layout.PALETTE_Y - 2, 20, 12, Colors.SELECTED_BG)
            
            # デバイススプライト表示
            if device["sprite"]:
                sprite = self.sprites[device["sprite"]]
                pyxel.blt(x_pos, Layout.PALETTE_Y, 0, sprite.x, sprite.y, 8, 8, 0)
            else:
                # スプライトがない場合は記号で表示
                if device["type"] == "BUSBAR":
                    pyxel.rect(x_pos + 2, Layout.PALETTE_Y - 2, 4, 12, Colors.BUSBAR)
                elif device["type"] == "WIRE_H":
                    pyxel.line(x_pos, Layout.PALETTE_Y + 4, x_pos + 8, Layout.PALETTE_Y + 4, Colors.BUSBAR)
                elif device["type"] == "WIRE_V":
                    pyxel.line(x_pos + 4, Layout.PALETTE_Y, x_pos + 4, Layout.PALETTE_Y + 8, Colors.BUSBAR)
            
            # デバイス番号表示
            pyxel.text(x_pos + 2, Layout.PALETTE_Y + Layout.PALETTE_NUMBER_OFFSET_Y, str(i + 1), Colors.TEXT)

    def _draw_device_grid(self):
        """PLCデバイス配置用グリッドを描画"""
        # グリッド設定をインスタンス変数に保存
        self.grid_size = Layout.GRID_SIZE
        self.grid_cols = Layout.GRID_COLS
        self.grid_rows = Layout.GRID_ROWS
        self.grid_start_x = Layout.GRID_START_X
        self.grid_start_y = Layout.GRID_START_Y
        
        # 縦線を描画
        for col in range(self.grid_cols + 1):
            x = self.grid_start_x + col * self.grid_size
            y1 = self.grid_start_y
            y2 = self.grid_start_y + self.grid_rows * self.grid_size
            pyxel.line(x, y1, x, y2, Colors.GRID_LINE)
        
        # 横線を描画
        for row in range(self.grid_rows + 1):
            y = self.grid_start_y + row * self.grid_size
            x1 = self.grid_start_x
            x2 = self.grid_start_x + self.grid_cols * self.grid_size
            pyxel.line(x1, y, x2, y, Colors.GRID_LINE)
        
        # グリッドデバイス描画
        self._draw_grid_devices()
    
    def _draw_grid_intersection_demo(self):
        """グリッド交点でのデバイス配置デモ"""
        # 交点座標を計算
        def get_intersection_pos(grid_x, grid_y):
            pixel_x = self.grid_start_x + grid_x * self.grid_size
            pixel_y = self.grid_start_y + grid_y * self.grid_size
            return pixel_x, pixel_y
        
        # デモ配置: ラダー図的なレイアウト
        # ライン1: 左バスバー -> X001 -> X002 -> Y001
        positions = [
            (0, 2),  # 左バスバー
            (2, 2),  # X001 (A接点)
            (4, 2),  # X002 (A接点) 
            (8, 2),  # Y001 (コイル)
        ]
        
        # デバイスを交点に配置
        for i, (gx, gy) in enumerate(positions):
            px, py = get_intersection_pos(gx, gy)
            
            if i == 0:  # 左バスバー
                pyxel.rect(px-2, py-6, 4, 12, Colors.BUSBAR)
                pyxel.text(px-8, py+8, "L", Colors.TEXT)
            elif i == 1:  # X001
                sprite = self.sprites["TYPE_A_ON"] if self.device_manager.get_device("X001").value else self.sprites["TYPE_A_OFF"]
                pyxel.blt(px-4, py-4, 0, sprite.x, sprite.y, 8, 8, 0)
                pyxel.text(px-8, py+8, "X001", Colors.TEXT)
            elif i == 2:  # X002
                sprite = self.sprites["TYPE_A_ON"] if self.device_manager.get_device("X002").value else self.sprites["TYPE_A_OFF"]
                pyxel.blt(px-4, py-4, 0, sprite.x, sprite.y, 8, 8, 0)
                pyxel.text(px-8, py+8, "X002", Colors.TEXT)
            elif i == 3:  # Y001
                sprite = self.sprites["LAMP_ON"] if self.device_manager.get_device("Y001").value else self.sprites["LAMP_OFF"]
                pyxel.blt(px-4, py-4, 0, sprite.x, sprite.y, 8, 8, 0)
                pyxel.text(px-8, py+8, "Y001", Colors.TEXT)
        
        # 横配線を描画（デバイス間接続）
        y_wire = self.grid_start_y + 2 * self.grid_size
        wire_color = Colors.WIRE_ON if (self.device_manager.get_device("X001").value and 
                          self.device_manager.get_device("X002").value) else Colors.WIRE_OFF
        
        # 左バスバー -> X001
        x1 = self.grid_start_x + 0 * self.grid_size + 2
        x2 = self.grid_start_x + 2 * self.grid_size - 4
        pyxel.line(x1, y_wire, x2, y_wire, wire_color)
        
        # X001 -> X002
        x1 = self.grid_start_x + 2 * self.grid_size + 4
        x2 = self.grid_start_x + 4 * self.grid_size - 4
        pyxel.line(x1, y_wire, x2, y_wire, wire_color)
        
        # X002 -> Y001
        x1 = self.grid_start_x + 4 * self.grid_size + 4
        x2 = self.grid_start_x + 8 * self.grid_size - 4
        pyxel.line(x1, y_wire, x2, y_wire, wire_color)


if __name__ == "__main__":
    PLCSimulator()

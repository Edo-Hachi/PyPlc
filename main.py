"""
PyPlc Main Module - Refactored

モジュール化されたPLCシミュレーターのメインコーディネーター。
各機能モジュールを統合し、システム全体の制御を行う。
"""

import pyxel
from SpriteManager import sprite_manager

# モジュール化された各コンポーネントをインポート
from config import WIDTH, HEIGHT, Layout, Colors, DeviceType
from grid_system import GridDeviceManager
from electrical_system import ElectricalSystem
from plc_logic import DeviceManager, LadderProgram, LadderLine, ContactA, ContactB, Coil, Timer, Counter
from ui_components import UIRenderer, MouseHandler


class PLCSimulator:
    """PLCシミュレーターのメインコーディネータークラス"""
    
    def __init__(self):
        # Pyxel初期化
        pyxel.init(WIDTH, HEIGHT, title="PLC Ladder Simulator")
        pyxel.mouse(True)
        pyxel.load("my_resource.pyxres")
        
        # コアシステム初期化
        self.device_manager = DeviceManager()
        self.ladder_program = LadderProgram()
        self.grid_device_manager = GridDeviceManager(Layout.GRID_COLS, Layout.GRID_ROWS)
        self.electrical_system = ElectricalSystem(self.grid_device_manager)
        
        # スプライト管理システム
        self._initialize_sprites()
        
        # UI システム初期化
        self._initialize_ui_systems()
        
        # テストデータセットアップ
        self._setup_test_systems()
    
    def _initialize_sprites(self):
        """スプライトキャッシュ初期化"""
        self.sprites = {
            "TYPE_A_ON": sprite_manager.get_sprite_by_name_and_tag("TYPE_A_ON"),
            "TYPE_A_OFF": sprite_manager.get_sprite_by_name_and_tag("TYPE_A_OFF"),
            "TYPE_B_ON": sprite_manager.get_sprite_by_name_and_tag("TYPE_B_ON"),
            "TYPE_B_OFF": sprite_manager.get_sprite_by_name_and_tag("TYPE_B_OFF"),
            "LAMP_ON": sprite_manager.get_sprite_by_name_and_tag("LAMP_ON"),
            "LAMP_OFF": sprite_manager.get_sprite_by_name_and_tag("LAMP_OFF"),
            "TIMER_ON": sprite_manager.get_sprite_by_name_and_tag("TIMER_ON"),
            "TIMER_OFF": sprite_manager.get_sprite_by_name_and_tag("TIMER_OFF"),
            "LINK_UP": sprite_manager.get_sprite_by_name_and_tag("LINK_UP"),
            "LINK_DOWN": sprite_manager.get_sprite_by_name_and_tag("LINK_DOWN"),
            "DEL": sprite_manager.get_sprite_by_name_and_tag("DEL")
        }
    
    def _initialize_ui_systems(self):
        """UIシステム初期化"""
        # デバイスパレット定義（元のコード形式）
        self.device_palette = [
            {"type": DeviceType.TYPE_A, "name": "A接点", "sprite": "TYPE_A_OFF"},
            {"type": DeviceType.TYPE_B, "name": "B接点", "sprite": "TYPE_B_OFF"},
            {"type": DeviceType.COIL, "name": "コイル", "sprite": "LAMP_OFF"},
            {"type": DeviceType.TIMER, "name": "タイマー", "sprite": "TIMER_OFF"},
            #{"type": DeviceType.BUSBAR, "name": "バスバー", "sprite": None},
            {"type": DeviceType.LINK_UP, "name": "上結線", "sprite": "LINK_UP"},
            {"type": DeviceType.LINK_DOWN, "name": "下結線", "sprite": "LINK_DOWN"},
            {"type": DeviceType.DEL, "name": "削除", "sprite": "DEL"}
        ]
        
        # 選択状態管理（元のコード形式）
        self.selected_device_type = DeviceType.TYPE_A
        
        # UI コンポーネント初期化
        self.ui_renderer = UIRenderer(self.sprites, self.device_palette)
        self.mouse_handler = MouseHandler(self.device_palette, self.selected_device_type)
    
    def _setup_test_systems(self):
        """テストシステムセットアップ"""
        # テスト用グリッドデバイス配置
        self._setup_test_grid_devices()
        
        # テスト用従来ラダー回路作成
        #self._setup_test_ladder_circuits()
    
    def _setup_test_grid_devices(self):
        
        """テスト用グリッドデバイス配置"""
        # グリッドAND回路: バスバー → X001 → X002 → Y001
        self.grid_device_manager.place_device(0, 2, DeviceType.BUSBAR)
        self.grid_device_manager.place_device(2, 2, DeviceType.TYPE_A, "X001")
        self.grid_device_manager.place_device(4, 2, DeviceType.TYPE_A, "X002")
        self.grid_device_manager.place_device(8, 2, DeviceType.COIL, "Y001")
        
        # 初期デバイス値設定
        self.device_manager.set_device_value("X001", False)
        self.device_manager.set_device_value("X002", False)
    
    def _setup_test_ladder_circuits(self):
        return
        """テスト用従来ラダー回路作成"""
        # テスト用AND回路: X001 AND X002 -> Y001
        line1 = LadderLine()
        line1.add_element(ContactA("X001"))
        line1.add_element(ContactA("X002"))
        line1.add_element(Coil("Y001"))
        self.ladder_program.add_line(line1)
        
        # テスト用タイマー回路: X003 -> T001(3秒) -> Y002
        line2 = LadderLine()
        line2.add_element(ContactA("X003"))
        line2.add_element(Timer("T001", 3.0))
        line2.add_element(Coil("Y002"))
        self.ladder_program.add_line(line2)
        
        # テスト用カウンター回路: X004 -> C001(3回) -> Y003
        line3 = LadderLine()
        line3.add_element(ContactA("X004"))
        line3.add_element(Counter("C001", 3))
        line3.add_element(Coil("Y003"))
        self.ladder_program.add_line(line3)
    
    def update(self):
        """メインアップデート処理"""
        # キーボード入力処理
        self._handle_keyboard_input()
        
        # マウス入力処理
        selected_device = self.mouse_handler.handle_mouse_input(self.grid_device_manager, self.device_manager)
        if selected_device is not None:
            self.selected_device_type = selected_device
        
        # システム状態更新
        self._update_systems()
        
        # 終了処理
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
    
    def _handle_keyboard_input(self):
        """キーボード入力処理"""
        # デバイス選択（1-8キー）
        for i in range(1, 9):
            if pyxel.btnp(getattr(pyxel, f"KEY_{i}")):
                if i - 1 < len(self.device_palette):
                    self.selected_device_type = self.device_palette[i - 1]["type"]
                    self.mouse_handler.selected_device_type = self.selected_device_type
        
        # デバイス操作（Shift+1-4キー）
        if pyxel.btn(pyxel.KEY_LSHIFT) or pyxel.btn(pyxel.KEY_RSHIFT):
            if pyxel.btnp(pyxel.KEY_1):
                device = self.device_manager.get_device("X001")
                device.value = not device.value
            elif pyxel.btnp(pyxel.KEY_2):
                device = self.device_manager.get_device("X002")
                device.value = not device.value
            elif pyxel.btnp(pyxel.KEY_3):
                device = self.device_manager.get_device("X003")
                device.value = not device.value
            elif pyxel.btnp(pyxel.KEY_4):
                device = self.device_manager.get_device("X004")
                device.value = not device.value
    
    def _update_systems(self):
        """システム状態更新"""
        # グリッドデバイス状態更新
        self.grid_device_manager.update_all_devices(self.device_manager)
        
        # 電気系統状態更新
        self.electrical_system.update_electrical_state()
        
        # 従来ラダープログラム実行
        self.ladder_program.scan_cycle(self.device_manager)
    
    def draw(self):
        """描画処理"""
        pyxel.cls(Colors.BLACK)
        
        # UI描画
        self.ui_renderer.draw_title()
        self.ui_renderer.draw_device_palette(self.selected_device_type, self.mouse_handler)
        self.ui_renderer.draw_device_grid(
            self.grid_device_manager, 
            self.electrical_system, 
            self.mouse_handler
        )
        
        # 従来ラダー図描画
        self.ui_renderer.draw_traditional_ladder(self.ladder_program)
    
    def run(self):
        """メインループ実行"""
        pyxel.run(self.update, self.draw)


def main():
    """メイン関数"""
    simulator = PLCSimulator()
    simulator.run()


if __name__ == "__main__":
    main()
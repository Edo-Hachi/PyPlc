"""
PyPlc Main Module - Refactored

モジュール化されたPLCシミュレーターのメインコーディネーター。
各機能モジュールを統合し、システム全体の制御を行う。
"""

import pyxel
from SpriteManager import sprite_manager

# モジュール化された各コンポーネントをインポート
from config import WIDTH, HEIGHT, Layout, Colors, DeviceType, SimulatorMode, PLCRunState
from grid_system import GridDeviceManager
from electrical_system import ElectricalSystem
from plc_logic import DeviceManager, LadderProgram, LadderLine, ContactA, ContactB, Coil, Timer, Counter
from ui_components import UIRenderer, MouseHandler
from pyxdlg import PyxDialog, InputType


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
            "DEL": sprite_manager.get_sprite_by_name_and_tag("DEL"),
            "CDEV_NML_ON": sprite_manager.get_sprite_by_name_and_tag("CDEV_NML_ON"),
            "CDEV_NML_OFF": sprite_manager.get_sprite_by_name_and_tag("CDEV_NML_OFF"),
            "CDEV_REV_ON": sprite_manager.get_sprite_by_name_and_tag("CDEV_REV_ON"),
            "CDEV_REV_OFF": sprite_manager.get_sprite_by_name_and_tag("CDEV_REV_OFF")
        }
    
    def _initialize_ui_systems(self):
        """UIシステム初期化"""
        # デバイスパレット定義（元のコード形式）
        self.device_palette = [
            {"type": DeviceType.TYPE_A, "name": "A Contact", "sprite": "TYPE_A_OFF"},
            {"type": DeviceType.TYPE_B, "name": "B Contact", "sprite": "TYPE_B_OFF"},
            {"type": DeviceType.COIL, "name": "Output Coil", "sprite": "CDEV_NML_OFF"},
            {"type": DeviceType.TIMER, "name": "Timer", "sprite": "TIMER_OFF"},
            {"type": DeviceType.LINK_UP, "name": "Link Up", "sprite": "LINK_UP"},
            {"type": DeviceType.LINK_DOWN, "name": "Link Down", "sprite": "LINK_DOWN"},
            {"type": DeviceType.DEL, "name": "Delete", "sprite": "DEL"}
        ]
        
        # 選択状態管理（元のコード形式）
        self.selected_device_type = DeviceType.TYPE_A
        
        # モード管理
        self.current_mode = SimulatorMode.EDIT
        
        # PLC実行状態管理
        self.plc_run_state = PLCRunState.STOPPED
        
        # ダイアログシステム初期化
        self.dialog = PyxDialog()
        
        # ステータスメッセージ管理
        self.status_message_timer = 0
        
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
        # グリッドAND回路: X001 → X002 → Y001 (左バスバーは自動)
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
        if self.current_mode == SimulatorMode.EDIT:
            mouse_result = self.mouse_handler.handle_mouse_input(self.grid_device_manager, self.device_manager)
            if mouse_result is not None:
                if isinstance(mouse_result, tuple) and mouse_result[0] == "DEVICE_CONFIG":
                    # デバイス設定ダイアログを表示
                    _, device = mouse_result
                    self._show_device_config_dialog(device)
                else:
                    # デバイスタイプ選択
                    self.selected_device_type = mouse_result
        elif self.current_mode == SimulatorMode.RUN:
            # RUNモードでは右クリックでデバイス操作
            mouse_result = self.mouse_handler.handle_run_mode_input(self.grid_device_manager, self.device_manager)
            if mouse_result is not None:
                if isinstance(mouse_result, tuple) and mouse_result[0] == "DEVICE_OPERATION":
                    # デバイス操作処理
                    _, device = mouse_result
                    self._handle_run_mode_device_operation(device)
            # RUNモードではマウスプレビューをクリア
            self.mouse_handler.show_preview = False
        
        # システム状態更新
        self._update_systems()
        
        # 終了処理
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
    
    def _handle_keyboard_input(self):
        """キーボード入力処理"""
        # モード切り替え（TABキー）
        if pyxel.btnp(pyxel.KEY_TAB):
            if self.current_mode == SimulatorMode.EDIT:
                self.current_mode = SimulatorMode.RUN
            elif self.current_mode == SimulatorMode.RUN:
                self.current_mode = SimulatorMode.EDIT
        
        # PLC実行制御（F5キー - RUNモードのみ）
        if pyxel.btnp(pyxel.KEY_F5) and self.current_mode == SimulatorMode.RUN:
            if self.plc_run_state == PLCRunState.STOPPED:
                self.plc_run_state = PLCRunState.RUNNING
            else:
                self.plc_run_state = PLCRunState.STOPPED
        
        # EDITモードでのデバイス選択（1-7キー）
        if self.current_mode == SimulatorMode.EDIT:
            for i in range(1, 8):
                if pyxel.btnp(getattr(pyxel, f"KEY_{i}")):
                    if i - 1 < len(self.device_palette):
                        self.selected_device_type = self.device_palette[i - 1]["type"]
                        self.mouse_handler.selected_device_type = self.selected_device_type
        
        # RUNモードまたはデバイス操作（Shift+1-4キー）
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
        # PLC実行中の場合のみ論理処理を実行
        if self.plc_run_state == PLCRunState.RUNNING:
            # グリッドデバイス状態更新
            self.grid_device_manager.update_all_devices(self.device_manager)
            
            # 電気系統状態更新
            self.electrical_system.update_electrical_state()
            
            # コイル状態とY接点デバイスの自動連動
            self.electrical_system.synchronize_coil_to_device(self.device_manager)
            
            # 従来ラダープログラム実行
            self.ladder_program.scan_cycle(self.device_manager)
        else:
            # 停止中でも電気系統の表示は更新（入力変更の反映のため）
            self.electrical_system.update_electrical_state()
            # 停止中でもコイル→Y接点連動は実行（表示更新のため）
            self.electrical_system.synchronize_coil_to_device(self.device_manager)
    
    def _show_device_config_dialog(self, device):
        """デバイス設定ダイアログを表示"""
        # 現在のデバイスアドレスを初期値として設定
        current_address = device.device_address if device.device_address else ""
        
        # デバイス設定ダイアログを表示
        success, new_address = self.dialog.input_text_dialog(
            "Device Settings",
            f"Device Address for {device.device_type.value}:",
            current_address,
            InputType.DEVICE_ADDRESS
        )
        
        if success and new_address and new_address != current_address:
            # 新しいアドレスを設定
            device.device_address = new_address.upper()
            
            # デバイスマネージャーにも登録
            if not self.device_manager.get_device(new_address):
                # 新しいデバイスとして登録
                self.device_manager.set_device_value(new_address, False)
            
            # 古いアドレスがあれば削除（必要に応じて）
            if current_address and current_address != new_address:
                # 古いアドレスの削除は他で使用されている可能性があるため慎重に行う
                pass
    
    def _handle_run_mode_device_operation(self, device):
        """RUNモードでのデバイス操作処理"""
        if device.device_type == DeviceType.TYPE_A:
            # A接点：ON/OFF切り替え
            if device.device_address:
                plc_device = self.device_manager.get_device(device.device_address)
                if plc_device:
                    plc_device.value = not plc_device.value
                    # ステータスメッセージで状態を表示
                    state = "ON" if plc_device.value else "OFF"
                    self.ui_renderer.status_message = f"{device.device_address}: {state}"
                    self.status_message_timer = 120  # 2秒間表示（60FPS想定）
        
        elif device.device_type == DeviceType.TYPE_B:
            # B接点：PLCブレイク（実行停止）
            if self.plc_run_state == PLCRunState.RUNNING:
                self.plc_run_state = PLCRunState.STOPPED
                self.ui_renderer.status_message = f"PLC BREAK at {device.device_address or 'B Contact'}"
                self.status_message_timer = 180  # 3秒間表示
            else:
                # 停止中の場合は再開
                self.plc_run_state = PLCRunState.RUNNING
                self.ui_renderer.status_message = f"PLC RESUME from {device.device_address or 'B Contact'}"
                self.status_message_timer = 180  # 3秒間表示
    
    def draw(self):
        """描画処理"""
        pyxel.cls(Colors.BLACK)
        
        # ステータスメッセージ管理
        if self.status_message_timer > 0:
            self.status_message_timer -= 1
        else:
            # タイマー終了時にメッセージをクリア
            self.ui_renderer.clear_status_message()
        
        # UI描画
        #self.ui_renderer.draw_title()
        self.ui_renderer.draw_device_palette(self.selected_device_type, self.mouse_handler)
        self.ui_renderer.draw_device_grid(
            self.grid_device_manager, 
            self.electrical_system, 
            self.mouse_handler
        )
        
        # 従来ラダー図描画
        self.ui_renderer.draw_traditional_ladder(self.ladder_program)
        
        # ステータスバー描画（最後に描画）
        self.ui_renderer.draw_status_bar(self.current_mode, self.plc_run_state)
    
    def run(self):
        """メインループ実行"""
        pyxel.run(self.update, self.draw)


def main():
    """メイン関数"""
    simulator = PLCSimulator()
    simulator.run()


if __name__ == "__main__":
    main()
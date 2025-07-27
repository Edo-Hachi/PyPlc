"""
PyPlc Main Module - Refactored

モジュール化されたPLCシミュレーターのメインコーディネーター。
各機能モジュールを統合し、システム全体の制御を行う。
"""

# TODO
# Runモードで、F5＞start  から F5>ストップになった時は給電を止めて、デバイスを初期状態に戻したい
# RUNモード実行中でインプットコイル（名前は Y01とつけた）に通電し、ONになった時。同じ名前をつけられたアウトプットコイルが連動するようにしてほしい。
# ーーー
# Y01のインプットコイルがONになればアウトプットコイルもONになる。電源が落ちれば、当然両方とも初期化される
# Y01のインプットコイルがONになり、同名のリバースタイプのアウトプットコイルがあるのなら、それはOFFになる。電源がオフになれば Y01の名前のリバースはOnに戻る
# ーーー
# こういった処理が、内部のデバイスオブジェクトで正常に反映されているのかもチェックしたい



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
        # デバッグログの初期化
        import logging
        debug_logger = logging.getLogger('PyPlc_Debug')
        debug_logger.debug("=== PyPlc Simulator Started ===")
        debug_logger.debug("Debug logging system initialized")
        
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
            "TIMER_STANBY": sprite_manager.get_sprite_by_name_and_tag("TIMER_STANBY"),
            "TIMER_CNTUP": sprite_manager.get_sprite_by_name_and_tag("TIMER_CNTUP"),
            "TIMER_ON": sprite_manager.get_sprite_by_name_and_tag("TIMER_ON"),
            "COUNTER_ON": sprite_manager.get_sprite_by_name_and_tag("COUNTER_ON"),
            "COUNTER_OFF": sprite_manager.get_sprite_by_name_and_tag("COUNTER_OFF"),
            "LINK_UP": sprite_manager.get_sprite_by_name_and_tag("LINK_UP"),
            "LINK_DOWN": sprite_manager.get_sprite_by_name_and_tag("LINK_DOWN"),
            "DEL": sprite_manager.get_sprite_by_name_and_tag("DEL"),
            "INCOIL_ON": sprite_manager.get_sprite_by_name_and_tag("INCOIL_ON"),
            "INCOIL_OFF": sprite_manager.get_sprite_by_name_and_tag("INCOIL_OFF"),
            "OUTCOIL_NML_ON": sprite_manager.get_sprite_by_name_and_tag("OUTCOIL_NML_ON"),
            "OUTCOIL_NML_OFF": sprite_manager.get_sprite_by_name_and_tag("OUTCOIL_NML_OFF"),
            "OUTCOIL_REV_ON": sprite_manager.get_sprite_by_name_and_tag("OUTCOIL_REV_ON"),
            "OUTCOIL_REV_OFF": sprite_manager.get_sprite_by_name_and_tag("OUTCOIL_REV_OFF"),
            "H_LINE_ON": sprite_manager.get_sprite_by_name_and_tag("H_LINE_ON"),
            "H_LINE_OFF": sprite_manager.get_sprite_by_name_and_tag("H_LINE_OFF"),
            "V_LINE_ON": sprite_manager.get_sprite_by_name_and_tag("V_LINE_ON"),
            "V_LINE_OFF": sprite_manager.get_sprite_by_name_and_tag("V_LINE_OFF")
        }
    
    def _initialize_ui_systems(self):
        """UIシステム初期化"""
        # デバイスパレット定義（元のコード形式）
        self.device_palette = [
            {"type": DeviceType.TYPE_A, "name": "A Contact", "sprite": "TYPE_A_OFF"},
            {"type": DeviceType.TYPE_B, "name": "B Contact", "sprite": "TYPE_B_OFF"},
            {"type": DeviceType.INCOIL, "name": "Input Coil", "sprite": "INCOIL_OFF"},
            {"type": DeviceType.COIL, "name": "Output Coil", "sprite": "OUTCOIL_NML_OFF"},
            {"type": DeviceType.OUTCOIL_REV, "name": "Rev Output", "sprite": "OUTCOIL_REV_OFF"},
            {"type": DeviceType.TIMER, "name": "Timer", "sprite": "TIMER_STANBY"},
            {"type": DeviceType.COUNTER, "name": "Counter", "sprite": "COUNTER_OFF"},
            {"type": DeviceType.WIRE_H, "name": "Wire H", "sprite": "H_LINE_OFF"},
            {"type": DeviceType.WIRE_V, "name": "Wire V", "sprite": "V_LINE_OFF"},
            {"type": DeviceType.LINK_UP, "name": "Link Up", "sprite": "LINK_UP"},
            {"type": DeviceType.LINK_DOWN, "name": "Link Down", "sprite": "LINK_DOWN"},
            {"type": DeviceType.DEL, "name": "Delete", "sprite": "DEL"}
        ]
        
        # 選択状態管理（元のコード形式）
        self.selected_device_type = DeviceType.TYPE_A
        
        # 3段デバイスパレット管理
        self.palette_row = 0  # 0=上段, 1=中段, 2=下段
        self.selected_device_index = 0  # 1-0キーに対応する0-9のインデックス
        
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
        # 現在はテスト用デバイス配置なし - ユーザーが自由に構築
        pass
    
    def update(self):
        """メインアップデート処理"""
        # キーボード入力処理
        self._handle_keyboard_input()
        
        # マウス入力処理
        if self.current_mode == SimulatorMode.EDIT:
            mouse_result = self.mouse_handler.handle_mouse_input(self.grid_device_manager, self.device_manager)
            if mouse_result is not None:
                if isinstance(mouse_result, tuple):
                    if mouse_result[0] == "DEVICE_CONFIG":
                        # デバイス設定ダイアログを表示
                        _, device = mouse_result
                        self._show_device_config_dialog(device)
                    else:
                        # デバイスタイプとインデックス選択
                        device_type, device_index = mouse_result
                        self.selected_device_type = device_type
                        self.selected_device_index = device_index
                        # マウス選択時はアクティブエリアも更新
                        self.palette_row = device_index // 5  # 0-4は上段(0), 5-9は中段(1), 10-14は下段(2)
                else:
                    # 従来の単一値の場合（後方互換性）
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
                # STOPする際は全デバイスを初期状態にリセット
                self.plc_run_state = PLCRunState.STOPPED
                self._reset_all_systems()
        
        # EDITモードでのデバイス選択（シフトキー切り替え方式）
        if self.current_mode == SimulatorMode.EDIT:
            # シフトキー押下でアクティブエリア切り替え（上段→中段→下段→上段...）
            if pyxel.btnp(pyxel.KEY_LSHIFT) or pyxel.btnp(pyxel.KEY_RSHIFT):
                self.palette_row = (self.palette_row + 1) % 3  # 0→1→2→0切り替え
            
            # 1-5キーでアクティブエリアのデバイス選択
            for i in range(1, 6):  # 1-5キー
                if pyxel.btnp(getattr(pyxel, f"KEY_{i}")):
                    col_index = i - 1  # 0-4
                    device_index = self.palette_row * 5 + col_index  # 0-14
                    if device_index < len(self.device_palette):
                        self.selected_device_index = device_index
                        self.selected_device_type = self.device_palette[device_index]["type"]
                        self.mouse_handler.selected_device_type = self.selected_device_type
            
            # 0キーはアクティブエリアの5番目のデバイス
            if pyxel.btnp(pyxel.KEY_0):
                col_index = 4  # 5番目は列インデックス4
                device_index = self.palette_row * 5 + col_index
                if device_index < len(self.device_palette):
                    self.selected_device_index = device_index
                    self.selected_device_type = self.device_palette[device_index]["type"]
                    self.mouse_handler.selected_device_type = self.selected_device_type
        
    
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
            
            # 同名アドレスコイルの連動処理（Input→Output/Reverse連動）
            self.electrical_system.synchronize_same_address_coils(self.device_manager)
            
            # 従来ラダープログラム実行
            self.ladder_program.scan_cycle(self.device_manager)
        else:
            # 停止中は構造更新のみ実行（縦方向結線表示のため）
            # 電力フロー計算は実行しない（リセット状態を維持するため）
            self.electrical_system.update_structure_only()
            # 入力変更があった場合のみ、グリッドデバイス状態を更新
            self.grid_device_manager.update_all_devices(self.device_manager)
    
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
    
    def _reset_all_systems(self):
        """全システムを初期状態にリセット（F5ストップ時）"""
        # PLCデバイスリセット
        self.device_manager.reset_all_devices()
        
        # グリッドデバイスリセット
        self.grid_device_manager.reset_all_devices()
        
        # 電気系統リセット
        self.electrical_system.reset_electrical_state()
        
        # リセット後にスプライト状態を強制更新
        self.grid_device_manager.update_all_devices(self.device_manager)
        
        # ステータスメッセージ表示
        self.ui_renderer.status_message = "All devices reset to initial state"
        self.status_message_timer = 120  # 2秒間表示
    
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
        self.ui_renderer.draw_device_palette(self.selected_device_type, self.mouse_handler, 
                                            self.palette_row, self.selected_device_index)
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
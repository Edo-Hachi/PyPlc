# TODO

#スキャンタイムはを動的変更はPyPlc.jsonを変更すれば良いので、F8-F5 での変更はコメントアウトで良い

#メモで
# PLCスキャンタイム: F5-F8キーで可変
# F5: 50ms（3フレーム間隔）
# F6: 100ms（6フレーム間隔）
# F7: 200ms（12フレーム間隔）
# F8: 500ms（30フレーム間隔）
#これはコンフィグに残しておいてほしい

#<完了>Configでグリッドサイズを変更し、配列情報、エディタ画面が正常に動作するかテストする
#<完了>グリッドの描画処理が複雑じゃないか？
#<完了>マウスカーソルの動作をフリーな移動にしたい。グリッド近くに来たときだけ、スナップするような仕組みにしたい（しきい値5px以下とか）
#<完了>スキャンタイムを動的に変更したい（configで）デバッグ中とかそんなに速くなくても良い（実働時も30FPSで動いていたら上等）


# For Ai Support
# このコメントは消さないでください

## 実行環境は .vscode/ 以下のファイルに定義してあります

# 返答は日本語でお願いします
# pythonとはいえ、型はちゃんと宣言してください
# コメントも日本語でつけて下さい
# ステップバイステップで作業をしながら git にチェックインしながらすすめるので、ユーザーに都度確認してください。
# ですので、ドンドンとコードを書いて進めないで下さい

#配列関係の処理をする時は  grid[row][col]  # [y座標][x座標] の順序 って書いておいてくれると、僕がわかりやすいです　

# Caution!
# Ver1のシステムでは、内部データと表示データの齟齬があり、混乱が発生しました。
# 今回は、まず、内部データをViewportに正確に表示できるか、徹底的にテストしましょう


import pyxel
from typing import Optional

# Import modules / モジュールインポート
from core.constants import DeviceType, GridConstraints, Layout, DeviceAddressRanges, AppConstants
from core.config_manager import PyPlcConfigManager, PyPlcConfig
from core.data_manager import PyPlcDataManager, CircuitData, DeviceData
from core.grid_manager import GridDeviceManager
from core.logic_element import LogicElement
from core.renderer import PyPlcRenderer
from core.input_handler import PyPlcInputHandler, MouseState
from core.plc_controller import PyPlcController, PlcScanState
from core.placement_system import PlacementSystem

# アプリケーション定数はcore/constants.pyに移動済み
# 描画関連の定数はcore/renderer.pyに移動済み

class PyPlcSimulator:
    def __init__(self):
        # Initialize configuration manager / 設定管理システム初期化
        self.config_manager = PyPlcConfigManager()
        self.config = self.config_manager.get_config()
        
        # Initialize data manager / データ管理システム初期化
        self.data_manager = PyPlcDataManager()
        
        # Initialize Pyxel / Pyxel初期化
        pyxel.init(
            self.config.window_width, 
            self.config.window_height, 
            title="PyPlc-v2 - PLC Ladder Simulator",
            fps=AppConstants.TARGET_FPS
        )
        
        # Show mouse cursor / マウスカーソル表示
        pyxel.mouse(True)
        
        # Initialize grid manager / グリッドマネージャー初期化
        self.grid_manager = GridDeviceManager(self.config)
        
        # Initialize renderer / レンダラー初期化
        self.renderer = PyPlcRenderer(self.config)
        
        # Initialize input handler / 入力ハンドラー初期化
        self.input_handler = PyPlcInputHandler(self.config)
        
        # Initialize PLC controller / PLCコントローラー初期化
        self.plc_controller = PyPlcController(self.config, AppConstants.TARGET_FPS)
        
        # Initialize placement system / 配置システム初期化
        self.placement_system = PlacementSystem(self.config)
        
        # Initialize mouse state / マウス状態初期化
        self.mouse_grid_pos = None  # マウスのグリッド座標
        self.show_cursor = False    # カーソル表示フラグ
        self.snap_mode = False      # スナップモード（CTRL押下時）
        
        # Setup test circuit using data manager / データ管理システムを使用したテスト回路セットアップ
        # self.data_manager.setup_circuit_on_grid(self.grid_manager)  # パレットテスト用に無効化
        
        pyxel.run(self.update, self.draw)
    
    def update(self) -> None:
        # Get key input state / キー入力状態取得
        key_input = self.input_handler.get_key_input()
        
        # Handle quit / 終了処理
        if key_input['quit']:
            pyxel.quit()
        
        # PLC scan time control / PLCスキャンタイム制御
        if key_input['scan_time_f5']:
            self.plc_controller.set_scan_time(50)   # 高速スキャン（50ms）
        elif key_input['scan_time_f6']:
            self.plc_controller.set_scan_time(100)  # 標準スキャン（100ms）
        elif key_input['scan_time_f7']:
            self.plc_controller.set_scan_time(200)  # 低速スキャン（200ms）
        elif key_input['scan_time_f8']:
            self.plc_controller.set_scan_time(500)  # 超低速スキャン（500ms）
        
        # Update mouse state / マウス状態更新
        mouse_state = self.input_handler.update_mouse_state()
        self.mouse_grid_pos = mouse_state.grid_pos
        self.show_cursor = mouse_state.show_cursor
        self.snap_mode = mouse_state.snap_mode
        
        # Update placement system / 配置システム更新
        self.placement_system.update()
        
        # PLC scan time control / PLCスキャンタイム制御
        current_frame = pyxel.frame_count
        self.plc_controller.update_scan_cycle(current_frame, self.grid_manager)
        
        # Test device interaction / テストデバイス操作（整合性テスト用）
        if key_input['toggle_device_1']:
            # Toggle X001 state at (5,5) / (5,5)のX001状態切り替え
            contact = self.grid_manager.get_device(5, 5)
            if contact:
                contact.active = not contact.active
                print(f"X001 state changed to: {contact.active}")  # デバッグ出力
        
        # 他のキー操作はコメントアウト
        # if pyxel.btnp(pyxel.KEY_2):
        #     # Toggle X002 state / X002状態切り替え
        #     contact = self.grid_manager.get_device(2, 4)
        #     if contact:
        #         contact.active = not contact.active
    
    # 入力系メソッドはcore/input_handler.pyに移動済み
    # PLCロジック系メソッドはcore/plc_controller.pyに移動済み
    

    
    def draw(self) -> None:
        pyxel.cls(pyxel.COLOR_BLACK)
        
        # Draw placement system (device palette) / 配置システム描画（デバイスパレット）
        self.placement_system.draw(self.renderer)
        
        # Draw grid / グリッド描画
        self.renderer.draw_grid()
        
        # Draw devices / デバイス描画
        self.renderer.draw_devices(self.grid_manager)
        
        # Draw device information / デバイス情報描画
        self.renderer.draw_device_info(self.grid_manager)
        
        # Draw mouse cursor / マウスカーソル描画
        self.renderer.draw_mouse_cursor(self.mouse_grid_pos, self.show_cursor)
        
        # Draw control information / 操作情報描画
        self.renderer.draw_controls()
        
        # Draw status bar with mouse position / マウス位置情報を含むステータスバー描画
        self.renderer.draw_status_bar(self.mouse_grid_pos, self.snap_mode, self.input_handler.is_editable_position)
    


if __name__ == "__main__":
    PyPlcSimulator()
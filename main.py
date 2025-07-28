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
from typing import List
from config import PyPlcConfig, DeviceType, Layout
from core.grid_manager import GridDeviceManager
from core.logic_element import LogicElement
from core.renderer import PyPlcRenderer

# アプリケーション定数 / Application Constants
class AppConstants:
    """アプリケーション全体の定数定義"""
    TARGET_FPS = 60           # 目標フレームレート（60FPS固定）

# 描画関連の定数はcore/renderer.pyに移動済み

class PyPlcSimulator:
    def __init__(self):
        # Load configuration / 設定読み込み
        self.config = PyPlcConfig.load_from_file()
        
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
        
        # Initialize mouse state / マウス状態初期化
        self.mouse_grid_pos = None  # マウスのグリッド座標
        self.show_cursor = False    # カーソル表示フラグ
        self.snap_mode = False      # スナップモード（CTRL押下時）
        
        # Initialize PLC scan time management / PLCスキャンタイム管理初期化
        self.last_scan_time = pyxel.frame_count  # 最後のスキャン実行時刻
        self.scan_interval_frames = int(self.config.scan_time_ms * AppConstants.TARGET_FPS / 1000)  # スキャン間隔
        
        # Test: Place some devices / テスト：いくつかのデバイス配置
        self._setup_test_circuit()
        
        pyxel.run(self.update, self.draw)
    
    def _setup_test_circuit(self) -> None:
        """Setup test circuit / テスト回路セットアップ"""
        # 内部データと表示データの整合性テスト用
        # Test data: A接点を(5,5)に配置 - データと表示の一致確認（編集可能エリア内）
        result = self.grid_manager.place_device(5, 5, DeviceType.CONTACT_A, "X001")
        print(f"Device placement result: {result}")
        print(f"Total devices: {len(self.grid_manager.get_all_devices())}")
        
        # デバイス確認
        device = self.grid_manager.get_device(5, 5)
        if device:
            print(f"Found device at (5,5): {device}")
        else:
            print("No device found at (5,5)")
        
        # 他のテストデータはコメントアウト
        # # Place B contact at (2, 4) / B接点を(2,4)に配置
        # self.grid_manager.place_device(2, 4, DeviceType.CONTACT_B, "X002")
        # 
        # # Place output coil at (2, 7) / 出力コイルを(2,7)に配置
        # self.grid_manager.place_device(2, 7, DeviceType.COIL, "Y001")
        # 
        # # Place timer at (4, 3) / タイマーを(4,3)に配置
        # self.grid_manager.place_device(4, 3, DeviceType.TIMER, "T001")
    
    def update(self) -> None:
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        

        # PLC scan time control / PLCスキャンタイム制御
        if pyxel.btnp(pyxel.KEY_F5):
            self._set_scan_time(50)   # 高速スキャン（50ms）
        elif pyxel.btnp(pyxel.KEY_F6):
            self._set_scan_time(100)  # 標準スキャン（100ms）
        elif pyxel.btnp(pyxel.KEY_F7):
            self._set_scan_time(200)  # 低速スキャン（200ms）
        elif pyxel.btnp(pyxel.KEY_F8):
            self._set_scan_time(500)  # 超低速スキャン（500ms）
        
        # Update mouse state / マウス状態更新
        self._update_mouse()
        
        # PLC scan time control / PLCスキャンタイム制御
        current_frame = pyxel.frame_count
        if current_frame - self.last_scan_time >= self.scan_interval_frames:
            self._execute_plc_scan()
            self.last_scan_time = current_frame
        
        # Test device interaction / テストデバイス操作（整合性テスト用）
        if pyxel.btnp(pyxel.KEY_1):
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
    
    def _update_mouse(self) -> None:
        """Update mouse state / マウス状態更新"""
        # CTRLキー状態チェック
        self.snap_mode = pyxel.btn(pyxel.KEY_CTRL)
        
        mouse_x = pyxel.mouse_x
        mouse_y = pyxel.mouse_y
        
        # Convert screen coordinates to grid coordinates / スクリーン座標をグリッド座標に変換
        grid_pos = self._screen_to_grid(mouse_x, mouse_y)
        
        if grid_pos and self._is_editable_position(grid_pos[0], grid_pos[1]):
            self.mouse_grid_pos = grid_pos
            self.show_cursor = self.snap_mode  # スナップモード時のみ表示
        else:
            self.mouse_grid_pos = None
            self.show_cursor = False
    
    def _old_screen_to_grid(self, screen_x: int, screen_y: int) -> tuple[int, int] | None:
        """Convert screen coordinates to grid coordinates (Original version) / スクリーン座標をグリッド座標に変換（旧版）"""
        grid_x = self.config.grid_origin_x
        grid_y = self.config.grid_origin_y
        cell_size = self.config.grid_cell_size
        
        # Check if mouse is within grid bounds / マウスがグリッド範囲内かチェック
        if (grid_x <= screen_x <= grid_x + self.config.grid_cols * cell_size and
            grid_y <= screen_y <= grid_y + self.config.grid_rows * cell_size):
            
            # Calculate nearest grid intersection / 最も近いグリッド交点を計算
            col = round((screen_x - grid_x) / cell_size)
            row = round((screen_y - grid_y) / cell_size)
            
            # Ensure within valid range / 有効範囲内かチェック
            if 0 <= row < self.config.grid_rows and 0 <= col < self.config.grid_cols:
                return (row, col)  # grid[row][col] # [y座標][x座標] の順序
        
        return None
    
    def _screen_to_grid(self, screen_x: int, screen_y: int) -> tuple[int, int] | None:
        """Convert screen coordinates to grid coordinates (Optimized: O(1) nearest neighbor) / スクリーン座標をグリッド座標に変換（最適化版：O(1)最近隣計算）"""
        if not self.snap_mode:
            # 通常モード: グリッド範囲外では何も返さない
            return None
        
        grid_x = self.config.grid_origin_x
        grid_y = self.config.grid_origin_y
        cell_size = self.config.grid_cell_size
        
        # 最も近いグリッド交点を数学的に直接計算（O(1)）
        nearest_col = round((screen_x - grid_x) / cell_size)
        nearest_row = round((screen_y - grid_y) / cell_size)
        
        # グリッド範囲内チェック
        if not (0 <= nearest_row < self.config.grid_rows and 0 <= nearest_col < self.config.grid_cols):
            return None
        
        # 最近隣交点との距離をチェック（平方根計算を回避して高速化）
        intersection_x = grid_x + nearest_col * cell_size
        intersection_y = grid_y + nearest_row * cell_size
        
        # 平方根計算を避けて二乗比較で高速化（2-3倍高速）
        distance_squared = (screen_x - intersection_x) ** 2 + (screen_y - intersection_y) ** 2
        threshold_squared = self.config.snap_threshold ** 2
        
        if distance_squared < threshold_squared:
            return (nearest_row, nearest_col)  # grid[row][col] # [y座標][x座標] の順序
        
        return None
    
    def _execute_plc_scan(self) -> None:
        """Execute PLC scan cycle / PLCスキャンサイクル実行"""
        # PLC logic execution would go here / PLCロジック実行処理をここに記述
        # For now, just update device states / 現在はデバイス状態更新のみ
        
        # Example: Update all devices based on their logic / 例：全デバイスをロジックに基づいて更新
        for device in self.grid_manager.get_all_devices():
            if not device.is_bus_device():
                # Placeholder for actual PLC logic / 実際のPLCロジックのプレースホルダー
                pass
        
        # Debug output for scan execution / スキャン実行のデバッグ出力
        # print(f"PLC scan executed at frame {pyxel.frame_count}")
    
    def _set_scan_time(self, scan_time_ms: int) -> None:
        """Set PLC scan time dynamically / PLCスキャンタイムを動的に設定"""
        self.config.scan_time_ms = scan_time_ms
        # Recalculate scan interval in frames / スキャン間隔をフレーム数で再計算
        # Use defined FPS constant / 定義されたFPS定数を使用
        self.scan_interval_frames = int(scan_time_ms * AppConstants.TARGET_FPS / 1000)
        print(f"PLC scan time changed to {scan_time_ms}ms ({self.scan_interval_frames} frames)")
    
    def _is_editable_position(self, row: int, col: int) -> bool:
        """Check if position is editable / 位置が編集可能かチェック"""
        # 列0（左バス）と列終端）は編集不可
        return 1 <= col <= self.config.grid_cols - 2
    
    def draw(self) -> None:
        pyxel.cls(pyxel.COLOR_BLACK)
        
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
        self.renderer.draw_status_bar(self.mouse_grid_pos, self.snap_mode, self._is_editable_position)
    


if __name__ == "__main__":
    PyPlcSimulator()
# For Ai Support
# このコメントは消さないでください
# 実行環境は .vscode/ 以下のファイルに定義してあります
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
from config import PyPlcConfig, DeviceType, Layout
from core.grid_manager import GridDeviceManager
from core.logic_element import LogicElement

class PyPlcSimulator:
    def __init__(self):
        # Load configuration / 設定読み込み
        self.config = PyPlcConfig.load_from_file()
        
        # Initialize Pyxel / Pyxel初期化
        pyxel.init(
            self.config.window_width, 
            self.config.window_height, 
            title="PyPlc-v2 - PLC Ladder Simulator"
        )
        
        # Initialize grid manager / グリッドマネージャー初期化
        self.grid_manager = GridDeviceManager(self.config)
        
        # Test: Place some devices / テスト：いくつかのデバイス配置
        self._setup_test_circuit()
        
        pyxel.run(self.update, self.draw)
    
    def _setup_test_circuit(self) -> None:
        """Setup test circuit / テスト回路セットアップ"""
        # 内部データと表示データの整合性テスト用
        # Test data: A接点を(1,1)に配置 - データと表示の一致確認（列0はバス専用のため1に変更）
        result = self.grid_manager.place_device(1, 1, DeviceType.CONTACT_A, "X001")
        print(f"Device placement result: {result}")
        print(f"Total devices: {len(self.grid_manager.get_all_devices())}")
        
        # デバイス確認
        device = self.grid_manager.get_device(1, 1)
        if device:
            print(f"Found device at (1,1): {device}")
        else:
            print("No device found at (1,1)")
        
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
        
        # Test device interaction / テストデバイス操作（整合性テスト用）
        if pyxel.btnp(pyxel.KEY_1):
            # Toggle X001 state at (1,1) / (1,1)のX001状態切り替え
            contact = self.grid_manager.get_device(1, 1)
            if contact:
                contact.active = not contact.active
                print(f"X001 state changed to: {contact.active}")  # デバッグ出力
        
        # 他のキー操作はコメントアウト
        # if pyxel.btnp(pyxel.KEY_2):
        #     # Toggle X002 state / X002状態切り替え
        #     contact = self.grid_manager.get_device(2, 4)
        #     if contact:
        #         contact.active = not contact.active
    
    def draw(self) -> None:
        pyxel.cls(pyxel.COLOR_BLACK)
        
        # Draw title / タイトル描画
        pyxel.text(10, 8, "PyPlc-v2 - Ladder Simulator", pyxel.COLOR_WHITE)
        
        # Draw grid / グリッド描画
        self._draw_grid()
        
        # Draw devices / デバイス描画
        self._draw_devices()
        
        # Draw device info / デバイス情報描画
        self._draw_device_info()
        
        # Draw controls / 操作説明描画
        self._draw_controls()
    
    def _draw_grid(self) -> None:
        """Draw grid lines / グリッド線描画（交点ベース）"""
        grid_x = self.config.grid_origin_x
        grid_y = self.config.grid_origin_y
        cell_size = self.config.grid_cell_size
        
        # Draw vertical lines (blue) / 縦線描画（青色）
        for col in range(self.config.grid_cols + 1):
            x = grid_x + col * cell_size
            pyxel.line(x, grid_y, x, grid_y + self.config.grid_rows * cell_size, pyxel.COLOR_DARK_BLUE)
        
        # Draw horizontal lines (blue) / 横線描画（青色）
        for row in range(self.config.grid_rows + 1):
            y = grid_y + row * cell_size
            pyxel.line(grid_x, y, grid_x + self.config.grid_cols * cell_size, y, pyxel.COLOR_DARK_BLUE)
        
        # Draw left bus line (orange) / 左バスライン描画（オレンジ色）
        left_bus_x = grid_x
        pyxel.line(left_bus_x, grid_y, left_bus_x, grid_y + self.config.grid_rows * cell_size, pyxel.COLOR_YELLOW)  # オレンジの代用
        
        # Draw right bus line (gray) / 右バスライン描画（グレー）
        right_bus_x = grid_x + self.config.grid_cols * cell_size
        pyxel.line(right_bus_x, grid_y, right_bus_x, grid_y + self.config.grid_rows * cell_size, pyxel.COLOR_GRAY)
    
    def _draw_devices(self) -> None:
        """Draw all devices / 全デバイス描画（交点ベース）"""
        grid_x = self.config.grid_origin_x
        grid_y = self.config.grid_origin_y
        cell_size = self.config.grid_cell_size
        
        all_devices = self.grid_manager.get_all_devices()
        print(f"Drawing {len(all_devices)} devices")  # デバッグ出力
        
        for device in all_devices:
            # バスデバイスはスキップ（グリッドラインで表現済み）
            if device.is_bus_device():
                print(f"Skipping bus device: {device.name}")  # デバッグ出力
                continue
            
            print(f"Drawing device: {device.name} at ({device.grid_row}, {device.grid_col})")  # デバッグ出力
            
            # 交点座標計算（グリッドライン交差点）
            intersection_x = grid_x + device.grid_col * cell_size
            intersection_y = grid_y + device.grid_row * cell_size
            
            # 8x8ピクセルのrectを交点中央に配置
            device_x = intersection_x - 4  # 8x8の中央なので-4
            device_y = intersection_y - 4
            
            print(f"Device position: intersection({intersection_x}, {intersection_y}) -> rect({device_x}, {device_y})")  # デバッグ出力
            
            # デバイス状態に基づく色選択
            color = pyxel.COLOR_GREEN if device.active else pyxel.COLOR_GRAY
            print(f"Device color: {color} (active: {device.active})")  # デバッグ出力
            
            # 8x8ピクセルのrectとして描画
            pyxel.rect(device_x, device_y, 8, 8, color)
            
            # デバイスシンボル描画（rect内中央）
            symbol_x = device_x + 2
            symbol_y = device_y + 2
            
            if device.device_type == DeviceType.CONTACT_A:
                pyxel.text(symbol_x, symbol_y, "A", pyxel.COLOR_WHITE)
            elif device.device_type == DeviceType.CONTACT_B:
                pyxel.text(symbol_x, symbol_y, "B", pyxel.COLOR_WHITE)
            elif device.device_type == DeviceType.COIL:
                pyxel.text(symbol_x, symbol_y, "O", pyxel.COLOR_WHITE)
            elif device.device_type == DeviceType.TIMER:
                pyxel.text(symbol_x, symbol_y, "T", pyxel.COLOR_WHITE)
            
            # デバイス名表示（rect下部）
            name_x = device_x - 4  # 名前を少し左にずらす
            name_y = device_y + 10  # rect下部
            pyxel.text(name_x, name_y, device.name, pyxel.COLOR_WHITE)
    
    def _draw_device_info(self) -> None:
        """Draw device information / デバイス情報描画"""
        info_y = self.config.status_area_y
        
        pyxel.text(10, info_y, "Device Status:", pyxel.COLOR_WHITE)
        
        # List key devices / 主要デバイスリスト表示
        y_offset = 0
        for device in self.grid_manager.get_all_devices():
            if not device.is_bus_device():
                status = "ON" if device.active else "OFF"
                pyxel.text(10, info_y + 12 + y_offset, f"{device.name}: {status}", pyxel.COLOR_WHITE)
                y_offset += 10
                if y_offset > 20:  # Limit display / 表示制限
                    break
    
    def _draw_controls(self) -> None:
        """Draw control information / 操作情報描画"""
        control_y = self.config.control_info_y
        pyxel.text(10, control_y, "Test: 1-Toggle X001 at (1,1), Q-Quit", pyxel.COLOR_WHITE)

if __name__ == "__main__":
    PyPlcSimulator()
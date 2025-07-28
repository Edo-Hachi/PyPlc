# For Ai Support
# このコメントは消さないでください
# 実行環境は .vscode/ 以下のファイルに定義してあります
# 返答は日本語でお願いします
# pythonとはいえ、型はちゃんと宣言してください
# コメントも日本語でつけて下さい
# ステップバイステップで作業をしながら git にチェックインしながらすすめるので、ユーザーに都度確認してください。
# ですので、ドンドンとコードを書いて進めないで下さい


# Caution!
# Ver1のシステムでは、内部データと表示データの齟齬があり、混乱が発生しました。
# 今回は、まず、内部データをViewportに正確に表示できるか、徹底的にテストしましょう



import pyxel
from config import PyPlcConfig, DeviceType, Colors, Layout
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
        # Test data: A接点を(1,0)に配置 - データと表示の一致確認
        self.grid_manager.place_device(1, 0, DeviceType.CONTACT_A, "X001")
        
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
            # Toggle X001 state at (1,0) / (1,0)のX001状態切り替え
            contact = self.grid_manager.get_device(1, 0)
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
        pyxel.cls(Colors.BACKGROUND)
        
        # Draw title / タイトル描画
        pyxel.text(10, 8, "PyPlc-v2 - Ladder Simulator", Colors.TEXT)
        
        # Draw grid / グリッド描画
        self._draw_grid()
        
        # Draw devices / デバイス描画
        self._draw_devices()
        
        # Draw device info / デバイス情報描画
        self._draw_device_info()
        
        # Draw controls / 操作説明描画
        self._draw_controls()
    
    def _draw_grid(self) -> None:
        """Draw grid lines / グリッド線描画"""
        grid_x = self.config.grid_origin_x
        grid_y = self.config.grid_origin_y
        cell_size = self.config.grid_cell_size
        
        # Draw vertical lines / 縦線描画
        for col in range(self.config.grid_cols + 1):
            x = grid_x + col * cell_size
            pyxel.line(x, grid_y, x, grid_y + self.config.grid_rows * cell_size, Colors.GRID_LINE)
        
        # Draw horizontal lines / 横線描画
        for row in range(self.config.grid_rows + 1):
            y = grid_y + row * cell_size
            pyxel.line(grid_x, y, grid_x + self.config.grid_cols * cell_size, y, Colors.GRID_LINE)
    
    def _draw_devices(self) -> None:
        """Draw all devices / 全デバイス描画"""
        grid_x = self.config.grid_origin_x
        grid_y = self.config.grid_origin_y
        cell_size = self.config.grid_cell_size
        
        for device in self.grid_manager.get_all_devices():
            x = grid_x + device.grid_col * cell_size + 2
            y = grid_y + device.grid_row * cell_size + 2
            
            # Choose color based on device state / デバイス状態に基づく色選択
            if device.is_bus_device():
                color = Colors.POWER_ON if device.powered else Colors.POWER_OFF
                # Draw bus as thick line / バスを太線で描画
                if device.device_type == DeviceType.L_SIDE:
                    pyxel.rect(x, y, 2, cell_size - 4, color)
                else:  # R_SIDE
                    pyxel.rect(x + cell_size - 6, y, 2, cell_size - 4, color)
            else:
                color = Colors.POWER_ON if device.active else Colors.POWER_OFF
                # Draw device as rectangle / デバイスを矩形で描画
                pyxel.rect(x, y, cell_size - 4, cell_size - 4, color)
                
                # Draw device symbol / デバイスシンボル描画
                symbol_x = x + 2
                symbol_y = y + 2
                
                if device.device_type == DeviceType.CONTACT_A:
                    pyxel.text(symbol_x, symbol_y, "A", Colors.TEXT)
                elif device.device_type == DeviceType.CONTACT_B:
                    pyxel.text(symbol_x, symbol_y, "B", Colors.TEXT)
                elif device.device_type == DeviceType.COIL:
                    pyxel.text(symbol_x, symbol_y, "O", Colors.TEXT)
                elif device.device_type == DeviceType.TIMER:
                    pyxel.text(symbol_x, symbol_y, "T", Colors.TEXT)
    
    def _draw_device_info(self) -> None:
        """Draw device information / デバイス情報描画"""
        info_y = self.config.status_area_y
        
        pyxel.text(10, info_y, "Device Status:", Colors.TEXT)
        
        # List key devices / 主要デバイスリスト表示
        y_offset = 0
        for device in self.grid_manager.get_all_devices():
            if not device.is_bus_device():
                status = "ON" if device.active else "OFF"
                pyxel.text(10, info_y + 12 + y_offset, f"{device.name}: {status}", Colors.TEXT)
                y_offset += 10
                if y_offset > 20:  # Limit display / 表示制限
                    break
    
    def _draw_controls(self) -> None:
        """Draw control information / 操作情報描画"""
        control_y = self.config.control_info_y
        pyxel.text(10, control_y, "Test: 1-Toggle X001 at (1,0), Q-Quit", Colors.TEXT)

if __name__ == "__main__":
    PyPlcSimulator()
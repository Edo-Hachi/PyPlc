# TODO

#グリッドの描画処理が複雑じゃないか？

#スキャンタイムを動的に変更したい（configで）デバッグ中とかそんなに速くなくても良い（実働時も30FPSで動いていたら上等）
#マウスカーソルの動作をフリーな移動にしたい。グリッド近くに来たときだけ、スナップするような仕組みにしたい（しきい値5px以下とか）

#<完了>Configでグリッドサイズを変更し、配列情報、エディタ画面が正常に動作するかテストする


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

# 描画定数 / Drawing Constants
class DrawingConstants:
    """描画関連の定数定義"""
    DEVICE_SIZE = 8           # デバイス矩形サイズ
    DEVICE_HALF_SIZE = 4      # デバイス中央配置用オフセット
    SYMBOL_OFFSET = 2         # シンボル描画オフセット
    NAME_OFFSET_Y = 10        # 名前表示Y方向オフセット
    NAME_OFFSET_X = -4        # 名前表示X方向オフセット

# デバイスシンボルマッピング / Device Symbol Mapping
DEVICE_SYMBOLS = {
    DeviceType.CONTACT_A: "A",
    DeviceType.CONTACT_B: "B",
    DeviceType.COIL: "O",
    DeviceType.TIMER: "T"
}

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
        
        # Initialize mouse state / マウス状態初期化
        self.mouse_grid_pos = None  # マウスのグリッド座標
        self.show_cursor = False    # カーソル表示フラグ
        
        # Test: Place some devices / テスト：いくつかのデバイス配置
        self._setup_test_circuit()
        
        pyxel.run(self.update, self.draw)
    
    def _setup_test_circuit(self) -> None:
        """Setup test circuit / テスト回路セットアップ"""
        # 内部データと表示データの整合性テスト用
        # Test data: A接点を(5,10)に配置 - データと表示の一致確認
        result = self.grid_manager.place_device(5, 10, DeviceType.CONTACT_A, "X001")
        print(f"Device placement result: {result}")
        print(f"Total devices: {len(self.grid_manager.get_all_devices())}")
        
        # デバイス確認
        device = self.grid_manager.get_device(5, 10)
        if device:
            print(f"Found device at (5,10): {device}")
        else:
            print("No device found at (5,10)")
        
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
        
        # Update mouse state / マウス状態更新
        self._update_mouse()
        
        # Test device interaction / テストデバイス操作（整合性テスト用）
        if pyxel.btnp(pyxel.KEY_1):
            # Toggle X001 state at (5,10) / (5,10)のX001状態切り替え
            contact = self.grid_manager.get_device(5, 10)
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
        mouse_x = pyxel.mouse_x
        mouse_y = pyxel.mouse_y
        
        # Convert screen coordinates to grid coordinates / スクリーン座標をグリッド座標に変換
        grid_pos = self._screen_to_grid(mouse_x, mouse_y)
        
        if grid_pos and self._is_editable_position(grid_pos[0], grid_pos[1]):
            self.mouse_grid_pos = grid_pos
            self.show_cursor = True
        else:
            self.mouse_grid_pos = None
            self.show_cursor = False
    
    def _screen_to_grid(self, screen_x: int, screen_y: int) -> tuple[int, int] | None:
        """Convert screen coordinates to grid coordinates / スクリーン座標をグリッド座標に変換"""
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
    
    def _is_editable_position(self, row: int, col: int) -> bool:
        """Check if position is editable / 位置が編集可能かチェック"""
        # 列0（左バス）と列終端）は編集不可
        return 1 <= col <= self.config.grid_cols - 2
    
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
        
        # Draw mouse cursor / マウスカーソル描画
        self._draw_mouse_cursor()
        
        # Draw controls / 操作説明描画
        self._draw_controls()
        
        # Draw status bar / ステータスバー描画
        self._draw_status_bar()
    
    def _draw_grid(self) -> None:
        """Draw grid lines / グリッド線描画（交点ベース）"""
        grid_x = self.config.grid_origin_x
        grid_y = self.config.grid_origin_y
        cell_size = self.config.grid_cell_size
        
        # Draw vertical lines (blue) / 縦線描画（青色）
        # 右バス線（列9）がグリッドの右端になるよう、余分な線は描画しない
        for col in range(self.config.grid_cols):
            x = grid_x + col * cell_size
            # 縦線の終点を最終行（grid_rows-1）の位置に合わせ、下段のはみ出しを防ぐ
            pyxel.line(x, grid_y, x, grid_y + (self.config.grid_rows - 1) * cell_size, pyxel.COLOR_DARK_BLUE)
        
        # Draw horizontal lines (blue) / 横線描画（青色）
        # 右バス線の位置（最終列）まで描画し、はみ出しを防ぐ
        # 最終行（grid_rows-1）までの横線を描画し、下端の余分な線を削除
        for row in range(self.config.grid_rows):
            y = grid_y + row * cell_size
            # 終点を右バス線（grid_cols-1）の位置に合わせる
            pyxel.line(grid_x, y, grid_x + (self.config.grid_cols - 1) * cell_size, y, pyxel.COLOR_DARK_BLUE)
        
        # Draw left bus line (orange) / 左バスライン描画（オレンジ色）
        # 2px幅の太い線で描画、下端のはみ出しを防ぐ
        left_bus_x = grid_x
        pyxel.rect(left_bus_x, grid_y, 2, (self.config.grid_rows - 1) * cell_size, pyxel.COLOR_YELLOW)  # オレンジの代用
        
        # Draw right bus line (gray) / 右バスライン描画（グレー）
        # 右バスは最終列（grid_cols-1）の位置に2px幅で描画、下端のはみ出しを防ぐ
        right_bus_x = grid_x + (self.config.grid_cols - 1) * cell_size
        pyxel.rect(right_bus_x, grid_y, 2, (self.config.grid_rows - 1) * cell_size, pyxel.COLOR_GRAY)
    
    def _draw_devices(self) -> None:
        """Draw all devices / 全デバイス描画（交点ベース）"""
        drawable_devices = self._get_drawable_devices()
        
        for device in drawable_devices:
            self._draw_single_device(device)
    
    def _get_drawable_devices(self) -> List[LogicElement]:
        """Get devices that should be drawn / 描画対象デバイス取得"""
        return [device for device in self.grid_manager.get_all_devices() 
                if not device.is_bus_device()]
    
    def _draw_single_device(self, device: LogicElement) -> None:
        """Draw a single device / 単一デバイス描画"""
        device_rect = self._calculate_device_rect(device)
        color = self._get_device_color(device)
        symbol = self._get_device_symbol(device)
        
        # デバイス本体描画
        pyxel.rect(device_rect['x'], device_rect['y'], 
                  DrawingConstants.DEVICE_SIZE, DrawingConstants.DEVICE_SIZE, color)
        
        # シンボル・名前描画
        self._draw_device_symbol(device_rect, symbol)
        self._draw_device_name(device_rect, device.name)
    
    def _calculate_device_rect(self, device: LogicElement) -> dict:
        """Calculate device rectangle position / デバイス矩形位置計算"""
        # 交点座標計算（グリッドライン交差点）
        intersection_x = self.config.grid_origin_x + device.grid_col * self.config.grid_cell_size
        intersection_y = self.config.grid_origin_y + device.grid_row * self.config.grid_cell_size
        
        # デバイス矩形を交点中央に配置
        return {
            'x': intersection_x - DrawingConstants.DEVICE_HALF_SIZE,
            'y': intersection_y - DrawingConstants.DEVICE_HALF_SIZE,
            'center_x': intersection_x,
            'center_y': intersection_y
        }
    
    def _get_device_color(self, device: LogicElement) -> int:
        """Get device color based on state / デバイス状態に基づく色取得"""
        return pyxel.COLOR_GREEN if device.active else pyxel.COLOR_GRAY
    
    def _get_device_symbol(self, device: LogicElement) -> str:
        """Get device symbol / デバイスシンボル取得"""
        return DEVICE_SYMBOLS.get(device.device_type, "?")
    
    def _draw_device_symbol(self, device_rect: dict, symbol: str) -> None:
        """Draw device symbol / デバイスシンボル描画"""
        symbol_x = device_rect['x'] + DrawingConstants.SYMBOL_OFFSET
        symbol_y = device_rect['y'] + DrawingConstants.SYMBOL_OFFSET
        pyxel.text(symbol_x, symbol_y, symbol, pyxel.COLOR_WHITE)
    
    def _draw_device_name(self, device_rect: dict, name: str) -> None:
        """Draw device name / デバイス名描画"""
        name_x = device_rect['x'] + DrawingConstants.NAME_OFFSET_X
        name_y = device_rect['y'] + DrawingConstants.NAME_OFFSET_Y
        pyxel.text(name_x, name_y, name, pyxel.COLOR_WHITE)
    
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
    
    def _draw_mouse_cursor(self) -> None:
        """Draw mouse cursor at editable positions / 編集可能位置にマウスカーソル描画"""
        if not self.show_cursor or not self.mouse_grid_pos:
            return
        
        row, col = self.mouse_grid_pos
        grid_x = self.config.grid_origin_x
        grid_y = self.config.grid_origin_y
        cell_size = self.config.grid_cell_size
        
        # Calculate intersection position / 交点位置計算
        intersection_x = grid_x + col * cell_size
        intersection_y = grid_y + row * cell_size
        
        # Draw cursor as a small circle / カーソルを小さな円で描画
        pyxel.circb(intersection_x, intersection_y, 3, pyxel.COLOR_YELLOW)
        
        # Draw crosshair / 十字線描画
        pyxel.line(intersection_x - 5, intersection_y, intersection_x + 5, intersection_y, pyxel.COLOR_YELLOW)
        pyxel.line(intersection_x, intersection_y - 5, intersection_x, intersection_y + 5, pyxel.COLOR_YELLOW)
    
    def _draw_controls(self) -> None:
        """Draw control information / 操作情報描画"""
        control_y = self.config.control_info_y
        pyxel.text(10, control_y, "Mouse: Hover over grid intersections, Q-Quit", pyxel.COLOR_WHITE)
    
    def _draw_status_bar(self) -> None:
        """Draw status bar with mouse position / マウス位置情報を含むステータスバー描画"""
        # ステータスバーの位置（画面下部）
        status_y = self.config.window_height - 20
        
        # 背景を黒でクリア
        pyxel.rect(0, status_y, self.config.window_width, 20, pyxel.COLOR_BLACK)
        
        # マウス位置情報表示
        if self.mouse_grid_pos:
            row, col = self.mouse_grid_pos
            position_text = f"Grid Position: Row={row}, Col={col} [grid[{row}][{col}]]"
            pyxel.text(10, status_y + 5, position_text, pyxel.COLOR_WHITE)
            
            # 編集可能かどうか表示
            if self._is_editable_position(row, col):
                pyxel.text(10, status_y + 12, "Editable: YES", pyxel.COLOR_GREEN)
            else:
                pyxel.text(10, status_y + 12, "Editable: NO (Bus area)", pyxel.COLOR_RED)
        else:
            # グリッド外の場合
            mouse_x, mouse_y = pyxel.mouse_x, pyxel.mouse_y
            pyxel.text(10, status_y + 5, f"Mouse: ({mouse_x}, {mouse_y}) - Outside grid", pyxel.COLOR_GRAY)
            pyxel.text(10, status_y + 12, "Editable: NO (Outside grid)", pyxel.COLOR_RED)

if __name__ == "__main__":
    PyPlcSimulator()
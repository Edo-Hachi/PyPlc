# PyPlc Ver3 - Clean Implementation Start
# 作成日: 2025-01-29
# 目標: PLC標準仕様完全準拠ラダー図シミュレーター

import pyxel
from config import DisplayConfig, SystemInfo, UIConfig, DeviceType
from core.grid_system import GridSystem
from core.input_handler import InputHandler, MouseState
from core.circuit_analyzer import CircuitAnalyzer

class PyPlcVer3:
    """PyPlc Ver3 - PLC標準仕様準拠シミュレーター"""
    
    def __init__(self):
        """アプリケーション初期化"""
        pyxel.init(
            DisplayConfig.WINDOW_WIDTH,
            DisplayConfig.WINDOW_HEIGHT,
            title=f"PyPlc Ver{SystemInfo.VERSION} - Circuit Solver",
            fps=DisplayConfig.TARGET_FPS
        )
        pyxel.mouse(True)
        
        # --- モジュールのインスタンス化 ---
        self.grid_system = GridSystem()
        self.input_handler = InputHandler(self.grid_system)
        self.circuit_analyzer = CircuitAnalyzer(self.grid_system)
        
        self.mouse_state: MouseState = MouseState()
        
        pyxel.run(self.update, self.draw)
    
    def update(self) -> None:
        """フレーム更新処理"""
        # 1. 入力処理
        self.mouse_state = self.input_handler.update_mouse_state()
        if self.input_handler.check_quit_command():
            pyxel.quit()
        self._handle_device_placement()

        # 2. 論理演算 (通電解析)
        self.circuit_analyzer.solve_ladder()

    def _handle_device_placement(self) -> None:
        """マウス入力に基づき、デバイスの配置・削除・状態変更を行う"""
        if self.mouse_state.hovered_pos is None or not self.mouse_state.is_snapped or not self.mouse_state.on_editable_area:
            return

        row, col = self.mouse_state.hovered_pos

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            device = self.grid_system.get_device(row, col)
            if device:
                self.grid_system.remove_device(row, col)
            else:
                self.grid_system.place_device(row, col, DeviceType.CONTACT_A, f"X{row}{col}")
        
        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            device = self.grid_system.get_device(row, col)
            if device:
                device.state = not device.state

    def draw(self) -> None:
        """描画処理"""
        # 3. 描画処理
        pyxel.cls(pyxel.COLOR_BLACK)
        self.grid_system.draw()
        self._draw_cursor_and_status()
        self._draw_header_footer()

    def _draw_cursor_and_status(self) -> None:
        """マウスカーソルと関連情報を描画する"""
        if self.mouse_state.hovered_pos is None: return
        row, col = self.mouse_state.hovered_pos
        
        if not self.mouse_state.on_editable_area:
            cursor_color, area_color = pyxel.COLOR_RED, pyxel.COLOR_RED
        else:
            area_color = pyxel.COLOR_GREEN
            cursor_color = pyxel.COLOR_YELLOW if self.mouse_state.is_snapped else pyxel.COLOR_WHITE

        x = self.grid_system.origin_x + col * self.grid_system.cell_size
        y = self.grid_system.origin_y + row * self.grid_system.cell_size
        
        pyxel.line(x - 4, y, x + 4, y, cursor_color)
        pyxel.line(x, y - 4, x, y + 4, cursor_color)
        
        status_text = f"Grid:({row},{col}) Snap:{'ON' if self.mouse_state.is_snapped else 'OFF'}"
        area_text = f"Area:{'EDITABLE' if self.mouse_state.on_editable_area else 'PROTECTED'}"
        
        pyxel.text(10, UIConfig.STATUS_AREA_Y, status_text, cursor_color)
        pyxel.text(180, UIConfig.STATUS_AREA_Y, area_text, area_color)

    def _draw_header_footer(self) -> None:
        """ヘッダーとフッターの情報を描画する"""
        pyxel.text(10, 10, f"PyPlc Ver{SystemInfo.VERSION} - Stage 4: Solver", pyxel.COLOR_GREEN)
        pyxel.text(10, DisplayConfig.WINDOW_HEIGHT - 20, "L-Click:Place/Del R-Click:Toggle Q:Quit", pyxel.COLOR_GRAY)

if __name__ == "__main__":
    PyPlcVer3()

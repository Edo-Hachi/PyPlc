# PyPlc Ver3 - Clean Implementation Start
# 作成日: 2025-01-29
# 目標: PLC標準仕様完全準拠ラダー図シミュレーター

import pyxel
from config import DisplayConfig, SystemInfo, UIConfig, UIBehaviorConfig, DeviceType
from core.grid_system import GridSystem
from core.input_handler import InputHandler, MouseState
from core.circuit_analyzer import CircuitAnalyzer
from core.device_palette import DevicePalette
from core.SpriteManager import sprite_manager # SpriteManagerをインポート

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
        
        # SpriteManagerからリソースファイルをロード
        if sprite_manager.resource_file:
            pyxel.load(sprite_manager.resource_file)
        
        # --- モジュールのインスタンス化 ---
        self.grid_system = GridSystem()
        self.input_handler = InputHandler(self.grid_system)
        self.circuit_analyzer = CircuitAnalyzer(self.grid_system)
        self.device_palette = DevicePalette()  # デバイスパレット追加
        
        self.mouse_state: MouseState = MouseState()
        
        pyxel.run(self.update, self.draw)
    
    def update(self) -> None:
        """フレーム更新処理"""
        # 1. 入力処理
        self.mouse_state = self.input_handler.update_mouse_state()
        if self.input_handler.check_quit_command():
            pyxel.quit()
        
        # デバイスパレット入力処理
        self.device_palette.update_input()
        
        self._handle_device_placement()

        # 2. 論理演算 (通電解析)
        self.circuit_analyzer.solve_ladder()

    def _handle_device_placement(self) -> None:
        """
        マウス入力に基づき、デバイスの配置・削除・状態変更を行う
        設定対応: 常時スナップモード or CTRL切り替えモード
        """
        # スナップモードが有効でない場合は何もしない（設定により判定）
        if not self.mouse_state.snap_mode:
            return
            
        # スナップ状態でない、または編集可能領域でない場合は何もしない
        if self.mouse_state.hovered_pos is None or not self.mouse_state.is_snapped or not self.mouse_state.on_editable_area:
            return

        row, col = self.mouse_state.hovered_pos

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            device = self.grid_system.get_device(row, col)
            
            # 選択されたデバイスタイプを取得
            selected_device_type = self.device_palette.get_selected_device_type()
            
            if device:
                # 既存デバイスがある場合
                if selected_device_type == DeviceType.DEL:
                    # 削除コマンドの場合は削除
                    self.grid_system.remove_device(row, col)
                else:
                    # 削除以外の場合は置き換え
                    self.grid_system.remove_device(row, col)
                    if selected_device_type != DeviceType.EMPTY:
                        address = f"X{row}{col}"  # 仮のアドレス生成
                        self.grid_system.place_device(row, col, selected_device_type, address)
            else:
                # 空きセルの場合、選択されたデバイスを配置
                if selected_device_type not in [DeviceType.DEL, DeviceType.EMPTY]:
                    address = f"X{row}{col}"  # 仮のアドレス生成
                    self.grid_system.place_device(row, col, selected_device_type, address)
        
        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            device = self.grid_system.get_device(row, col)
            if device:
                device.state = not device.state

    def draw(self) -> None:
        """描画処理"""
        # 3. 描画処理
        pyxel.cls(pyxel.COLOR_BLACK)
        
        # デバイスパレット描画（最初に描画）
        self.device_palette.draw()
        
        # グリッドシステム描画
        self.grid_system.draw()
        
        # UI情報描画
        self._draw_cursor_and_status()
        self._draw_header_footer()

    def _draw_cursor_and_status(self) -> None:
        """
        マウスカーソルと詳細ステータス情報を描画する
        Ver2準拠: 詳細情報表示、スナップモード状態、操作ガイダンス
        """
        # ステータスバー背景描画（Ver2準拠の拡張表示領域）
        status_y = DisplayConfig.WINDOW_HEIGHT - 40  # 高さ拡張（20→40）
        pyxel.rect(0, status_y, DisplayConfig.WINDOW_WIDTH, 40, pyxel.COLOR_BLACK)
        
        # スナップモード状態表示（設定対応）
        if UIBehaviorConfig.ALWAYS_SNAP_MODE:
            mode_text = "ALWAYS SNAP"
            mode_color = pyxel.COLOR_GREEN
        else:
            mode_text = "SNAP MODE" if self.mouse_state.snap_mode else "FREE MODE"
            mode_color = pyxel.COLOR_YELLOW if self.mouse_state.snap_mode else pyxel.COLOR_WHITE
        pyxel.text(200, status_y + 2, mode_text, mode_color)
        
        # マウスカーソル描画とステータス情報
        if self.mouse_state.hovered_pos is not None:
            # カーソル描画
            self._draw_detailed_cursor()
            
            # マウス位置詳細情報（Ver2準拠）
            row, col = self.mouse_state.hovered_pos
            position_text = f"Grid Position: Row={row}, Col={col} [grid[{row}][{col}]]"
            pyxel.text(10, status_y + 5, position_text, pyxel.COLOR_WHITE)
            
            # 編集可能性詳細表示（Ver2準拠の色分け）
            if self.mouse_state.on_editable_area:
                pyxel.text(10, status_y + 15, "Editable: YES", pyxel.COLOR_GREEN)
            else:
                pyxel.text(10, status_y + 15, "Editable: NO (Bus area)", pyxel.COLOR_RED)
                
            # スナップ状態詳細表示
            snap_text = f"Snap: {'ON' if self.mouse_state.is_snapped else 'OFF'}"
            snap_color = pyxel.COLOR_YELLOW if self.mouse_state.is_snapped else pyxel.COLOR_GRAY
            pyxel.text(10, status_y + 25, snap_text, snap_color)
        else:
            # スナップ範囲外時の詳細メッセージ（Ver2準拠）
            mouse_x, mouse_y = pyxel.mouse_x, pyxel.mouse_y
            if self.mouse_state.snap_mode:
                pyxel.text(10, status_y + 5, f"Mouse: ({mouse_x}, {mouse_y}) - No snap target", pyxel.COLOR_GRAY)
                pyxel.text(10, status_y + 15, "Move closer to grid intersection", pyxel.COLOR_CYAN)
            else:
                pyxel.text(10, status_y + 5, f"Mouse: ({mouse_x}, {mouse_y}) - Free movement", pyxel.COLOR_GRAY)
                pyxel.text(10, status_y + 15, "Hold CTRL to enable snap mode", pyxel.COLOR_CYAN)
    
    def _draw_detailed_cursor(self) -> None:
        """
        詳細マウスカーソル描画（Ver2準拠）
        十字線付きの視覚的に分かりやすいカーソル
        """
        if not self.mouse_state.snap_mode or not self.mouse_state.hovered_pos:
            return
        
        row, col = self.mouse_state.hovered_pos
        x = self.grid_system.origin_x + col * self.grid_system.cell_size
        y = self.grid_system.origin_y + row * self.grid_system.cell_size
        
        # カーソル色決定
        if not self.mouse_state.on_editable_area:
            cursor_color = pyxel.COLOR_RED
        elif self.mouse_state.is_snapped:
            cursor_color = pyxel.COLOR_YELLOW
        else:
            cursor_color = pyxel.COLOR_WHITE
        
        # 十字線付き詳細カーソル（Ver2準拠）
        pyxel.circb(x, y, 3, cursor_color)
        pyxel.line(x - 5, y, x + 5, y, cursor_color)
        pyxel.line(x, y - 5, x, y + 5, cursor_color)

    def _draw_header_footer(self) -> None:
        """ヘッダーとフッターの情報を描画する"""
        #pyxel.text(10, 10, f"PyPlc Ver{SystemInfo.VERSION} - Stage 4: Solver", pyxel.COLOR_GREEN)
        
        # フッター操作ガイド（設定に応じて表示切り替え）
        footer_y = DisplayConfig.WINDOW_HEIGHT - 20
        if UIBehaviorConfig.ALWAYS_SNAP_MODE:
            pyxel.text(10, footer_y, "L-Click:Place/Del R-Click:Toggle Q:Quit", pyxel.COLOR_GRAY)
        else:
            pyxel.text(10, footer_y, "CTRL:Snap L-Click:Place/Del R-Click:Toggle Q:Quit", pyxel.COLOR_GRAY)

if __name__ == "__main__":
    PyPlcVer3()
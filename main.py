# PyPlc Ver3 - Clean Implementation Start
# 作成日: 2025-01-28
# 目標: PLC標準仕様完全準拠ラダー図シミュレーター

# For AI Support
# このコメントは消さないでください

## 実行環境は .vscode/ 以下のファイルに定義してあります

# 返答は日本語でお願いします
# pythonとはいえ、型はちゃんと宣言してください
# コメントも日本語でつけて下さい
# ステップバイステップで作業をしながら git にチェックインしながらすすめるので、ユーザーに都度確認してください。
# ですので、ドンドンとコードを書いて進めないで下さい

# 配列関係の処理をする時は  grid[row][col]  # [y座標][x座標] の順序 って書いておいてくれると、僕がわかりやすいです　

import pyxel
from typing import Optional
from config import DisplayConfig, SystemInfo, UIConfig
from core.grid_system import GridSystem
from core.input_handler import InputHandler, MouseState


class PyPlcVer3:
    """PyPlc Ver3 - PLC標準仕様準拠シミュレーター"""
    
    def __init__(self):
        """アプリケーション初期化"""
        pyxel.init(
            DisplayConfig.WINDOW_WIDTH,
            DisplayConfig.WINDOW_HEIGHT,
            title=f"PyPlc Ver{SystemInfo.VERSION} - Input System",
            fps=DisplayConfig.TARGET_FPS
        )
        pyxel.mouse(True)
        
        # --- モジュールのインスタンス化 ---
        self.grid_system = GridSystem()
        self.input_handler = InputHandler(self.grid_system)
        
        # --- 状態変数の初期化 ---
        self.mouse_state: MouseState = MouseState()
        
        pyxel.run(self.update, self.draw)
    
    def update(self) -> None:
        """フレーム更新処理"""
        # InputHandlerでマウス状態を更新
        self.mouse_state = self.input_handler.update_mouse_state()
        
        # 終了コマンドをチェック
        if self.input_handler.check_quit_command():
            pyxel.quit()
    
    def draw(self) -> None:
        """描画処理"""
        pyxel.cls(pyxel.COLOR_BLACK)
        
        # グリッド描画
        self.grid_system.draw()
        
        # カーソルとステータス情報の描画
        self._draw_cursor_and_status()
        
        # ヘッダーとフッターの描画
        self._draw_header_footer()

    def _draw_cursor_and_status(self) -> None:
        """マウスカーソルと関連情報を描画する"""
        if self.mouse_state.hovered_pos is None:
            return

        row, col = self.mouse_state.hovered_pos

        # --- 色の決定ロジック (優先順位を明確化) ---

        # 1. まず、編集可能領域かどうかで色を決定する
        if not self.mouse_state.on_editable_area:
            # 保護領域にいる場合、カーソルとエリアテキストは両方「赤」で確定
            cursor_color = pyxel.COLOR_RED
            area_color = pyxel.COLOR_RED
        else:
            # 編集可能領域にいる場合、エリアテキストは「緑」で確定
            area_color = pyxel.COLOR_GREEN
            
            # その上で、スナップ状態に応じてカーソルの色を決定する
            if self.mouse_state.is_snapped:
                cursor_color = pyxel.COLOR_YELLOW  # スナップ時: 黄色
            else:
                cursor_color = pyxel.COLOR_WHITE   # 非スナップ時: 白色

        # --- 描画処理 ---

        # グリッド交点のスクリーン座標を計算
        x = self.grid_system.origin_x + col * self.grid_system.cell_size
        y = self.grid_system.origin_y + row * self.grid_system.cell_size
        
        # 十字カーソルを描画
        pyxel.line(x - 4, y, x + 4, y, cursor_color)
        pyxel.line(x, y - 4, x, y + 4, cursor_color)
        
        # ステータス情報を描画
        status_text = f"Grid: ({row}, {col})"
        snap_text = f"Snap: {'ON' if self.mouse_state.is_snapped else 'OFF'}"
        area_text = f"Area: {'EDITABLE' if self.mouse_state.on_editable_area else 'PROTECTED'}"

        pyxel.text(10, UIConfig.STATUS_AREA_Y, status_text, pyxel.COLOR_WHITE)
        pyxel.text(100, UIConfig.STATUS_AREA_Y, snap_text, cursor_color) # snap_textはカーソルと同じ色で表示
        pyxel.text(180, UIConfig.STATUS_AREA_Y, area_text, area_color)




    def _draw_header_footer(self) -> None:
        """ヘッダーとフッターの情報を描画する"""
        # Ver3 ステージ情報
        pyxel.text(
            10, 10,
            f"PyPlc Ver{SystemInfo.VERSION} - Stage 2: Input Handler",
            pyxel.COLOR_GREEN
        )
        
        # 終了方法の表示
        pyxel.text(
            10, DisplayConfig.WINDOW_HEIGHT - 20,
            "Press Q or ESC to quit",
            pyxel.COLOR_GRAY
        )


if __name__ == "__main__":
    PyPlcVer3()
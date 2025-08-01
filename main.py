# PyPlc Ver3 - Clean Implementation Start
# 作成日: 2025-01-28
# 目標: PLC標準仕様完全準拠ラダー図シミュレーター

# For AI Support
# このコメントは消さないでください

## 実行環境は .vscode/ 以下のファイルに定義してあります

# For AI Support
# _Ver3_definition.md  を参考にプロジェクト設計を進めてください

# 返答は日本語でお願いします
# pythonとはいえ、型はちゃんと宣言してください
# コメントも日本語でつけて下さい
# ステップバイステップで作業をしながら git にチェックインしながらすすめるので、ユーザーに都度確認してください。
# ですので、ドンドンとコードを書いて進めないで下さい

# 配列関係の処理をする時は  grid[row][col]  # [y座標][x座標] の順序 って書いておいてくれると、僕がわかりやすいです

import pyxel
from config import DisplayConfig, SystemInfo
from core.grid_system import GridSystem


class PyPlcVer3:
    """PyPlc Ver3 - PLC標準仕様準拠シミュレーター"""
    
    def __init__(self):
        """アプリケーション初期化"""
        # Pyxel初期化（config.pyの定数を使用）
        pyxel.init(
            DisplayConfig.WINDOW_WIDTH,
            DisplayConfig.WINDOW_HEIGHT,
            title=f"PyPlc Ver{SystemInfo.VERSION} - Visual Foundation",
            fps=DisplayConfig.TARGET_FPS
        )
        
        # マウスカーソル表示
        pyxel.mouse(True)
        
        # --- モジュールのインスタンス化 ---
        # GridSystemをインスタンス化
        self.grid_system = GridSystem()
        
        # アプリケーション開始
        pyxel.run(self.update, self.draw)
    
    def update(self) -> None:
        """フレーム更新処理"""
        # QキーまたはESCキーで終了
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
    
    def draw(self) -> None:
        """描画処理"""
        # 背景をクリア（黒）
        pyxel.cls(pyxel.COLOR_BLACK)
        
        # GridSystemにグリッド描画を委譲
        self.grid_system.draw()
        
        # Ver3開始メッセージ
        pyxel.text(
            10, 10,
            f"PyPlc Ver{SystemInfo.VERSION} - Stage 1: Grid System",
            pyxel.COLOR_GREEN
        )
        
        # 終了方法の表示
        pyxel.text(
            10, DisplayConfig.WINDOW_HEIGHT - 20,
            "Press Q or ESC to quit",
            pyxel.COLOR_GRAY
        )


if __name__ == "__main__":
    # Ver3アプリケーション起動
    PyPlcVer3()

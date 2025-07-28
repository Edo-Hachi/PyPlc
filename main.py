import pyxel

#ユーザーへの返答は日本語でお願いします
#型宣言はしっかりやりましょう
#ステップバイステップで作業を進めますので、いきなりコーディングしないで下さい。ユーザーがgitに都度チェックインします
#バージョン１だった時のコードは BeforeRemake/ 以下にあります（複雑すぎるので、取り込む時はシンプルな構造に落とし込むことを最優先にしてください）。

class PyPlcSimulator:
    def __init__(self):
        pyxel.init(256, 256, title="PyPlc-v2")
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
    
    def draw(self):
        pyxel.cls(0)
        pyxel.text(128 - 20, 128, "Hello World", 7)

if __name__ == "__main__":
    PyPlcSimulator()
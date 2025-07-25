"""
PyPlc Configuration Module

システム全体の設定定数、レイアウト定義、色定義、デバイスタイプ定義を管理するモジュール。
main.pyから分離して設定の一元管理を実現。
"""

from enum import Enum

# 画面サイズ定数
WIDTH = 256
HEIGHT = 256

# レイアウト定数
class Layout:
    # 基本配置
    TITLE_X = 10
    TITLE_Y = 5
    
    # デバイスパレット
    PALETTE_Y = 16
    PALETTE_START_X = 20
    PALETTE_DEVICE_WIDTH = 24
    PALETTE_NUMBER_OFFSET_Y = -8
    
    # グリッド設定
    GRID_SIZE = 16
    GRID_COLS = 10
    GRID_ROWS = 10
    GRID_START_X = 16
    GRID_START_Y = 32
    
    # デバイス状態表示
    DEVICE_STATUS_Y = 160
    DEVICE_STATUS_X = 10
    DEVICE_STATUS_SPACING = 12
    DEVICE_STATUS_X2 = 90
    TIMER_COUNTER_X = 170
    
    # 操作説明
    CONTROLS_Y = 240
    CONTROLS_X = 10
    
    # スプライトテスト（右上）
    SPRITE_TEST_X = 160
    SPRITE_TEST_Y = 10

# 色定数

#>> to Claude
#色番号がハードコーディングされてるので、pyxel.COLOR_XXXXX で置き換えてください
class Colors:
    GRID_LINE = 1        # ダークグレイ
    WIRE_OFF = 1         # グレイ（通電なし）
    WIRE_ON = 11         # 緑（通電中）
    SELECTED_BG = 6      # 黄色（選択背景）
    TEXT = 7             # 白
    BUSBAR = 7           # 白
    BLACK = 0            # 黒

# デバイスタイプ定義
class DeviceType(Enum):
    EMPTY = "EMPTY"          # 空のグリッド
    BUSBAR = "BUSBAR"        # バスバー
    TYPE_A = "TYPE_A"        # A接点
    TYPE_B = "TYPE_B"        # B接点
    COIL = "COIL"            # コイル
    TIMER = "TIMER"          # タイマー
    COUNTER = "COUNTER"      # カウンター
    WIRE_H = "WIRE_H"        # 横配線
    WIRE_V = "WIRE_V"        # 縦配線
    LINK_UP = "LINK_UP"      # 上方向結線点(ラインから上方向に接続を作成する分岐)
    LINK_DOWN = "LINK_DOWN"  # 下方向結線点（ラインから舌方向に接続を作成する分岐）
    DEL = "DEL"              # 削除デバイス

# バスバー接続方向
class BusbarDirection(Enum):
    NONE = 0
    UP = 1
    DOWN = 2
    BOTH = 3
"""
PyPlc Configuration Module

システム全体の設定定数、レイアウト定義、色定義、デバイスタイプ定義を管理するモジュール。
main.pyから分離して設定の一元管理を実現。
"""

import pyxel
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
    PALETTE_Y_MIDDLE = 32  # 中段のY座標
    PALETTE_Y_LOWER = 48   # 下段のY座標
    PALETTE_START_X = 20
    PALETTE_DEVICE_WIDTH = 24
    PALETTE_NUMBER_OFFSET_Y = -8
    PALETTE_ROW_HEIGHT = 16  # 上段・下段間の高さ
    
    # グリッド設定
    GRID_SIZE = 16
    GRID_COLS = 10
    GRID_ROWS = 10
    GRID_START_X = 16
    GRID_START_Y = 72
    
    # デバイス状態表示
    DEVICE_STATUS_Y = 192
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
    
    # ステータスバー（画面下部）
    STATUS_BAR_Y = 248
    STATUS_BAR_HEIGHT = 8
    STATUS_BAR_X = 0
    STATUS_BAR_WIDTH = WIDTH
    MODE_DISPLAY_X = WIDTH - 40  # 右端からのオフセット

# 色定数 (Pyxel COLOR constants)
class Colors:
    GRID_LINE = pyxel.COLOR_DARK_BLUE      # グリッド線
    WIRE_OFF = pyxel.COLOR_GRAY            # グレイ（通電なし）
    WIRE_ON = pyxel.COLOR_ORANGE           # オレンジ（通電中）
    SELECTED_BG = pyxel.COLOR_YELLOW       # 黄色（選択背景）
    TEXT = pyxel.COLOR_WHITE               # 白（テキスト）
    BUSBAR = pyxel.COLOR_ORANGE            # オレンジ（バスバー）
    BLACK = pyxel.COLOR_BLACK              # 黒（背景）
    STATUS_BAR_BG = pyxel.COLOR_NAVY       # ステータスバー背景
    MODE_EDIT = pyxel.COLOR_YELLOW         # EDITモード表示色
    MODE_RUN = pyxel.COLOR_LIME            # RUNモード表示色
    PLC_STOPPED = pyxel.COLOR_RED          # PLC停止中表示色
    PLC_RUNNING = pyxel.COLOR_LIME         # PLC実行中表示色

# デバイスタイプ定義
class DeviceType(Enum):
    EMPTY = "EMPTY"          # 空のグリッド
    BUSBAR = "BUSBAR"        # バスバー
    TYPE_A = "TYPE_A"        # A接点
    TYPE_B = "TYPE_B"        # B接点
    COIL = "COIL"            # 出力コイル（OUTCOIL_NML）
    INCOIL = "INCOIL"        # 入力コイル（内部処理用）
    OUTCOIL_REV = "OUTCOIL_REV"  # 反転出力コイル
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

# シミュレーターモード
class SimulatorMode(Enum):
    EDIT = "EDIT"        # 回路構築モード
    RUN = "RUN"          # シミュレーション実行モード
    DIALOG = "DIALOG"    # モーダルダイアログ有効（一時的）

# PLC実行状態
class PLCRunState(Enum):
    STOPPED = "STOPPED"  # 停止中
    RUNNING = "RUNNING"  # 実行中
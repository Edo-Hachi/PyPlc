"""
PyPlc Ver3 Device Palette Module
作成日: 2025-08-01
目標: デバイス選択パレットシステム（Ver2資産をベースにVer3向けシンプル実装）
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pyxel

from config import DeviceType, DEVICE_PALETTE_DEFINITIONS, PALETTE_LAYOUT_CONFIG


@dataclass
class PaletteDevice:
    """パレットデバイス定義"""
    device_type: DeviceType    # デバイス種別
    display_name: str          # 画面表示名（例: [A_CNTC]）
    key_bind: int             # キーバインド（1-9, 0=10）
    row: int                  # 配置行（0=上段, 1=下段）
    description: str = ""     # 説明文（オプション）


@dataclass
class PaletteState:
    """パレット状態管理"""
    current_row: int = 0           # 現在の行（0=上段, 1=下段）
    selected_index: Optional[int] = None     # 選択されたデバイスインデックス（0-9、None=何も選択されていない）
    is_shift_pressed: bool = False # Shiftキー押下状態


class DevicePalette:
    """
    デバイスパレット管理クラス
    - Ver2のplacement_systemをベースに、よりシンプルで可読性の高い実装
    - 10×2デバイスパレット（上段・下段）
    - 1-0キー選択 + Shift行切り替え + マウス選択対応
    """
    
    def __init__(self):
        """DevicePaletteの初期化"""
        self.state = PaletteState()
        self.devices = self._create_palette_devices_from_config()
        
        # パレット表示設定（config.pyから取得）
        self.palette_layout_config = PALETTE_LAYOUT_CONFIG
    
    def _create_palette_devices_from_config(self) -> List[List[PaletteDevice]]:
        """config.pyの定義からパレットデバイスを作成"""
        
        def create_row_from_tuples(row_data: List[tuple], row_index: int) -> List[PaletteDevice]:
            """タプルリストからPaletteDeviceの行を作成"""
            row_devices = []
            for device_type, display_name, key_bind, description in row_data:
                device = PaletteDevice(
                    device_type=device_type,
                    display_name=display_name,
                    key_bind=key_bind,
                    row=row_index,
                    description=description
                )
                row_devices.append(device)
            return row_devices
        
        # 上段・下段それぞれを作成
        top_row = create_row_from_tuples(DEVICE_PALETTE_DEFINITIONS["top_row"], 0)
        bottom_row = create_row_from_tuples(DEVICE_PALETTE_DEFINITIONS["bottom_row"], 1)
        
        return [top_row, bottom_row]
    
    def get_selected_device_type(self) -> DeviceType:
        """現在選択中のデバイスタイプを取得"""
        # 何も選択されていない場合は空を返す
        if self.state.selected_index is None:
            return DeviceType.EMPTY
            
        current_devices = self.devices[self.state.current_row]
        selected_device = current_devices[self.state.selected_index]
        return selected_device.device_type
    
    def set_dialog_mode(self, enabled: bool) -> None:
        """ダイアログモードの設定"""
        if enabled:
            # ダイアログモード有効時は選択状態をクリア
            if self.state.selected_index is not None:  # 既にNoneなら保存不要
                self.previous_selection = self.state.selected_index  # 復元用に保存
                self.state.selected_index = None
        else:
            # ダイアログモード無効時は前の選択状態を復元
            if hasattr(self, 'previous_selection'):
                self.state.selected_index = self.previous_selection
                delattr(self, 'previous_selection')  # メモリクリーンアップ
    
    def get_selected_device(self) -> Optional[PaletteDevice]:
        """現在選択中のPaletteDeviceを取得"""
        if self.state.selected_index is None:
            return None
        current_devices = self.devices[self.state.current_row]
        return current_devices[self.state.selected_index]
    
    def get_device_at_position(self, row: int, index: int) -> Optional[PaletteDevice]:
        """指定位置のPaletteDeviceを取得"""
        if 0 <= row < len(self.devices) and 0 <= index < len(self.devices[row]):
            return self.devices[row][index]
        return None
    
    def set_selection(self, row: int, index: int) -> bool:
        """選択状態を設定"""
        if 0 <= row < len(self.devices) and 0 <= index < len(self.devices[row]):
            self.state.current_row = row
            self.state.selected_index = index
            return True
        return False
    
    def switch_row(self) -> None:
        """現在の行を切り替え（0⇔1）"""
        self.state.current_row = 1 - self.state.current_row
    
    def get_palette_info(self) -> str:
        """現在のパレット状態情報を文字列で取得（デバッグ用）"""
        selected_device = self.get_selected_device()
        device_name = selected_device.display_name if selected_device else "NONE"
        return f"Row:{self.state.current_row} Index:{self.state.selected_index} Device:{device_name}"
    
    def _get_device_position_from_mouse(self) -> Optional[Tuple[int, int]]:
        """マウス座標からパレット内の(row, index)を取得（シンプル設計）"""
        mouse_x = pyxel.mouse_x
        mouse_y = pyxel.mouse_y
        
        # パレット設定を取得（可読性のため変数に展開）
        palette_x = self.palette_layout_config["palette_x"]
        palette_y = self.palette_layout_config["palette_y"]
        device_width = self.palette_layout_config["device_width"]
        device_height = self.palette_layout_config["device_height"]
        row_spacing = self.palette_layout_config["row_spacing"]
        
        # X座標チェック（10個のデバイス範囲内か）
        if not (palette_x <= mouse_x < palette_x + device_width * 10):
            return None
        
        # Y座標チェック（上段・下段のどちらか）
        if palette_y <= mouse_y < palette_y + device_height:
            row = 0  # 上段
        elif palette_y + device_height + row_spacing <= mouse_y < palette_y + device_height * 2 + row_spacing:
            row = 1  # 下段
        else:
            return None  # パレット領域外
        
        # インデックス計算（0-9）
        index = (mouse_x - palette_x) // device_width
        if 0 <= index < 10:
            return (row, index)
        
        return None
    
    def update_input(self) -> bool:
        """
        入力処理（キーボード・マウス）
        戻り値: 選択状態が変更された場合True
        """
        changed = False
        
        # キーボード入力処理
        if self._handle_keyboard_input():
            changed = True
        
        # マウス入力処理
        if self._handle_mouse_input():
            changed = True
            
        return changed
    
    def _handle_mouse_input(self) -> bool:
        """
        マウス入力処理（シンプル設計）
        戻り値: 選択状態が変更された場合True
        """
        # 左クリックが押された時のみ処理
        if not pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            return False
        
        # マウス位置からパレット内のデバイス位置を取得
        mouse_position = self._get_device_position_from_mouse()
        if mouse_position is None:
            return False  # パレット領域外なので何もしない
        
        row, index = mouse_position
        
        # クリック位置のデバイスを取得
        clicked_device = self.devices[row][index]
        
        # EMPTYデバイスの場合は選択しない
        if clicked_device.device_type == DeviceType.EMPTY:
            return False
        
        # 選択状態を直接更新（Ver2準拠のシンプル設計）
        self.state.current_row = row
        self.state.selected_index = index
        
        return True  # 選択状態が変更された
    
    def _handle_keyboard_input(self) -> bool:
        """
        キーボード入力処理（1-0キー + Shift処理）
        戻り値: 選択状態が変更された場合True
        """
        changed = False
        
        # Shiftキー状態更新と行切り替え
        shift_pressed = pyxel.btn(pyxel.KEY_LSHIFT) or pyxel.btn(pyxel.KEY_RSHIFT)  
        
        # Shiftキーが新たに押された場合、行を切り替え
        if shift_pressed and not self.state.is_shift_pressed:
            self.switch_row()
            changed = True
        
        self.state.is_shift_pressed = shift_pressed
        
        # 1-9キー処理
        for i in range(1, 10):
            if pyxel.btnp(getattr(pyxel, f"KEY_{i}")):
                self.state.selected_index = i - 1  # 1キー→インデックス0
                changed = True
                break
        
        # 0キー処理（10番目のデバイス）
        if pyxel.btnp(pyxel.KEY_0):
            self.state.selected_index = 9  # 0キー→インデックス9
            changed = True
            
        return changed
    
    def draw(self) -> None:
        """デバイスパレット描画"""
        self._draw_palette_background()
        self._draw_devices()
        self._draw_selection_indicator()
        self._draw_help_text()
    
    def _draw_palette_background(self) -> None:
        """パレット背景描画"""
        # メイン背景はBLACK
        pyxel.cls(pyxel.COLOR_BLACK)

        # パレット全体の背景（10個×2行）
        palette_width = self.palette_layout_config["device_width"] * 10  # 10個分
        palette_height = self.palette_layout_config["device_height"] * 2 + self.palette_layout_config["row_spacing"] + 4  # 2行 + 間隔
        
        pyxel.rect(
            self.palette_layout_config["palette_x"] - 2, 
            self.palette_layout_config["palette_y"] - 2, 
            palette_width +2, 
            palette_height , 
            pyxel.COLOR_DARK_BLUE
        )
    
    def _draw_devices(self) -> None:
        """デバイス描画（1行に10個のシンプル表示）"""
        # 上段（行0）: 1-0キー（10個）
        for i in range(10):
            device = self.devices[0][i]
            x = self.palette_layout_config["palette_x"] + i * self.palette_layout_config["device_width"]
            y = self.palette_layout_config["palette_y"]
            self._draw_single_device(device, x, y)
        
        # 下段（行1）: 1-0キー（10個）
        for i in range(10):
            device = self.devices[1][i]
            x = self.palette_layout_config["palette_x"] + i * self.palette_layout_config["device_width"]
            y = self.palette_layout_config["palette_y"] + self.palette_layout_config["device_height"] + self.palette_layout_config["row_spacing"]  # 少し間隔をあける
            self._draw_single_device(device, x, y)
    
    def _draw_single_device(self, device, x: int, y: int) -> None:
        """単一デバイスの描画"""
        # デバイス背景色決定
        if device.device_type == DeviceType.EMPTY:
            bg_color = pyxel.COLOR_GRAY
            text_color = pyxel.COLOR_DARK_BLUE
        elif device.device_type == DeviceType.DEL:
            bg_color = pyxel.COLOR_RED
            text_color = pyxel.COLOR_WHITE
        else:
            bg_color = pyxel.COLOR_NAVY  # 通常デバイスの背景色をNAVYに変更
            text_color = pyxel.COLOR_WHITE # 通常デバイスのテキスト色をWHITEに変更
        
        # デバイス枠描画
        pyxel.rect(x, y, self.palette_layout_config["device_width"] - 2, self.palette_layout_config["device_height"], bg_color)
        pyxel.rectb(x, y, self.palette_layout_config["device_width"] - 2, self.palette_layout_config["device_height"], pyxel.COLOR_DARK_BLUE) # ボーダー色をDARK_BLUEに変更
        
        # デバイス名表示
        if device.display_name:  # 空でない場合のみ表示
            pyxel.text(x + 2, y + 4, device.display_name, text_color)
    
    def _draw_selection_indicator(self) -> None:
        """選択状態インジケーター描画"""
        # 現在の行インジケーター（>マーク）
        row_y = self.palette_layout_config["palette_y"] + self.state.current_row * (self.palette_layout_config["device_height"] + self.palette_layout_config["row_spacing"]) + 4
        pyxel.text(self.palette_layout_config["palette_x"] - 10, row_y, ">", pyxel.COLOR_YELLOW)
        
        # 選択されたデバイスのハイライト（何かが選択されている場合のみ）
        if self.state.selected_index is not None:
            selected_x = self.palette_layout_config["palette_x"] + self.state.selected_index * self.palette_layout_config["device_width"]
            selected_y = self.palette_layout_config["palette_y"] + self.state.current_row * (self.palette_layout_config["device_height"] + self.palette_layout_config["row_spacing"])
            
            # 黄色い枠でハイライト
            pyxel.rectb(
                selected_x - 1, 
                selected_y - 1, 
                self.palette_layout_config["device_width"], 
                self.palette_layout_config["device_height"] + 2, 
                pyxel.COLOR_YELLOW
            )
        
        # マウスホバーエフェクト（シンプル設計）
        self._draw_mouse_hover_effect()
    
    def _draw_mouse_hover_effect(self) -> None:
        """マウスホバーエフェクト描画（可読性重視のシンプル実装）"""
        # マウス位置からパレット内位置を取得
        hover_position = self._get_device_position_from_mouse()
        if hover_position is None:
            return  # パレット領域外なので何もしない
        
        hover_row, hover_index = hover_position
        
        # ホバー位置のデバイスを取得
        hover_device = self.devices[hover_row][hover_index]
        
        # EMPTYデバイスの場合はホバーエフェクトを表示しない
        if hover_device.device_type == DeviceType.EMPTY:
            return
        
        # 現在選択中と同じ位置の場合は何もしない（重複を避ける）
        if (self.state.selected_index is not None and 
            hover_row == self.state.current_row and 
            hover_index == self.state.selected_index):
            return
        
        # ホバー位置の座標計算
        hover_x = self.palette_layout_config["palette_x"] + hover_index * self.palette_layout_config["device_width"]
        hover_y = self.palette_layout_config["palette_y"] + hover_row * (self.palette_layout_config["device_height"] + self.palette_layout_config["row_spacing"])
        
        # 薄い枠でホバー表示
        pyxel.rectb(
            hover_x - 1, 
            hover_y - 1, 
            self.palette_layout_config["device_width"], 
            self.palette_layout_config["device_height"] + 2, 
            pyxel.COLOR_WHITE
        )
    
    def _draw_help_text(self) -> None:
        """ヘルプテキスト描画"""
        help_y = self.palette_layout_config["palette_y"] + 30
        
        # ヘルプテキスト領域の背景
        help_bg_x = self.palette_layout_config["palette_x"] - 2
        help_bg_y = help_y - 2
        help_bg_width = 200 # 適当な幅
        help_bg_height = 20 # 適当な高さ
        pyxel.rect(help_bg_x, help_bg_y, help_bg_width, help_bg_height, pyxel.COLOR_DARK_BLUE)

        # 基本操作説明
        pyxel.text(self.palette_layout_config["palette_x"], help_y, "1-0:Select Device", pyxel.COLOR_WHITE)
        pyxel.text(self.palette_layout_config["palette_x"], help_y + 8, "SHIFT:Switch Row", pyxel.COLOR_WHITE)
        
        # 現在の状態表示
        shift_status = "ON" if self.state.is_shift_pressed else "OFF"
        pyxel.text(self.palette_layout_config["palette_x"] + 120, help_y, f"SHIFT:{shift_status}", pyxel.COLOR_YELLOW)
        
        selected_device = self.get_selected_device()
        device_name = selected_device.display_name if selected_device else "NONE"
        pyxel.text(self.palette_layout_config["palette_x"] + 120, help_y + 8, f"Selected:{device_name}", pyxel.COLOR_YELLOW)


# For AI Support - このコメントは消さないでください
# データ構造の実装完了
# - PaletteDevice: デバイス定義（DeviceSelectMenu.txt仕様準拠）
# - PaletteState: パレット状態管理
# - DevicePalette: 基本的なパレット管理機能
# - 上段: 実用デバイス（CONTACT_A/B, COIL_STD/REV, LINK系, DEL）
# - 下段: 将来拡張用（全てEMPTY）
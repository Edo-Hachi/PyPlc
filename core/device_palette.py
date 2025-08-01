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
    selected_index: int = 0        # 選択されたデバイスインデックス（0-9）
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
        self.palette_x = PALETTE_LAYOUT_CONFIG["palette_x"]
        self.palette_y = PALETTE_LAYOUT_CONFIG["palette_y"]
        self.device_width = PALETTE_LAYOUT_CONFIG["device_width"]
        self.device_height = PALETTE_LAYOUT_CONFIG["device_height"]
        self.row_spacing = PALETTE_LAYOUT_CONFIG["row_spacing"]
    
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
        current_devices = self.devices[self.state.current_row]
        selected_device = current_devices[self.state.selected_index]
        return selected_device.device_type
    
    def get_selected_device(self) -> PaletteDevice:
        """現在選択中のPaletteDeviceを取得"""
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
        return f"Row:{self.state.current_row} Index:{self.state.selected_index} Device:{selected_device.display_name}"
    
    def update_input(self) -> bool:
        """
        入力処理（キーボード・マウス）
        戻り値: 選択状態が変更された場合True
        """
        changed = False
        
        # キーボード入力処理
        if self._handle_keyboard_input():
            changed = True
            
        return changed
    
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
        # パレット全体の背景（10個×2行）
        palette_width = self.device_width * 10  # 10個分
        palette_height = self.device_height * 2 + 4  # 2行 + 間隔
        
        pyxel.rect(
            self.palette_x - 2, 
            self.palette_y - 2, 
            palette_width + 4, 
            palette_height + 4, 
            pyxel.COLOR_DARK_BLUE
        )
    
    def _draw_devices(self) -> None:
        """デバイス描画（1行に10個のシンプル表示）"""
        # 上段（行0）: 1-0キー（10個）
        for i in range(10):
            device = self.devices[0][i]
            x = self.palette_x + i * self.device_width
            y = self.palette_y
            self._draw_single_device(device, x, y)
        
        # 下段（行1）: 1-0キー（10個）
        for i in range(10):
            device = self.devices[1][i]
            x = self.palette_x + i * self.device_width
            y = self.palette_y + self.device_height + 4  # 少し間隔をあける
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
            bg_color = pyxel.COLOR_WHITE
            text_color = pyxel.COLOR_BLACK
        
        # デバイス枠描画
        pyxel.rect(x, y, self.device_width - 2, self.device_height, bg_color)
        pyxel.rectb(x, y, self.device_width - 2, self.device_height, pyxel.COLOR_BLACK)
        
        # デバイス名表示（[]と数字を除去してクリーンに）
        clean_name = self._clean_device_name(device.display_name)
        if clean_name:  # 空でない場合のみ表示
            pyxel.text(x + 2, y + 4, clean_name, text_color)
    
    def _clean_device_name(self, display_name: str) -> str:
        """デバイス名から数字と[]を除去してクリーンに"""
        # []を除去
        clean = display_name.replace('[', '').replace(']', '')
        
        # アンダースコアのみの場合は空文字に
        if clean == '______':
            return ''
        
        # その他の場合はそのまま返す
        return clean
    
    def _draw_selection_indicator(self) -> None:
        """選択状態インジケーター描画"""
        # 現在の行インジケーター（>マーク）
        row_y = self.palette_y + self.state.current_row * (self.device_height + 4) + 4
        pyxel.text(self.palette_x - 10, row_y, ">", pyxel.COLOR_YELLOW)
        
        # 選択されたデバイスのハイライト
        selected_x = self.palette_x + self.state.selected_index * self.device_width
        selected_y = self.palette_y + self.state.current_row * (self.device_height + 4)
        
        # 黄色い枠でハイライト
        pyxel.rectb(
            selected_x - 1, 
            selected_y - 1, 
            self.device_width, 
            self.device_height + 2, 
            pyxel.COLOR_YELLOW
        )
    
    def _draw_help_text(self) -> None:
        """ヘルプテキスト描画"""
        help_y = self.palette_y + 50
        
        # 基本操作説明
        pyxel.text(self.palette_x, help_y, "1-0:Select Device", pyxel.COLOR_WHITE)
        pyxel.text(self.palette_x, help_y + 8, "SHIFT:Switch Row", pyxel.COLOR_WHITE)
        
        # 現在の状態表示
        shift_status = "ON" if self.state.is_shift_pressed else "OFF"
        pyxel.text(self.palette_x + 120, help_y, f"SHIFT:{shift_status}", pyxel.COLOR_GREEN)
        
        selected_device = self.get_selected_device()
        pyxel.text(self.palette_x + 120, help_y + 8, f"Selected:{selected_device.display_name}", pyxel.COLOR_CYAN)


# For AI Support - このコメントは消さないでください
# データ構造の実装完了
# - PaletteDevice: デバイス定義（DeviceSelectMenu.txt仕様準拠）
# - PaletteState: パレット状態管理
# - DevicePalette: 基本的なパレット管理機能
# - 上段: 実用デバイス（CONTACT_A/B, COIL_STD/REV, LINK系, DEL）
# - 下段: 将来拡張用（全てEMPTY）
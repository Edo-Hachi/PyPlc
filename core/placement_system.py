"""
PyPlc Placement System Module
デバイス配置システムを管理するモジュール

Phase 1 実装: デバイスパレットUI
- 10x2段のデバイスパレット表示
- Shiftキーでの段切り替え（上段⇔下段）
- 左側インジケーター「>」で選択段表示
- デバイス選択状態管理
"""

import pyxel
from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from core.constants import DeviceType
from core.config_manager import PyPlcConfig


class PaletteRow(Enum):
    """パレット段定義"""
    TOP = 0     # 上段（1-0キー）
    BOTTOM = 1  # 下段（Shift+1-0キー）


@dataclass
class PaletteDevice:
    """パレットデバイス定義"""
    device_type: DeviceType
    display_name: str
    short_name: str  # パレット表示用の短縮名


class DevicePalette:
    """デバイスパレット管理クラス"""
    
    def __init__(self, config: PyPlcConfig):
        """デバイスパレット初期化"""
        self.config = config
        
        # パレット定義（10x2段 = 20デバイス）
        self.palette_devices = self._initialize_palette_devices()
        
        # 選択状態管理
        self.current_row = PaletteRow.TOP
        self.selected_device_index = 0  # 0-9の範囲
        
        # ===== パレット表示定数 =====
        # デバイスアイコンサイズ
        self.DEVICE_ICON_WIDTH = 24     # デバイスアイコンの幅
        self.DEVICE_ICON_HEIGHT = 8     # デバイスアイコンの高さ（背景矩形サイズ）
        
        # パレットレイアウト
        self.DEVICE_SPACING_X = 2       # デバイス間の横スペース
        self.ROW_SPACING_Y = 12         # 段間の縦スペース（段の配置間隔）
        self.PALETTE_MARGIN_TOP = 12    # パレット上部マージン
        self.PALETTE_MARGIN_BOTTOM = 8  # パレット下部マージン（グリッドとの間）
        
        # キー番号表示
        self.KEY_NUMBER_OFFSET_Y = -8   # キー番号表示のYオフセット（パレット上部）
        
        # インジケーター
        self.INDICATOR_WIDTH = 12       # 左側インジケーター（「>」）の幅
        
        # ===== 計算用定数（派生値） =====
        # 段間の空白スペース = ROW_SPACING_Y - DEVICE_ICON_HEIGHT
        self.ROW_BLANK_SPACE = self.ROW_SPACING_Y - self.DEVICE_ICON_HEIGHT  # = 4px
    
    def _initialize_palette_devices(self) -> List[List[PaletteDevice]]:
        """パレットデバイス定義初期化"""
        # 上段（1-0キー）: 基本デバイス
        top_row = [
            PaletteDevice(DeviceType.CONTACT_A, "A Contact", "A_DEV"),
            PaletteDevice(DeviceType.CONTACT_B, "B Contact", "B_DEV"),
            PaletteDevice(DeviceType.COIL, "Output Coil", "COIL"),
            PaletteDevice(DeviceType.INCOIL, "Input Coil", "OUT_S"),
            PaletteDevice(DeviceType.OUTCOIL_REV, "Reverse Coil", "OUT_R"),
            PaletteDevice(DeviceType.TIMER, "Timer", "TIMER"),
            PaletteDevice(DeviceType.COUNTER, "Counter", "COUNT"),
            PaletteDevice(DeviceType.LINK_UP, "Link Up", "L_UP"),
            PaletteDevice(DeviceType.LINK_DOWN, "Link Down", "L_DN"),
            PaletteDevice(DeviceType.DEL, "Delete", "DEL")
        ]
        
        # 下段（Shift+1-0キー）: 拡張デバイス（将来用）
        bottom_row = [
            PaletteDevice(DeviceType.WIRE_H, "Horizontal Wire", "W_H"),
            PaletteDevice(DeviceType.WIRE_V, "Vertical Wire", "W_V"),
            PaletteDevice(DeviceType.EMPTY, "Empty", "EMTY"),
            PaletteDevice(DeviceType.EMPTY, "Reserved", "RSV4"),
            PaletteDevice(DeviceType.EMPTY, "Reserved", "RSV5"),
            PaletteDevice(DeviceType.EMPTY, "Reserved", "RSV6"),
            PaletteDevice(DeviceType.EMPTY, "Reserved", "RSV7"),
            PaletteDevice(DeviceType.EMPTY, "Reserved", "RSV8"),
            PaletteDevice(DeviceType.EMPTY, "Reserved", "RSV9"),
            PaletteDevice(DeviceType.EMPTY, "Reserved", "RSV0")
        ]
        
        return [top_row, bottom_row]
    
    def handle_key_input(self) -> bool:
        """
        キー入力処理
        
        Returns:
            bool: 選択状態が変更された場合True
        """
        changed = False
        
        # Shiftキーでの段切り替え（上段⇔下段）
        if pyxel.btnp(pyxel.KEY_LSHIFT) or pyxel.btnp(pyxel.KEY_RSHIFT):
            self.current_row = PaletteRow.BOTTOM if self.current_row == PaletteRow.TOP else PaletteRow.TOP
            changed = True
        
        # 1-9キーでのデバイス選択
        for i in range(1, 10):
            if pyxel.btnp(getattr(pyxel, f"KEY_{i}")):
                self.selected_device_index = i - 1
                changed = True
                break
        
        # 0キーでの10番目のデバイス選択
        if pyxel.btnp(pyxel.KEY_0):
            self.selected_device_index = 9
            changed = True
        
        return changed
    
    def handle_mouse_input(self) -> bool:
        """
        マウス入力処理（パレットクリック選択）
        
        Returns:
            bool: 選択状態が変更された場合True
        """
        changed = False
        
        # 左クリック時のみ処理
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mouse_x = pyxel.mouse_x
            mouse_y = pyxel.mouse_y
            
            # パレット領域内のクリック判定
            palette_y = self.config.palette_y
            palette_start_x = self.config.grid_origin_x
            
            # 上段・下段の両方をチェック（マージン適用）
            for row_idx in range(2):
                row_y = palette_y + self.PALETTE_MARGIN_TOP + row_idx * self.ROW_SPACING_Y
                
                # マウスY座標がこの段の範囲内かチェック
                if row_y <= mouse_y <= row_y + self.DEVICE_ICON_HEIGHT:
                    
                    # デバイスアイコン上のクリック判定
                    for i in range(10):
                        device_x = palette_start_x + i * (self.DEVICE_ICON_WIDTH + self.DEVICE_SPACING_X)
                        
                        # マウスX座標がこのデバイスの範囲内かチェック
                        if device_x <= mouse_x <= device_x + self.DEVICE_ICON_WIDTH:
                            # クリックされたデバイスを選択
                            self.current_row = PaletteRow.TOP if row_idx == 0 else PaletteRow.BOTTOM
                            self.selected_device_index = i
                            changed = True
                            break
                
                if changed:
                    break
        
        return changed
    
    def get_selected_device(self) -> PaletteDevice:
        """現在選択されているデバイスを取得"""
        return self.palette_devices[self.current_row.value][self.selected_device_index]
    
    def draw_palette(self, renderer_instance) -> None:
        """
        デバイスパレット描画（10x2段 + 左側インジケーター）
        
        Args:
            renderer_instance: PyPlcRendererインスタンス
        """
        palette_y = self.config.palette_y
        indicator_x = self.config.grid_origin_x - self.INDICATOR_WIDTH
        palette_start_x = self.config.grid_origin_x
        
        # 上段と下段の両方を描画（上下マージン適用）
        for row_idx in range(2):
            row_y = palette_y + self.PALETTE_MARGIN_TOP + row_idx * self.ROW_SPACING_Y
            devices = self.palette_devices[row_idx]
            
            # 段インジケーター描画（「>」マーク）
            if self.current_row.value == row_idx:
                pyxel.text(indicator_x, row_y + 2, ">", pyxel.COLOR_YELLOW)
            
            # この段のデバイス描画
            for i, device in enumerate(devices):
                x = palette_start_x + i * (self.DEVICE_ICON_WIDTH + self.DEVICE_SPACING_X)
                
                # 選択状態の背景色（現在の段かつ選択中のデバイス）
                if (self.current_row.value == row_idx and i == self.selected_device_index):
                    pyxel.rect(x - 1, row_y - 1, self.DEVICE_ICON_WIDTH + 2, self.DEVICE_ICON_HEIGHT + 2, pyxel.COLOR_YELLOW)
                
                # デバイス背景
                pyxel.rect(x, row_y, self.DEVICE_ICON_WIDTH, self.DEVICE_ICON_HEIGHT, pyxel.COLOR_DARK_BLUE)
                
                # デバイス短縮名表示（小さめフォント用に調整）
                text_x = x + 1
                text_y = row_y + 1
                pyxel.text(text_x, text_y, device.short_name[:5], pyxel.COLOR_WHITE)  # 5文字まで
        
        # キー番号表示（上段のみ、パレット上部に表示）
        for i in range(10):
            key_num = str(i + 1) if i < 9 else "0"
            num_x = palette_start_x + i * (self.DEVICE_ICON_WIDTH + self.DEVICE_SPACING_X) + self.DEVICE_ICON_WIDTH // 2 - 2
            num_y = palette_y + self.PALETTE_MARGIN_TOP + self.KEY_NUMBER_OFFSET_Y
            pyxel.text(num_x, num_y, key_num, pyxel.COLOR_LIME)
        
        # 操作説明
        help_y = palette_y + self.PALETTE_MARGIN_TOP + 2 * self.ROW_SPACING_Y + self.PALETTE_MARGIN_BOTTOM
        pyxel.text(palette_start_x, help_y, "1-0:Select Device  SHIFT:Switch Row", pyxel.COLOR_GRAY)


class PlacementSystem:
    """デバイス配置システム統合クラス"""
    
    def __init__(self, config: PyPlcConfig):
        """配置システム初期化"""
        self.config = config
        self.device_palette = DevicePalette(config)
        self.grid_manager = None  # GridDeviceManagerは後でセットされる
        
        # 配置状態管理
        self.placement_enabled = True
        self.preview_position: Optional[Tuple[int, int]] = None
        
        # テスト出力管理
        self.debug_output_timer = 0
        self.last_click_info = None  # 最後のクリック情報
        
        # 配置結果フィードバック
        self.placement_feedback = None  # 配置結果メッセージ
        self.feedback_timer = 0         # フィードバック表示タイマー
    
    def set_grid_manager(self, grid_manager) -> None:
        """GridDeviceManagerを設定"""
        self.grid_manager = grid_manager
    
    def update(self) -> bool:
        """
        配置システム更新
        
        Returns:
            bool: 状態が変更された場合True
        """
        # パレット入力処理
        palette_key_changed = self.device_palette.handle_key_input()
        
        # パレットマウス処理
        palette_mouse_changed = self.device_palette.handle_mouse_input()
        
        # グリッドマウス処理（将来実装）
        # grid_mouse_changed = self._handle_grid_mouse_input()
        
        # グリッドマウス処理
        grid_mouse_changed = self._handle_grid_mouse_input()
        
        # テスト出力タイマー更新
        if self.debug_output_timer > 0:
            self.debug_output_timer -= 1
        
        return palette_key_changed or palette_mouse_changed or grid_mouse_changed
    
    def get_selected_device_type(self) -> DeviceType:
        """現在選択されているデバイスタイプを取得"""
        return self.device_palette.get_selected_device().device_type
    
    def get_selected_device_info(self) -> PaletteDevice:
        """現在選択されているデバイス情報を取得"""
        return self.device_palette.get_selected_device()
    
    def draw(self, renderer_instance) -> None:
        """配置システム描画"""
        # デバイスパレット描画
        self.device_palette.draw_palette(renderer_instance)
        
        # プレビュー描画（将来実装）
        # self._draw_placement_preview(renderer_instance)
        
        # 座標デバッグ出力描画
        if self.debug_output_timer > 0:
            self._draw_debug_info()
    
    def _handle_grid_mouse_input(self) -> bool:
        """
        グリッドマウス処理（配置・座標変換テスト）
        
        Returns:
            bool: 状態が変更された場合True
        """
        changed = False
        
        # 左クリック時のみ処理
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mouse_x = pyxel.mouse_x
            mouse_y = pyxel.mouse_y
            
            # マウス座標→グリッド座標変換
            grid_pos = self._convert_mouse_to_grid(mouse_x, mouse_y)
            
            if grid_pos:
                grid_row, grid_col = grid_pos
                
                # デバッグ出力（座標変換テスト）
                self._output_coordinate_debug(mouse_x, mouse_y, grid_row, grid_col)
                
                # グリッド範囲内かつ編集可能領域チェック
                if self._is_valid_placement_position(grid_row, grid_col):
                    # 選択されているデバイス情報取得
                    selected_device = self.device_palette.get_selected_device()
                    
                    # 実際のデバイス配置処理
                    if self.grid_manager is not None:
                        # DELデバイスの場合は削除処理
                        if selected_device.device_type == DeviceType.DEL:
                            success = self.grid_manager.remove_device(grid_row, grid_col)
                            if success:
                                print(f"[PLACEMENT] デバイス削除成功: ({grid_row}, {grid_col})")
                            else:
                                print(f"[PLACEMENT] デバイス削除失敗: ({grid_row}, {grid_col})")
                        else:
                            # 通常デバイスの配置処理
                            success = self.grid_manager.place_device(grid_row, grid_col, selected_device.device_type)
                            if success:
                                print(f"[PLACEMENT] デバイス配置成功: {selected_device.short_name} at ({grid_row}, {grid_col})")
                            else:
                                print(f"[PLACEMENT] デバイス配置失敗: {selected_device.short_name} at ({grid_row}, {grid_col})")
                        
                        changed = True
                    else:
                        print(f"[PLACEMENT] GridDeviceManager未設定")
                else:
                    print(f"[PLACEMENT] 配置不可能位置: ({grid_row}, {grid_col})")
        
        return changed
    
    def _convert_mouse_to_grid(self, mouse_x: int, mouse_y: int) -> Optional[Tuple[int, int]]:
        """
        マウス座標をグリッド座標に変換
        
        Args:
            mouse_x: マウスX座標
            mouse_y: マウスY座標
            
        Returns:
            Optional[Tuple[int, int]]: グリッド座標(row, col) または None
        """
        # グリッド原点からの相対座標計算
        relative_x = mouse_x - self.config.grid_origin_x
        relative_y = mouse_y - self.config.grid_origin_y
        
        # グリッド範囲外チェック
        if relative_x < 0 or relative_y < 0:
            return None
        
        # グリッド座標計算
        grid_col = relative_x // self.config.grid_cell_size  # X座標→列
        grid_row = relative_y // self.config.grid_cell_size  # Y座標→行
        
        # グリッド範囲チェック
        if (0 <= grid_row < self.config.grid_rows and 
            0 <= grid_col < self.config.grid_cols):
            return (grid_row, grid_col)
        
        return None
    
    def _is_valid_placement_position(self, grid_row: int, grid_col: int) -> bool:
        """
        デバイス配置可能位置チェック
        
        Args:
            grid_row: グリッド行（Y座標）
            grid_col: グリッド列（X座標）
            
        Returns:
            bool: 配置可能な場合True
        """
        # 編集可能領域取得 (start_col, end_col, start_row, end_row)
        start_col, end_col, start_row, end_row = self.config.get_editable_area()
        
        # 編集可能領域内チェック
        return (start_row <= grid_row <= end_row and 
                start_col <= grid_col <= end_col)
    
    def _output_coordinate_debug(self, mouse_x: int, mouse_y: int, 
                                 grid_row: int, grid_col: int) -> None:
        """
        座標変換デバッグ出力
        
        Args:
            mouse_x: マウスX座標
            mouse_y: マウスY座標  
            grid_row: グリッド行
            grid_col: グリッド列
        """
        # デバッグ出力タイマー設定（60フレーム = 1秒表示）
        self.debug_output_timer = 60
        
        # 最新のクリック情報を保存
        self.last_click_info = {
            'mouse_pos': (mouse_x, mouse_y),
            'grid_pos': (grid_row, grid_col),
            'valid_placement': self._is_valid_placement_position(grid_row, grid_col),
            'selected_device': self.device_palette.get_selected_device().short_name
        }
        
        # コンソール出力
        print(f"[座標変換テスト]")
        print(f"  マウス座標: ({mouse_x}, {mouse_y})")
        print(f"  グリッド座標: row={grid_row}, col={grid_col}")
        print(f"  配列アクセス: grid[{grid_row}][{grid_col}]  # [y座標][x座標]")
        
        # グリッド原点情報
        print(f"  グリッド原点: ({self.config.grid_origin_x}, {self.config.grid_origin_y})")
        print(f"  セルサイズ: {self.config.grid_cell_size}px")
        
        # 編集可能領域情報
        start_col, end_col, start_row, end_row = self.config.get_editable_area()
        print(f"  編集可能領域: rows {start_row}-{end_row}, cols {start_col}-{end_col}")
        print(f"  配置可能: {self._is_valid_placement_position(grid_row, grid_col)}")
        print("-" * 50)
    
    def _draw_debug_info(self) -> None:
        """画面上にデバッグ情報を描画"""
        if hasattr(self, 'last_click_info'):
            info = self.last_click_info
            debug_y = self.config.status_area_y + 20
            
            # デバッグ情報表示
            pyxel.text(16, debug_y, f"Mouse: {info['mouse_pos']}", pyxel.COLOR_YELLOW)
            pyxel.text(16, debug_y + 8, f"Grid: {info['grid_pos']}", pyxel.COLOR_YELLOW)
            pyxel.text(16, debug_y + 16, f"Valid: {info['valid_placement']}", 
                      pyxel.COLOR_GREEN if info['valid_placement'] else pyxel.COLOR_RED)
            pyxel.text(16, debug_y + 24, f"Device: {info['selected_device']}", pyxel.COLOR_CYAN)
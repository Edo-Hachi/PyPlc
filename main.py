# PyPlc Ver3 - Clean Implementation Start
# 作成日: 2025-01-29
# 目標: PLC標準仕様完全準拠ラダー図シミュレーター

#Todo
#Virtical Curcuit > Branch CirCuitへの変更箇所をレビューする
#Save,Load時のファイル名のDLGを実装する（Ver2で実装したDLGシステムを参考に）
#SpraiteDefinerわりとバグ多いので、どっかで見直す


import pyxel
from config import DisplayConfig, SystemInfo, UIConfig, UIBehaviorConfig, DeviceType, SimulatorMode, PLCRunState
from core.grid_system import GridSystem
from core.input_handler import InputHandler, MouseState
from core.circuit_analyzer import CircuitAnalyzer
from core.device_palette import DevicePalette
from dialogs import DialogManager  # ダイアログシステム統合管理をインポート
from core.SpriteManager import sprite_manager # SpriteManagerをインポート

class PyPlcVer3:
    """PyPlc Ver3 - PLC標準仕様準拠シミュレーター"""
    
    def __init__(self):
        """アプリケーション初期化"""
        pyxel.init(
            DisplayConfig.WINDOW_WIDTH,
            DisplayConfig.WINDOW_HEIGHT,
            title=f"PyPlc Ver{SystemInfo.VERSION} - Circuit Solver",
            fps=DisplayConfig.TARGET_FPS,
            quit_key=pyxel.KEY_F12  # F12キーのみで終了、ESCキー無効化
        )
        pyxel.mouse(True)
        
        # SpriteManagerからリソースファイルをロード
        if sprite_manager.resource_file:
            pyxel.load(sprite_manager.resource_file)
        
        # --- モード管理システム (Ver1設計継承) ---
        self.current_mode = SimulatorMode.EDIT  # 起動時はEDITモード
        self.plc_run_state = PLCRunState.STOPPED  # 初期状態は停止中
        
        # --- モジュールのインスタンス化 ---
        self.grid_system = GridSystem()
        self.input_handler = InputHandler(self.grid_system)
        self.circuit_analyzer = CircuitAnalyzer(self.grid_system)
        self.device_palette = DevicePalette()  # デバイスパレット追加
        self.dialog_manager = DialogManager()  # ダイアログシステム統合管理
        
        self.mouse_state: MouseState = MouseState()
        
        pyxel.run(self.update, self.draw)
    
    def update(self) -> None:
        """フレーム更新処理"""
        # 1. 入力処理
        self.mouse_state = self.input_handler.update_mouse_state()
        if self.input_handler.check_quit_command():
            pyxel.quit()
        
        # Edit/Runモード切り替え (Ver1実装継承)
        self._handle_mode_switching()
        
        # F5キーでのPLC実行制御 (Ver1実装継承)
        self._handle_plc_control()
        
        # F6キーでの全システムリセット (Ver1実装継承)
        self._handle_full_system_reset()
        
        
        # デバイスパレット入力処理（EDITモードでのみ有効）
        if self.current_mode == SimulatorMode.EDIT:
            self.device_palette.update_input()
        
        # デバイス配置・接点操作処理（モード別分離）
        self._handle_device_placement()
        self._handle_device_operation()

        # 2. 論理演算 (通電解析) - PLC実行状態による制御
        if (self.current_mode == SimulatorMode.RUN and 
            self.plc_run_state == PLCRunState.RUNNING):
            # RUNモードかつPLC実行中の場合のみ回路解析実行
            self.circuit_analyzer.solve_ladder()
        # EDITモードまたはPLC停止中は回路解析を停止

    def _handle_device_placement(self) -> None:
        """
        マウス入力に基づき、デバイスの配置・削除・状態変更を行う
        設定対応: 常時スナップモード or CTRL切り替えモード
        Edit/Runモード対応: EDITモードでのみデバイス配置可能
        """
        # EDITモードでない場合はデバイス配置を無効化
        if self.current_mode != SimulatorMode.EDIT:
            return
        
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
        
        # 右クリック処理: EDITモードでのデバイスID編集ダイアログ表示
        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            device = self.grid_system.get_device(row, col)
            if device:
                self.dialog_manager.show_device_id_dialog(
                    device, row, col, 
                    self._draw_background_for_dialog,
                    self.grid_system
                )

    def _handle_device_operation(self) -> None:
        """
        RUNモードでのデバイス操作処理（右クリックでの状態切り替え）
        接点のON/OFF切り替えが可能
        """
        # RUNモードでない場合は接点操作を無効化（将来的には制限を緩和予定）
        if self.current_mode != SimulatorMode.RUN:
            return
        
        # スナップモードが有効でない場合は何もしない
        if not self.mouse_state.snap_mode:
            return
            
        # スナップ状態でない、または編集可能領域でない場合は何もしない
        if self.mouse_state.hovered_pos is None or not self.mouse_state.is_snapped or not self.mouse_state.on_editable_area:
            return

        row, col = self.mouse_state.hovered_pos
        
        # 右クリックでデバイス状態切り替え（接点のON/OFF操作）
        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            device = self.grid_system.get_device(row, col)
            if device and self._is_operable_device(device):
                device.state = not device.state

    def _is_operable_device(self, device) -> bool:
        """
        RUNモードで操作可能なデバイスかどうかを判定
        主に接点系デバイス（CONTACT_A, CONTACT_B）が対象
        """
        operable_types = {
            DeviceType.CONTACT_A,  # A接点
            DeviceType.CONTACT_B,  # B接点
            # 将来的にタイマー、カウンターなども追加予定
        }
        return device.device_type in operable_types

    def draw(self) -> None:
        """描画処理"""
        # 3. 描画処理
        pyxel.cls(pyxel.COLOR_BLACK)
        
        # デバイスパレット描画（最初に描画）- モード別表示制御
        if self.current_mode == SimulatorMode.EDIT:
            self.device_palette.draw()
        else:
            # RUNモード時は編集不可メッセージを表示
            self._draw_palette_disabled_message()
        
        # グリッドシステム描画
        self.grid_system.draw()
        
        # RUNモード時のデバイス情報表示（マウスオーバー）
        # if self.current_mode == SimulatorMode.RUN:
        #     self._draw_device_info_on_hover()
        
        # UI情報描画
        self._draw_cursor_and_status()
        self._draw_mode_status_bar()  # Edit/Runモード状態表示追加
        self._draw_header_footer()

    def _draw_cursor_and_status(self) -> None:
        """
        マウスカーソルと詳細ステータス情報を描画する
        Ver2準拠: 詳細情報表示、スナップモード状態、操作ガイダンス
        """
        # ステータスバー背景描画（Ver2準拠の拡張表示領域）
        status_y = DisplayConfig.WINDOW_HEIGHT - (40 + 16)  # 高さ拡張（20→40）
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

            # デバイス情報表示: ホバーしているデバイスのstateとis_energizedを表示（EDIT/RUN共通）
            hovered_device = self.grid_system.get_device(row, col)
            if hovered_device:
                device_id = hovered_device.address if hovered_device.address else "N/A"
                device_debug_text = f"Device: {hovered_device.device_type.value} ID:{device_id} State:{hovered_device.state} Energized:{hovered_device.is_energized}"
                pyxel.text(10, status_y + 35, device_debug_text, pyxel.COLOR_WHITE)
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
        
        # フッター操作ガイド（設定に応じて表示切り替え）- 16px上に移動
        footer_y = DisplayConfig.WINDOW_HEIGHT - 60 #36  # -20から-36に変更（16px上に移動）
        if UIBehaviorConfig.ALWAYS_SNAP_MODE:
            pyxel.text(10, footer_y, "L-Click:Place/Del R-Click:Toggle F12:Quit", pyxel.COLOR_GRAY)
        else:
            pyxel.text(10, footer_y, "CTRL:Snap L-Click:Place/Del R-Click:Toggle F12:Quit", pyxel.COLOR_GRAY)

    def _handle_mode_switching(self) -> None:
        """
        Edit/Runモード切り替え処理 (Ver1設計継承)
        TABキーでEDIT ⇔ RUN切り替え
        """
        # TABキーでEDIT/RUN切り替え
        if pyxel.btnp(pyxel.KEY_TAB):
            if self.current_mode == SimulatorMode.EDIT:
                self.current_mode = SimulatorMode.RUN
                self.plc_run_state = PLCRunState.STOPPED  # RUNモードに入る時は停止状態から開始
            else:
                self.current_mode = SimulatorMode.EDIT
                self.plc_run_state = PLCRunState.STOPPED  # EDITモードに戻る時も停止状態
                self._reset_all_systems()  # EDITモードに戻る時はデバイス状態を初期化

    def _draw_mode_status_bar(self) -> None:
        """
        Edit/Runモード状態表示バー描画 (Ver1設計継承)
        画面上部にモード情報とPLC実行状態を表示
        """
        # ステータスバー背景描画（画面上部）
        status_bar_y = 2
        status_bar_height = 8
        pyxel.rect(0, status_bar_y, DisplayConfig.WINDOW_WIDTH, status_bar_height, pyxel.COLOR_NAVY)
        
        # モード表示（右端）
        mode_text = f"Mode: {self.current_mode.value}"
        mode_color = pyxel.COLOR_YELLOW if self.current_mode == SimulatorMode.EDIT else pyxel.COLOR_LIME
        mode_x = DisplayConfig.WINDOW_WIDTH - len(mode_text) * 4 - 10  # 右端から10px余白
        pyxel.text(mode_x, status_bar_y + 2, mode_text, mode_color)
        
        # PLC実行状態表示（中央）
        if self.current_mode == SimulatorMode.RUN:
            plc_text = f"PLC: {self.plc_run_state.value}"
            plc_color = pyxel.COLOR_LIME if self.plc_run_state == PLCRunState.RUNNING else pyxel.COLOR_RED
            plc_x = DisplayConfig.WINDOW_WIDTH // 2 - len(plc_text) * 2  # 中央配置
            pyxel.text(plc_x, status_bar_y + 2, plc_text, plc_color)
            
            # F5キーヒント表示（PLC状態の隣）
            hint_text = " F5:Start" if self.plc_run_state == PLCRunState.STOPPED else " F5:Stop"
            pyxel.text(plc_x + len(plc_text) * 4, status_bar_y + 2, hint_text, pyxel.COLOR_CYAN)
        
        # TABキーヒント表示（左端）
        tab_hint = "TAB:Mode F6:Reset Ctrl+S:Save Ctrl+O:Load"
        pyxel.text(10, status_bar_y + 2, tab_hint, pyxel.COLOR_WHITE)

    def _handle_plc_control(self) -> None:
        """
        F5キーでのPLC実行制御処理 (Ver1設計継承)
        RUNモード時のみF5キーでSTOPPED ⇔ RUNNING切り替え
        """
        # F5キーでのPLC制御（RUNモードのみ）
        if pyxel.btnp(pyxel.KEY_F5) and self.current_mode == SimulatorMode.RUN:
            if self.plc_run_state == PLCRunState.STOPPED:
                self.plc_run_state = PLCRunState.RUNNING
            else:
                self.plc_run_state = PLCRunState.STOPPED
                self._reset_all_systems()  # 停止時は全システムリセット

    def _handle_full_system_reset(self) -> None:
        """
        F6キーでの全システムリセット処理 (Ver1設計継承)
        デバイス配置を維持したまま、状態のみを完全初期化
        """
        # F6キーでの全システムリセット（モード制限なし）
        if pyxel.btnp(pyxel.KEY_F6):
            # PLC実行状態を停止に
            self.plc_run_state = PLCRunState.STOPPED
            
            # 全システムリセット実行
            self._reset_all_systems()
            
            # デバイス個別状態のリセット（接点のON/OFF状態など）
            self._reset_all_device_states()

    def _reset_all_systems(self) -> None:
        """
        F5ストップ時・EDITモード復帰時の全システムリセット (Ver1設計継承)
        全デバイス・回路状態を初期状態に戻す
        """
        # グリッドシステムの全デバイス通電状態リセット
        self.grid_system.reset_all_energized_states()
        
        # 追加のリセット処理（将来拡張時）
        # - タイマー・カウンターの値リセット
        # - 内部リレー状態リセット
        # - エラー状態クリア

    def _reset_all_device_states(self) -> None:
        """
        全デバイスの個別状態をリセット（F6キー専用）
        配置は維持、状態のみ初期化（接点のON/OFF等）
        """
        for row in range(self.grid_system.rows):
            for col in range(self.grid_system.cols):
                device = self.grid_system.get_device(row, col)
                if device:
                    # デバイスの個別状態を初期値に戻す
                    device.state = False  # 接点のON/OFF状態をOFFに
                    # 将来的にタイマー・カウンターの現在値もリセット


    def _draw_device_info_on_hover(self) -> None:
        """
        RUNモード時のマウスオーバーデバイス情報表示
        マウス位置のデバイス情報（アドレス、状態）を画面に表示
        """
        # マウス座標を取得
        mouse_x = pyxel.mouse_x
        mouse_y = pyxel.mouse_y
        
        # マウス座標をグリッド座標に変換
        grid_x = (mouse_x - self.grid_system.origin_x) // self.grid_system.cell_size
        grid_y = (mouse_y - self.grid_system.origin_y) // self.grid_system.cell_size
        
        # グリッド範囲内かチェック
        if (0 <= grid_y < self.grid_system.rows and 
            0 <= grid_x < self.grid_system.cols):
            
            # 該当位置のデバイスを取得
            device = self.grid_system.get_device(grid_y, grid_x)
            
            if device and device.device_type not in [DeviceType.L_SIDE, DeviceType.R_SIDE]:
                # デバイス情報を構築
                device_info = []
                
                # Device type display
                device_type_name = {
                    DeviceType.CONTACT_A: "A_Contact",
                    DeviceType.CONTACT_B: "B_Contact", 
                    DeviceType.COIL_STD: "Std_Coil",
                    DeviceType.COIL_REV: "Rev_Coil",
                    DeviceType.LINK_HORZ: "H_Link",
                    DeviceType.LINK_BRANCH: "Branch",
                    DeviceType.LINK_VIRT: "V_Link"
                }.get(device.device_type, device.device_type.value)
                
                device_info.append(f"Type: {device_type_name}")
                
                # デバイスID表示（必ず表示）
                device_id = device.address if device.address and device.address.strip() else "N/A"
                device_info.append(f"ID: {device_id}")
                
                # 状態表示
                if device.device_type in [DeviceType.CONTACT_A, DeviceType.CONTACT_B]:
                    state_text = "ON" if device.state else "OFF"
                    device_info.append(f"State: {state_text}")
                elif device.device_type in [DeviceType.COIL_STD, DeviceType.COIL_REV]:
                    energized_text = "Energized" if device.is_energized else "De-energized"
                    device_info.append(f"Status: {energized_text}")
                
                # Power state display (all devices)
                power_text = "Powered" if device.is_energized else "No_Power"
                device_info.append(f"Power: {power_text}")
                
                # 情報ボックスの描画位置を計算
                info_x = mouse_x + 10
                info_y = mouse_y - 10
                
                # 画面端での位置調整
                max_width = max(len(line) * 4 for line in device_info) + 8
                if info_x + max_width > DisplayConfig.WINDOW_WIDTH:
                    info_x = mouse_x - max_width - 10
                
                info_height = len(device_info) * 8 + 4
                if info_y < 0:
                    info_y = mouse_y + 20
                elif info_y + info_height > DisplayConfig.WINDOW_HEIGHT:
                    info_y = DisplayConfig.WINDOW_HEIGHT - info_height
                
                # 情報ボックス背景描画
                pyxel.rect(info_x - 2, info_y - 2, max_width, info_height, pyxel.COLOR_DARK_BLUE)
                pyxel.rectb(info_x - 2, info_y - 2, max_width, info_height, pyxel.COLOR_WHITE)
                
                # デバイス情報テキスト描画
                for i, line in enumerate(device_info):
                    pyxel.text(info_x, info_y + i * 8, line, pyxel.COLOR_WHITE)

    def _draw_palette_disabled_message(self) -> None:
        """
        RUNモード時のデバイスパレット無効化メッセージ表示
        デバイスパレットエリアに編集不可であることを明示
        """
        # パレットエリアの位置情報（config.pyから取得）
        palette_y = UIConfig.PALETTE_Y
        palette_width = 280  # パレット幅の概算
        palette_height = 25  # パレット高さの概算
        
        # 背景を暗い色で塗りつぶし（Pyxel色定数を正しく使用）
        pyxel.rect(16, palette_y, palette_width, palette_height, pyxel.COLOR_DARK_BLUE)
        
        # 編集不可メッセージを中央に表示
        message = "Device Palette: Disabled in RUN Mode"
        message_x = 16 + (palette_width - len(message) * 4) // 2  # 中央揃え
        message_y = palette_y + 8
        pyxel.text(message_x, message_y, message, pyxel.COLOR_WHITE)
        
        # 追加ヒント表示
        hint = "Press TAB to return to EDIT mode"
        hint_x = 16 + (palette_width - len(hint) * 4) // 2  # 中央揃え
        hint_y = palette_y + 16
        pyxel.text(hint_x, hint_y, hint, pyxel.COLOR_GRAY)

    def _draw_background_for_dialog(self) -> None:
        """
        ダイアログ表示中のバックグラウンド描画
        ダイアログのモーダル効果のため、現在の画面状態を描画
        """
        # 通常の描画処理を実行（ダイアログ以外）
        pyxel.cls(pyxel.COLOR_BLACK)
        
        # デバイスパレット描画
        if self.current_mode == SimulatorMode.EDIT:
            self.device_palette.draw()
        else:
            self._draw_palette_disabled_message()
        
        # グリッドシステム描画
        self.grid_system.draw()
        
        # UI情報描画（ダイアログ以外）
        self._draw_cursor_and_status()
        self._draw_mode_status_bar()
        self._draw_header_footer()

if __name__ == "__main__":
    PyPlcVer3()
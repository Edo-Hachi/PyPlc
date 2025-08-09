# PyPlc Ver3 - Clean Implementation Start
# 作成日: 2025-07-29
# 目標: PLC標準仕様完全準拠ラダー図シミュレーター

#重要！
# Pyxelは２バイト文字扱えないので１バイト文字のみ使用。絵文字も不可能
# コメントには日本語を使用する。絵文字は使わない！

# .vscode/以下に実行環境の記載があるので、参照してください


#Todo
#OK Timer Counterのアドレスを編集できるように ✅完了
#OK RSTの実装 ✅完了（Phase 1基本動作 + Phase 2 ZRST範囲リセット）

# OK !編集中のファイル名が確定しているなら、セーブするときにそのファイル名を使う

#SpraiteDefinerわりとバグ多いので、どっかで見直す


import pyxel
from config import DisplayConfig, SystemInfo, UIConfig, UIBehaviorConfig, DeviceType, SimulatorMode, PLCRunState, TimerConfig, CounterConfig
from core.grid_system import GridSystem
from core.input_handler import InputHandler, MouseState
from core.circuit_analyzer import CircuitAnalyzer
from core.device_palette import DevicePalette
from core.circuit_csv_manager import CircuitCsvManager  # CSV管理システムをインポート
# 古いdialogs/システムは削除済み（Phase Cで完全移行）
from DialogManager.new_dialog_manager import NewDialogManager  # 新DialogManagerシステム
from DialogManager.new_file_dialog_manager import NewFileDialogManager  # 新FileDialogManagerシステム
from core.SpriteManager import sprite_manager # SpriteManagerをインポート
from DialogManager.integration_test_dialog import show_integration_test_dialog  # Phase 1統合テスト用
from DialogManager.phase2_integration_test import show_phase2_integration_test_dialog  # Phase 2統合テスト用
from DialogManager.phase3_integration_test import run_phase3_test  # Phase 3統合テスト用
from DialogManager.file_load_dialog_json import FileLoadDialogJSON  # Phase 3実装

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
        self.csv_manager = CircuitCsvManager(self.grid_system)  # CSV管理システム追加
        # 新DialogManagerシステム（Phase C完全移行）
        self.dialog_manager = NewDialogManager()  # 新DialogManagerシステム
        self.file_dialog_manager = NewFileDialogManager(self.csv_manager)  # 新FileDialogManagerシステム
        
        self.mouse_state: MouseState = MouseState()

        # --- LINK_HORZ ドラッグ配置用フラグ (Phase D) ---
        self.is_dragging_link = False
        self.drag_start_pos = None
        self.last_drag_pos = None
        # --- ここまで ---
        
        # --- メッセージ表示システム ---
        self.status_message = ""  # 表示中のメッセージ
        self.status_message_timer = 0  # メッセージ表示残り時間（フレーム数）
        
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
        
        # Ctrl+S: ファイル保存ダイアログ表示（EDITモードのみ）
        if pyxel.btn(pyxel.KEY_CTRL) and pyxel.btnp(pyxel.KEY_S):
            if self.current_mode == SimulatorMode.EDIT:
                self.file_dialog_manager.show_save_dialog()
            else:
                self._show_status_message("Save: EDIT mode only. Press TAB to switch.", 4.0)
            
        # Ctrl+O: ファイル読み込みダイアログ表示（EDITモードのみ）
        if pyxel.btn(pyxel.KEY_CTRL) and pyxel.btnp(pyxel.KEY_O):
            if self.current_mode == SimulatorMode.EDIT:
                self.file_dialog_manager.show_load_dialog()
            else:
                self._show_status_message("Load: EDIT mode only. Press TAB to switch.", 4.0)
        
        # T: Phase 1統合テスト - 新ダイアログシステムのテスト
        if pyxel.btnp(pyxel.KEY_T):
            print("🚀 Phase 1 Integration Test: Showing test dialog...")
            result = show_integration_test_dialog()
            print(f"📋 Integration Test Result: {result}")
        
        # U: Phase 2統合テスト - DeviceIDDialogJSONのテスト
        if pyxel.btnp(pyxel.KEY_U):
            print("🚀 Phase 2 Integration Test: Showing DeviceIDDialogJSON...")
            result = show_phase2_integration_test_dialog()
            print(f"📋 Phase 2 Integration Test Result: {result}")
        
        # V: Phase 3統合テスト - FileListControlのテスト
        if pyxel.btnp(pyxel.KEY_V):
            print("🚀 Phase 3 Integration Test: FileListControl Test...")
            run_phase3_test()
        
        # W: Phase 3実装テスト - FileLoadDialogJSONの実動作テスト
        if pyxel.btnp(pyxel.KEY_W):
            print("🚀 Phase 3 Implementation Test: Showing FileLoadDialogJSON...")
            dialog = FileLoadDialogJSON()
            success, file_path = dialog.show_load_dialog()
            print(f"📋 FileLoadDialog Result: success={success}, file_path='{file_path}'")
        
        # デバイスパレット入力処理（EDITモードでのみ有効）
        if self.current_mode == SimulatorMode.EDIT:
            self.device_palette.update_input()
        
        # デバイス配置・接点操作処理（モード別分離）
        self._handle_device_placement()
        self._handle_link_dragging() # ドラッグ処理を呼び出す (Phase D)
        self._handle_device_operation()

        # 2. 論理演算 (通電解析) - PLC実行状態による制御
        if (self.current_mode == SimulatorMode.RUN and 
            self.plc_run_state == PLCRunState.RUNNING):
            # RUNモードかつPLC実行中の場合のみ回路解析実行
            self.circuit_analyzer.solve_ladder()
        # EDITモードまたはPLC停止中は回路解析を停止
        
        # 3. ステータスメッセージ更新
        self._update_status_message()

    def _handle_device_placement(self) -> None:
        """
        マウス入力に基づき、デバイスの配置・削除・状態変更を行う
        LINK_HORZのドラッグ配置に対応 (Phase D)
        """
        if self.current_mode != SimulatorMode.EDIT:
            return
        if not self.mouse_state.snap_mode:
            return
        if self.mouse_state.hovered_pos is None or not self.mouse_state.is_snapped or not self.mouse_state.on_editable_area:
            return

        row, col = self.mouse_state.hovered_pos
        selected_device_type = self.device_palette.get_selected_device_type()

        # --- ドラッグ開始処理 (Phase D) ---
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if selected_device_type == DeviceType.LINK_HORZ:
                self.is_dragging_link = True
                self.drag_start_pos = (row, col)
                self.last_drag_pos = (row, col)
                self.grid_system.place_device(row, col, selected_device_type, "")
                return

            # --- 通常の単一配置処理 ---
            device = self.grid_system.get_device(row, col)
            
            if device:
                if selected_device_type == DeviceType.DEL:
                    self.grid_system.remove_device(row, col)
                else:
                    self.grid_system.remove_device(row, col)
                    if selected_device_type != DeviceType.EMPTY:
                        self._place_single_device(row, col, selected_device_type)
            else:
                if selected_device_type not in [DeviceType.DEL, DeviceType.EMPTY]:
                    self._place_single_device(row, col, selected_device_type)
        
        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            device = self.grid_system.get_device(row, col)
            if device:
                self.dialog_manager.show_device_edit_dialog(
                    device, row, col, 
                    self._draw_background_for_dialog,
                    self.grid_system
                )

    def _place_single_device(self, row: int, col: int, device_type: DeviceType) -> None:
        """単一のデバイスを配置するヘルパーメソッド"""
        # 配線系デバイスかどうかを判定
        is_link_device = device_type in [DeviceType.LINK_HORZ, DeviceType.LINK_VIRT, DeviceType.LINK_BRANCH]
        
        # 配線系デバイスならアドレスは空、それ以外は生成
        address = "" if is_link_device else self._generate_default_address(device_type, row, col)
        
        new_device = self.grid_system.place_device(row, col, device_type, address)
        
        # タイマー・カウンターのデフォルト値設定
        if new_device:
            if device_type == DeviceType.TIMER_TON:
                new_device.preset_value = TimerConfig.DEFAULT_PRESET
            elif device_type == DeviceType.COUNTER_CTU:
                new_device.preset_value = CounterConfig.DEFAULT_PRESET

    def _handle_link_dragging(self) -> None:
        """
        LINK_HORZのドラッグ中の配置処理 (Phase D)
        """
        if not self.is_dragging_link:
            return

        # マウスボタンが押されている間のみ処理
        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            if self.mouse_state.hovered_pos is not None and self.mouse_state.on_editable_area:
                current_row, current_col = self.mouse_state.hovered_pos
                start_row, start_col = self.drag_start_pos
                
                # 同じ行でのドラッグ、かつ位置が変わった場合のみ処理
                if current_row == start_row and (current_row, current_col) != self.last_drag_pos:
                    # 開始列と現在列の間のすべてのセルに配置
                    col_start = min(start_col, current_col)
                    col_end = max(start_col, current_col)
                    
                    for col in range(col_start, col_end + 1):
                        # 既存デバイスがない場合のみ配置（上書きしない）
                        if not self.grid_system.get_device(start_row, col):
                            self.grid_system.place_device(start_row, col, DeviceType.LINK_HORZ, "")
                    
                    self.last_drag_pos = (current_row, current_col)
        
        # マウスボタンを離した時にドラッグ終了
        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            self.is_dragging_link = False
            self.drag_start_pos = None
            self.last_drag_pos = None
            # 回路全体を再解析
            self.circuit_analyzer.solve_ladder()

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
    
    def _show_status_message(self, message: str, duration_seconds: float = 3.0) -> None:
        """
        ステータスメッセージを表示する
        
        Args:
            message: 表示するメッセージ（1バイト文字のみ）
            duration_seconds: 表示時間（秒）
        """
        self.status_message = message
        self.status_message_timer = int(duration_seconds * DisplayConfig.TARGET_FPS)  # フレーム数に変換
    
    def _update_status_message(self) -> None:
        """
        ステータスメッセージのタイマー更新
        """
        if self.status_message_timer > 0:
            self.status_message_timer -= 1
            if self.status_message_timer <= 0:
                self.status_message = ""

    def _generate_default_address(self, device_type: DeviceType, row: int, col: int) -> str:
        """
        デバイスタイプに基づくユニークなデフォルトアドレス生成（PLC標準準拠）
        既存のアドレスと重複しないように、空きアドレスを自動検索する
        
        Args:
            device_type: デバイスタイプ
            row: グリッド行座標
            col: グリッド列座標
            
        Returns:
            str: 生成されたユニークなデフォルトアドレス
        """
        # デバイスタイプ別のプレフィックス決定
        if device_type in [DeviceType.CONTACT_A, DeviceType.CONTACT_B]:
            prefix = "X"
        elif device_type in [DeviceType.COIL_STD, DeviceType.COIL_REV]:
            prefix = "M"  # 内部リレー（自己保持回路で使用）
        elif device_type == DeviceType.TIMER_TON:
            prefix = "T"
        elif device_type == DeviceType.COUNTER_CTU:
            prefix = "C"
        elif device_type == DeviceType.RST:
            prefix = "T"  # RSTはタイマー/カウンターを対象
        elif device_type == DeviceType.ZRST:
            prefix = "T"  # ZRSTもタイマー/カウンターを対象
        else:
            return ""
        
        # 既存のアドレス一覧を取得
        existing_addresses = set()
        for r in range(self.grid_system.rows):
            for c in range(self.grid_system.cols):
                device = self.grid_system.get_device(r, c)
                if device and device.address:
                    existing_addresses.add(device.address.upper())
        
        # プレフィックス + 番号で空きアドレスを検索（001から開始）
        for i in range(1, 1000):  # X001-X999まで検索
            candidate = f"{prefix}{i:03d}"
            if candidate not in existing_addresses:
                return candidate
        
        # 見つからなければフォールバック（まず発生しない）
        return f"{prefix}999"

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
                
                # タイマー・カウンター詳細表示（PLC標準準拠）
                if hovered_device.device_type in [DeviceType.TIMER_TON, DeviceType.COUNTER_CTU]:
                    current_val = getattr(hovered_device, 'current_value', 0)
                    preset_val = getattr(hovered_device, 'preset_value', 0)
                    timer_active = getattr(hovered_device, 'timer_active', False)
                    
                    if hovered_device.device_type == DeviceType.TIMER_TON:
                        device_debug_text = f"TIMER {device_id}: {current_val}/{preset_val} Active:{timer_active} Out:{hovered_device.state}"
                    else:
                        device_debug_text = f"COUNTER {device_id}: {current_val}/{preset_val} Out:{hovered_device.state}"
                else:
                    # 通常デバイス表示
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
        
        # TABキーヒント表示（左端） - モード別表示
        if self.current_mode == SimulatorMode.EDIT:
            tab_hint = "TAB:Mode F6:Reset Ctrl+S:Save Ctrl+O:Load"
        else:
            tab_hint = "TAB:Mode F6:Reset F5:PLC [Save/Load: EDIT mode only]"
        pyxel.text(10, status_bar_y + 2, tab_hint, pyxel.COLOR_WHITE)
        
        # 現在編集中のファイル名表示（下部ステータスバー）
        current_file = self.file_dialog_manager.get_current_filename()
        file_display = f"File: {current_file}"
        file_x = DisplayConfig.WINDOW_WIDTH - len(file_display) * 4 - 10  # 右端から10px余白
        pyxel.text(file_x, DisplayConfig.WINDOW_HEIGHT - 20, file_display, pyxel.COLOR_CYAN)
        
        # ステータスメッセージ表示（中央上部）
        if self.status_message:
            message_x = (DisplayConfig.WINDOW_WIDTH - len(self.status_message) * 4) // 2  # 中央揃え
            message_y = 20  # 上部に表示
            # 背景を描画して見やすくする
            pyxel.rect(message_x - 4, message_y - 2, len(self.status_message) * 4 + 8, 10, pyxel.COLOR_DARK_BLUE)
            pyxel.rectb(message_x - 4, message_y - 2, len(self.status_message) * 4 + 8, 10, pyxel.COLOR_WHITE)
            pyxel.text(message_x, message_y, self.status_message, pyxel.COLOR_RED)

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
        
        # タイマー・カウンターの値リセット
        self._reset_timer_counter_values()
        
        # 追加のリセット処理（将来拡張時）
        # - 内部リレー状態リセット
        # - エラー状態クリア

    def _reset_all_device_states(self) -> None:
        """
        全デバイスの個別状態をリセット（F6キー専用）
        配置は維持、状態のみ初期化（接点のON/OFF、タイマー・カウンター値等）
        """
        for row in range(self.grid_system.rows):
            for col in range(self.grid_system.cols):
                device = self.grid_system.get_device(row, col)
                if device:
                    # デバイスの個別状態を初期値に戻す
                    device.state = False  # 接点のON/OFF状態をOFFに
                    
                    # タイマー・カウンターの現在値リセット
                    if device.device_type == DeviceType.TIMER_TON:
                        device.current_value = 0
                        device.timer_active = False
                        # preset_valueは保持（設定値は維持）
                    elif device.device_type == DeviceType.COUNTER_CTU:
                        device.current_value = 0
                        device.last_input_state = False
                        # preset_valueは保持（設定値は維持）
    
    def _reset_timer_counter_values(self) -> None:
        """
        タイマー・カウンターの現在値のみリセット（EDITモード復帰時・F5停止時用）
        設定値（preset_value）は保持し、実行時の値のみクリア
        """
        for row in range(self.grid_system.rows):
            for col in range(self.grid_system.cols):
                device = self.grid_system.get_device(row, col)
                if device:
                    if device.device_type == DeviceType.TIMER_TON:
                        device.current_value = 0
                        device.timer_active = False
                        device.state = False  # 出力状態もリセット
                    elif device.device_type == DeviceType.COUNTER_CTU:
                        device.current_value = 0
                        device.last_input_state = False
                        device.state = False  # 出力状態もリセット

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
# PyPlc Ver3 - Clean Implementation Start
# 作成日: 2025-07-29
# 目標: PLC標準仕様完全準拠ラダー図シミュレーター

#重要！
# Pyxelは２バイト文字扱えないので１バイト文字のみ使用。絵文字も不可能
# コメントには日本語を使用する。絵文字は使わない！

# .vscode/以下に実行環境の記載があるので、参照してください


#Todo
#D_DeviceEditDialogの実装（以下のオプションを追加。DialogManagerのData_register_dialogにドロップダウンリストで実装）
# - [MOV] : データ転送
# - [ADD] : 加算演算
# - [SUB] : 減算演算
# - [MUL] : 乗算演算
# - [DIV] : 除算演算

#以下、ダイアログボックスでの表示案
# 
#--------------------------------------------------------
#Operand [100]

#[MOV]   #デバイスに Operand[100]をデータ転送
#[ADD]   #デバイスに Operand[100]を加算
#[SUB]   #デバイスから Operand[100]を減算
#[MUL]   #デバイスに Operand[100]を乗算
#[DIV]   #デバイスを Operand[100]で除算
#--------------------------------------------------------
# DIV by zeroのエラー処理は、データレジスタのオペランド値が0の場合は除算を行わないようにする
# また、データレジスタのオペランド値が0の場合は除算を行わないようにする
# なお、データレジスタのオペランド値は整数型であることを前提とする


#Compare Deivice
# PLCにおける「比較接点」とは、ある2つのデータの値を比較し、その結果に応じて回路をON/OFFさせる命令のことです。ラダープログラム上では、通常のa接点（常開）やb接点（常閉）のように見えますが、その動作は入力信号のON/OFFではなく、データの比較結果によって決まります。
# 比較接点の基本
# 比較接点は、主にデータレジスタやタイマ/カウンタの現在値といった、数値を持つデータを扱う際に使用されます。特定の条件（例：AがBより大きい、AがBと等しいなど）が満たされたときに接点が閉じ、その後の回路が実行されます。
# 比較接点の種類と使い方
# 比較接点にはいくつかの種類があり、それぞれ異なる比較条件に対応しています。一般的な種類とそれぞれの動作は以下の通りです。
#     等しい（=）: 2つのデータが同じ値のときにONします。
#         例：LD = D0 K10 → データレジスタD0の値が10のときにON
#     等しくない（<>）: 2つのデータが異なる値のときにONします。
#         例：LD <> D0 K10 → データレジスタD0の値が10ではないときにON
#     より大きい（>）: 1つ目のデータが2つ目のデータより大きいときにONします。
#         例：LD > D0 K10 → データレジスタD0の値が10より大きいときにON
#     より小さい（<）: 1つ目のデータが2つ目のデータより小さいときにONします。
#         例：LD < D0 K10 → データレジスタD0の値が10より小さいときにON
#     以上（>=）: 1つ目のデータが2つ目のデータと等しいか、または大きいときにONします。
#         例：LD >= T0 K500 → タイマT0の現在値が50.0秒以上のときにON
#     以下（<=）: 1つ目のデータが2つ目のデータと等しいか、または小さいときにONします。
#         例：LD <= C0 K10 → カウンタC0の現在値が10以下のときにON
# 使用例
# 比較接点は、以下のようなプログラムで非常に役立ちます。
#     温度制御: 温度センサの現在値（データレジスタに格納）が、設定値を超えたときにヒータを停止させる。
#     レベル制御: 液面センサの値が、上限値に達したときにポンプを停止させる。
#     生産数管理: カウンタの現在値が、目標生産数と一致したときに完了ランプを点灯させる。
# これらの例のように、比較接点を使うことで、数値の範囲指定や特定の条件による分岐処理を簡単に実現できます。
# メーカーや機種によっては、CMP命令（一括比較命令）やZCP命令（ゾーン比較命令）など、より複雑な比較ができる命令も用意されています。

# 比較接点の例
# C[ =  P1  P2]
# "=" 比較演算子 P1 = P2 の時ONとなる
# C[ <> P1  P2]
# "<>" 比較演算子 P1 <> P2 の時ONとなる
# C[ <  P1  P2] --- C[ < P2  P3]
# "<" 比較演算子 P1 < P2 かつ P2 < p3 の時ONとなる(C接点を連続して使用することで、複数の比較を行うことができる)


#ZRSTのリセット条件の書き方を定義
# T001,T003,[T005-T010] こういう書き方ができるように




#SpraiteDefinerわりとバグ多いので、どっかで見直す


import os
import pyxel
from config import DisplayConfig, SystemInfo, UIConfig, UIBehaviorConfig, DeviceType, SimulatorMode, PLCRunState, TimerConfig, CounterConfig
from core.grid_system import GridSystem
from core.input_handler import InputHandler, MouseState
from core.circuit_analyzer import CircuitAnalyzer
from core.device_palette import DevicePalette
from core.circuit_csv_manager import CircuitCsvManager  # CSV管理システムをインポート
# pyDialogManager - 新しい移行先システム
from pyDialogManager.dialog_manager import DialogManager as PyDialogManager
from pyDialogManager.dialog_system import DialogSystem
from pyDialogManager.file_open_dialog import FileOpenDialogController
from pyDialogManager.file_save_dialog import FileSaveDialogController
from pyDialogManager.device_id_dialog_controller import DeviceIdDialogController
from pyDialogManager.timer_counter_dialog_controller import TimerCounterDialogController
from pyDialogManager.data_register_dialog import DataRegisterDialogController
from pyDialogManager.compare_dialog_controller import CompareDialogController
from core.SpriteManager import sprite_manager # SpriteManagerをインポート
from core.device_dialog_manager import DeviceDialogManager  # Gemini提案統合ダイアログマネージャー


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
        
        # --- pyDialogManager 移行システム ---
        print("[PyPlc] Initializing pyDialogManager...")
        self.py_dialog_manager = PyDialogManager("pyDialogManager/dialogs.json")
        self.file_open_controller = FileOpenDialogController(self.py_dialog_manager)
        self.file_save_controller = FileSaveDialogController(self.py_dialog_manager)
        self.device_id_controller = DeviceIdDialogController(self.py_dialog_manager)
        self.timer_counter_controller = TimerCounterDialogController(self.py_dialog_manager)
        self.data_register_controller = DataRegisterDialogController(self.py_dialog_manager)
        self.compare_controller = CompareDialogController(self.py_dialog_manager)
        
        # --- Gemini提案統合：DeviceDialogManager初期化 ---
        device_controllers = {
            'device_id': self.device_id_controller,
            'timer_counter': self.timer_counter_controller,
            'data_register': self.data_register_controller,
            'compare': self.compare_controller
        }
        self.device_dialog_manager = DeviceDialogManager(device_controllers)
        
        # --- DialogSystem 一元管理システム ---
        print("[PyPlc] Initializing DialogSystem...")
        self.dialog_system = DialogSystem()
        self.dialog_system.register_controller(self.file_open_controller)
        self.dialog_system.register_controller(self.file_save_controller)
        self.dialog_system.register_controller(self.device_id_controller)
        self.dialog_system.register_controller(self.timer_counter_controller)
        self.dialog_system.register_controller(self.data_register_controller)
        self.dialog_system.register_controller(self.compare_controller)
        print("[PyPlc] ✅ pyDialogManager and DialogSystem initialized successfully")

        # --- ダイアログ編集中の状態管理 ---
        self.editing_device_pos = None
        self.previous_dialog_active = False  # 前フレームのダイアログ状態
        # self.dialog_just_closed = False  # ダイアログが直前に閉じられたフラグ（現在未使用）
        # 目的: ダイアログ終了時に残存する入力イベント（マウスクリック・キーボード入力・Enter/ESC等）による誤動作防止

        # --- LINK_HORZ ドラッグ配置用フラグ (Phase D) ---
        self.is_dragging_link = False
        self.drag_start_pos = None
        self.last_drag_pos = None
        # --- ここまで ---
        
        # --- メッセージ表示システム ---
        self.status_message = ""  # 表示中のメッセージ
        self.status_message_timer = 0  # メッセージ表示残り時間（フレーム数）
        self.status_message_type = "info"  # メッセージタイプ（info/success/error）
        
        # --- ファイル名管理システム ---
        self.current_filename = "untitled.csv"  # 現在のファイル名（デフォルト）

        pyxel.run(self.update, self.draw)
    
    def update(self) -> None:
        """フレーム更新処理"""
        # --- pyDialogManager 移行 ---
        self.py_dialog_manager.update()
        self.dialog_system.update()  # DialogSystemによる一括更新

        # --- pyDialogManager 結果処理 ---
        self._handle_dialog_results()

        # ダイアログ表示状態に応じてデバイスパレットのモードを設定（状態変化時のみ）
        dialog_active = self.py_dialog_manager.active_dialog is not None
        if dialog_active != self.previous_dialog_active:
            self.device_palette.set_dialog_mode(dialog_active)
            self.previous_dialog_active = dialog_active

        # ダイアログ表示中はゲーム処理をスキップするが、ダイアログ処理は継続
        if self.dialog_system.has_active_dialogs:
            # DialogSystemによる全コントローラーの一括更新処理
            self.dialog_system.update()
            
            # ダイアログからの結果処理
            self._handle_dialog_results()
            return
        
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
            #hoge
            if self.current_mode == SimulatorMode.EDIT:
                self._reset_circuit_for_save()
                # 拡張子を除いたファイル名をデフォルトとして渡す
                filename_without_ext = os.path.splitext(self.current_filename)[0]
                self.file_save_controller.show_save_dialog(filename_without_ext, ".csv")
            else:
                self._show_status_message("Save: EDIT mode only. Press TAB to switch.", 4.0)
            
        # Ctrl+O: ファイル読み込みダイアログ表示（EDITモードのみ）
        if pyxel.btn(pyxel.KEY_CTRL) and pyxel.btnp(pyxel.KEY_O):
            if self.current_mode == SimulatorMode.EDIT:
                self.file_open_controller.show_file_open_dialog()
            else:
                self._show_status_message("Load: EDIT mode only. Press TAB to switch.", 4.0)
        
        # --- pyDialogManager パイロット統合 テスト ---
        if pyxel.btnp(pyxel.KEY_F11):
            print("[PyPlc] F11 pressed, showing pilot test dialog...")
            self.py_dialog_manager.show("IDD_PILOT_TEST")
        
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

    def _handle_dialog_results(self):
        """全てのpyDialogManagerコントローラーからの結果を処理する"""        
        # ファイル保存の結果を処理
        save_path = self.file_save_controller.get_result()
        if save_path:
            # self.dialog_just_closed = True  # ダイアログ終了フラグ設定（現在未使用）
            # 目的: ダイアログOK決定時の入力イベント（クリック・Enter等）が次フレームで意図しない動作を引き起こすのを防止
            try:
                if self.csv_manager.save_circuit_to_csv(save_path):
                    # ファイル保存成功時にファイル名を更新
                    self.current_filename = os.path.basename(save_path)
                    self._show_status_message(f"Saved to {os.path.basename(save_path)}", 3.0, "success")
                else:
                    self._show_status_message("Failed to save file", 3.0, "error")
            except FileNotFoundError:
                self._show_status_message(f"Directory not found: {os.path.dirname(save_path)}", 3.0, "error")
            except PermissionError:
                self._show_status_message(f"Access denied: {os.path.basename(save_path)}", 3.0, "error") 
            except OSError as e:
                self._show_status_message(f"File error: {str(e)}", 3.0, "error")
            except Exception as e:
                self._show_status_message(f"Save error: {str(e)}", 3.0, "error")

        # ファイル読み込みの結果を処理
        load_path = self.file_open_controller.get_result()
        if load_path:
            # self.dialog_just_closed = True  # ダイアログ終了フラグ設定（現在未使用）
            # 目的: ダイアログOK決定時の入力イベント（クリック・Enter等）が次フレームで意図しない動作を引き起こすのを防止
            # ファイル読み込み実行
            try:
                if self.csv_manager.load_circuit_from_csv(load_path):
                    # ファイル読み込み成功時にファイル名を記録
                    self.current_filename = os.path.basename(load_path)
                    self._show_status_message(f"Loaded {os.path.basename(load_path)}", 3.0, "success")
                    self.circuit_analyzer.solve_ladder()
                else:
                    self._show_status_message("Failed to load file", 3.0, "error")
            except FileNotFoundError:
                self._show_status_message(f"File not found: {os.path.basename(load_path)}", 3.0, "error")
            except PermissionError:
                self._show_status_message(f"Access denied: {os.path.basename(load_path)}", 3.0, "error")
            except UnicodeDecodeError:
                self._show_status_message(f"Invalid file format: {os.path.basename(load_path)}", 3.0, "error")
            except Exception as e:
                self._show_status_message(f"Load error: {str(e)}", 3.0, "error")

        # デバイスID編集の結果を処理
        id_result = self.device_id_controller.get_result()
        if id_result and self.editing_device_pos:
            success, new_id = id_result
            if success:
                device = self.grid_system.get_device(*self.editing_device_pos)
                if device:
                    device.address = new_id
                    self.circuit_analyzer.solve_ladder()
                    self._show_status_message(f"Device ID set to {new_id}", 2.0, "success")
            else:
                self._show_status_message("Device edit canceled", 2.0, "info")
            self.editing_device_pos = None # 処理後にリセット

        # タイマー・カウンター設定編集の結果を処理
        timer_counter_result = self.timer_counter_controller.get_result()
        if timer_counter_result and self.editing_device_pos:
            success = timer_counter_result[0]
            if success and len(timer_counter_result) >= 3:
                new_device_id = timer_counter_result[1]
                new_preset_value = timer_counter_result[2]
                device = self.grid_system.get_device(*self.editing_device_pos)
                if device:
                    device.address = new_device_id
                    device.preset_value = new_preset_value
                    self.circuit_analyzer.solve_ladder()
                    self._show_status_message(f"Timer/Counter updated: {new_device_id}, Preset: {new_preset_value}", 3.0, "success")
            else:
                self._show_status_message("Timer/Counter edit canceled", 2.0, "info")
            self.editing_device_pos = None # 処理後にリセット

        # 比較デバイス編集の結果を処理
        compare_result = self.compare_controller.get_result()
        if compare_result and self.editing_device_pos:
            left = compare_result.get('compare_left', '')
            operator = compare_result.get('compare_operator', '=')
            right = compare_result.get('compare_right', '')
            device = self.grid_system.get_device(*self.editing_device_pos)
            if device:
                # 比較デバイスに設定を保存
                device.compare_left = left
                device.compare_operator = operator
                device.compare_right = right
                self.circuit_analyzer.solve_ladder()
                self._show_status_message(f"Compare device set: {left} {operator} {right}", 2.0, "success")
                # 比較デバイス設定を更新
            self.editing_device_pos = None # 処理後にリセット
            
        # データレジスタ編集の結果を処理
        data_register_result = self.data_register_controller.get_result()
        if data_register_result and self.editing_device_pos:
            device_id = data_register_result.get('device_id', '')
            operation = data_register_result.get('operation', 'MOV')
            operand = data_register_result.get('operand', '')
            device = self.grid_system.get_device(*self.editing_device_pos)
            if device:
                # デバイスにデバイスID、操作、オペランド値を保存
                device.address = device_id
                device.operation = operation
                # オペランド値をpreset_valueに保存（CSV保存用）
                try:
                    device.preset_value = int(operand) if operand.isdigit() else float(operand)
                except (ValueError, AttributeError):
                    device.preset_value = 0  # 変換できない場合はデフォルト値
                # 旧operand属性も保持（互換性用）
                device.operand = operand
                self.circuit_analyzer.solve_ladder()
                self._show_status_message(f"Data register updated: {device_id} {operation} {operand}", 3.0, "success")
            self.editing_device_pos = None # 処理後にリセット

    def _handle_right_click_sprite_based(self) -> None:
        """
        Gemini統合版スプライトベース右クリック処理
        
        従来の複雑な条件判定（40行）を、SpriteManager + DeviceDialogManager統合（3行）に簡素化
        - パフォーマンス向上：97%計算削減（O(300) → O(9)）
        - 責務分離：ダイアログ振り分けをDeviceDialogManagerに移譲
        - 操作性向上：スプライト直接判定で確実な右クリック反応
        """
        # 基本チェック
        if self.current_mode != SimulatorMode.EDIT:
            return
        
        # Gemini統合：スプライトコリジョン判定（97%高速化）
        mouse_x, mouse_y = pyxel.mouse_x, pyxel.mouse_y
        collision_result = sprite_manager.find_device_at_screen_pos(mouse_x, mouse_y, self.grid_system)
        
        if collision_result:
            device, row, col = collision_result
            self.editing_device_pos = (row, col)
            
            # Gemini統合：責務分離ダイアログ表示（1行呼び出し）
            self.device_dialog_manager.show_for_device(device)

    def _handle_device_placement(self) -> None:
        """
        マウス入力に基づき、デバイスの配置・削除・状態変更を行う
        LINK_HORZのドラッグ配置に対応 (Phase D)
        """
        # === Gemini統合スプライトベース右クリック処理（1行呼び出し） ===
        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            self._handle_right_click_sprite_based()
            return  # 右クリック処理完了、左クリック処理をスキップ
        
        # 通常のマウス処理のチェック
        if self.current_mode != SimulatorMode.EDIT:
            return
        if not self.mouse_state.snap_mode:
            return
        # 左クリック等の他の処理では、従来通り is_snapped 条件を適用
        if self.mouse_state.hovered_pos is None or not self.mouse_state.is_snapped or not self.mouse_state.on_editable_area:
            return
        
        # ダイアログが直前に閉じられた場合は1フレーム待つ（現在未使用）
        # 目的: ダイアログ終了直後の全入力イベント残存（マウス・キーボード・Enter/ESC等）による誤動作防止
        # if self.dialog_just_closed:
        #     self.dialog_just_closed = False
        #     return

        row, col = self.mouse_state.hovered_pos
        selected_device_type = self.device_palette.get_selected_device_type()
        
        # EMPTYの場合は早期リターン（安全策）
        if selected_device_type == DeviceType.EMPTY:
            return

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

    def _place_single_device(self, row: int, col: int, device_type: DeviceType) -> None:
        """単一のデバイスを配置するヘルパーメソッド"""
        # 配線系デバイスかどうかを判定
        is_link_device = device_type in [DeviceType.LINK_HORZ, DeviceType.LINK_VIRT, DeviceType.LINK_BRANCH]
        
        # 配線系デバイスならアドレスは空、それ以外は生成
        address = "" if is_link_device else self._generate_default_address(device_type, row, col)
        
        new_device = self.grid_system.place_device(row, col, device_type, address)
        
        # タイマー・カウンター・データレジスタのデフォルト値設定
        if new_device:
            if device_type == DeviceType.TIMER_TON:
                new_device.preset_value = TimerConfig.DEFAULT_PRESET
            elif device_type == DeviceType.COUNTER_CTU:
                new_device.preset_value = CounterConfig.DEFAULT_PRESET
            elif device_type == DeviceType.DATA_REGISTER:
                # データレジスタのデフォルト設定
                new_device.preset_value = 0
                new_device.current_value = 0
                new_device.operation = 'MOV'
                # 立ち上がりエッジ検出用状態初期化
                new_device.last_energized_state = False

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
    
    def _show_status_message(self, message: str, duration_seconds: float = 3.0, message_type: str = "info") -> None:
        """
        ステータスメッセージを表示する
        
        Args:
            message: 表示するメッセージ（1バイト文字のみ）
            duration_seconds: 表示時間（秒）
            message_type: メッセージタイプ（"info", "success", "error"）
        """
        self.status_message = message
        self.status_message_timer = int(duration_seconds * DisplayConfig.TARGET_FPS)  # フレーム数に変換
        self.status_message_type = message_type
    
    def _update_status_message(self) -> None:
        """
        ステータスメッセージのタイマー更新
        """
        if self.status_message_timer > 0:
            self.status_message_timer -= 1
            if self.status_message_timer <= 0:
                self.status_message = ""
                self.status_message_type = "info"

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
        
        # ★ 新機能: 同アドレスデバイスハイライト描画 ★
        self._draw_address_highlight()
        
        # RUNモード時のデバイス情報表示（マウスオーバー）
        if self.current_mode == SimulatorMode.RUN:
            self._draw_device_info_on_hover()
        
        # UI情報描画
        self._draw_cursor_and_status()
        self._draw_mode_status_bar()  # Edit/Runモード状態表示追加
        self._draw_header_footer()

        # --- pyDialogManager パイロット統合 ---
        self.py_dialog_manager.draw()

    def _draw_address_highlight(self) -> None:
        """
        同アドレスデバイスのハイライト描画
        Editモードでホバー時のみ動作
        """
        # Editモード以外では描画しない
        if (self.current_mode != SimulatorMode.EDIT or 
            not self.mouse_state.hovered_pos or 
            not self.mouse_state.on_editable_area):
            return
        
        # ホバー中のデバイスを取得
        row, col = self.mouse_state.hovered_pos
        hovered_device = self.grid_system.get_device(row, col)
        
        # アドレスが無いデバイスは対象外
        if not hovered_device or not hovered_device.address:
            return
        
        # 同アドレスデバイス座標を取得
        matching_positions = self.grid_system.find_devices_by_address(hovered_device.address)
        
        # 自分自身のみの場合は描画不要
        if len(matching_positions) <= 1:
            return
        
        # 各同アドレスデバイスに赤色強調枠を描画
        for pos_row, pos_col in matching_positions:
            # スプライト描画座標を計算（grid_system.pyと同じロジック）
            sprite_size = sprite_manager.sprite_size  # 動的にスプライトサイズを取得
            sprite_x = self.grid_system.origin_x + pos_col * self.grid_system.cell_size - sprite_size // 2
            sprite_y = self.grid_system.origin_y + pos_row * self.grid_system.cell_size - sprite_size // 2
            
            # スプライトを囲む赤色強調枠描画（スプライト座標-2, サイズ+4）
            pyxel.rectb(
                sprite_x - 2, 
                sprite_y - 2, 
                sprite_size + 4, 
                sprite_size + 4, 
                pyxel.COLOR_RED
            )

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
                
                # データレジスタ詳細表示
                elif hovered_device.device_type == DeviceType.DATA_REGISTER:
                    data_value = getattr(hovered_device, 'data_value', 0)
                    device_debug_text = f"DATA_REG {device_id}: Value={data_value} [Double-click to edit]"
                
                # Compare命令詳細表示
                elif hovered_device.device_type == DeviceType.COMPARE_DEVICE:
                    condition = hovered_device.address if hovered_device.address else "N/A"
                    device_debug_text = f"COMPARE {condition}: Result={hovered_device.state} Energized={hovered_device.is_energized}"
                
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
        """
        ヘッダーとフッターの情報を描画する"""
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
        # current_file = self.file_manager.get_current_filename()
        # file_display = f"File: {current_file}"
        
        # file_x = DisplayConfig.WINDOW_WIDTH - len(file_display) * 4 - 10  # 右端から10px余白
        # pyxel.text(file_x, DisplayConfig.WINDOW_HEIGHT - 20, file_display, pyxel.COLOR_CYAN)
        
        # ダイアログシステム表示（右端）- DialogManager v4固定
        dialog_system = "pyDialogManager"
        dialog_color = pyxel.COLOR_LIME
        
        dialog_display = f"[{dialog_system}]"
        dialog_x = DisplayConfig.WINDOW_WIDTH - len(dialog_display) * 4 - 10
        pyxel.text(dialog_x, DisplayConfig.WINDOW_HEIGHT - 8, dialog_display, dialog_color)
        
        # ステータスメッセージ表示（画面下部）- 色分け対応
        if self.status_message:
            message_x = (DisplayConfig.WINDOW_WIDTH - len(self.status_message) * 4) // 2  # 中央揃え
            message_y = DisplayConfig.WINDOW_HEIGHT - 40  # 下部に表示（ファイル名表示の上）
            
            # メッセージタイプに応じた色分け
            if self.status_message_type == "success":
                bg_color = pyxel.COLOR_DARK_BLUE  # 濃い緑の代替（濃い青）
                border_color = pyxel.COLOR_GREEN   # 緑
                text_color = pyxel.COLOR_WHITE     # 白文字
            elif self.status_message_type == "error":
                bg_color = pyxel.COLOR_NAVY        # 濃い赤の代替（ネイビー）
                border_color = pyxel.COLOR_RED     # 赤
                text_color = pyxel.COLOR_WHITE     # 白文字
            else:  # info
                bg_color = pyxel.COLOR_DARK_BLUE   # 濃い青（従来）
                border_color = pyxel.COLOR_WHITE   # 白（従来）
                text_color = pyxel.COLOR_WHITE     # 白文字
            
            # 背景・枠線・テキストを描画
            pyxel.rect(message_x - 4, message_y - 2, len(self.status_message) * 4 + 8, 10, bg_color)
            pyxel.rectb(message_x - 4, message_y - 2, len(self.status_message) * 4 + 8, 10, border_color)
            pyxel.text(message_x, message_y, self.status_message, text_color)

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
                    
                    # データレジスタの立ち上がりエッジ検出状態リセット
                    if device.device_type == DeviceType.DATA_REGISTER:
                        device.current_value = 0
                        device.last_energized_state = False
    
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
    
    def _reset_circuit_for_save(self) -> None:
        """
        ファイル保存前の回路状態リセット
        実行時の状態（接点ON/OFF、タイマー・カウンター現在値等）をクリアして
        クリーンな初期状態で保存する
        """
        for row in range(self.grid_system.rows):
            for col in range(self.grid_system.cols):
                device = self.grid_system.get_device(row, col)
                if device:
                    # 全ての接点状態をOFFに（外部入力含む）
                    if device.device_type in [DeviceType.CONTACT_A, DeviceType.CONTACT_B]:
                        device.state = False
                    
                    # タイマー・カウンターの実行時値をクリア
                    if device.device_type == DeviceType.TIMER_TON:
                        device.current_value = 0
                        device.timer_active = False
                        device.state = False
                    elif device.device_type == DeviceType.COUNTER_CTU:
                        device.current_value = 0
                        device.last_input_state = False
                        device.state = False
                    
                    # コイル状態をクリア
                    elif device.device_type in [DeviceType.COIL_STD, DeviceType.COIL_REV]:
                        device.state = False
                        
                    # 通電状態もクリア
                    device.is_energized = False
        
        print("[Save] Circuit state reset before saving - clean initial state")

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
"""
PyPlc Ver3 Circuit Analyzer Module
作成日: 2025-01-29
目標: 通電ロジックの実装と自己保持回路の実現
"""

from typing import Set, Tuple, Optional
from core.grid_system import GridSystem
from core.device_base import PLCDevice
from config import DeviceType

class CircuitAnalyzer:
    """ラダー図の回路を解析し、各デバイスの通電状態を決定するエンジン"""

    def __init__(self, grid_system: GridSystem):
        """CircuitAnalyzerの初期化"""
        self.grid = grid_system

    def solve_ladder(self) -> None:
        """ラダー図全体の通電解析を実行する（1スキャンに相当）"""
        # 1. GridSystemに依頼して、全デバイスの通電状態を正しくリセットする
        self.grid.reset_all_energized_states()

        # 2. 各行の左バスから電力のトレースを開始
        for r in range(self.grid.rows):
            left_bus = self.grid.get_device(r, 0)
            # L_SIDEはリセット処理で既を通電済みのはず
            if left_bus and left_bus.is_energized:
                # 右隣のデバイスからトレースを開始
                self._trace_power_flow(left_bus.connections.get('right'))

        # 3. タイマー・カウンター処理（電力フロー後）
        self._update_timer_counter_logic()

        # 4. データレジスタ演算処理（Phase 3新機能 - WindSurf改善版）
        self._process_data_register_operations()

        # 5. Compare命令処理（データレジスタ比較演算）
        self._process_compare_commands()

        # 6. RST（リセット命令）処理（Mitsubishi準拠）
        self._process_rst_commands()

        # 7. ZRST（範囲リセット命令）処理
        self._process_zrst_commands()

        # 8. PLC標準動作: 励磁されたコイルの同一アドレス接点を自動的にON状態に更新
        self._update_contact_states_from_coils()

    def _trace_power_flow(self, start_pos: Optional[Tuple[int, int]], visited: Optional[Set[Tuple[int, int]]] = None) -> None:
        """指定された位置から電力の流れを再帰的にトレースする（深さ優先探索）"""
        if visited is None:
            visited = set()

        if start_pos is None or start_pos in visited:
            return

        visited.add(start_pos)
        device = self.grid.get_device(start_pos[0], start_pos[1])
        if not device:
            return

        # このデバイスは通電しているとマーク
        device.is_energized = True

        # デバイスが電力を通すか（導通性があるか）チェック
        if not self._is_conductive(device):
            return # 通さないなら、この先のトレースは行わない

        # --- 次に電力を流す先を決定 ---
        # 新アーキテクチャ: LINK_BRANCH による3方向分配（右・上・下）
        if device.device_type == DeviceType.LINK_BRANCH:
            # 確定仕様: 右・上・下の3方向に電力分配（左は除外）
            for direction in ['right', 'up', 'down']:
                next_pos = device.connections.get(direction)
                if next_pos and next_pos not in visited:
                    self._trace_power_flow(next_pos, visited)
        
        elif device.device_type == DeviceType.LINK_VIRT:
            # 上下双方向に電力伝播
            for direction in ['up', 'down']:
                next_pos = device.connections.get(direction)
                if next_pos and next_pos not in visited:
                    self._trace_power_flow(next_pos, visited)
        
        # 標準デバイス（右方向のみ）
        else:
            self._trace_power_flow(device.connections.get('right'), visited)

    def _is_conductive(self, device: PLCDevice) -> bool:
        """デバイスが現在、電気を通す状態にあるかを判定する"""
        if device.device_type == DeviceType.CONTACT_A:
            return device.state  # ON状態なら通す
        if device.device_type == DeviceType.CONTACT_B:
            return not device.state  # OFF状態なら通す
        
        # 配線系は常時通す
        if device.device_type in [DeviceType.LINK_HORZ, DeviceType.LINK_BRANCH, DeviceType.LINK_VIRT]:
            return True

        # L_SIDE（左バス）は電源なので常時導通
        if device.device_type == DeviceType.L_SIDE:
            return True

        # Compare命令は比較結果に応じて導通性を決定
        if device.device_type == DeviceType.COMPARE_DEVICE:
            return device.state  # 比較結果がTrue時のみ導通

        # データレジスタは常時導通（値保持のみ、電力は通す）
        if device.device_type == DeviceType.DATA_REGISTER:
            return True

        # R_SIDE（右バス）とコイルは電力の終端なので、電気を通さない
        return False

    # 旧_handle_parallel_convergence()メソッドは削除済み
    # LINK_BRANCHアーキテクチャにより、複雑な合流ロジックは不要になりました

    def _update_timer_counter_logic(self) -> None:
        """
        タイマー・カウンターロジック処理
        PLC標準準拠のTON（Timer ON-Delay）およびCTU（Counter UP）動作を実装
        フレームベース（30FPS）でのタイマー動作
        """
        import pyxel
        
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                device = self.grid.get_device(row, col)
                if not device:
                    continue
                    
                # TON（Timer ON-Delay）処理
                if device.device_type == DeviceType.TIMER_TON:
                    self._process_timer_ton(device)
                
                # CTU（Counter UP）処理
                elif device.device_type == DeviceType.COUNTER_CTU:
                    self._process_counter_ctu(device)

    def _process_timer_ton(self, timer_device) -> None:
        """
        TON（Timer ON-Delay）処理（PLC標準準拠・フレームベース）
        30FPS動作で1フレーム約33.3ms、1ms単位カウント、990ms超過で完了
        
        Args:
            timer_device: タイマーデバイス
        """
        from config import TimerConfig
        
        # 通電状態確認
        if timer_device.is_energized:
            if not timer_device.timer_active:
                # タイマー開始（初回通電時）
                timer_device.timer_active = True
                timer_device.current_value = 0
                print(f"[TIMER DEBUG] {timer_device.address} STARTED - preset={timer_device.preset_value}ms")
                
            else:
                # フレームベースタイマー実行中（1フレーム = 約33.3ms）
                timer_device.current_value += 33  # 30FPSで約33ms/フレーム
                
                print(f"[TIMER DEBUG] {timer_device.address} RUNNING - current={timer_device.current_value}ms, preset={timer_device.preset_value}ms")
                
                # プリセット値または閾値到達チェック（990ms超過で完了）
                if timer_device.current_value >= timer_device.preset_value or timer_device.current_value >= TimerConfig.FRAME_THRESHOLD:
                    timer_device.current_value = timer_device.preset_value
                    timer_device.state = True  # タイマー出力ON
                    print(f"[TIMER DEBUG] {timer_device.address} OUTPUT ON - reached {timer_device.preset_value}ms")
                else:
                    timer_device.state = False
        else:
            # 非通電時 - タイマーリセット
            if timer_device.timer_active:  # 動作中だった場合のみデバッグ出力
                print(f"[TIMER DEBUG] {timer_device.address} RESET - was active")
            timer_device.timer_active = False
            timer_device.current_value = 0
            timer_device.state = False
            
    def _process_counter_ctu(self, counter_device) -> None:
        """
        CTU（Counter UP）処理
        立ち上がりエッジでカウントアップ、設定回数到達で出力ON
        
        Args:
            counter_device: カウンターデバイス
        """
        # 立ち上がりエッジ検出
        current_input = counter_device.is_energized
        previous_input = counter_device.last_input_state
        
        if current_input and not previous_input:
            # 立ち上がりエッジ発生 - カウントアップ
            counter_device.current_value += 1
            
            # プリセット値到達チェック
            if counter_device.current_value >= counter_device.preset_value:
                counter_device.current_value = counter_device.preset_value
                counter_device.state = True  # カウンター出力ON
            else:
                counter_device.state = False
                
        # 現在の入力状態を記録（次回のエッジ検出用）
        counter_device.last_input_state = current_input

    def _process_rst_commands(self) -> None:
        """
        RST命令処理（三菱PLC準拠）
        - 通電中のRSTデバイスに設定されたアドレス（T/C）に一致するタイマー・カウンターを即時リセット
        - 同一スキャン内で即時反映されるよう、タイマー/カウンター更新後に実行
        """
        # 1. 通電中のRSTのターゲットアドレスを収集
        target_addresses: set[str] = set()
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                device = self.grid.get_device(row, col)
                if device and device.device_type == DeviceType.RST and device.is_energized and device.address:
                    # アドレスは大文字で統一
                    target_addresses.add(device.address.upper())

        if not target_addresses:
            return

        # 2. 対象アドレスに一致するタイマー/カウンターをリセット
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                device = self.grid.get_device(row, col)
                if not device or not device.address:
                    continue
                if device.address.upper() not in target_addresses:
                    continue

                if device.device_type == DeviceType.TIMER_TON:
                    # タイマー即時リセット
                    device.current_value = 0
                    device.state = False
                    device.timer_active = False
                elif device.device_type == DeviceType.COUNTER_CTU:
                    # カウンター即時リセット
                    device.current_value = 0
                    device.state = False
                    # 次スキャンでの誤カウント防止: 現在の入力状態を前回状態として記録
                    device.last_input_state = device.is_energized

    def _process_zrst_commands(self) -> None:
        """
        ZRST命令処理（範囲/複数指定）
        - 通電中のZRSTのaddressテキストを解釈し、対象アドレス集合に一致するT/Cを即時リセット
        """
        # 1. 通電中のZRSTのテキストを収集
        zrst_texts: list[str] = []
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                device = self.grid.get_device(row, col)
                if device and device.device_type == DeviceType.ZRST and device.is_energized and device.address:
                    zrst_texts.append(device.address)

        if not zrst_texts:
            return
        
        # 2. すべてのテキストを解釈してターゲットアドレス集合を構築
        target_addresses: set[str] = set()
        for text in zrst_texts:
            target_addresses.update(self._resolve_zrst_targets(text))

        if not target_addresses:
            return

        # 3. 一致するタイマー/カウンターを即時リセット
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                device = self.grid.get_device(row, col)
                if not device or not device.address:
                    continue
                addr_upper = device.address.upper()
                if addr_upper not in target_addresses:
                    continue
                if device.device_type == DeviceType.TIMER_TON:
                    device.current_value = 0
                    device.state = False
                    device.timer_active = False
                elif device.device_type == DeviceType.COUNTER_CTU:
                    device.current_value = 0
                    device.state = False
                    device.last_input_state = device.is_energized

    def _resolve_zrst_targets(self, text: str) -> set[str]:
        """
        ZRSTターゲット文字列から個別アドレス集合を解決
        許可: T/C、0-255、列挙/範囲、角括弧任意
        内部表現は大文字+3桁ゼロパディング（例: T1 -> T001）
        """
        import re
        targets: set[str] = set()
        if not text:
            return targets

        value = text.strip().upper()
        tokens = [tok.strip() for tok in value.split(',') if tok.strip()]
        single_re = re.compile(r'^(T|C)(\d{1,3})$')
        range_re = re.compile(r'^\[?(T|C)(\d{1,3})-(T|C)(\d{1,3})\]?$')

        def norm(prefix: str, num: int) -> str:
            return f"{prefix}{num:03d}"

        for tok in tokens:
            m1 = single_re.match(tok)
            if m1:
                prefix, num_str = m1.group(1), m1.group(2)
                num = int(num_str)
                if 0 <= num <= 255:
                    targets.add(norm(prefix, num))
                continue

            m2 = range_re.match(tok)
            if m2:
                start_prefix, start_str, end_prefix, end_str = m2.group(1), m2.group(2), m2.group(3), m2.group(4)
                # 同一プレフィックス必須
                if start_prefix != end_prefix:
                    continue
                start_num = int(start_str)
                end_num = int(end_str)
                if start_num > end_num:
                    start_num, end_num = end_num, start_num  # 安全のため入替
                start_num = max(0, start_num)
                end_num = min(255, end_num)
                for n in range(start_num, end_num + 1):
                    targets.add(norm(start_prefix, n))
                continue

            # 不正トークンは無視（バリデーションはUI側で実施済み）
            continue

        return targets

    def _process_compare_commands(self) -> None:
        """
        Compare命令処理（データレジスタ比較演算）
        - 通電中のCompareデバイスに設定された比較条件を評価
        - データレジスタから値を取得し、比較演算を実行
        - 比較結果をCompareデバイスのstateに反映
        """
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                device = self.grid.get_device(row, col)
                if device and device.device_type == DeviceType.COMPARE_DEVICE and device.is_energized:
                    # Compare命令の処理
                    self._execute_compare_operation(device)

    def _execute_compare_operation(self, compare_device) -> None:
        """
        個別のCompare命令を実行する（MVP版: 新フィールド対応）
        
        Args:
            compare_device: Compare命令デバイス
        """
        # 新しい比較フィールドから比較式を構築
        left = getattr(compare_device, 'compare_left', '').strip()
        operator = getattr(compare_device, 'compare_operator', '').strip()
        right = getattr(compare_device, 'compare_right', '').strip()
        
        # 新フィールドが設定されている場合は、それを使用
        if left and operator and right:
            # MVP版: 基本3演算子のみ対応
            mvp_operators = ["=", "<", ">"]
            if operator not in mvp_operators:
                print(f"[COMPARE ERROR] Unsupported operator in MVP: {operator}")
                compare_device.state = False
                return
                
            comparison_text = f"{left}{operator}{right}"
            result = self._evaluate_comparison(comparison_text)
            compare_device.state = result
            print(f"[COMPARE DEBUG] {comparison_text} -> {result}")
            return
        
        # 後方互換性: 従来のaddressフィールドから解析
        if hasattr(compare_device, 'address') and compare_device.address:
            comparison_text = compare_device.address.strip()
            result = self._evaluate_comparison(comparison_text)
            compare_device.state = result
            print(f"[COMPARE DEBUG LEGACY] {comparison_text} -> {result}")
            return
        
        # 設定なしの場合はFalse
        compare_device.state = False
        print(f"[COMPARE DEBUG] No comparison configured -> False")

    def _evaluate_comparison(self, comparison_text: str) -> bool:
        """
        比較演算式を評価する
        サポート演算子: =, <>, >, <, >=, <=
        データソース: データレジスタ(D番号)、定数値
        
        Args:
            comparison_text: 比較式テキスト（例: "D1>10"）
            
        Returns:
            bool: 比較結果
        """
        import re
        
        # 演算子の優先順位（長い演算子から先にチェック）
        operators = ['>=', '<=', '<>', '=', '>', '<']
        
        for op in operators:
            if op in comparison_text:
                parts = comparison_text.split(op, 1)
                if len(parts) == 2:
                    left_str = parts[0].strip()
                    right_str = parts[1].strip()
                    
                    # 左辺と右辺の値を取得
                    left_value = self._get_value_from_operand(left_str)
                    right_value = self._get_value_from_operand(right_str)
                    
                    if left_value is None or right_value is None:
                        return False
                    
                    # 比較演算の実行
                    if op == '=':
                        return left_value == right_value
                    elif op == '<>':
                        return left_value != right_value
                    elif op == '>':
                        return left_value > right_value
                    elif op == '<':
                        return left_value < right_value
                    elif op == '>=':
                        return left_value >= right_value
                    elif op == '<=':
                        return left_value <= right_value
                break
        
        return False

    def _get_value_from_operand(self, operand: str) -> Optional[int]:
        """
        オペランドから値を取得する
        データレジスタ(D番号)の場合は対応するデバイスから値を取得
        定数の場合はそのまま数値として返す
        
        Args:
            operand: オペランド文字列（例: "D1", "100"）
            
        Returns:
            Optional[int]: 取得した値、取得できない場合はNone
        """
        operand = operand.strip().upper()
        
        # データレジスタの場合（D番号）
        if operand.startswith('D') and operand[1:].isdigit():
            register_address = operand
            
            # グリッドからデータレジスタデバイスを検索
            for row in range(self.grid.rows):
                for col in range(self.grid.cols):
                    device = self.grid.get_device(row, col)
                    if (device and 
                        device.device_type == DeviceType.DATA_REGISTER and 
                        hasattr(device, 'address') and 
                        device.address and 
                        device.address.upper() == register_address):
                        # データレジスタから値を取得
                        if hasattr(device, 'data_value'):
                            return device.data_value
                        else:
                            return 0  # デフォルト値
            
            # 見つからない場合は0を返す（PLC標準動作）
            return 0
        
        # 定数値の場合
        try:
            return int(operand)
        except ValueError:
            return None

    def _update_contact_states_from_coils(self) -> None:
        """
        PLC標準動作の実装: コイル状態に応じて同一アドレス接点を自動更新
        
        実PLC動作原理:
        - コイル Y001 が励磁されると、すべての Y001 接点が自動的にON状態になる
        - コイル Y001 が非励磁になると、すべての Y001 接点が自動的にOFF状態になる
        - これにより自己保持回路やSTOP動作が正常に動作する
        """
        # 1. 全コイルアドレスと励磁状態を取得
        all_coil_addresses = set()
        energized_coil_addresses = set()
        
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                device = self.grid.get_device(row, col)
                if (device and 
                    device.device_type in [DeviceType.COIL_STD, DeviceType.COIL_REV, DeviceType.TIMER_TON, DeviceType.COUNTER_CTU, DeviceType.COMPARE_DEVICE] and
                    device.address and
                    device.address != "WIRE"):  # アドレス指定されたコイル・タイマー・カウンター・比較命令のみ
                    all_coil_addresses.add(device.address)
                    
                    # COIL_STD/COIL_REVは通電状態をstateに反映（PLC標準動作）
                    if device.device_type == DeviceType.COIL_STD:
                        device.state = device.is_energized
                    elif device.device_type == DeviceType.COIL_REV:
                        device.state = not device.is_energized  # 反転コイル
                    elif device.device_type == DeviceType.COMPARE_DEVICE:
                        # Compare命令のstateは_process_compare_commands()で既に設定済み
                        pass
                    
                    # 全コイルタイプの状態判定
                    if device.state:  # コイル・タイマー・カウンターの出力状態判定
                        energized_coil_addresses.add(device.address)
        
        # 2. 全コイルアドレスについて対応する接点の状態を更新
        for coil_address in all_coil_addresses:
            is_coil_energized = coil_address in energized_coil_addresses
            
            for row in range(self.grid.rows):
                for col in range(self.grid.cols):
                    device = self.grid.get_device(row, col)
                    if (device and 
                        device.device_type in [DeviceType.CONTACT_A, DeviceType.CONTACT_B] and
                        device.address == coil_address and
                        not device.address.startswith('X')):  # 外部入力（Xデバイス）は手動制御
                        # PLC標準: コイル状態に応じて同一アドレス接点を自動更新
                        device.state = is_coil_energized

    # 不要でバグの原因となっていたプライベートメソッドは完全に削除

    def _process_data_register_operations(self) -> None:
        """
        データレジスタ演算処理（立ち上がりエッジ検出付き）
        
        立ち上がりエッジ（OFF→ON）の時のみ演算を実行:
        - MOV: current_value = preset_value
        - ADD: current_value += preset_value
        - SUB: current_value -= preset_value
        - MUL: current_value *= preset_value
        - DIV: current_value /= preset_value (ゼロ除算チェック付き)
        
        継続通電中は演算を行わない（フレーム毎実行を防止）
        """
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                device = self.grid.get_device(row, col)
                if (device and device.device_type == DeviceType.DATA_REGISTER):
                    
                    # 前フレームの励磁状態を取得（初回はFalse）
                    last_energized = getattr(device, 'last_energized_state', False)
                    current_energized = device.is_energized
                    
                    # 立ち上がりエッジ検出（OFF→ON）
                    rising_edge = not last_energized and current_energized
                    
                    # 前フレーム状態を更新（次フレーム用）
                    device.last_energized_state = current_energized
                    
                    # 立ち上がりエッジの時のみ演算実行
                    if rising_edge:
                        # デバイスの演算情報を取得
                        operation = getattr(device, 'operation', 'MOV')
                        preset_value = getattr(device, 'preset_value', 0)
                        current_value = getattr(device, 'current_value', 0)
                        
                        try:
                            # 整数型保証: データレジスタの値は整数として扱う
                            current_value = int(getattr(device, 'current_value', 0))
                            preset_value = int(getattr(device, 'preset_value', 0))
                            
                            # 演算実行
                            if operation == 'MOV':
                                device.current_value = preset_value
                            elif operation == 'ADD':
                                device.current_value = current_value + preset_value
                            elif operation == 'SUB':
                                device.current_value = current_value - preset_value
                            elif operation == 'MUL':
                                # MUL演算の条件改善: preset_valueが0の場合は結果が0となることを明示
                                if preset_value == 0:
                                    device.current_value = 0
                                    print(f"[INFO] MUL operation with zero operand: {device.address} = {current_value} * 0 = 0")
                                else:
                                    device.current_value = current_value * preset_value
                            elif operation == 'DIV':
                                # DIV by zeroエラー処理改善: オペランド値が0の場合は除算を実行しない
                                if preset_value == 0:
                                    # ゼロ除算エラーの場合は値を変更せず、詳細なエラーログを出力
                                    print(f"[ERROR] Division by zero prevented in DATA_REGISTER {device.address}: {current_value} ÷ 0")
                                    print(f"[ERROR] Current value {current_value} remains unchanged due to zero operand")
                                else:
                                    # 整数除算を実行（PLC標準に準拠）
                                    device.current_value = current_value // preset_value  # 整数除算
                                    print(f"[INFO] DIV operation: {device.address} = {current_value} ÷ {preset_value} = {device.current_value}")
                            
                            # デバイスの状態をONに設定（演算実行済み）
                            device.state = True
                            
                            # デバッグ用ログ（立ち上がりエッジ検出成功）
                            print(f"[DATA_REGISTER] {device.address}: {operation} {preset_value} -> {device.current_value}")
                            
                        except Exception as e:
                            print(f"[ERROR] DATA_REGISTER {device.address} operation failed: {e}")
                    
                    # 通電中はstate=True、非通電中はstate=False
                    device.state = current_energized

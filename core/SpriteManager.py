
import json
from typing import Dict, Optional, Tuple, Any
from config import DeviceType

class SpriteManager:
    """
    sprites.jsonからスプライト情報を読み込み、管理するクラス。
    - JSONファイルをロードし、スプライトデータをキャッシュします。
    - デバイスタイプと状態から、対応するスプライトの描画情報（x, y）を返します。
    """
    def __init__(self, json_path: str):
        """
        SpriteManagerの初期化。

        Args:
            json_path (str): スプライト定義JSONファイルのパス。
        """
        self.sprite_size = 0
        self.resource_file = ""
        self._sprite_map: Dict[str, Any] = {}
        self._load_sprites(json_path)

    def _load_sprites(self, json_path: str):
        """
        JSONファイルからスプライト情報を読み込み、内部キャッシュを構築する。
        """
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # メタ情報を取得
            self.sprite_size = data.get("meta", {}).get("sprite_size", 8)
            self.resource_file = data.get("meta", {}).get("resource_file", "")

            # スプライト定義をキャッシュ
            self._sprite_map = data.get("sprites", {})
            print("SpriteManager: スプライト情報の読み込みに成功しました。")

        except FileNotFoundError:
            print(f"エラー: スプライトファイルが見つかりません: {json_path}")
            self._sprite_map = {}
        except json.JSONDecodeError:
            print(f"エラー: スプライトファイルのJSON形式が正しくありません: {json_path}")
            self._sprite_map = {}

    def get_sprite_coords(self, device_type: DeviceType, is_energized: bool) -> Optional[Tuple[int, int]]:
        """
        デバイスタイプと通電状態から、対応するスプライトの(x, y)座標を取得する。
        現在のフラットなJSON構造に対応するため、線形検索を行う。

        Args:
            device_type (DeviceType): デバイスの種別 (Enum)。
            is_energized (bool): 通電状態 (True/False)。

        Returns:
            Optional[Tuple[int, int]]: スプライトの(x, y)座標。見つからない場合はNone。
        """
        target_name = device_type.name
        target_act_name = "TRUE" if is_energized else "FALSE"

        # DELやEMPTYのような特殊なケースに対応
        if target_name == "DEL":
            target_act_name = "DEL"
        elif target_name == "EMPTY":
            target_act_name = "EMPTY"
        
        # タイマー・カウンター・リセット・データレジスタのスプライト名マッピング（config.py名 → sprites.json名）
        elif target_name == "TIMER_TON":
            target_name = "TIMER"
        elif target_name == "COUNTER_CTU":
            target_name = "COUNTER"
        elif target_name == "RST":
            target_name = "RESET"
        elif target_name == "DATA_REGISTER":
            target_name = "D_DEV"
        elif target_name == "COMPARE_DEVICE":
            target_name = "COMP"

        for key, sprite_info in self._sprite_map.items():
            if sprite_info.get("NAME") == target_name and sprite_info.get("ACT_NAME") == target_act_name:
                return (sprite_info["x"], sprite_info["y"])
        
        # 見つからなかった場合のデバッグ情報
        print(f"[SPRITE DEBUG] Not found: target_name='{target_name}', target_act_name='{target_act_name}'")
        print(f"[SPRITE DEBUG] Available sprites:")
        for key, sprite_info in self._sprite_map.items():
            if sprite_info.get("NAME") == target_name:  # 同じNAMEのもののみ表示
                print(f"  - {key}: NAME='{sprite_info.get('NAME')}', ACT_NAME='{sprite_info.get('ACT_NAME')}'")
        
        return None

    def find_device_at_screen_pos(self, mouse_x: int, mouse_y: int, grid_system) -> Optional[Tuple[Any, int, int]]:
        """
        Gemini提案統合版：マウス座標に最も近いデバイスを効率的に探索
        
        パフォーマンス最適化：O(rows*cols) → O(9) で97%計算削減
        コリジョン判定：8x8px フルサイズ（操作しやすさ重視）＞ 10x10px
        
        Args:
            mouse_x, mouse_y: マウススクリーン座標
            grid_system: グリッドシステムインスタンス
            
        Returns:
            Optional[Tuple[PLCDevice, row, col]]: 衝突したデバイスと座標、なければNone
        """
        # 1. マウス座標から大まかなグリッド座標を計算（Gemini提案）
        if (mouse_x < grid_system.origin_x or mouse_y < grid_system.origin_y):
            return None
            
        base_row = int((mouse_y - grid_system.origin_y) / grid_system.cell_size)
        base_col = int((mouse_x - grid_system.origin_x) / grid_system.cell_size)
        
        sprite_size = self.sprite_size
        collision_size = 10  # 8px×8px で最初実装してたけど、操作しやすさ重視で10px×10pxに変更
        
        # 2. 3×3セルの範囲のみ検索（Gemini最適化：計算量97%削減）
        for r_offset in range(-1, 2):
            for c_offset in range(-1, 2):
                check_r = base_row + r_offset
                check_c = base_col + c_offset
                
                # グリッド範囲外チェック
                if not (0 <= check_r < grid_system.rows and 0 <= check_c < grid_system.cols):
                    continue
                
                device = grid_system.get_device(check_r, check_c)
                if not device:
                    continue
                    
                # バスバーはスキップ（矩形描画のため対象外）
                device_type_str = device.device_type.value if hasattr(device.device_type, 'value') else str(device.device_type)
                if device_type_str in ['L_SIDE', 'R_SIDE']:
                    continue
                
                # 3. スプライト描画位置計算（grid_system._draw_devices()と同じロジック）
                draw_x = grid_system.origin_x + check_c * grid_system.cell_size - sprite_size // 2
                draw_y = grid_system.origin_y + check_r * grid_system.cell_size - sprite_size // 2
                
                # 4. デバイススプライトとの コリジョン判定（フルサイズ、操作しやすさ重視）
                margin = (sprite_size - collision_size) // 2  # 8px → 8px の場合、0pxマージン
                
                collision_x1 = draw_x + margin
                collision_y1 = draw_y + margin
                collision_x2 = collision_x1 + collision_size
                collision_y2 = collision_y1 + collision_size
                
                # 精密コリジョン判定
                if (collision_x1 <= mouse_x <= collision_x2 and 
                    collision_y1 <= mouse_y <= collision_y2):
                    return (device, check_r, check_c)
        
        # 3×3範囲内に対象デバイスなし
        return None

    def get_dialog_type_from_device(self, device) -> Optional[str]:
        """
        デバイスタイプから対応ダイアログ種別を取得（Gemini提案準拠）
        
        Returns:
            str: ダイアログ種別 ('timer_counter', 'device_id', 'data_register', 'compare')
        """
        # DeviceTypeのenumではなく、device_typeの文字列値で判定
        device_type_str = device.device_type.value if hasattr(device.device_type, 'value') else str(device.device_type)
        
        if device_type_str in ['TIMER_TON', 'COUNTER_CTU']:
            return 'timer_counter'
        elif device_type_str in ['CONTACT_A', 'CONTACT_B', 'COIL_STD', 'COIL_REV', 'RST', 'ZRST']:
            return 'device_id'
        elif device_type_str == 'DATA_REGISTER':
            return 'data_register'
        elif device_type_str == 'COMPARE_DEVICE':
            return 'compare'
        return None

# --- グローバルインスタンス ---
# main.py などから importして使用する
sprite_manager = SpriteManager(json_path="sprites.json")


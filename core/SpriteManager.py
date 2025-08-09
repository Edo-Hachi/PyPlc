
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
        
        # タイマー・カウンターのスプライト名マッピング（config.py名 → sprites.json名）
        elif target_name == "TIMER_TON":
            target_name = "TIMER"
        elif target_name == "COUNTER_CTU":
            target_name = "COUNTER"

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

# --- グローバルインスタンス ---
# main.py などから importして使用する
sprite_manager = SpriteManager(json_path="sprites.json")


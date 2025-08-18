"""
DialogSystem - ダイアログコントローラー一元管理システム

目的: 複数のダイアログコントローラーを統合管理し、main.pyの保守性を向上させる
作成日: 2025-08-18
"""

from typing import List, Any, Protocol


class DialogController(Protocol):
    """ダイアログコントローラーが実装すべきインターフェース"""
    
    def update(self) -> None:
        """コントローラーの更新処理"""
        ...
    
    def is_active(self) -> bool:
        """ダイアログがアクティブかどうかを返す"""
        ...


class DialogSystem:
    """
    ダイアログシステム一元管理クラス
    
    機能:
    - 複数のダイアログコントローラーを登録・管理
    - 全コントローラーの一括更新処理
    - アクティブダイアログの状態監視
    """
    
    def __init__(self):
        """DialogSystemの初期化"""
        self.controllers: List[DialogController] = []
        
    def register_controller(self, controller: DialogController) -> DialogController:
        """
        ダイアログコントローラーを登録
        
        Args:
            controller: 登録するダイアログコントローラー
            
        Returns:
            登録されたコントローラー（チェーン用）
        """
        self.controllers.append(controller)
        return controller
        
    def update(self) -> None:
        """
        登録されている全コントローラーの更新処理を実行
        
        各コントローラーのupdate()メソッドを順次呼び出す
        update()メソッドを持たないコントローラーは安全にスキップされる
        """
        for controller in self.controllers:
            if hasattr(controller, 'update') and callable(getattr(controller, 'update')):
                controller.update()
                
    @property
    def has_active_dialogs(self) -> bool:
        """
        アクティブなダイアログがあるかチェック
        
        Returns:
            bool: いずれかのコントローラーがアクティブな場合True
        """
        for controller in self.controllers:
            if hasattr(controller, 'is_active') and callable(getattr(controller, 'is_active')):
                if controller.is_active():
                    return True
        return False
        
    def get_active_dialog_count(self) -> int:
        """
        アクティブなダイアログの数を取得
        
        Returns:
            int: アクティブなダイアログの数
        """
        count = 0
        for controller in self.controllers:
            if hasattr(controller, 'is_active') and callable(getattr(controller, 'is_active')):
                if controller.is_active():
                    count += 1
        return count
        
    def get_registered_controllers(self) -> List[DialogController]:
        """
        登録されているコントローラーのリストを取得（デバッグ用）
        
        Returns:
            List[DialogController]: 登録済みコントローラーのリスト
        """
        return self.controllers.copy()
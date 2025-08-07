"""
BaseDialog - ダイアログシステムの基底クラス

PyPlc Ver3 Dialog System - Phase 1 MVP Implementation
疎結合イベントシステムとモーダル処理を提供
"""

import pyxel
from typing import Dict, List, Any, Callable, Optional
from abc import ABC, abstractmethod


class BaseDialog(ABC):
    """
    すべてのダイアログの基底クラス
    
    機能:
    - モーダルダイアログ処理
    - イベントシステム統合
    - 基本的な描画・入力処理
    - 疎結合コールバックシステム
    """
    
    def __init__(self, title: str = "", width: int = 200, height: int = 150):
        """
        BaseDialog初期化
        
        Args:
            title: ダイアログタイトル
            width: ダイアログ幅
            height: ダイアログ高さ
        """
        self.title = title
        self.width = width
        self.height = height
        
        # ダイアログ位置（中央配置）
        self.x = (pyxel.width - width) // 2
        self.y = (pyxel.height - height) // 2
        
        # ダイアログ状態
        self.is_visible = False
        self.result = None
        self.result_ready = False
        
        # コントロール管理
        self.controls: Dict[str, Any] = {}
        self.control_order: List[str] = []
        
        # イベントシステム
        self.event_callbacks: Dict[str, List[Callable]] = {}
        
        # 入力状態
        self.mouse_x = 0
        self.mouse_y = 0
        self.last_mouse_state = False
        
    def add_control(self, control_id: str, control: Any) -> None:
        """
        コントロールを追加
        
        Args:
            control_id: コントロールID
            control: コントロールオブジェクト
        """
        self.controls[control_id] = control
        if control_id not in self.control_order:
            self.control_order.append(control_id)
    
    def get_control(self, control_id: str) -> Optional[Any]:
        """
        コントロールを取得
        
        Args:
            control_id: コントロールID
            
        Returns:
            コントロールオブジェクト（存在しない場合はNone）
        """
        return self.controls.get(control_id)
    
    def on(self, event_name: str, callback: Callable) -> None:
        """
        イベントコールバックを登録（疎結合イベントシステム）
        
        Args:
            event_name: イベント名
            callback: コールバック関数
        """
        if event_name not in self.event_callbacks:
            self.event_callbacks[event_name] = []
        self.event_callbacks[event_name].append(callback)
    
    def emit(self, event_name: str, *args, **kwargs) -> None:
        """
        イベントを発火
        
        Args:
            event_name: イベント名
            *args: イベント引数
            **kwargs: イベントキーワード引数
        """
        if event_name in self.event_callbacks:
            for callback in self.event_callbacks[event_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Event callback error: {e}")
    
    def show(self) -> Any:
        """
        ダイアログをモーダル表示
        
        Returns:
            ダイアログの結果
        """
        self.is_visible = True
        self.result = None
        self.result_ready = False
        
        # モーダルループ開始前にイベント発火
        self.emit("dialog_show")
        
        # モーダルループ
        while self.is_visible and not self.result_ready:
            # 背景クリア（重要：座標系の問題を回避）
            pyxel.cls(pyxel.COLOR_BLACK)
            
            # 入力処理
            self._handle_input()
            
            # 描画処理
            self._draw()
            
            # フレーム更新
            pyxel.flip()
        
        # ダイアログ終了時にイベント発火
        self.emit("dialog_close", self.result)
        
        return self.result
    
    def close(self, result: Any = None) -> None:
        """
        ダイアログを閉じる
        
        Args:
            result: ダイアログの結果
        """
        self.result = result
        self.result_ready = True
        self.is_visible = False
    
    def _handle_input(self) -> None:
        """
        入力処理（基本実装）
        """
        # マウス位置更新
        self.mouse_x = pyxel.mouse_x
        self.mouse_y = pyxel.mouse_y
        
        # マウスクリック検出
        mouse_clicked = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
        
        # ESCキーでキャンセル
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.close(False)
            return
        
        # 各コントロールの入力処理
        for control_id in self.control_order:
            control = self.controls[control_id]
            if hasattr(control, 'handle_input'):
                control.handle_input(self.mouse_x, self.mouse_y, mouse_clicked)
        
        # カスタム入力処理
        self._handle_custom_input()
    
    def _handle_custom_input(self) -> None:
        """
        カスタム入力処理（サブクラスでオーバーライド）
        """
        pass
    
    def _draw(self) -> None:
        """
        描画処理
        """
        # ダイアログ背景
        pyxel.rect(self.x, self.y, self.width, self.height, pyxel.COLOR_GRAY)
        pyxel.rectb(self.x, self.y, self.width, self.height, pyxel.COLOR_WHITE)
        
        # タイトル描画
        if self.title:
            title_x = self.x + 5
            title_y = self.y + 5
            pyxel.text(title_x, title_y, self.title, pyxel.COLOR_WHITE)
        
        # 各コントロールの描画
        for control_id in self.control_order:
            control = self.controls[control_id]
            if hasattr(control, 'draw'):
                control.draw(self.x, self.y)
        
        # カスタム描画処理
        self._draw_custom()
    
    @abstractmethod
    def _draw_custom(self) -> None:
        """
        カスタム描画処理（サブクラスで実装）
        """
        pass
    
    def _point_in_rect(self, px: int, py: int, rect_x: int, rect_y: int, 
                      rect_w: int, rect_h: int) -> bool:
        """
        点が矩形内にあるかチェック
        
        Args:
            px, py: 点の座標
            rect_x, rect_y: 矩形の左上座標
            rect_w, rect_h: 矩形のサイズ
            
        Returns:
            点が矩形内にある場合True
        """
        return (rect_x <= px <= rect_x + rect_w and 
                rect_y <= py <= rect_y + rect_h)

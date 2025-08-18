"""
データレジスタ設定ダイアログのコントローラー（モックアップ）
"""
from .dialog_manager import DialogManager

class DataRegisterDialogController:
    """データレジスタ設定ダイアログのロジックを管理する（現在モックアップ）"""

    # TODO: このダイアログは現在モックアップです。
    # Phase 3の後半で、以下の機能を実装する必要があります:
    #   - ドロップダウン（またはリストボックス）での操作選択 (MOV, ADD, SUB, etc.)
    #   - オペランド（操作対象の値）を入力するテキストボックス
    #   - 入力値のバリデーション
    #   - 結果をmain.pyに返すための完全な結果処理

    def __init__(self, dialog_manager: DialogManager):
        self.dialog_manager = dialog_manager
        self.active_dialog = None

    def show_dialog(self):
        """ダイアログを表示する"""
        self.dialog_manager.show("IDD_DATA_REGISTER_MOCKUP")
        self.active_dialog = self.dialog_manager.active_dialog

    def update(self):
        """フレームごとの更新処理"""
        # マネージャーと自身のアクティブダイアログが一致しない場合、自身を非アクティブ化
        if self.active_dialog and self.active_dialog != self.dialog_manager.active_dialog:
            self.active_dialog = None

        if not self.active_dialog:
            return

        # OKボタンでダイアログを閉じるだけのシンプルな処理
        ok_button = self._find_widget("IDOK")
        if ok_button and ok_button.is_pressed:
            self.dialog_manager.close()

    def get_result(self):
        """結果取得（モックアップのため常にNone）""" 
        return None

    def _find_widget(self, widget_id: str):
        """ウィジェットIDでウィジェットを検索"""
        if not self.active_dialog:
            return None
        for widget in self.active_dialog.widgets:
            if hasattr(widget, 'id') and widget.id == widget_id:
                return widget
        return None

    def is_active(self) -> bool:
        """ダイアログがアクティブかどうかを返す"""
        return self.dialog_manager.active_dialog is not None and self.active_dialog is not None

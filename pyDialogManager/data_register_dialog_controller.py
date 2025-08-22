"""
データレジスタ設定ダイアログのコントローラー（モックアップ）
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.base_dialog_controller import PyPlcDialogController
from .dialog_manager import DialogManager

class DataRegisterDialogController(PyPlcDialogController):
    """データレジスタ設定ダイアログのロジックを管理する（現在モックアップ）"""

    # TODO: このダイアログは現在モックアップです。
    # Phase 3の後半で、以下の機能を実装する必要があります:
    #   - ドロップダウン（またはリストボックス）での操作選択 (MOV, ADD, SUB, etc.)
    #   - オペランド（操作対象の値）を入力するテキストボックス
    #   - 入力値のバリデーション
    #   - 結果をmain.pyに返すための完全な結果処理

    def __init__(self, dialog_manager: DialogManager):
        super().__init__(dialog_manager)

    def show_dialog(self):
        """ダイアログを表示する"""
        self._safe_show_dialog("IDD_DATA_REGISTER_MOCKUP")

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

    # get_result()は基底クラスから継承

    # _find_widget()は基底クラスから継承

    # is_active()は基底クラスから継承（Stale参照検出機能付き）

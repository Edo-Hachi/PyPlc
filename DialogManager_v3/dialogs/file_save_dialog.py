"""
PyPlc Ver3 Dialog System - FileSaveDialog
Refactored to align with DialogManager_v3 architecture.
"""
import os
import re
import pyxel
from typing import Optional, Tuple

from ..core.base_dialog import BaseDialog
from ..controls.textbox_control import TextBoxControl
from ..controls.label_control import LabelControl
from ..controls.button_control import ButtonControl

class FileSaveDialogJSON(BaseDialog):
    """
    A dialog for saving a file.
    This class is implemented following the clean architecture of DialogManager_v3,
    relying on BaseDialog for event handling and drawing.
    """

    def __init__(self,
                 default_filename: str = "my_circuit",
                 title: str = "Save Circuit File",
                 width: int = 340,
                 height: int = 280):
        """
        Initializes the FileSaveDialog.
        """
        # Dialog settings
        x = (pyxel.width - width) // 2
        y = (pyxel.height - height) // 2
        super().__init__(title=title, x=x, y=y, width=width, height=height)

        # --- State ---
        self.dialog_result: Optional[bool] = None
        self.input_filename: str = ""

        # --- Create Controls ---
        self.add_control(LabelControl(x=20, y=30, text="File name:"))

        self.filename_textbox = TextBoxControl(
            x=20, y=55, width=300, height=25,
            max_length=50,
            input_filter="filename_safe"
        )
        self.filename_textbox.suggest_filename(default_filename, ".csv")
        self.add_control(self.filename_textbox)

        self.preview_label = LabelControl(
            x=20, y=90, width=300,
            text=f"Will be saved as: {self.filename_textbox.text}",
            color=pyxel.COLOR_YELLOW
        )
        self.add_control(self.preview_label)
        
        self.status_label = LabelControl(
            x=20, y=115, width=300,
            text="Enter filename and click Save"
        )
        self.add_control(self.status_label)

        self.error_label = LabelControl(
            x=20, y=140, width=300,
            text="", color=pyxel.COLOR_RED
        )
        self.error_label.visible = False
        self.add_control(self.error_label)

        self.save_button = ButtonControl(
            x=70, y=190, width=80, height=30, text="Save"
        )
        self.add_control(self.save_button)

        self.cancel_button = ButtonControl(
            x=190, y=190, width=80, height=30, text="Cancel"
        )
        self.add_control(self.cancel_button)

        # --- Event Handlers ---
        self.filename_textbox.on('change', self._on_text_changed)
        self.filename_textbox.on('enter', self._on_save_pressed)
        self.save_button.on('click', self._on_save_pressed)
        self.cancel_button.on('click', self._on_cancel_pressed)

        # Set initial focus
        self.focused_control = self.filename_textbox

    def _on_save_pressed(self, sender=None, data=None):
        """Handles the Save button click or Enter key press."""
        filename = self.filename_textbox.get_edited_filename()
        if filename and self.filename_textbox.has_valid_filename():
            self.input_filename = filename
            self.dialog_result = True
            self.close(True)
        else:
            self._show_error_message("Invalid or empty filename.")

    def _on_cancel_pressed(self, sender=None, data=None):
        """Handles the Cancel button click."""
        self.dialog_result = False
        self.close(False)

    def _on_text_changed(self, sender, data):
        """Handles text changes for real-time preview and validation."""
        self._update_filename_preview()
        self._validate_filename_realtime()

    def _update_filename_preview(self):
        """Updates the label showing the final filename."""
        current_text = self.filename_textbox.text
        if current_text:
            if not current_text.lower().endswith('.csv'):
                 preview_text = f"Will be saved as: {current_text}.csv"
            else:
                 preview_text = f"Will be saved as: {current_text}"
        else:
            preview_text = "Enter a filename."
        self.preview_label.text = preview_text

    def _validate_filename_realtime(self):
        """Performs real-time validation and shows/hides the error label."""
        if self.filename_textbox.has_valid_filename():
            self._clear_error_message()
            self.status_label.text = "Ready to save."
        else:
            if self.filename_textbox.text:
                self._show_error_message("Filename contains invalid characters.")
            else:
                self._clear_error_message()
                self.status_label.text = "Enter filename and click Save."

    def _show_error_message(self, message: str):
        """Shows an error message."""
        self.error_label.text = message
        self.error_label.visible = True

    def _clear_error_message(self):
        """Clears the error message."""
        self.error_label.text = ""
        self.error_label.visible = False

    def show_save_dialog(self) -> Tuple[bool, str]:
        """
        Shows the dialog modally and returns the result.
        This is the main entry point for this dialog.
        """
        self.dialog_result = None
        self.error_label.visible = False
        self.focused_control = self.filename_textbox
        
        success = self.show_modal_loop()

        if success and self.dialog_result:
            return True, self.input_filename
        else:
            return False, ""

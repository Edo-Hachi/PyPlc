"""
PyPlc Ver3 - DeviceIdDialog for DialogManager_v3

Allows users to input a device ID (address) for PLC devices like contacts and coils.
This is a core component for setting device parameters.
"""
import re
import pyxel
from typing import Tuple, Optional

from ..core.base_dialog import BaseDialog
from ..controls.label_control import LabelControl
from ..controls.textbox_control import TextBoxControl
from ..controls.button_control import ButtonControl
from config import DeviceType

class DeviceIdDialog(BaseDialog):
    """
    A dialog for inputting a device ID (e.g., X001, Y10, M100).
    It uses the components from DialogManager_v3.
    """

    def __init__(self, device_type: DeviceType, current_id: str = ""):
        """
        Initializes the DeviceIdDialog.

        Args:
            device_type: The type of the PLC device.
            current_id: The current ID of the device, to be displayed initially.
        """
        # Dialog settings
        dialog_width = 220
        dialog_height = 140
        dialog_x = (pyxel.width - dialog_width) // 2
        dialog_y = (pyxel.height - dialog_height) // 2
        
        super().__init__(
            x=dialog_x,
            y=dialog_y,
            width=dialog_width,
            height=dialog_height,
            title="Set Device ID"
        )

        self.device_type = device_type
        self.result_id: Optional[str] = None

        # --- Create Controls ---
        self.add_control(LabelControl(x=20, y=25, text=f"Type: {self.device_type.name}"))
        self.add_control(LabelControl(x=20, y=40, text="Enter Device ID:"))

        self.device_id_input = TextBoxControl(
            x=20, y=60, width=180, height=20,
            text=current_id,
            input_filter="filename_safe"
        )
        self.add_control(self.device_id_input)

        self.error_label = LabelControl(x=20, y=85, width=180, text="", color=pyxel.COLOR_RED)
        self.error_label.visible = False
        self.add_control(self.error_label)

        self.ok_button = ButtonControl(x=20, y=100, width=80, height=20, text="OK")
        self.add_control(self.ok_button)

        self.cancel_button = ButtonControl(x=120, y=100, width=80, height=20, text="Cancel")
        self.add_control(self.cancel_button)

        # --- Event Handlers ---
        self.device_id_input.on('enter', self._on_enter_pressed)
        self.device_id_input.on('change', self._on_text_changed)
        self.ok_button.on('click', self._on_ok_clicked)
        self.cancel_button.on('click', self._on_cancel_clicked)

        # Set initial focus
        self.focused_control = self.device_id_input

    def _on_text_changed(self, sender, data):
        """Handles the text change event for real-time validation."""
        input_text = data.get('value', '')
        is_valid, error_message = self._validate_address(input_text)
        if not is_valid and input_text:
            self.error_label.text = error_message
            self.error_label.visible = True
        else:
            self.error_label.visible = False

    def _validate_address(self, address: str) -> Tuple[bool, str]:
        """
        Validates the PLC device address based on its type.
        Routes to specific validation functions for special device types.
        """
        address = address.strip().upper()
        if not address:
            return False, "ID cannot be empty."

        if self.device_type == DeviceType.RST:
            return self._validate_rst_address(address)

        if self.device_type == DeviceType.ZRST:
            if not re.match(r'^[TC0-9,\s-]*$', address):
                return False, "Invalid chars for ZRST. Use T,C,0-9,-,,"
            return True, ""

        match = re.match(r'^([XYMLTCD])(\d+)$', address)
        if not match:
            return False, "Format error. Use e.g., X0, M100."

        prefix = match.group(1)
        number = int(match.group(2))

        valid_prefixes = {
            DeviceType.CONTACT_A: "XYMLTC",
            DeviceType.CONTACT_B: "XYMLTC",
            DeviceType.COIL_STD: "YM",
            DeviceType.COIL_REV: "YM",
            DeviceType.TIMER_TON: "T",
            DeviceType.COUNTER_CTU: "C",
        }.get(self.device_type)

        if valid_prefixes and prefix not in valid_prefixes:
            return False, f"'{prefix}' is not valid for {self.device_type.name}."

        if prefix in "TC" and not (0 <= number <= 255):
            return False, "T/C number must be 0-255."

        return True, ""

    def _validate_rst_address(self, address: str) -> Tuple[bool, str]:
        """Validates a target address for an RST instruction."""
        match = re.match(r'^(T|C)(\d+)$', address)
        if not match:
            return False, "RST target must be T or C (e.g., T5)."
        
        number = int(match.group(2))
        if not (0 <= number <= 255):
            return False, "RST target number must be 0-255."
            
        return True, ""

    def _on_enter_pressed(self, sender, data):
        """Handles the Enter key press event in the textbox."""
        self._on_ok_clicked(sender, data)

    def _on_ok_clicked(self, sender, data):
        """Handles the OK button click event."""
        input_text = self.device_id_input.text
        is_valid, error_message = self._validate_address(input_text)
        if is_valid:
            self.result_id = input_text.strip().upper()
            self.close(True)
        else:
            self.error_label.text = error_message
            self.error_label.visible = True

    def _on_cancel_clicked(self, sender, data):
        """Handles the Cancel button click event."""
        self.close(False)

    def show(self) -> Tuple[bool, str]:
        """
        Shows the dialog modally and returns the result.

        Returns:
            A tuple of (bool, str), where bool is True if OK was clicked
            and the string is the entered device ID.
        """
        self.error_label.visible = False
        success = self.show_modal_loop()
        if success and self.result_id is not None:
            return (True, self.result_id)
        else:
            return (False, "")

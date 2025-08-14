"""
DialogManager_v3 Example

This file demonstrates the basic usage of DialogManager_v3.
"""
import os
import sys
import pyxel
from pathlib import Path

# Add project root directory to path
sys.path.append(str(Path(__file__).parent.parent))

from DialogManager_v3 import BaseDialog, dialog_loader, ButtonControl, LabelControl


class SampleApp:
    """Application that demonstrates the usage of DialogManager_v3"""
    
    def __init__(self):
        """Initialize the application."""
        # Initialize Pyxel window
        pyxel.init(400, 300, title="DialogManager_v3 Sample", fps=30)
        
        # Show mouse cursor
        pyxel.mouse(True)
        
        # Load sample dialog
        self.load_sample_dialog()
        
        # Create custom dialog
        self.create_custom_dialog()
        
        # Currently displayed dialog
        self.current_dialog = None
        
        # Enable keyboard input
        pyxel.run(self.update, self.draw)
    
    def load_sample_dialog(self):
        """Load sample dialog from JSON file."""
        try:
            # Build path based on script directory
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Print current working directory (for debugging)
            print(f"Current working directory: {os.getcwd()}")
            
            # Directly specify the path to the definitions directory
            definitions_dir = os.path.abspath(os.path.join(base_dir, "definitions"))
            print(f"Definitions directory: {definitions_dir}")
            
            # Check if directory exists
            if not os.path.exists(definitions_dir):
                # Try to create directory if it doesn't exist
                try:
                    os.makedirs(definitions_dir, exist_ok=True)
                    print(f"Created definitions directory: {definitions_dir}")
                except Exception as e:
                    raise FileNotFoundError(f"Failed to create definitions directory: {e}")
            
            # Set loader's base path (specify parent directory)
            dialog_loader.base_path = Path(base_dir)
            print(f"Loader base path: {dialog_loader.base_path}")
            
            # Show available definition files (for debugging)
            print("\nAvailable definition files:")
            json_files = list(Path(definitions_dir).glob("*.json"))
            if not json_files:
                print("  No definition files found")
            else:
                for f in json_files:
                    print(f"  - {f.name}")
            
            # Directly specify the sample dialog path
            sample_file = Path(definitions_dir) / "sample_dialog.json"
            print(f"\nAttempting to load file: {sample_file}")
            
            if not sample_file.exists():
                # Create sample file if it doesn't exist
                sample_content = """{
  "title": "Sample Dialog",
  "width": 300,
  "height": 200,
  "modal": true,
  "controls": [
    {
      "type": "label",
      "id": "lbl_message",
      "x": 20,
      "y": 20,
      "text": "Hello World",
      "color": 7
    },
    {
      "type": "button",
      "id": "btn_ok",
      "x": 100,
      "y": 150,
      "width": 80,
      "height": 24,
      "text": "OK",
      "color": 5,
      "hover_color": 13
    }
  ]
}"""
                with open(sample_file, 'w', encoding='utf-8') as f:
                    f.write(sample_content)
                print("Created sample dialog file")
            
            # Load dialog
            print("\nLoading dialog...")
            
            # Load dialog definition
            dialog_def = dialog_loader.load_dialog_definition("sample_dialog")
            
            # Create dialog
            self.sample_dialog = dialog_loader.create_dialog(
                dialog_def,
                dialog_class=BaseDialog
            )
            
            if self.sample_dialog is None:
                raise ValueError("Failed to create dialog (returned None)")
                
            print("\nSuccessfully created dialog!")
            print(f"Number of controls loaded: {len(self.sample_dialog.controls)}")
            
            # Set up click event for OK button
            ok_button = self.sample_dialog.find_control_by_id("btn_ok")
            if ok_button:
                ok_button.on("click", self.on_ok_click)  # Method name changed to on_ok_click
            else:
                print("Warning: OK button not found")
                
        except Exception as e:
            import traceback
            print("\n=== Error loading dialog ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print("\nStack trace:")
            traceback.print_exc()
            print("======================================\n")
            
            # Fallback to default dialog on error
            print("\nCreating default dialog...")
            self.sample_dialog = BaseDialog(
                title="Default Dialog",
                width=300,
                height=200
            )
            
            # Add a label to display the error message
            from DialogManager_v3.controls import LabelControl
            error_label = LabelControl(
                x=20, y=50,
                text=f"Error: {str(e)}",
                color=8
            )
            self.sample_dialog.controls.append(error_label)
            
            # Set up click event for Cancel button
            cancel_button = self.sample_dialog.find_control_by_id("btn_cancel")
            if cancel_button:
                cancel_button.on("click", self.on_cancel_click)
                
            print("Created default dialog.")
            
            # Display error message
            print(f"\n=== Error loading dialog ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}\n")
            
            # Print stack trace
            import traceback
            traceback.print_exc()
            print("="*40 + "\n")
    
    def create_custom_dialog(self):
        """Create a custom dialog programmatically."""
        # Create custom dialog
        self.custom_dialog = BaseDialog(
            title="Custom Dlg",
            width=250,
            height=180
        )
        
        # Add label
        label = LabelControl(
            x=20,
            y=20,
            text="This is a programmatically created dialog.",
            color=7
        )
        self.custom_dialog.add_control(label)
        
        # Add close button
        close_button = ButtonControl(
            x=150,
            y=130,
            width=80,
            height=30,
            text="Close",
            bg_color=8,
            hover_color=10
        )
        close_button.on("click", self.on_close_custom_dialog)
        self.custom_dialog.add_control(close_button)
    
    def on_ok_click(self, sender, data):
        """Event handler when OK button is clicked"""
        print("OK button was clicked.")
        
        # Get the message label
        lbl_message = self.sample_dialog.find_control_by_id("lbl_message")
        
        if lbl_message:
            print(f"Message: {lbl_message.text}")
        else:
            print("Message label not found.")
        
        # Close dialog
        self.sample_dialog.visible = False
        self.current_dialog = None
    
    def on_cancel_click(self, sender, data):
        """Event handler when Cancel button is clicked"""
        print("Cancel button was clicked.")
        
        # Close dialog
        self.sample_dialog.visible = False
        self.current_dialog = None
    
    def on_close_custom_dialog(self, sender, data):
        """Event handler when custom dialog's close button is clicked"""
        print("Closing custom dialog.")
        self.custom_dialog.visible = False
        self.current_dialog = None
    
    def update(self):
        """Update the game state."""
        # Handle mouse input
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mouse_x = pyxel.mouse_x
            mouse_y = pyxel.mouse_y
            if self.current_dialog:
                # Pass mouse click to the current dialog
                self.current_dialog.handle_mouse(mouse_x, mouse_y, True)
        
        # Show sample dialog on SPACE key
        if pyxel.btnp(pyxel.KEY_SPACE) and not self.current_dialog:
            self.sample_dialog.visible = True
            self.current_dialog = self.sample_dialog
            print("Sample dialog displayed.")
            print(f"Number of controls: {len(self.sample_dialog.controls)}")
            for i, control in enumerate(self.sample_dialog.controls):
                print(f"  {i+1}. {control.__class__.__name__} (visible={getattr(control, 'visible', True)})")
        
        # Show custom dialog on C key
        if pyxel.btnp(pyxel.KEY_C) and not self.current_dialog:
            self.custom_dialog.show_modal()
            self.current_dialog = self.custom_dialog
            print("Custom dialog displayed.")
        
        # Close dialog on ESC key
        if pyxel.btnp(pyxel.KEY_ESCAPE) and self.current_dialog:
            self.current_dialog.hide()
            self.current_dialog = None
            print("Dialog closed.")
        
        # Update current dialog
        if self.current_dialog:
            # Handle continuous mouse movement for hover effects
            mouse_x = pyxel.mouse_x
            mouse_y = pyxel.mouse_y
            self.current_dialog.handle_mouse(mouse_x, mouse_y, False)
            self.current_dialog.update()
    
    def draw(self):
        """Draw the game."""
        # Clear background
        pyxel.cls(0)
        
        # Draw instruction text
        pyxel.text(10, 10, "DialogManager_v3 Sample Application", 7)
        pyxel.text(10, 30, "SPACE: Show sample dialog", 7)
        pyxel.text(10, 45, "C Key: Show custom dialog", 7)
        pyxel.text(10, 60, "ESC: Close dialog", 7)
        
        # Draw currently displayed dialog
        if self.current_dialog:
            self.current_dialog.draw()


if __name__ == "__main__":
    # Start the application
    app = SampleApp()

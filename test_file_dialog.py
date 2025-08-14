"""
File Dialog Test

This script tests the FileLoadDialog implementation.
"""
import os
import sys
import pyxel
from pathlib import Path

# Add the DialogManager_v3 directory to the Python path
sys.path.append(str(Path(__file__).parent / "DialogManager_v3"))

from dialogs.file_load_dialog import FileLoadDialogJSON

class FileDialogTest:
    def __init__(self):
        # Initialize Pyxel
        pyxel.init(640, 480, title="File Dialog Test")
        
        # Application state
        self.selected_file = "No file selected"
        self.file_dialog = None
        self.show_dialog = False
        
        # Set color palette
        self._setup_colors()
        
        # Start the main loop
        pyxel.run(self.update, self.draw)
    
    def _setup_colors(self):
        """Set up the color palette"""
        pyxel.colors[0] = 0x000000  # Black
        pyxel.colors[1] = 0x1D2B53  # Dark blue
        pyxel.colors[2] = 0x7E2553  # Dark purple
        pyxel.colors[3] = 0x008751  # Dark green
        pyxel.colors[4] = 0xAB5236  # Brown
        pyxel.colors[5] = 0x5F574F  # Dark gray
        pyxel.colors[6] = 0xC2C3C7  # Light gray
        pyxel.colors[7] = 0xFFF1E8  # White
        pyxel.colors[8] = 0xFF004D  # Red
        pyxel.colors[9] = 0xFFA300  # Orange
        pyxel.colors[10] = 0xFFEC27  # Yellow
        pyxel.colors[11] = 0x00E436  # Green
        pyxel.colors[12] = 0x29ADFF  # Blue
        pyxel.colors[13] = 0x83769C  # Indigo
        pyxel.colors[14] = 0xFF77A8  # Pink
        pyxel.colors[15] = 0xFFCCAA  # Peach
    
    def update(self):
        """Update game state"""
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        
        # Open file dialog when SPACE is pressed
        if pyxel.btnp(pyxel.KEY_SPACE) and not self.show_dialog:
            self._open_file_dialog()
        
        # Update file dialog if it's open
        if self.show_dialog and self.file_dialog:
            self.file_dialog.update()
            
            # Check if dialog was closed
            if not self.file_dialog.visible:
                if not self.file_dialog.cancelled and self.file_dialog.selected_file:
                    self.selected_file = f"Selected: {self.file_dialog.selected_file}"
                else:
                    self.selected_file = "Dialog was cancelled"
                self.show_dialog = False
                self.file_dialog = None
    
    def _open_file_dialog(self):
        """Open the file dialog"""
        self.file_dialog = FileLoadDialogJSON(
            initial_dir=os.path.expanduser("~"),
            file_pattern="*.*",
            title="ファイルを選択"
        )
        self.show_dialog = True
        self.selected_file = "Selecting file..."
    
    def draw(self):
        """Draw the game"""
        # Clear screen
        pyxel.cls(0)
        
        # Draw title
        pyxel.text(10, 10, "File Dialog Test", 7)
        pyxel.text(10, 20, "Press SPACE to open file dialog", 8)
        pyxel.text(10, 30, "Press ESC to exit", 8)
        
        # Draw selected file
        pyxel.text(10, 100, self.selected_file, 7)
        
        # Draw file dialog if it's open
        if self.show_dialog and self.file_dialog:
            self.file_dialog.draw()

if __name__ == "__main__":
    FileDialogTest()

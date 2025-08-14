"""
File Dialog Example Runner

This script runs the file dialog example from the root directory.
"""
import os
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent))

# Import the example module
from DialogManager_v3.examples import file_dialog_example

# This will run the example when the script is executed
if __name__ == "__main__":
    # The example will run automatically when imported
    pass

"""
PyPlc Ver3 Dialog System - FileLoadDialog
Refactored to align with DialogManager_v3 architecture.
"""
import os
import pyxel
from typing import Optional, List, Tuple

from ..core.base_dialog import BaseDialog
from ..controls.label_control import LabelControl
from ..controls.textbox_control import TextBoxControl
from ..controls.button_control import ButtonControl
from ..controls.listbox_control import ListBoxControl
from ..controls.dropdown_control import DropdownControl
from ..filesystem import FileSystemError, FileType, FileInfo, fs
from ..filesystem.utils import FileOperations, FileSorter

class FileLoadDialogJSON(BaseDialog):
    """
    A dialog for loading a file, rewritten for the clean v3 architecture.
    It now properly uses control objects and the BaseDialog's event loop.
    """

    def __init__(self, 
                 initial_dir: Optional[str] = None, 
                 file_pattern: str = "*",
                 title: str = "Open File",
                 width: int = 340,
                 height: int = 280):
        
        x = (pyxel.width - width) // 2
        y = (pyxel.height - height) // 2
        super().__init__(x=x, y=y, width=width, height=height, title=title)

        # --- State ---
        self.current_dir = os.path.abspath(initial_dir or ".")
        self.file_patterns = self._parse_file_pattern(file_pattern)
        self.filtered_files: List[FileInfo] = []
        self.selected_file_path: Optional[str] = None

        # --- Create Controls ---
        self.path_textbox = TextBoxControl(x=10, y=20, width=self.width - 90, height=18, text=self.current_dir, readonly=True)
        self.up_button = ButtonControl(x=self.width - 70, y=20, width=60, height=18, text="Up")
        
        self.file_list_box = ListBoxControl(x=10, y=45, width=self.width - 20, height=self.height - 130, item_height=12)

        self.filename_textbox = TextBoxControl(x=80, y=self.height - 77, width=self.width - 100, height=20)

        filter_items = ['All Files (*.*)', 'CSV Files (*.csv)', 'Text Files (*.txt)']
        self.filter_dropdown = DropdownControl(x=80, y=self.height - 52, width=150, height=20, items=filter_items)

        self.open_button = ButtonControl(x=self.width - 160, y=self.height - 30, width=70, height=25, text="Open")
        self.cancel_button = ButtonControl(x=self.width - 80, y=self.height - 30, width=70, height=25, text="Cancel")

        # --- Add Controls to Dialog ---
        self.add_control(LabelControl(x=10, y=8, text="Current Folder:"))
        self.add_control(self.path_textbox)
        self.add_control(self.up_button)
        self.add_control(self.file_list_box)
        self.add_control(LabelControl(x=10, y=self.height - 75, text="File Name:"))
        self.add_control(self.filename_textbox)
        self.add_control(LabelControl(x=10, y=self.height - 50, text="File Type:"))
        self.add_control(self.filter_dropdown)
        self.add_control(self.open_button)
        self.add_control(self.cancel_button)

        # --- Event Handlers ---
        self.up_button.on('click', self._on_up_clicked)
        self.open_button.on('click', self._on_open_clicked)
        self.cancel_button.on('click', self._on_cancel_clicked)
        self.file_list_box.on('select', self._on_file_selected)
        self.file_list_box.on('activate', self._on_file_activated) # Handles double-click
        self.filename_textbox.on('enter', self._on_open_clicked)
        self.filter_dropdown.on('change', self._on_filter_changed)

        # --- Initial Setup ---
        self._update_filter_pattern()
        self.refresh_file_list()
        self.focused_control = self.file_list_box

    def _parse_file_pattern(self, pattern_str: str) -> List[str]:
        return [p.strip() for p in pattern_str.split(',')]

    def refresh_file_list(self):
        try:
            all_entries = FileOperations.list_directory(self.current_dir, sort_key=FileSorter.by_type)
            
            # Apply filters
            dirs = [e for e in all_entries if e.file_type == FileType.DIRECTORY]
            files = [e for e in all_entries if e.file_type == FileType.FILE]

            if "*.*" not in self.file_patterns:
                files = [f for f in files if any(f.name.lower().endswith(p.lower().lstrip('*')) for p in self.file_patterns)]

            self.filtered_files = sorted(dirs + files, key=lambda x: (x.file_type != FileType.DIRECTORY, x.name.lower()))

            # Update listbox items
            self.file_list_box.items = [f"[DIR] {f.name}" if f.file_type == FileType.DIRECTORY else f.name for f in self.filtered_files]
            self.path_textbox.text = self.current_dir
        except FileSystemError as e:
            self.file_list_box.items = ["Error loading files."]
            print(f"Error listing directory: {e}")

    def _change_directory(self, new_dir: str):
        if os.path.isdir(new_dir):
            self.current_dir = os.path.abspath(new_dir)
            self.refresh_file_list()
        else:
            print(f"Attempted to change to invalid directory: {new_dir}")

    # --- Event Handlers ---
    def _on_up_clicked(self, sender, data):
        parent_dir = os.path.dirname(self.current_dir)
        if parent_dir != self.current_dir:
            self._change_directory(parent_dir)

    def _on_file_selected(self, sender, data):
        index = data.get('index', -1)
        if 0 <= index < len(self.filtered_files):
            selected_item = self.filtered_files[index]
            if selected_item.file_type == FileType.FILE:
                self.filename_textbox.text = selected_item.name
            else:
                self.filename_textbox.text = ""

    def _on_file_activated(self, sender, data):
        index = data.get('index', -1)
        if 0 <= index < len(self.filtered_files):
            selected_item = self.filtered_files[index]
            if selected_item.file_type == FileType.DIRECTORY:
                self._change_directory(selected_item.path)
            else:
                self.selected_file_path = selected_item.path
                self.close(True)

    def _on_open_clicked(self, sender, data):
        # If a file is selected in the listbox, open it.
        selected_index = self.file_list_box.selected_index
        if 0 <= selected_index < len(self.filtered_files):
            self._on_file_activated(self.file_list_box, {'index': selected_index})
            return

        # Otherwise, try to open what's in the textbox.
        filename = self.filename_textbox.get_edited_filename()
        if filename:
            path_to_check = os.path.join(self.current_dir, filename)
            if os.path.isfile(path_to_check):
                self.selected_file_path = path_to_check
                self.close(True)

    def _on_cancel_clicked(self, sender, data):
        self.close(False)

    def _on_filter_changed(self, sender, data):
        self._update_filter_pattern()
        self.refresh_file_list()

    def _update_filter_pattern(self):
        selected_index = self.filter_dropdown.selected_index
        if selected_index == 0: # All Files
            self.file_patterns = ["*.*"]
        elif selected_index == 1: # CSV
            self.file_patterns = [".csv"]
        elif selected_index == 2: # Text
            self.file_patterns = [".txt"]
        else:
            self.file_patterns = ["*.*"]

    # --- Main show method ---
    def show_load_dialog(self) -> Tuple[bool, str]:
        success = self.show_modal_loop()
        if success and self.selected_file_path:
            return True, self.selected_file_path
        else:
            return False, ""
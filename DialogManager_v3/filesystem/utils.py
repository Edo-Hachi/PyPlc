"""
File system utilities for DialogManager_v3

Provides higher-level file operations and utilities on top of the file system abstraction.
"""
import os
from typing import List, Optional, Callable, Dict, Any, Union, Tuple
from pathlib import Path
import fnmatch
import re
from datetime import datetime
from . import FileInfo, FileType, fs, FileSystemError

class FileFilter:
    """File filtering utilities"""
    
    @staticmethod
    def by_name(patterns: Union[str, List[str]], case_sensitive: bool = False) -> Callable[[FileInfo], bool]:
        """Filter files by name pattern (supports wildcards)"""
        if isinstance(patterns, str):
            patterns = [patterns]
            
        # Convert to regex patterns
        regex_patterns = []
        for pattern in patterns:
            # Convert wildcard to regex
            regex = fnmatch.translate(pattern)
            if not case_sensitive:
                regex = f'(?i){regex}'
            regex_patterns.append(re.compile(regex))
        
        def _filter(file_info: FileInfo) -> bool:
            for pattern in regex_patterns:
                if pattern.fullmatch(file_info.name):
                    return True
            return False
            
        return _filter
    
    @staticmethod
    def by_extension(extensions: Union[str, List[str]], case_sensitive: bool = False) -> Callable[[FileInfo], bool]:
        """Filter files by extension"""
        if isinstance(extensions, str):
            extensions = [extensions]
        
        # Normalize extensions (remove leading . and make lowercase if not case sensitive)
        normalized_exts = []
        for ext in extensions:
            if ext.startswith('.'):
                ext = ext[1:]
            if not case_sensitive:
                ext = ext.lower()
            normalized_exts.append(ext)
        
        def _filter(file_info: FileInfo) -> bool:
            if file_info.file_type != FileType.FILE:
                return False
                
            # Get file extension
            _, ext = os.path.splitext(file_info.name)
            if ext.startswith('.'):
                ext = ext[1:]
            
            if not case_sensitive:
                ext = ext.lower()
                
            return ext in normalized_exts
            
        return _filter
    
    @staticmethod
    def by_type(file_types: Union[FileType, List[FileType]]) -> Callable[[FileInfo], bool]:
        """Filter files by type"""
        if isinstance(file_types, FileType):
            file_types = [file_types]
            
        def _filter(file_info: FileInfo) -> bool:
            return file_info.file_type in file_types
            
        return _filter
    
    @staticmethod
    def by_regex(pattern: str, flags: int = 0) -> Callable[[FileInfo], bool]:
        """Filter files by regex pattern"""
        regex = re.compile(pattern, flags)
        
        def _filter(file_info: FileInfo) -> bool:
            return bool(regex.search(file_info.name))
            
        return _filter

class FileSorter:
    """File sorting utilities"""
    
    @staticmethod
    def by_name(files: List[FileInfo], reverse: bool = False) -> List[FileInfo]:
        """Sort files by name"""
        return sorted(files, key=lambda f: f.name.lower(), reverse=reverse)
    
    @staticmethod
    def by_size(files: List[FileInfo], reverse: bool = False) -> List[FileInfo]:
        """Sort files by size"""
        return sorted(files, key=lambda f: f.size, reverse=reverse)
    
    @staticmethod
    def by_modified(files: List[FileInfo], reverse: bool = True) -> List[FileInfo]:
        """Sort files by modification time (newest first by default)"""
        return sorted(files, key=lambda f: f.modified_time, reverse=reverse)
    
    @staticmethod
    def by_type(files: List[FileInfo], reverse: bool = False) -> List[FileInfo]:
        """Sort files by type (directories first by default)"""
        return sorted(files, key=lambda f: (f.file_type != FileType.DIRECTORY, f.name.lower()), reverse=reverse)

class FileOperations:
    """High-level file operations"""
    
    @staticmethod
    def list_directory(
        path: str,
        filters: Optional[List[Callable[[FileInfo], bool]]] = None,
        sort_key: Optional[Callable[[List[FileInfo]], List[FileInfo]]] = None,
        include_hidden: bool = False
    ) -> List[FileInfo]:
        """
        List directory contents with filtering and sorting
        
        Args:
            path: Directory path
            filters: List of filter functions
            sort_key: Sorting function (e.g., FileSorter.by_name)
            include_hidden: Include hidden files/directories
            
        Returns:
            List of FileInfo objects
        """
        try:
            # Get directory contents
            entries = fs.list_directory(path)
            
            # Apply filters
            if not include_hidden:
                entries = [e for e in entries if not e.is_hidden]
                
            if filters:
                for filter_func in filters:
                    entries = [e for e in entries if filter_func(e)]
            
            # Apply sorting
            if sort_key:
                entries = sort_key(entries)
            else:
                # Default sort: directories first, then by name
                entries = FileSorter.by_type(entries)
                
            return entries
            
        except Exception as e:
            raise FileSystemError(f"Error listing directory {path}: {e}")
    
    @staticmethod
    def find_files(
        root_dir: str,
        pattern: str = "*",
        recursive: bool = True,
        case_sensitive: bool = False
    ) -> List[FileInfo]:
        """
        Find files matching a pattern
        
        Args:
            root_dir: Starting directory
            pattern: File pattern (e.g., '*.txt')
            recursive: Search subdirectories
            case_sensitive: Case-sensitive search
            
        Returns:
            List of matching FileInfo objects
        """
        try:
            if not fs.exists(root_dir) or not fs.is_dir(root_dir):
                return []
                
            results = []
            
            # Convert pattern to regex
            regex = re.compile(fnmatch.translate(pattern), 0 if case_sensitive else re.IGNORECASE)
            
            def _scan(directory: str):
                try:
                    for entry in fs.list_directory(directory):
                        if entry.file_type == FileType.DIRECTORY and recursive:
                            _scan(entry.path)
                        elif regex.fullmatch(entry.name):
                            results.append(entry)
                except Exception:
                    # Skip directories we can't access
                    pass
            
            _scan(root_dir)
            return results
            
        except Exception as e:
            raise FileSystemError(f"Error finding files: {e}")

# Common file type filters
is_image = FileFilter.by_extension(['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'])
is_document = FileFilter.by_extension(['txt', 'pdf', 'doc', 'docx', 'odt', 'rtf'])
is_archive = FileFilter.by_extension(['zip', 'rar', '7z', 'tar', 'gz', 'bz2'])
is_code = FileFilter.by_extension(['py', 'js', 'html', 'css', 'c', 'cpp', 'h', 'hpp', 'java', 'cs'])

# Common sort functions
sort_by_name = FileSorter.by_name
sort_by_size = FileSorter.by_size
sort_by_modified = FileSorter.by_modified
sort_by_type = FileSorter.by_type

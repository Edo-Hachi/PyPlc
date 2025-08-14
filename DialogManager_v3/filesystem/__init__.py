"""
File System Abstraction Layer for DialogManager_v3

This module provides a platform-independent interface for file system operations,
allowing for easy testing and future extensions.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple, BinaryIO, Union, Iterator
from pathlib import Path
import os
import stat
from enum import Enum, auto
from datetime import datetime

class FileType(Enum):
    """File type enumeration"""
    FILE = auto()
    DIRECTORY = auto()
    SYMLINK = auto()
    OTHER = auto()

class FileInfo:
    """File system entry information"""
    def __init__(self, 
                 name: str, 
                 path: str, 
                 size: int, 
                 file_type: FileType,
                 modified_time: float,
                 is_hidden: bool = False):
        self.name = name
        self.path = path
        self.size = size
        self.file_type = file_type
        self.modified_time = modified_time
        self.is_hidden = is_hidden

    @property
    def modified_datetime(self) -> datetime:
        """Convert modified timestamp to datetime"""
        return datetime.fromtimestamp(self.modified_time)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'path': self.path,
            'size': self.size,
            'type': self.file_type.name.lower(),
            'modified': self.modified_time,
            'is_hidden': self.is_hidden
        }

class FileSystemError(Exception):
    """Base exception for file system operations"""
    pass

class FileSystemProvider(ABC):
    """Abstract base class for file system providers"""
    
    @abstractmethod
    def list_directory(self, path: str) -> List[FileInfo]:
        """List contents of a directory"""
        pass
    
    @abstractmethod
    def get_file_info(self, path: str) -> Optional[FileInfo]:
        """Get information about a file or directory"""
        pass
    
    @abstractmethod
    def is_file(self, path: str) -> bool:
        """Check if path is a file"""
        pass
    
    @abstractmethod
    def is_dir(self, path: str) -> bool:
        """Check if path is a directory"""
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if path exists"""
        pass
    
    @abstractmethod
    def mkdir(self, path: str, parents: bool = False, exist_ok: bool = False) -> None:
        """Create a directory"""
        pass
    
    @abstractmethod
    def remove(self, path: str) -> None:
        """Remove a file"""
        pass
    
    @abstractmethod
    def rmdir(self, path: str) -> None:
        """Remove a directory"""
        pass
    
    @abstractmethod
    def open_file(self, path: str, mode: str = 'r', **kwargs) -> BinaryIO:
        """Open a file"""
        pass
    
    @abstractmethod
    def walk(self, top: str) -> Iterator[Tuple[str, List[str], List[str]]]:
        """Directory tree generator"""
        pass
    
    @abstractmethod
    def glob(self, pattern: str) -> List[str]:
        """Find files by pattern"""
        pass
    
    @abstractmethod
    def get_size(self, path: str) -> int:
        """Get file size in bytes"""
        pass
    
    @abstractmethod
    def get_mtime(self, path: str) -> float:
        """Get last modified time as timestamp"""
        pass

class LocalFileSystem(FileSystemProvider):
    """Local file system implementation"""
    
    def __init__(self):
        self._cwd = os.getcwd()
    
    def _get_file_type(self, path: str) -> FileType:
        """Determine file type from stat result"""
        try:
            mode = os.stat(path).st_mode
            if stat.S_ISREG(mode):
                return FileType.FILE
            elif stat.S_ISDIR(mode):
                return FileType.DIRECTORY
            elif stat.S_ISLNK(mode):
                return FileType.SYMLINK
            return FileType.OTHER
        except OSError:
            raise FileSystemError(f"Cannot determine type of {path}")
    
    def _create_file_info(self, path: str, name: str) -> FileInfo:
        """Create FileInfo from path and name"""
        try:
            full_path = os.path.join(path, name) if path else name
            stat_info = os.stat(full_path)
            return FileInfo(
                name=name,
                path=full_path,
                size=stat_info.st_size,
                file_type=self._get_file_type(full_path),
                modified_time=stat_info.st_mtime,
                is_hidden=name.startswith('.')
            )
        except OSError as e:
            raise FileSystemError(f"Error getting info for {name}: {e}")
    
    def list_directory(self, path: str) -> List[FileInfo]:
        try:
            if not os.path.isdir(path):
                raise NotADirectoryError(f"{path} is not a directory")
            
            entries = []
            for name in os.listdir(path):
                try:
                    entries.append(self._create_file_info(path, name))
                except FileSystemError:
                    continue
            return entries
        except OSError as e:
            raise FileSystemError(f"Error listing directory {path}: {e}")
    
    def get_file_info(self, path: str) -> Optional[FileInfo]:
        try:
            if not os.path.exists(path):
                return None
            dirname, basename = os.path.split(path)
            return self._create_file_info(dirname, basename)
        except OSError as e:
            raise FileSystemError(f"Error getting file info for {path}: {e}")
    
    def is_file(self, path: str) -> bool:
        return os.path.isfile(path)
    
    def is_dir(self, path: str) -> bool:
        return os.path.isdir(path)
    
    def exists(self, path: str) -> bool:
        return os.path.exists(path)
    
    def mkdir(self, path: str, parents: bool = False, exist_ok: bool = False) -> None:
        try:
            if parents:
                os.makedirs(path, exist_ok=exist_ok)
            else:
                os.mkdir(path)
        except OSError as e:
            raise FileSystemError(f"Error creating directory {path}: {e}")
    
    def remove(self, path: str) -> None:
        try:
            os.remove(path)
        except OSError as e:
            raise FileSystemError(f"Error removing file {path}: {e}")
    
    def rmdir(self, path: str) -> None:
        try:
            os.rmdir(path)
        except OSError as e:
            raise FileSystemError(f"Error removing directory {path}: {e}")
    
    def open_file(self, path: str, mode: str = 'r', **kwargs) -> BinaryIO:
        try:
            return open(path, mode, **kwargs)
        except OSError as e:
            raise FileSystemError(f"Error opening file {path}: {e}")
    
    def walk(self, top: str) -> Iterator[Tuple[str, List[str], List[str]]]:
        try:
            yield from os.walk(top)
        except OSError as e:
            raise FileSystemError(f"Error walking directory {top}: {e}")
    
    def glob(self, pattern: str) -> List[str]:
        from glob import glob
        try:
            return glob(pattern)
        except Exception as e:
            raise FileSystemError(f"Error in glob pattern {pattern}: {e}")
    
    def get_size(self, path: str) -> int:
        try:
            return os.path.getsize(path)
        except OSError as e:
            raise FileSystemError(f"Error getting size of {path}: {e}")
    
    def get_mtime(self, path: str) -> float:
        try:
            return os.path.getmtime(path)
        except OSError as e:
            raise FileSystemError(f"Error getting mtime of {path}: {e}")

# Default file system instance
fs = LocalFileSystem()

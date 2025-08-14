"""
Tests for the file system abstraction layer
"""
import os
import tempfile
import shutil
import pytest
from pathlib import Path
from datetime import datetime, timedelta

from DialogManager_v3.filesystem import (
    FileSystemError,
    FileType,
    FileInfo,
    fs,
    FileOperations,
    FileFilter,
    FileSorter
)

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    
    # Create test files and directories
    test_files = [
        "test.txt",
        "image.jpg",
        "document.pdf",
        "script.py",
        ".hidden_file",
        "subdir/subfile.txt"
    ]
    
    for file_path in test_files:
        full_path = os.path.join(temp_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write("Test content")
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_list_directory(temp_dir):
    """Test listing directory contents"""
    entries = fs.list_directory(temp_dir)
    
    # Should list top-level files and directories
    names = {e.name for e in entries}
    assert "test.txt" in names
    assert "subdir" in names
    assert ".hidden_file" not in names  # Hidden files should be filtered by default
    
    # Test file info
    for entry in entries:
        if entry.name == "test.txt":
            assert entry.file_type == FileType.FILE
            assert entry.size > 0
            assert isinstance(entry.modified_time, float)
            assert not entry.is_hidden
        elif entry.name == "subdir":
            assert entry.file_type == FileType.DIRECTORY

def test_file_operations(temp_dir):
    """Test basic file operations"""
    # Test file info
    test_file = os.path.join(temp_dir, "test.txt")
    file_info = fs.get_file_info(test_file)
    assert file_info is not None
    assert file_info.name == "test.txt"
    assert file_info.file_type == FileType.FILE
    
    # Test non-existent file
    assert fs.get_file_info("non_existent_file") is None
    
    # Test create and delete file
    new_file = os.path.join(temp_dir, "new_file.txt")
    with fs.open_file(new_file, 'w') as f:
        f.write("Test content")
    
    assert fs.exists(new_file)
    assert fs.is_file(new_file)
    
    fs.remove(new_file)
    assert not fs.exists(new_file)
    
    # Test directory operations
    new_dir = os.path.join(temp_dir, "new_dir")
    fs.mkdir(new_dir)
    assert fs.is_dir(new_dir)
    
    # Test recursive directory creation
    nested_dir = os.path.join(temp_dir, "a/b/c")
    fs.mkdir(nested_dir, parents=True)
    assert fs.is_dir(nested_dir)

def test_file_filtering(temp_dir):
    """Test file filtering and sorting"""
    # Get all entries including hidden
    all_entries = FileOperations.list_directory(temp_dir, include_hidden=True)
    all_names = {e.name for e in all_entries}
    assert ".hidden_file" in all_names
    
    # Test extension filter
    text_files = FileOperations.list_directory(
        temp_dir,
        filters=[FileFilter.by_extension(['txt', 'py'])]
    )
    text_names = {e.name for e in text_files}
    assert "test.txt" in text_names
    assert "script.py" in text_names
    assert "image.jpg" not in text_names
    
    # Test name pattern filter
    image_files = FileOperations.list_directory(
        temp_dir,
        filters=[FileFilter.by_name("*.jpg")]
    )
    assert len(image_files) == 1
    assert image_files[0].name == "image.jpg"
    
    # Test type filter
    dirs = FileOperations.list_directory(
        temp_dir,
        filters=[FileFilter.by_type(FileType.DIRECTORY)]
    )
    assert len(dirs) >= 1  # At least 'subdir'
    assert all(d.file_type == FileType.DIRECTORY for d in dirs)

def test_file_sorting(temp_dir):
    """Test file sorting"""
    # Create some test files with different sizes
    files = [
        ("a.txt", 100, 3600),  # name, size, seconds_ago
        ("b.txt", 300, 7200),
        ("c.txt", 200, 0),
    ]
    
    now = datetime.now()
    for name, size, seconds_ago in files:
        path = os.path.join(temp_dir, name)
        with open(path, 'wb') as f:
            f.write(b'x' * size)
        # Set modification time
        mtime = (now - timedelta(seconds=seconds_ago)).timestamp()
        os.utime(path, (mtime, mtime))
    
    # Get file infos
    entries = fs.list_directory(temp_dir)
    
    # Sort by name
    sorted_names = [e.name for e in FileSorter.by_name(entries)]
    assert sorted_names == ["a.txt", "b.txt", "c.txt"]
    
    # Sort by size
    sorted_sizes = [e.size for e in FileSorter.by_size(entries)]
    assert sorted_sizes == [100, 200, 300]
    
    # Sort by modified time (newest first by default)
    sorted_modified = [e.name for e in FileSorter.by_modified(entries)]
    assert sorted_modified == ["c.txt", "a.txt", "b.txt"]

def test_find_files(temp_dir):
    """Test recursive file finding"""
    # Create some test files
    test_files = [
        "docs/readme.txt",
        "docs/api.txt",
        "src/main.py",
        "src/utils.py",
        "src/tests/test_main.py",
    ]
    
    for file_path in test_files:
        full_path = os.path.join(temp_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write("Test content")
    
    # Find all .py files
    py_files = FileOperations.find_files(temp_dir, "*.py")
    py_paths = {f.path for f in py_files}
    
    assert os.path.join(temp_dir, "src/main.py") in py_paths
    assert os.path.join(temp_dir, "src/utils.py") in py_paths
    assert os.path.join(temp_dir, "src/tests/test_main.py") in py_paths
    assert len(py_files) == 3
    
    # Non-recursive search
    top_level_py = FileOperations.find_files(os.path.join(temp_dir, "src"), "*.py", recursive=False)
    assert len(top_level_py) == 2  # main.py and utils.py

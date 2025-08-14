# File System Abstraction Layer

A platform-independent interface for file system operations, designed to support the DialogManager_v3's file dialogs.

## Features

- **Unified Interface**: Single API for all file system operations
- **Cross-Platform**: Works consistently across different operating systems
- **Type Hints**: Full Python type hint support for better IDE integration
- **Error Handling**: Consistent error handling with `FileSystemError`
- **File Filtering**: Powerful filtering by name, extension, type, etc.
- **Sorting**: Built-in sorting by name, size, modification time, etc.
- **Asynchronous Support**: Designed with async operations in mind

## Core Components

### `FileSystemProvider` (ABC)

Abstract base class defining the file system operations:

```python
class FileSystemProvider(ABC):
    @abstractmethod
    def list_directory(self, path: str) -> List[FileInfo]: ...
    
    @abstractmethod
    def get_file_info(self, path: str) -> Optional[FileInfo]: ...
    
    @abstractmethod
    def is_file(self, path: str) -> bool: ...
    
    # ... and other methods
```

### `FileInfo`

Data class containing file/directory information:

```python
file_info = fs.get_file_info("path/to/file.txt")
print(f"Name: {file_info.name}")
print(f"Path: {file_info.path}")
print(f"Size: {file_info.size} bytes")
print(f"Type: {file_info.file_type}")
print(f"Modified: {file_info.modified_datetime}")
print(f"Hidden: {file_info.is_hidden}")
```

### `LocalFileSystem`

Default implementation using the local file system:

```python
from DialogManager_v3.filesystem import fs  # default LocalFileSystem instance

# List directory contents
entries = fs.list_directory("/path/to/directory")

# Get file info
file_info = fs.get_file_info("/path/to/file.txt")

# Check if path exists
if fs.exists("/some/path"):
    print("Path exists!")
```

## File Operations

### Filtering Files

```python
from DialogManager_v3.filesystem import FileOperations, FileFilter

# Get all Python files
python_files = FileOperations.list_directory(
    "/path/to/directory",
    filters=[FileFilter.by_extension('py')]
)

# Get files matching pattern
matching_files = FileOperations.list_directory(
    "/path/to/directory",
    filters=[FileFilter.by_name("*.txt")]
)

# Get directories only
dirs = FileOperations.list_directory(
    "/path/to/directory",
    filters=[FileFilter.by_type(FileType.DIRECTORY)]
)

# Multiple filters (AND condition)
filtered = FileOperations.list_directory(
    "/path/to/directory",
    filters=[
        FileFilter.by_extension(['jpg', 'png', 'gif']),
        lambda f: f.size > 1024  # Custom filter function
    ]
)
```

### Sorting Files

```python
from DialogManager_v3.filesystem import FileOperations, FileSorter

# Sort by name (case-insensitive)
sorted_by_name = FileOperations.list_directory(
    "/path/to/directory",
    sort_key=FileSorter.by_name
)

# Sort by size (largest first)
sorted_by_size = FileOperations.list_directory(
    "/path/to/directory",
    sort_key=lambda files: FileSorter.by_size(files, reverse=True)
)

# Sort by modification time (newest first is default)
sorted_by_modified = FileOperations.list_directory(
    "/path/to/directory",
    sort_key=FileSorter.by_modified
)
```

### Finding Files

```python
from DialogManager_v3.filesystem import FileOperations

# Find all Python files recursively
python_files = FileOperations.find_files(
    "/path/to/search",
    "*.py"
)

# Find files in a single directory (non-recursive)
top_level = FileOperations.find_files(
    "/path/to/search",
    "*.txt",
    recursive=False
)
```

## Common File Types

Predefined filters for common file types:

```python
from DialogManager_v3.filesystem import is_image, is_document, is_archive, is_code

# Usage with filters
images = FileOperations.list_directory(
    "/path/to/directory",
    filters=[is_image]
)
```

## Error Handling

All file operations raise `FileSystemError` on failure:

```python
from DialogManager_v3.filesystem import FileSystemError, fs

try:
    with fs.open_file("/nonexistent/file.txt", 'r') as f:
        content = f.read()
except FileSystemError as e:
    print(f"File operation failed: {e}")
```

## Testing

Run the test suite with pytest:

```bash
pytest DialogManager_v3/tests/test_filesystem.py -v
```

## Extending

To implement a custom file system provider:

1. Subclass `FileSystemProvider`
2. Implement all abstract methods
3. Register your provider or use it directly

```python
class CustomFileSystem(FileSystemProvider):
    def list_directory(self, path: str) -> List[FileInfo]:
        # Your implementation
        pass
    
    # Implement other abstract methods...

# Usage
custom_fs = CustomFileSystem()
entries = custom_fs.list_directory("/some/path")
```

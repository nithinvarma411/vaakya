"""
File Operations Module
Handles file and folder operations across different platforms.
"""

import platform
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class FileOperations:
    """Platform-aware file and folder operations."""

    def __init__(self) -> None:
        self.system = platform.system().lower()

    def create_file(self, file_path: Union[str, Path], content: str = "") -> bool:
        """Create a file with optional content."""
        try:
            path = Path(file_path)
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"✅ Created file: {path}")
            return True

        except Exception as e:
            print(f"❌ Error creating file {file_path}: {e}")
            return False

    def create_folder(self, folder_path: Union[str, Path]) -> bool:
        """Create a folder (and parent directories if needed)."""
        try:
            path = Path(folder_path)
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created folder: {path}")
            return True

        except Exception as e:
            print(f"❌ Error creating folder {folder_path}: {e}")
            return False

    def delete_file(self, file_path: Union[str, Path]) -> bool:
        """Delete a file."""
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
                print(f"✅ Deleted file: {path}")
                return True
            else:
                print(f"❌ File not found: {path}")
                return False

        except Exception as e:
            print(f"❌ Error deleting file {file_path}: {e}")
            return False

    def delete_folder(self, folder_path: Union[str, Path]) -> bool:
        """Delete a folder and its contents."""
        try:
            path = Path(folder_path)
            if path.exists() and path.is_dir():
                shutil.rmtree(path)
                print(f"✅ Deleted folder: {path}")
                return True
            else:
                print(f"❌ Folder not found: {path}")
                return False

        except Exception as e:
            print(f"❌ Error deleting folder {folder_path}: {e}")
            return False

    def copy_file(
        self, source: Union[str, Path], destination: Union[str, Path]
    ) -> bool:
        """Copy a file from source to destination."""
        try:
            src_path = Path(source)
            dest_path = Path(destination)

            if not src_path.exists():
                print(f"❌ Source file not found: {src_path}")
                return False

            # Create destination directory if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(src_path, dest_path)
            print(f"✅ Copied {src_path} to {dest_path}")
            return True

        except Exception as e:
            print(f"❌ Error copying file: {e}")
            return False

    def copy_folder(
        self, source: Union[str, Path], destination: Union[str, Path]
    ) -> bool:
        """Copy a folder and its contents."""
        try:
            src_path = Path(source)
            dest_path = Path(destination)

            if not src_path.exists():
                print(f"❌ Source folder not found: {src_path}")
                return False

            shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
            print(f"✅ Copied folder {src_path} to {dest_path}")
            return True

        except Exception as e:
            print(f"❌ Error copying folder: {e}")
            return False

    def move_file(
        self, source: Union[str, Path], destination: Union[str, Path]
    ) -> bool:
        """Move a file from source to destination."""
        try:
            src_path = Path(source)
            dest_path = Path(destination)

            if not src_path.exists():
                print(f"❌ Source file not found: {src_path}")
                return False

            # Create destination directory if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.move(str(src_path), str(dest_path))
            print(f"✅ Moved {src_path} to {dest_path}")
            return True

        except Exception as e:
            print(f"❌ Error moving file: {e}")
            return False

    def move_folder(
        self, source: Union[str, Path], destination: Union[str, Path]
    ) -> bool:
        """Move a folder from source to destination."""
        try:
            src_path = Path(source)
            dest_path = Path(destination)

            if not src_path.exists():
                print(f"❌ Source folder not found: {src_path}")
                return False

            shutil.move(str(src_path), str(dest_path))
            print(f"✅ Moved folder {src_path} to {dest_path}")
            return True

        except Exception as e:
            print(f"❌ Error moving folder: {e}")
            return False

    def list_directory(self, directory_path: Union[str, Path]) -> Optional[List[str]]:
        """List contents of a directory."""
        try:
            path = Path(directory_path)
            if not path.exists():
                print(f"❌ Directory not found: {path}")
                return None

            if not path.is_dir():
                print(f"❌ Not a directory: {path}")
                return None

            contents = [item.name for item in path.iterdir()]
            print(f"📁 Directory contents of {path}:")
            for item in sorted(contents):
                item_path = path / item
                if item_path.is_dir():
                    print(f"  📁 {item}/")
                else:
                    print(f"  📄 {item}")

            return contents

        except Exception as e:
            print(f"❌ Error listing directory {directory_path}: {e}")
            return None

    def read_file(self, file_path: Union[str, Path]) -> Optional[str]:
        """Read content from a file."""
        try:
            path = Path(file_path)
            if not path.exists():
                print(f"❌ File not found: {path}")
                return None

            with open(path, encoding="utf-8") as f:
                content = f.read()

            print(f"✅ Read file: {path} ({len(content)} characters)")
            return content

        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
            return None

    def write_file(
        self, file_path: Union[str, Path], content: str, append: bool = False
    ) -> bool:
        """Write content to a file."""
        try:
            path = Path(file_path)
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)

            mode = "a" if append else "w"
            with open(path, mode, encoding="utf-8") as f:
                f.write(content)

            action = "Appended to" if append else "Wrote to"
            print(f"✅ {action} file: {path}")
            return True

        except Exception as e:
            print(f"❌ Error writing to file {file_path}: {e}")
            return False

    def file_exists(self, file_path: Union[str, Path]) -> bool:
        """Check if a file exists."""
        return Path(file_path).is_file()

    def folder_exists(self, folder_path: Union[str, Path]) -> bool:
        """Check if a folder exists."""
        return Path(folder_path).is_dir()

    def get_file_info(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Get information about a file."""
        try:
            path = Path(file_path)
            if not path.exists():
                print(f"❌ File not found: {path}")
                return None

            stat = path.stat()
            info = {
                "name": path.name,
                "path": str(path.absolute()),
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "is_file": path.is_file(),
                "is_directory": path.is_dir(),
            }

            print(f"📋 File info for {path.name}:")
            print(f"  Size: {info['size']} bytes")
            print(f"  Type: {'File' if info['is_file'] else 'Directory'}")

            return info

        except Exception as e:
            print(f"❌ Error getting file info for {file_path}: {e}")
            return None

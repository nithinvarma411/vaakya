"""
Operations package for modular agent functionality.
Each operation module handles specific platform-aware tasks.
"""

from .app_operations import AppOperations
from .file_operations import FileOperations
from .web_operations import WebOperations

__all__ = ["AppOperations", "FileOperations", "WebOperations"]

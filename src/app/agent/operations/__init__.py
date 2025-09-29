"""
Operations package for modular agent functionality.
Each operation module handles specific platform-aware tasks.
"""

from .app_operations import AppOperations
from .utilities import UtilityFunctions
from .web_operations import WebOperations

__all__ = ["AppOperations", "UtilityFunctions", "WebOperations"]

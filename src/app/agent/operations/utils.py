"""
Shared utilities for the operations system.

This module provides common utilities that can be used across different operation modules.
"""

import platform
from typing import Dict, Any

class PlatformUtils:
    """Utility class for cross-platform operations shared across all operations."""
    
    @staticmethod
    def get_system_type() -> str:
        """Get the current operating system type."""
        system = platform.system().lower()
        if system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"
        else:
            return "linux"
    
    @staticmethod
    def get_platform_info() -> Dict[str, Any]:
        """Get comprehensive platform information."""
        return {
            "system": platform.system(),
            "release": platform.release(), 
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "system_type": PlatformUtils.get_system_type()
        }

# Global platform info that can be accessed by any operation
PLATFORM_INFO = PlatformUtils.get_platform_info()
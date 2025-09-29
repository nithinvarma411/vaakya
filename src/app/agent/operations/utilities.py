"""
Utility Functions for Vaakya Voice Assistant

This module provides essential utility functions for the AI agent to perform
common operations and safely interact with the system.
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from src.app.agent.operations.app_operations import AppOperations


class UtilityFunctions:
    """Collection of essential utility functions for the AI agent."""

    def __init__(self) -> None:
        """Initialize utility functions."""
        self.system = platform.system().lower()
        self.app_ops = AppOperations()

    def get_system_information(self) -> Dict[str, str]:
        """Get OS, architecture, and system information.

        Returns:
            Dict[str, str]: System information
        """
        return {
            "os": platform.system(),
            "architecture": platform.machine(),
            "platform": platform.platform(),
        }

    def get_current_directory(self) -> str:
        """Get the current working directory.

        Returns:
            str: Current working directory path
        """
        return os.getcwd()

    def get_user_home_directory(self) -> str:
        """Get the user's home directory.

        Returns:
            str: User's home directory path
        """
        return str(Path.home())

    def resolve_path(self, path: str) -> str:
        """Resolve relative paths to absolute paths.

        Args:
            path (str): Path to resolve

        Returns:
            str: Absolute path
        """
        return str(Path(path).resolve())

    def validate_path(self, path: str) -> bool:
        """Check if a path is safe and accessible.

        Args:
            path (str): Path to validate

        Returns:
            bool: True if path is valid and accessible
        """
        try:
            path_obj = Path(path)
            return path_obj.exists() and os.access(path, os.R_OK)
        except Exception:
            return False

    def execute_shell_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute a shell command safely.

        Args:
            command (str): Command to execute
            timeout (int): Timeout in seconds

        Returns:
            Dict[str, Any]: Command execution result
        """
        try:
            # Validate command safety
            if not self.validate_shell_command(command):
                return {"error": "Command not allowed", "command": command}

            # Execute command
            result = subprocess.run(
                command,
                check=False,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            return {
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "error": f"Command timed out after {timeout} seconds",
                "command": command,
            }
        except Exception as e:
            return {"error": f"Error executing command: {e!s}", "command": command}

    def validate_shell_command(self, command: str) -> bool:
        """Check if a shell command is safe to execute.

        Args:
            command (str): Shell command to validate

        Returns:
            bool: True if command is safe to execute
        """
        # Define allowed commands based on the system
        if self.system == "windows":
            safe_commands = [
                "dir",
                "echo",
                "cd",
                "copy",
                "move",
                "del",
                "type",
                "findstr",
                "where",
                "tasklist",
                "ping",
                "ipconfig",
                "path",
                "cls",
                "chdir",
                "mkdir",
                "rmdir",
            ]
        else:
            safe_commands = [
                "ls",
                "pwd",
                "cd",
                "cp",
                "mv",
                "rm",
                "cat",
                "echo",
                "grep",
                "find",
                "which",
                "ps",
                "ping",
                "ifconfig",
                "whoami",
                "clear",
                "mkdir",
                "rmdir",
            ]

        # Parse the command to check if it's allowed
        cmd_parts = command.split()
        if not cmd_parts:
            return False

        # Check if the first command is in the whitelist
        first_cmd = cmd_parts[0].replace('"', "").replace("'", "")
        return first_cmd in safe_commands

    def sanitize_input(self, input_str: str) -> str:
        """Sanitize user input to prevent injection.

        Args:
            input_str (str): Input string to sanitize

        Returns:
            str: Sanitized input string
        """
        # Remove potentially dangerous characters
        dangerous_chars = [
            ";",
            "&",
            "|",
            "`",
            ",",
            "<",
            ">",
            "(",
            ")",
            "{",
            "}",
            "[",
            "]",
            "$",
        ]
        sanitized = input_str
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")
        return sanitized.strip()

    def locate_app_path(self, app_name: str) -> Optional[str]:
        """
        Locate the path of an application using fuzzy search through the app operations system.

        Args:
            app_name (str): Name of the application to locate

        Returns:
            Optional[str]: Path to the application if found, None otherwise
        """
        try:
            # Use the app operations to find the app
            matched_app = self.app_ops.find_app_fuzzy(app_name)

            if matched_app and self.app_ops._app_cache:
                app_path = self.app_ops._app_cache.get(matched_app)
                if app_path:
                    return app_path
            return None
        except Exception as e:
            print(f"Error locating app {app_name}: {e}")
            return None

    MAX_DEPTH = 3  # Maximum directory depth to search

    def _get_default_search_paths(self) -> list[str]:
        """Get default search paths based on the operating system."""
        if self.system == "windows":
            return [
                os.path.expanduser("~"),
                "C:\\Program Files",
                "C:\\Program Files (x86)",
                "C:\\Users",
                os.path.expanduser("~\\Desktop"),
                os.path.expanduser("~\\Documents"),
            ]
        elif self.system == "darwin":  # macOS
            return [
                os.path.expanduser("~"),
                "/Applications",
                "/System/Applications",
                os.path.expanduser("~/Applications"),
                os.path.expanduser("~"),
                os.path.expanduser("~/Desktop"),
                os.path.expanduser("~/Documents"),
            ]
        else:  # Linux and other Unix-like systems
            return [
                os.path.expanduser("~"),
                "/usr/bin",
                "/usr/local/bin",
                "/opt",
                os.path.expanduser("~/Desktop"),
                os.path.expanduser("~/Documents"),
                "/home",
            ]

    def locate_file_or_folder(
        self, name: str, search_paths: Optional[list[str]] = None
    ) -> Optional[str]:
        """
        Locate a file or folder by searching through common system paths.

        Args:
            name (str): Name of the file or folder to locate
            search_paths (Optional[list]): List of paths to search in (default: common system paths)

        Returns:
            Optional[str]: Path to the file or folder if found, None otherwise
        """
        if search_paths is None:
            search_paths = self._get_default_search_paths()

        try:
            # Normalize the name for comparison
            name_lower = name.lower()

            for base_path in search_paths:
                if not os.path.exists(base_path):
                    continue

                # Walk through the directory tree
                for root, dirs, files in os.walk(base_path):
                    # Check if the name matches any of the directories
                    for dir_name in dirs:
                        if name_lower in dir_name.lower():
                            full_path = os.path.join(root, dir_name)
                            return str(full_path)

                    # Check if the name matches any of the files
                    for file_name in files:
                        if name_lower in file_name.lower():
                            full_path = os.path.join(root, file_name)
                            return str(full_path)

                    # Limit depth to prevent excessive searching
                    if root[len(base_path) :].count(os.sep) >= self.MAX_DEPTH:
                        dirs[:] = []  # Don't recurse deeper into this directory

        except Exception as e:
            print(f"Error searching for {name}: {e}")

        return None

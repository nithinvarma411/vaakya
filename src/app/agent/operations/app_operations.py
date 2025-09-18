"""
App Operations Module
Handles application launching with fuzzy search across different platforms.
"""

import os
import platform
import subprocess
from typing import ClassVar, List, Optional

from fuzzywuzzy import fuzz

from src.app.config.settings import settings


class AppOperations:
    """Platform-aware application operations with fuzzy search."""

    # Use settings for constants - keeping ClassVar for compatibility
    MAX_APPS_LIMIT: ClassVar[int] = settings.app_operations.MAX_APPS_LIMIT
    FUZZY_THRESHOLD: ClassVar[int] = settings.app_operations.FUZZY_THRESHOLD
    COMMAND_TIMEOUT: ClassVar[int] = settings.app_operations.COMMAND_TIMEOUT

    SKIP_EXECUTABLES: ClassVar[List[str]] = [
        "systemd",
        "dbus",
        "update",
        "install",
        "config",
    ]

    def __init__(self) -> None:
        self.system = platform.system().lower()
        self._app_cache: Optional[List[str]] = None

    def _discover_macos_apps(self) -> List[str]:
        """Discover macOS applications."""
        apps = []
        app_dirs = ["/Applications", os.path.expanduser("~/Applications")]

        for apps_dir in app_dirs:
            if not os.path.exists(apps_dir):
                continue
            try:
                for item in os.listdir(apps_dir):
                    if item.endswith(".app"):
                        apps.append(item.replace(".app", ""))
            except OSError:
                continue
        return apps

    def _discover_linux_apps(self) -> List[str]:
        """Discover Linux applications."""
        apps = []

        # Check desktop files
        desktop_dirs = [
            "/usr/share/applications",
            "/usr/local/share/applications",
            os.path.expanduser("~/.local/share/applications"),
        ]

        for app_dir in desktop_dirs:
            if not os.path.exists(app_dir):
                continue
            try:
                for item in os.listdir(app_dir):
                    if item.endswith(".desktop"):
                        apps.append(item.replace(".desktop", "").replace("-", " "))
            except OSError:
                continue

        # Check bin paths
        bin_paths = ["/usr/bin", "/usr/local/bin", "/bin"]
        for bin_path in bin_paths:
            if not os.path.exists(bin_path):
                continue
            try:
                for item in os.listdir(bin_path):
                    if os.access(os.path.join(bin_path, item), os.X_OK) and not any(
                        skip in item.lower() for skip in self.SKIP_EXECUTABLES
                    ):
                        apps.append(item)
                        if len(apps) > self.MAX_APPS_LIMIT:
                            break
            except OSError:
                continue
        return apps

    def _discover_windows_apps(self) -> List[str]:
        """Discover Windows applications."""
        apps = []
        common_paths = [
            "C:\\Program Files",
            "C:\\Program Files (x86)",
        ]

        for app_dir in common_paths:
            if not os.path.exists(app_dir):
                continue
            try:
                for item in os.listdir(app_dir):
                    if os.path.isdir(os.path.join(app_dir, item)):
                        apps.append(item)
            except OSError:
                continue
        return apps

    def discover_apps(self) -> List[str]:
        """Discover available applications on the system."""
        try:
            if self.system == "darwin":
                apps = self._discover_macos_apps()
            elif self.system == "linux":
                apps = self._discover_linux_apps()
            elif self.system == "windows":
                apps = self._discover_windows_apps()
            else:
                apps = []
        except Exception as e:
            print(f"Warning: Error discovering apps: {e}")
            apps = []

        # Remove duplicates and cache
        self._app_cache = list(set(apps))
        return self._app_cache

    def find_app_fuzzy(
        self, query: str, threshold: Optional[int] = None
    ) -> Optional[str]:
        """Find the best matching app using fuzzy search."""
        if threshold is None:
            threshold = settings.app_operations.FUZZY_THRESHOLD

        if not self._app_cache:
            self.discover_apps()

        if not self._app_cache:
            return None

        best_match = None
        best_score = 0

        query_lower = query.lower()

        for app in self._app_cache:
            app_lower = app.lower()

            # Direct substring match gets highest priority
            if query_lower in app_lower:
                score = int(95 + (len(query) / len(app)) * 5)
            else:
                # Fuzzy matching
                score = int(fuzz.ratio(query_lower, app_lower))
                # Bonus for partial matches
                if any(word in app_lower for word in query_lower.split()):
                    score += 10

            if score > best_score and score >= threshold:
                best_score = int(score)
                best_match = app

        return best_match

    def _launch_macos_app(self, app_name: str) -> bool:
        """Launch app on macOS."""
        try:
            result = subprocess.run(
                ["open", "-a", app_name],
                check=False,
                capture_output=True,
                text=True,
                timeout=self.COMMAND_TIMEOUT,
            )
            if result.returncode == 0:
                print(f"✅ Launched {app_name}")
                return True
            print(f"❌ Failed to launch {app_name}: {result.stderr}")
            return False
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout launching {app_name}")
            return False

    def _launch_linux_app(self, app_name: str) -> bool:
        """Launch app on Linux."""
        commands = [
            ["gtk-launch", app_name],
            [app_name],
            ["nohup", app_name],
        ]

        for cmd in commands:
            try:
                result = subprocess.run(
                    cmd,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=self.COMMAND_TIMEOUT,
                )
                if result.returncode == 0:
                    print(f"✅ Launched {app_name}")
                    return True
            except (subprocess.TimeoutExpired, OSError):
                continue

        print(f"❌ Failed to launch {app_name}")
        return False

    def _launch_windows_app(self, app_name: str) -> bool:
        """Launch app on Windows."""
        try:
            result = subprocess.run(
                ["start", "", app_name],
                check=False,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.COMMAND_TIMEOUT,
            )
            if result.returncode == 0:
                print(f"✅ Launched {app_name}")
                return True
            print(f"❌ Failed to launch {app_name}: {result.stderr}")
            return False
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout launching {app_name}")
            return False

    def launch_app(self, app_name: str) -> bool:
        """Launch an application by name."""
        try:
            # First try fuzzy search
            matched_app = self.find_app_fuzzy(app_name)
            app_to_launch = matched_app if matched_app else app_name

            if matched_app:
                print(f"🎯 Found app: {app_to_launch}")
            else:
                print(f"🔍 Trying direct launch: {app_to_launch}")

            if self.system == "darwin":
                return self._launch_macos_app(app_to_launch)
            elif self.system == "linux":
                return self._launch_linux_app(app_to_launch)
            elif self.system == "windows":
                return self._launch_windows_app(app_to_launch)
            else:
                print(f"❌ Unsupported system: {self.system}")
                return False

        except Exception as e:
            print(f"❌ Error launching {app_name}: {e}")
            return False

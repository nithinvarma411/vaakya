"""
App Operations Module
Handles application launching with fuzzy search across different platforms.
"""

import json
import os
import platform
import subprocess
from pathlib import Path
from typing import ClassVar, Dict, List, Optional

from fuzzywuzzy import fuzz

from src.app.config.settings import settings


class AppOperations:
    """Platform-aware application operations with fuzzy search."""

    # Use settings for constants - keeping ClassVar for compatibility
    MAX_APPS_LIMIT: ClassVar[int] = settings.app_operations.MAX_APPS_LIMIT
    FUZZY_THRESHOLD: ClassVar[int] = settings.app_operations.FUZZY_THRESHOLD
    COMMAND_TIMEOUT: ClassVar[int] = settings.app_operations.COMMAND_TIMEOUT

    def __init__(self) -> None:
        self.system = platform.system().lower()
        self._app_cache: Optional[Dict[str, str]] = None

    def _discover_macos_apps(self) -> Dict[str, str]:
        """Discover macOS applications."""
        apps = {}
        app_dirs = ["/Applications", os.path.expanduser("~/Applications")]

        for apps_dir in app_dirs:
            if not os.path.exists(apps_dir):
                continue
            try:
                for item in os.listdir(apps_dir):
                    if item.endswith(".app"):
                        app_name = item.replace(".app", "")
                        apps[app_name.lower()] = os.path.join(apps_dir, item)
            except OSError:
                continue
        return apps

    def _discover_linux_apps(self) -> Dict[str, str]:
        """Discover Linux applications."""
        apps = {}

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
                        app_name = item.replace(".desktop", "").replace("-", " ")
                        apps[app_name.lower()] = os.path.join(app_dir, item)
            except OSError:
                continue

        # Check bin paths
        bin_paths = ["/usr/bin", "/usr/local/bin", "/bin"]
        for bin_path in bin_paths:
            if not os.path.exists(bin_path):
                continue
            try:
                for item in os.listdir(bin_path):
                    if (
                        os.access(os.path.join(bin_path, item), os.X_OK)
                        and not any(
                            skip in item.lower()
                            for skip in settings.app_operations.SKIP_EXECUTABLES
                        )
                        and len(apps) < self.MAX_APPS_LIMIT
                    ):
                        apps[item.lower()] = os.path.join(bin_path, item)
            except OSError:
                continue
        return apps

    def _discover_windows_apps(self) -> Dict[str, str]:  # noqa: PLR0912, PLR0915
        """Discover Windows applications using proper PowerShell methods."""
        apps = {}

        # Method 1: Get-StartApps - Gets all installed apps with AppIDs
        try:
            print("Discovering apps using Get-StartApps...")
            result = subprocess.run(
                ["powershell", "-Command", "Get-StartApps | ConvertTo-Json"],
                check=False,
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0 and result.stdout.strip():
                start_apps = json.loads(result.stdout)
                if isinstance(start_apps, list):
                    for app in start_apps:
                        if app.get("Name") and app.get("AppID"):
                            app_name = app["Name"].strip()
                            app_id = app["AppID"].strip()
                            if app_name and len(app_name) > 1:
                                apps[app_name.lower()] = f"appid:{app_id}"
                                print(f"Found app: {app_name} -> {app_id}")
                elif (
                    isinstance(start_apps, dict)
                    and start_apps.get("Name")
                    and start_apps.get("AppID")
                ):
                    # Single app case
                    app_name = start_apps["Name"].strip()
                    app_id = start_apps["AppID"].strip()
                    if app_name and len(app_name) > 1:
                        apps[app_name.lower()] = f"appid:{app_id}"
                        print(f"Found app: {app_name} -> {app_id}")
        except Exception as e:
            print(f"Error discovering apps with Get-StartApps: {e}")

        # Method 2: Get-AppxPackage - Gets Windows Store/UWP apps
        try:
            print("Discovering UWP apps using Get-AppxPackage...")
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Get-AppxPackage | Where-Object {$_.Name -notlike '*Microsoft.VCLibs*' -and $_.Name -notlike '*Microsoft.NET*'} | Select-Object Name, PackageFamilyName, InstallLocation | ConvertTo-Json",
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0 and result.stdout.strip():
                packages = json.loads(result.stdout)
                if isinstance(packages, list):
                    for package in packages:
                        if package.get("Name") and package.get("PackageFamilyName"):
                            # Extract readable name from package name
                            full_name = package["Name"]
                            if "." in full_name:
                                app_name = full_name.split(".")[-1]  # Get last part
                            else:
                                app_name = full_name

                            if app_name and len(app_name) > 1:
                                package_family = package["PackageFamilyName"]
                                apps[app_name.lower()] = f"package:{package_family}"
                                print(f"Found UWP app: {app_name} -> {package_family}")
                elif (
                    isinstance(packages, dict)
                    and packages.get("Name")
                    and packages.get("PackageFamilyName")
                ):
                    # Single package case
                    full_name = packages["Name"]
                    if "." in full_name:
                        app_name = full_name.split(".")[-1]
                    else:
                        app_name = full_name

                    if app_name and len(app_name) > 1:
                        package_family = packages["PackageFamilyName"]
                        apps[app_name.lower()] = f"package:{package_family}"
                        print(f"Found UWP app: {app_name} -> {package_family}")
        except Exception as e:
            print(f"Error discovering UWP apps with Get-AppxPackage: {e}")

        # Method 3: Start Menu shortcuts (fallback)
        try:
            print("Discovering Start Menu shortcuts...")
            start_menu_paths = [
                Path.home()
                / "AppData"
                / "Roaming"
                / "Microsoft"
                / "Windows"
                / "Start Menu"
                / "Programs",
                Path("C:/ProgramData/Microsoft/Windows/Start Menu/Programs"),
            ]

            for start_path in start_menu_paths:
                if start_path.exists():
                    for lnk_file in start_path.rglob("*.lnk"):
                        try:
                            app_name = lnk_file.stem
                            if (
                                app_name
                                and len(app_name) > 1
                                and app_name.lower() not in apps
                            ):
                                # Only add if not already found by PowerShell methods
                                apps[app_name.lower()] = str(lnk_file)
                                print(f"Found shortcut: {app_name} -> {lnk_file}")
                        except Exception:
                            continue
        except Exception as e:
            print(f"Error discovering Start Menu apps: {e}")

        print(f"Discovered {len(apps)} total Windows applications")
        return apps

    def discover_apps(self) -> List[str]:
        """Discover available applications on the system."""
        try:
            if self.system == "darwin":
                apps_dict = self._discover_macos_apps()
            elif self.system == "linux":
                apps_dict = self._discover_linux_apps()
            elif self.system == "windows":
                apps_dict = self._discover_windows_apps()
            else:
                apps_dict = {}
        except Exception as e:
            print(f"Warning: Error discovering apps: {e}")
            apps_dict = {}

        # Cache the full dictionary for launching
        self._app_cache = apps_dict
        # Return just the app names for compatibility
        return list(apps_dict.keys())

    def find_app_fuzzy(  # noqa: PLR0912
        self, query: str, threshold: Optional[int] = None
    ) -> Optional[str]:
        """Find the best matching app using improved fuzzy search."""
        if threshold is None:
            threshold = settings.app_operations.FUZZY_THRESHOLD

        if not self._app_cache:
            self.discover_apps()

        if not self._app_cache:
            return None

        best_match = None
        best_score = 0

        query_lower = query.lower().strip()
        query_words = query_lower.split()

        for app in self._app_cache:
            app_lower = app.lower().strip()
            app_words = app_lower.split()

            score = 0

            # Priority 1: Exact match (highest priority)
            if query_lower == app_lower:
                score = 1000

            # Priority 2: Query is exact word in app name
            elif query_lower in app_words:
                score = 950

            # Priority 3: App starts with query
            elif app_lower.startswith(query_lower):
                score = 900 + int((len(query_lower) / len(app_lower)) * 50)

            # Priority 4: Any word in app starts with query
            elif any(word.startswith(query_lower) for word in app_words):
                score = 850

            # Priority 5: Query contains app name (for short app names)
            elif (
                len(app_lower) <= settings.app_operations.SHORT_APP_NAME_THRESHOLD
                and app_lower in query_lower
            ):
                score = 800

            # Priority 6: Strong substring match
            elif query_lower in app_lower:
                # Prefer matches where query is a larger portion of the app name
                score = 700 + int((len(query_lower) / len(app_lower)) * 100)

            # Priority 7: Word-based matching
            else:
                word_matches = 0
                partial_matches = 0

                for query_word in query_words:
                    # Exact word match
                    if query_word in app_words:
                        word_matches += 1
                    # Partial word match (word starts with query word)
                    elif any(
                        app_word.startswith(query_word) for app_word in app_words
                    ) or any(
                        query_word.startswith(app_word)
                        for app_word in app_words
                        if len(app_word)
                        >= settings.app_operations.MIN_WORD_LENGTH_FOR_PARTIAL_MATCH
                    ):
                        partial_matches += 1

                if word_matches > 0:
                    score = 600 + (word_matches * 100) + (partial_matches * 25)
                elif partial_matches > 0:
                    score = 400 + (partial_matches * 50)
                else:
                    # Fallback to fuzzy string matching
                    fuzzy_score = fuzz.ratio(query_lower, app_lower)
                    if (
                        fuzzy_score >= settings.app_operations.FUZZY_MATCH_THRESHOLD
                    ):  # Only consider good fuzzy matches
                        score = fuzzy_score + 200  # Boost to compete with other methods

            # Bonus for shorter app names (prefer specific matches)
            if (
                score > 0
                and len(app_lower) <= settings.app_operations.BONUS_APP_NAME_LENGTH
            ):
                score += 10

            # Penalty for very long app names that might be less relevant
            if len(app_lower) > settings.app_operations.PENALTY_APP_NAME_LENGTH:
                score = int(score * 0.9)

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

    def _launch_windows_app(self, app_path: str) -> bool:  # noqa: PLR0911, PLR0912
        """Launch a Windows application using multiple methods."""
        try:
            # Method 1: App ID launch (for apps discovered via Get-StartApps)
            if app_path.startswith("appid:"):
                app_id = app_path[6:]  # Remove 'appid:' prefix
                print(f"Launching app with ID: {app_id}")

                # Try launching via PowerShell Start-Process with AppID
                try:
                    if app_id.startswith(("C:\\", "c:\\")):
                        # Direct executable path
                        subprocess.Popen([app_id], shell=False)
                        return True
                    else:
                        # UWP App ID - use shell:appsFolder
                        result = subprocess.run(
                            [
                                "powershell",
                                "-Command",
                                f'Start-Process "shell:appsFolder\\{app_id}"',
                            ],
                            check=False,
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        return result.returncode == 0
                except Exception as e:
                    print(f"PowerShell launch failed: {e}")

                # Fallback: Try with explorer shell:appsFolder
                try:
                    subprocess.Popen(
                        ["explorer", f"shell:appsFolder\\{app_id}"], shell=False
                    )
                    return True
                except Exception as e:
                    print(f"Explorer shell launch failed: {e}")

            # Method 2: Package family launch (for UWP apps)
            elif app_path.startswith("package:"):
                package_family = app_path[8:]  # Remove 'package:' prefix
                print(f"Launching UWP package: {package_family}")

                try:
                    result = subprocess.run(
                        [
                            "powershell",
                            "-Command",
                            f'Start-Process "shell:appsFolder\\{package_family}!App"',
                        ],
                        check=False,
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    return result.returncode == 0
                except Exception as e:
                    print(f"UWP package launch failed: {e}")

            # Method 3: Direct execution for .exe files
            elif app_path.endswith(".exe") and Path(app_path).exists():
                print(f"Launching executable: {app_path}")
                subprocess.Popen([app_path], shell=False)
                return True

            # Method 4: Shell execution for .lnk files
            elif app_path.endswith(".lnk") and Path(app_path).exists():
                print(f"Launching shortcut: {app_path}")
                subprocess.Popen(
                    ["cmd", "/c", "start", "", f'"{app_path}"'], shell=False
                )
                return True

            # Method 5: Try as Windows Store app directory
            elif Path(app_path).exists() and Path(app_path).is_dir():
                print(f"Searching for executable in directory: {app_path}")
                for exe_file in Path(app_path).rglob("*.exe"):
                    try:
                        subprocess.Popen([str(exe_file)], shell=False)
                        return True
                    except Exception:
                        continue

            # Method 6: Try with explorer (final fallback)
            print(f"Trying explorer fallback: {app_path}")
            subprocess.Popen(["explorer", app_path], shell=False)
            return True

        except Exception as e:
            print(f"Error launching Windows app {app_path}: {e}")
            return False

    def launch_app(self, app_name: str) -> bool:  # noqa: PLR0911
        """Launch an application by name."""
        try:
            # First try fuzzy search
            matched_app = self.find_app_fuzzy(app_name)

            if matched_app and self._app_cache:
                app_path = self._app_cache[matched_app]
                print(f"🎯 Found app: {matched_app} -> {app_path}")

                if self.system == "darwin":
                    return self._launch_macos_app(matched_app)
                elif self.system == "linux":
                    return self._launch_linux_app(matched_app)
                elif self.system == "windows":
                    return self._launch_windows_app(app_path)
                else:
                    print(f"❌ Unsupported system: {self.system}")
                    return False
            else:
                # Fallback to direct launch
                print(f"🔍 Trying direct launch: {app_name}")

                if self.system == "darwin":
                    return self._launch_macos_app(app_name)
                elif self.system == "linux":
                    return self._launch_linux_app(app_name)
                elif self.system == "windows":
                    return self._launch_windows_app(app_name)
                else:
                    print(f"❌ Unsupported system: {self.system}")
                    return False

        except Exception as e:
            print(f"❌ Error launching {app_name}: {e}")
            return False

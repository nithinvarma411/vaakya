"""
App Operations Module
Handles application launching with fuzzy search across different platforms.
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import List, Optional
from fuzzywuzzy import fuzz


class AppOperations:
    """Platform-aware application operations with fuzzy search."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self._app_cache = None
    
    def discover_apps(self) -> List[str]:
        """Discover available applications on the system."""
        apps = []
        
        try:
            if self.system == "darwin":  # macOS
                # Check Applications folder
                apps_dir = "/Applications"
                if os.path.exists(apps_dir):
                    for item in os.listdir(apps_dir):
                        if item.endswith('.app'):
                            apps.append(item.replace('.app', ''))
                
                # Check user Applications
                user_apps = os.path.expanduser("~/Applications")
                if os.path.exists(user_apps):
                    for item in os.listdir(user_apps):
                        if item.endswith('.app'):
                            apps.append(item.replace('.app', ''))
                            
            elif self.system == "linux":
                # Check /usr/share/applications for .desktop files
                for app_dir in ["/usr/share/applications", "/usr/local/share/applications", 
                               os.path.expanduser("~/.local/share/applications")]:
                    if os.path.exists(app_dir):
                        try:
                            for item in os.listdir(app_dir):
                                if item.endswith('.desktop'):
                                    apps.append(item.replace('.desktop', '').replace('-', ' '))
                        except:
                            continue
                            
                # Also check common bin paths
                for bin_path in ["/usr/bin", "/usr/local/bin", "/bin"]:
                    if os.path.exists(bin_path):
                        try:
                            for item in os.listdir(bin_path):
                                if os.access(os.path.join(bin_path, item), os.X_OK):
                                    # Filter common non-app executables
                                    if not any(skip in item.lower() for skip in 
                                             ['systemd', 'dbus', 'update', 'install', 'config']):
                                        apps.append(item)
                                        if len(apps) > 50:  # Limit to avoid too many
                                            break
                        except:
                            continue
                            
            elif self.system == "windows":
                # Check common application directories
                common_paths = [
                    "C:\\Program Files",
                    "C:\\Program Files (x86)",
                ]
                for app_dir in common_paths:
                    if os.path.exists(app_dir):
                        try:
                            for item in os.listdir(app_dir):
                                if os.path.isdir(os.path.join(app_dir, item)):
                                    apps.append(item)
                        except:
                            continue
        
        except Exception as e:
            print(f"Warning: Error discovering apps: {e}")
        
        # Remove duplicates and cache
        self._app_cache = list(set(apps))
        return self._app_cache
    
    def find_app_fuzzy(self, query: str, threshold: int = 60) -> Optional[str]:
        """Find the best matching app using fuzzy search."""
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
                score = 95 + (len(query) / len(app)) * 5
            else:
                # Fuzzy matching
                score = fuzz.ratio(query_lower, app_lower)
                # Bonus for partial matches
                if any(word in app_lower for word in query_lower.split()):
                    score += 10
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = app
        
        return best_match
    
    def launch_app(self, app_name: str) -> bool:
        """Launch an application by name."""
        try:
            # First try fuzzy search
            matched_app = self.find_app_fuzzy(app_name)
            
            if matched_app:
                app_to_launch = matched_app
                print(f"🎯 Found app: {app_to_launch}")
            else:
                app_to_launch = app_name
                print(f"🔍 Trying direct launch: {app_to_launch}")
            
            if self.system == "darwin":  # macOS
                result = subprocess.run(['open', '-a', app_to_launch], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"✅ Launched {app_to_launch}")
                    return True
                else:
                    print(f"❌ Failed to launch {app_to_launch}: {result.stderr}")
                    return False
                    
            elif self.system == "linux":
                # Try multiple launch methods
                commands = [
                    ['gtk-launch', app_to_launch],
                    [app_to_launch],
                    ['nohup', app_to_launch],
                ]
                
                for cmd in commands:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            print(f"✅ Launched {app_to_launch}")
                            return True
                    except:
                        continue
                        
                print(f"❌ Failed to launch {app_to_launch}")
                return False
                
            elif self.system == "windows":
                result = subprocess.run(['start', '', app_to_launch], 
                                      shell=True, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"✅ Launched {app_to_launch}")
                    return True
                else:
                    print(f"❌ Failed to launch {app_to_launch}: {result.stderr}")
                    return False
                    
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout launching {app_name}")
            return False
        except Exception as e:
            print(f"❌ Error launching {app_name}: {e}")
            return False
        
        return False
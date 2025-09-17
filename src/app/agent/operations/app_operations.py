"""
Application operations module - Cross-platform app launching functionality.
"""

import subprocess
import shutil
import logging
from typing import Dict, Any, List
from kani import AIFunction
from .utils import PLATFORM_INFO

logger = logging.getLogger(__name__)

def launch_app(app_name: str) -> str:
    """
    Launch any application cross-platform by name.
    
    Args:
        app_name: Name of the application to launch (e.g., "Chrome", "Spotify", "VS Code")
        
    Returns:
        String indicating success or failure
    """
    try:
        system = PLATFORM_INFO['system_type']
        
        if system == "windows":
            return _launch_windows_app(app_name)
        elif system == "macos":  # macOS
            return _launch_macos_app(app_name)
        elif system == "linux":
            return _launch_linux_app(app_name)
        else:
            return f"Unsupported operating system: {system}"
            
    except Exception as e:
        logger.error(f"Error launching app {app_name}: {e}")
        return f"Failed to launch {app_name}: {str(e)}"

def _launch_windows_app(app_name: str) -> str:
    """Launch app on Windows with smart discovery."""
    try:
        import subprocess
        
        # Try direct command first
        try:
            result = subprocess.run(['start', '', app_name], 
                                   capture_output=True, text=True, timeout=5, shell=True)
            if result.returncode == 0:
                return f"Successfully launched {app_name} on Windows"
        except Exception:
            pass
        
        # Try with .exe extension
        try:
            result = subprocess.run(['start', '', f"{app_name}.exe"], 
                                   capture_output=True, text=True, timeout=5, shell=True)
            if result.returncode == 0:
                return f"Successfully launched {app_name}.exe on Windows"
        except Exception:
            pass
        
        # Try common name variations
        variations = [
            app_name.lower().replace(" ", ""),
            app_name.lower(),
            app_name.replace(" ", ""),
            app_name.title(),
            f"{app_name.lower()}.exe"
        ]
        
        # For generic terms, try to find appropriate apps dynamically
        if app_name.lower() in ['browser', 'editor', 'code', 'music', 'video', 'terminal']:
            # Use Windows registry or common locations to find apps dynamically
            # For now, try some common executable patterns
            common_patterns = [
                f"{app_name.lower()}.exe",
                f"ms{app_name.lower()}.exe",  # Microsoft apps
                f"google-{app_name.lower()}.exe",  # Google apps
            ]
            variations.extend(common_patterns)
        
        for variation in variations:
            try:
                result = subprocess.run(['start', '', variation], 
                                       capture_output=True, text=True, timeout=5, shell=True)
                if result.returncode == 0:
                    return f"Successfully launched {variation} on Windows"
            except Exception:
                continue
        
        return f"Could not find or launch '{app_name}' on Windows. Make sure the app is installed and try using the exact executable name."
        
    except Exception as e:
        return f"Failed to launch {app_name} on Windows: {str(e)}"

def _get_windows_category_apps(category: str) -> List[str]:
    """Get common Windows apps for a category - DEPRECATED, use dynamic discovery."""
    # This function is deprecated - we now use dynamic discovery
    return []

def _launch_macos_app(app_name: str) -> str:
    """Launch app on macOS with smart app discovery."""
    try:
        import subprocess
        import os
        
        # First try the exact app name
        try:
            result = subprocess.run(['open', '-a', app_name], 
                                   capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return f"Successfully launched {app_name} on macOS"
        except Exception:
            pass
        
        # If exact name fails, try to find similar apps
        try:
            # Get list of all applications
            result = subprocess.run(['mdfind', 'kMDItemKind == "Application"'], 
                                   capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                all_apps = result.stdout.strip().split('\n')
                app_names = []
                
                for app_path in all_apps:
                    if app_path and app_path.endswith('.app'):
                        # Extract app name from path
                        base_name = os.path.basename(app_path).replace('.app', '')
                        app_names.append((base_name, app_path))
                
                # Find closest match
                app_name_lower = app_name.lower()
                
                # First try exact matches
                exact_matches = [(name, path) for name, path in app_names 
                               if name.lower() == app_name_lower]
                
                if exact_matches:
                    name, path = exact_matches[0]
                    subprocess.run(['open', '-a', name], timeout=5)
                    return f"Successfully launched {name} on macOS"
                
                # Then try partial matches
                partial_matches = [(name, path) for name, path in app_names 
                                 if app_name_lower in name.lower() or name.lower() in app_name_lower]
                
                # If no partial matches, try category-based matching for generic terms
                if not partial_matches:
                    partial_matches = _find_apps_by_category(app_name_lower, app_names)
                
                if partial_matches:
                    # Try the first few matches
                    for name, path in partial_matches[:3]:
                        try:
                            result = subprocess.run(['open', '-a', name], 
                                                   capture_output=True, text=True, timeout=5)
                            if result.returncode == 0:
                                return f"Successfully launched {name} on macOS (closest match to '{app_name}')"
                        except Exception:
                            continue
                    
                    # If we couldn't launch any, suggest alternatives
                    suggestions = [name for name, _ in partial_matches[:5]]
                    return f"Could not launch '{app_name}' but found similar apps: {', '.join(suggestions)}. Try using one of these exact names."
        
        except Exception as e:
            pass
        
        return f"Could not find application '{app_name}' on macOS. Make sure the app is installed and try using the exact app name."
        
    except Exception as e:
        return f"Failed to launch {app_name} on macOS: {str(e)}"

def _find_apps_by_category(query: str, app_names: List[tuple]) -> List[tuple]:
    """Find apps by category/type when user gives generic terms using fuzzy matching."""
    category_matches = []
    
    # Use fuzzy matching based on common patterns in app names
    # This is dynamic - it looks at what's actually installed
    query_lower = query.lower()
    query_words = query_lower.replace(' ', '').split()
    
    # Direct keyword matching - look for query terms in app names
    for name, path in app_names:
        name_lower = name.lower()
        
        # Check if any word in the query appears in the app name
        for word in query_words:
            if len(word) > 2 and word in name_lower:
                category_matches.append((name, path))
        
        # Check for category-based fuzzy matching
        if _is_category_match(query_lower, name_lower):
            category_matches.append((name, path))
    
    # Remove duplicates while preserving order
    seen = set()
    unique_matches = []
    for item in category_matches:
        if item[0] not in seen:
            seen.add(item[0])
            unique_matches.append(item)
    
    return unique_matches

def _is_category_match(query: str, app_name: str) -> bool:
    """Check if an app name matches a category query using dynamic fuzzy logic."""
    # Dynamic category matching based on common naming patterns
    # This looks for patterns in app names rather than specific hardcoded lists
    if 'browser' in query:
        return any(word in app_name for word in ['browser', 'web']) or app_name.endswith('browser')
    elif 'editor' in query or 'edit' in query:
        return any(word in app_name for word in ['edit', 'text', 'code']) or 'editor' in app_name
    elif 'music' in query or 'audio' in query:
        return any(word in app_name for word in ['music', 'audio', 'player', 'sound', 'media']) or 'music' in app_name
    elif 'video' in query or 'media' in query:
        return any(word in app_name for word in ['video', 'player', 'media', 'movie', 'film']) or 'video' in app_name
    elif 'terminal' in query or 'console' in query:
        return any(word in app_name for word in ['terminal', 'console', 'shell', 'cmd']) or 'terminal' in app_name
    elif 'calculator' in query or 'calc' in query:
        return any(word in app_name for word in ['calculator', 'calc']) or 'calc' in app_name
    elif 'mail' in query or 'email' in query:
        return any(word in app_name for word in ['mail', 'email']) or 'mail' in app_name
    
    return False

def _launch_linux_app(app_name: str) -> str:
    """Launch app on Linux with smart discovery."""
    try:
        import subprocess
        import shutil
        
        # Try the app name directly first
        app_command = app_name.lower().replace(" ", "-")
        
        if shutil.which(app_command):
            try:
                subprocess.Popen([app_command])
                return f"Successfully launched {app_command} on Linux"
            except Exception:
                pass
        
        # Try common variations
        variations = [
            app_name.lower(),
            app_name.lower().replace(" ", ""),
            app_name.lower().replace(" ", "-"),
            f"gnome-{app_name.lower()}",
            f"{app_name.lower()}-browser" if "browser" not in app_name.lower() else app_name.lower(),
            app_name  # Original case
        ]
        
        # For generic terms, try category-based matching using dynamic pattern matching
        if app_name.lower() in ['browser', 'editor', 'code', 'music', 'video', 'terminal']:
            # Instead of hardcoded lists, try dynamic pattern matching
            # This will work with whatever apps are actually available on the system
            category_patterns = []
            category = app_name.lower()
            
            if 'browser' in category:
                category_patterns = [f'{category}', f'web-{category}', f'{category}-browser']
            elif 'editor' in category or 'code' in category:
                category_patterns = [f'{category}', f'text-{category}', f'{category}-editor']
            elif 'music' in category:
                category_patterns = [f'{category}', f'audio-{category}', f'{category}-player']
            elif 'video' in category:
                category_patterns = [f'{category}', f'media-{category}', f'{category}-player']
            elif 'terminal' in category:
                category_patterns = [f'{category}', f'console', f'shell']
            
            variations.extend(category_patterns)
        
        successful_launches = []
        available_commands = []
        
        for variation in variations:
            if shutil.which(variation):
                available_commands.append(variation)
                try:
                    subprocess.Popen([variation])
                    return f"Successfully launched {variation} on Linux"
                except Exception:
                    continue
        
        if available_commands:
            return f"Found commands {', '.join(available_commands)} but failed to launch them. Try running manually."
        
        return f"App '{app_name}' not found in PATH on Linux. Make sure it's installed and available in PATH."
            
    except Exception as e:
        return f"Failed to launch {app_name} on Linux: {str(e)}"

def _get_linux_category_apps(category: str) -> List[str]:
    """Get common Linux apps for a category - DEPRECATED, use dynamic discovery."""
    # This function is deprecated - we now use dynamic discovery
    return []

def get_system_info() -> str:
    """
    Get basic system information.
    
    Returns:
        String with system information
    """
    try:
        info = f"System: {PLATFORM_INFO['system']}\n"
        info += f"Release: {PLATFORM_INFO['release']}\n"
        info += f"Version: {PLATFORM_INFO['version']}\n"
        info += f"Machine: {PLATFORM_INFO['machine']}\n"
        info += f"Processor: {PLATFORM_INFO['processor']}"
        
        return info
        
    except Exception as e:
        return f"Failed to get system info: {str(e)}"

def list_installed_apps() -> str:
    """
    List installed applications on the system.
    
    Returns:
        String with list of available applications
    """
    try:
        system = PLATFORM_INFO['system_type']
        
        if system == "macos":
            return _list_macos_apps()
        elif system == "windows":
            return _list_windows_apps()
        elif system == "linux":
            return _list_linux_apps()
        else:
            return f"App listing not supported on {system}"
            
    except Exception as e:
        return f"Failed to list apps: {str(e)}"

def _list_macos_apps() -> str:
    """List applications on macOS."""
    try:
        import subprocess
        import os
        
        result = subprocess.run(['mdfind', 'kMDItemKind == "Application"'], 
                               capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            all_apps = result.stdout.strip().split('\n')
            app_names = []
            
            for app_path in all_apps:
                if app_path and app_path.endswith('.app'):
                    base_name = os.path.basename(app_path).replace('.app', '')
                    app_names.append(base_name)
            
            # Sort and limit to reasonable number
            app_names = sorted(set(app_names))[:50]  # Top 50 apps
            
            if app_names:
                return f"Installed applications on macOS:\n" + "\n".join(f"• {app}" for app in app_names)
            else:
                return "No applications found on macOS"
        else:
            return "Could not retrieve application list on macOS"
            
    except Exception as e:
        return f"Failed to list macOS apps: {str(e)}"

def _list_windows_apps() -> str:
    """List applications on Windows."""
    try:
        # This is a simplified version - Windows app discovery is complex
        return "App listing on Windows requires more complex implementation. Try using the exact application name or check your Start Menu."
    except Exception as e:
        return f"Failed to list Windows apps: {str(e)}"

def _list_linux_apps() -> str:
    """List applications on Linux."""
    try:
        import subprocess
        import os
        
        # Get applications from PATH
        path_dirs = os.environ.get('PATH', '').split(':')
        executables = set()
        
        for directory in path_dirs[:10]:  # Limit to avoid too many results
            try:
                if os.path.isdir(directory):
                    for file in os.listdir(directory):
                        if os.access(os.path.join(directory, file), os.X_OK):
                            executables.add(file)
            except (PermissionError, OSError):
                continue
        
        # Filter to common application names - return ALL executables, let AI decide
        common_apps = []
        
        for exe in sorted(executables):
            # Include any executable that looks like it could be an application
            # (more than 2 characters and not obviously a system command)
            if len(exe) > 2 and not exe.startswith('.'):
                common_apps.append(exe)
        
        if common_apps:
            return f"Available applications on Linux:\n" + "\n".join(f"• {app}" for app in common_apps[:50])
        else:
            return "Could not find applications on Linux"
            
    except Exception as e:
        return f"Failed to list Linux apps: {str(e)}"

# Define AI functions for Kani
launch_app_function = AIFunction(
    launch_app,
    name="launch_app",
    desc="Launch any application by name. Works cross-platform (Windows, macOS, Linux). You can use specific app names like 'Chrome', 'Spotify', 'Calculator', or generic terms like 'browser', 'code editor', 'music player', 'text editor', 'terminal', 'video player'. The system will find and launch the best matching application."
)

get_system_info_function = AIFunction(
    get_system_info,
    name="get_system_info", 
    desc="Get basic system information including OS, version, and hardware details."
)

list_installed_apps_function = AIFunction(
    list_installed_apps,
    name="list_installed_apps",
    desc="List applications installed on the system to help find the correct app name to launch."
)

def get_functions() -> List[AIFunction]:
    """Get all AI functions from this module."""
    return [
        launch_app_function,
        get_system_info_function,
        list_installed_apps_function
    ]
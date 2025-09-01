from pathlib import Path
import os
import ctypes
from ctypes import wintypes

# CSIDL constants for special folders
CSIDL_DESKTOP = 0x0000
CSIDL_DOCUMENTS = 0x0005
CSIDL_DOWNLOADS = 0x000c
CSIDL_MUSIC = 0x000d
CSIDL_VIDEOS = 0x000e
CSIDL_PICTURES = 0x0027

def get_special_folder_path(csidl):
    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, csidl, None, 0, buf)
    return buf.value

def list_immediate_subfolders(path: str):
    """Return only immediate folders inside the given path"""
    try:
        return [
            item.name
            for item in Path(path).iterdir()
            if item.is_dir()
        ]
    except Exception:
        return []

def get_user_folders():
    
    folder_paths = {}

    try:
        folder_paths["desktop"] = get_special_folder_path(CSIDL_DESKTOP)
        folder_paths["documents"] = get_special_folder_path(CSIDL_DOCUMENTS)
        folder_paths["downloads"] = get_special_folder_path(CSIDL_DOWNLOADS)
        folder_paths["music"] = get_special_folder_path(CSIDL_MUSIC)
        folder_paths["videos"] = get_special_folder_path(CSIDL_VIDEOS)
        folder_paths["pictures"] = get_special_folder_path(CSIDL_PICTURES)
    except Exception:
        # fallback to Path.home()
        home = Path.home()
        fallback_folders = ["Desktop", "Documents", "Downloads", "Pictures", "Videos", "Music"]
        for folder in fallback_folders:
            path = home / folder
            if path.exists():
                folder_paths[folder.lower()] = str(path)

    # Build final response: folder path + its immediate child folders
    result = {}
    for name, path in folder_paths.items():
        if path:
            result[name] = {
                "path": path,
                "folders": list_immediate_subfolders(path)
            }

    return result

import os
import glob
import win32com.client

def resolve_shortcut(path):
    """Resolve a Windows .lnk shortcut to its target .exe path."""
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(path)
        target = shortcut.Targetpath
        if target and target.lower().endswith(".exe"):
            return target
    except Exception:
        return None
    return None

def get_installed_apps():
    """Scan Start Menu shortcuts and return app name → exe path mapping."""
    apps = {}

    start_menu_paths = [
        os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs"),
        os.path.join(os.environ["ProgramData"], "Microsoft", "Windows", "Start Menu", "Programs"),
    ]

    for base in start_menu_paths:
        if not os.path.exists(base):
            continue

        # find all .lnk files
        for lnk_path in glob.glob(base + "/**/*.lnk", recursive=True):
            exe_path = resolve_shortcut(lnk_path)
            if exe_path:
                app_name = os.path.splitext(os.path.basename(lnk_path))[0].lower()
                apps[app_name] = exe_path

    return apps

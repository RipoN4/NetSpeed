"""
NETSpeed - Cross-Platform Non-Root Autostart Module
Enables or disables automatic launch on system startup for Windows (HKCU Run key)
and macOS (User LaunchAgent plist) without requiring administrator or root privileges.
"""

import os
import sys
from pathlib import Path

APP_NAME = "NETSpeed"
MACOS_PLIST_LABEL = "com.ripon.netspeed"


def _get_launch_command() -> str:
    """Return the exact command needed to launch NETSpeed."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    else:
        py_exe = sys.executable
        if sys.platform == "win32":
            pyw = py_exe.replace("python.exe", "pythonw.exe")
            if os.path.exists(pyw):
                py_exe = pyw
        
        main_py = os.path.abspath(sys.argv[0])
        if not main_py.endswith(".py"):
            main_py = str(Path(__file__).parent / "main.py")
            
        return f'"{py_exe}" "{main_py}"'


def _win_is_enabled() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ
        ) as key:
            try:
                val, _ = winreg.QueryValueEx(key, APP_NAME)
                return bool(val)
            except FileNotFoundError:
                return False
    except Exception as e:
        print(f"[NETSpeed Autostart] Windows check failed: {e}")
        return False


def _win_set_enabled(enable: bool) -> bool:
    if sys.platform != "win32":
        return False
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            key_path,
            0,
            winreg.KEY_SET_VALUE
        ) as key:
            if enable:
                cmd = _get_launch_command()
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
                print(f"[NETSpeed Autostart] Windows startup enabled: {cmd}")
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                    print("[NETSpeed Autostart] Windows startup disabled.")
                except FileNotFoundError:
                    pass
        return True
    except Exception as e:
        print(f"[NETSpeed Autostart] Windows set failed: {e}")
        return False


def _macos_plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{MACOS_PLIST_LABEL}.plist"


def _macos_is_enabled() -> bool:
    if sys.platform != "darwin":
        return False
    return _macos_plist_path().exists()


def _macos_set_enabled(enable: bool) -> bool:
    if sys.platform != "darwin":
        return False
    plist_file = _macos_plist_path()
    try:
        if enable:
            plist_file.parent.mkdir(parents=True, exist_ok=True)
            if getattr(sys, "frozen", False):
                args_xml = f"        <string>{sys.executable}</string>\n"
            else:
                py_exe = sys.executable
                main_py = str(Path(__file__).parent / "main.py")
                args_xml = f"        <string>{py_exe}</string>\n        <string>{main_py}</string>\n"

            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{MACOS_PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
{args_xml}    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>ProcessType</key>
    <string>Interactive</string>
</dict>
</plist>
"""
            with open(plist_file, "w", encoding="utf-8") as f:
                f.write(plist_content)
            print(f"[NETSpeed Autostart] macOS LaunchAgent created: {plist_file}")
            return True
        else:
            if plist_file.exists():
                plist_file.unlink()
                print("[NETSpeed Autostart] macOS LaunchAgent removed.")
            return True
    except Exception as e:
        print(f"[NETSpeed Autostart] macOS set failed: {e}")
        return False


def is_autostart_supported() -> bool:
    return sys.platform in ("win32", "darwin")


def is_autostart_enabled() -> bool:
    if sys.platform == "win32":
        return _win_is_enabled()
    elif sys.platform == "darwin":
        return _macos_is_enabled()
    return False


def set_autostart(enable: bool) -> bool:
    if sys.platform == "win32":
        return _win_set_enabled(enable)
    elif sys.platform == "darwin":
        return _macos_set_enabled(enable)
    return False

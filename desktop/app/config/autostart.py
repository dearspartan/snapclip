import sys
import os
import winreg
import logging

logger = logging.getLogger("snapclip.autostart")

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "SnapClipAgent"

def set_autostart(enabled: bool) -> bool:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_ALL_ACCESS)
        if enabled:
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                python_exe = sys.executable
                main_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
                exe_path = f'"{python_exe}" "{main_script}"'
            
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
            logger.info(f"Enabled autostart: {exe_path}")
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
                logger.info("Disabled autostart")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        logger.error(f"Failed to configure autostart registry: {e}")
        return False

def is_autostart_enabled() -> bool:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception:
        return False

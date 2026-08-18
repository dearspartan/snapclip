import ctypes
import time
import logging
from pynput.keyboard import Controller, Key

logger = logging.getLogger("snapclip.autopaste")

# Win32 SendInput constants
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
VK_CONTROL = 0x11
VK_V = 0x56

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT),
                ("ki", KEYBDINPUT),
                ("hi", HARDWAREINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("union", INPUT_UNION)]

class AutoPaster:
    def __init__(self):
        self.keyboard = Controller()

    def trigger_ctrl_v(self) -> bool:
        """Inject Ctrl+V using native Win32 SendInput for maximum speed & reliability."""
        try:
            # Create array of 4 keyboard inputs: Ctrl Down, V Down, V Up, Ctrl Up
            inputs = (INPUT * 4)()
            
            # 1. Ctrl Down
            inputs[0].type = INPUT_KEYBOARD
            inputs[0].union.ki.wVk = VK_CONTROL
            inputs[0].union.ki.dwFlags = 0

            # 2. V Down
            inputs[1].type = INPUT_KEYBOARD
            inputs[1].union.ki.wVk = VK_V
            inputs[1].union.ki.dwFlags = 0

            # 3. V Up
            inputs[2].type = INPUT_KEYBOARD
            inputs[2].union.ki.wVk = VK_V
            inputs[2].union.ki.dwFlags = KEYEVENTF_KEYUP

            # 4. Ctrl Up
            inputs[3].type = INPUT_KEYBOARD
            inputs[3].union.ki.wVk = VK_CONTROL
            inputs[3].union.ki.dwFlags = KEYEVENTF_KEYUP

            # Send input to active Windows focused control
            sent = ctypes.windll.user32.SendInput(4, ctypes.byref(inputs), ctypes.sizeof(INPUT))
            if sent == 4:
                return True
            else:
                logger.warning(f"SendInput sent {sent}/4 events, attempting pynput fallback")
        except Exception as e:
            logger.error(f"Win32 SendInput failed: {e}. Falling back to pynput.")

        # Fallback to pynput
        try:
            with self.keyboard.pressed(Key.ctrl):
                self.keyboard.press('v')
                self.keyboard.release('v')
            return True
        except Exception as e:
            logger.error(f"pynput Ctrl+V trigger failed: {e}")
            return False

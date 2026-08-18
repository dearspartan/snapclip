import pyperclip
import logging
from typing import Optional

logger = logging.getLogger("snapclip.clipboard")

class ClipboardManager:
    def __init__(self):
        pass

    def get_text(self) -> str:
        try:
            return pyperclip.paste() or ""
        except Exception as e:
            logger.error(f"Failed to read clipboard text: {e}")
            return ""

    def set_text(self, text: str) -> bool:
        try:
            pyperclip.copy(text)
            return True
        except Exception as e:
            logger.error(f"Failed to copy text to clipboard: {e}")
            return False

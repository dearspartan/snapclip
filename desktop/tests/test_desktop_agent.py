import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
import json
import websockets
import urllib.request
from app.storage.database import DatabaseManager
from app.pairing.auth import AuthManager
from app.clipboard.clipboard_manager import ClipboardManager
from app.clipboard.auto_paste import AutoPaster
from app.server.api import create_app

def test_database_and_auth(tmp_path):
    db_file = str(tmp_path / "test_snapclip.db")
    db = DatabaseManager(db_file)
    auth = AuthManager(db)

    pin = auth.get_pairing_pin()
    assert len(pin) == 6
    assert pin.isdigit()

    # Invalid PIN returns None
    assert auth.verify_pin_and_create_token("000000", "Phone") is None

    # Valid PIN returns Token
    token = auth.verify_pin_and_create_token(pin, "TestPhone")
    assert token is not None
    assert token.startswith("snapclip_")
    assert auth.validate_token(token) is True

def test_clipboard_manager():
    mgr = ClipboardManager()
    success = mgr.set_text("SnapClip Unit Test Text")
    assert success is True
    assert mgr.get_text() == "SnapClip Unit Test Text"

if __name__ == "__main__":
    print("Running quick standalone validation test...")
    db = DatabaseManager("test_snapclip.db")
    auth = AuthManager(db)
    pin = auth.get_pairing_pin()
    print(f"[OK] Generated PIN: {pin}")
    token = auth.verify_pin_and_create_token(pin, "TestDevice")
    print(f"[OK] Created Token: {token}")
    assert auth.validate_token(token)
    print("[OK] Auth Token Validation passed!")
    
    clip = ClipboardManager()
    clip.set_text("SnapClip Quick Test")
    assert clip.get_text() == "SnapClip Quick Test"
    print("[OK] Clipboard set/get passed!")
    print("ALL TESTS PASSED!")

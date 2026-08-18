import sys
import os
import time
import json
import threading
import asyncio
import urllib.request
import websockets
import pyperclip

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.storage.database import DatabaseManager
from app.pairing.auth import AuthManager
from app.clipboard.clipboard_manager import ClipboardManager
from app.clipboard.auto_paste import AutoPaster
from app.server.api import create_app
import uvicorn

def main():
    print("[TEST] Starting SnapClip Live Verification...")
    db = DatabaseManager("live_test.db")
    auth_mgr = AuthManager(db)
    clip_mgr = ClipboardManager()
    auto_paster = AutoPaster()

    app = create_app(db, auth_mgr, clip_mgr, auto_paster)
    config = uvicorn.Config(app=app, host="127.0.0.1", port=8766, log_level="warning")
    server = uvicorn.Server(config)

    # Run uvicorn in background thread
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    time.sleep(1.5) # Wait for server thread startup
    print("[TEST] Server started on http://127.0.0.1:8766")

    try:
        # 1. Fetch PIN
        pin = auth_mgr.get_pairing_pin()
        print(f"[TEST] Active PIN: {pin}")

        # 2. Perform HTTP Pairing Request
        pair_payload = json.dumps({"pin": pin, "device_name": "Test Android Phone"}).encode('utf-8')
        req = urllib.request.Request(
            "http://127.0.0.1:8766/api/pair",
            data=pair_payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            token = data["token"]
            print(f"[TEST] HTTP Pairing Success! Auth Token: {token}")

        # 3. Connect via WebSocket
        async def client_flow():
            ws_url = f"ws://127.0.0.1:8766/ws?token={token}"
            async with websockets.connect(ws_url) as ws:
                print("[TEST] WebSocket Connected successfully!")

                test_text = "SnapClip End-to-End Live Verification Text OK"
                payload = json.dumps({
                    "type": "paste",
                    "request_id": "req_live_101",
                    "text": test_text
                })
                await ws.send(payload)
                print("[TEST] Sent paste payload over WebSocket")

                raw_resp = await ws.recv()
                resp_obj = json.loads(raw_resp)
                print(f"[TEST] Received WebSocket response: {resp_obj}")

                assert resp_obj["type"] == "paste_result"
                assert resp_obj["request_id"] == "req_live_101"
                assert resp_obj["success"] is True

        asyncio.run(client_flow())

        # 4. Verify Clipboard Content
        time.sleep(0.2)
        clipboard_text = pyperclip.paste()
        print(f"[TEST] Windows Clipboard text: '{clipboard_text}'")
        assert clipboard_text == "SnapClip End-to-End Live Verification Text OK"
        print("[TEST] SUCCESS: End-to-End Live Verification PASSED PERFECTLY!")

    finally:
        server.should_exit = True

if __name__ == "__main__":
    main()

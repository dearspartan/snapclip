import json
import logging
import asyncio
from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect, status
from app.clipboard.clipboard_manager import ClipboardManager
from app.clipboard.auto_paste import AutoPaster
from app.pairing.auth import AuthManager

logger = logging.getLogger("snapclip.ws")

class WebSocketHandler:
    def __init__(self, auth_manager: AuthManager, clipboard_mgr: ClipboardManager, auto_paster: AutoPaster):
        self.auth_manager = auth_manager
        self.clipboard_mgr = clipboard_mgr
        self.auto_paster = auto_paster
        self.active_connections: Dict[str, WebSocket] = {}

    async def disconnect_token(self, token: str):
        if token in self.active_connections:
            ws = self.active_connections.pop(token)
            try:
                await ws.close(code=status.WS_1000_NORMAL_CLOSURE, reason="Unpaired by user")
            except Exception:
                pass

    async def disconnect_all(self):
        tokens = list(self.active_connections.keys())
        for token in tokens:
            await self.disconnect_token(token)

    async def handle_connection(self, websocket: WebSocket, token: str):
        # Validate authentication token
        if not self.auth_manager.validate_token(token):
            logger.warning(f"Rejected unauthenticated WebSocket attempt with token: {token}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Unauthorized token")
            return

        await websocket.accept()
        self.active_connections[token] = websocket
        logger.info(f"WebSocket client connected. Active clients: {len(self.active_connections)}")

        try:
            while True:
                data_text = await websocket.receive_text()
                try:
                    msg = json.loads(data_text)
                except json.JSONDecodeError:
                    logger.error("Malformed JSON message received")
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Malformed JSON payload"
                    }))
                    continue

                msg_type = msg.get("type")

                if msg_type == "paste":
                    request_id = msg.get("request_id", "")
                    text = msg.get("text", "")
                    
                    logger.info(f"Received paste request '{request_id}' with text length: {len(text)}")
                    
                    # 1. Update Clipboard
                    copied = self.clipboard_mgr.set_text(text)
                    
                    # 2. Trigger Ctrl + V
                    pasted = False
                    if copied:
                        # Give tiny delay for Windows OS clipboard buffer update
                        await asyncio.sleep(0.03)
                        pasted = self.auto_paster.trigger_ctrl_v()

                    success = copied and pasted
                    
                    # 3. Respond result
                    await websocket.send_text(json.dumps({
                        "type": "paste_result",
                        "request_id": request_id,
                        "success": success
                    }))

                elif msg_type == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))

                elif msg_type == "device_info":
                    import socket
                    await websocket.send_text(json.dumps({
                        "type": "device_info",
                        "pc_name": socket.gethostname(),
                        "status": "online"
                    }))

                else:
                    logger.warning(f"Unknown message type received: {msg_type}")
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"Unsupported command: {msg_type}"
                    }))

        except WebSocketDisconnect:
            logger.info("WebSocket client disconnected")
        except Exception as e:
            logger.error(f"WebSocket exception: {e}")
        finally:
            if token in self.active_connections and self.active_connections[token] == websocket:
                del self.active_connections[token]

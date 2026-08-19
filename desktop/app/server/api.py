import socket
from fastapi import FastAPI, WebSocket, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.storage.database import DatabaseManager
from app.pairing.auth import AuthManager
from app.pairing.qr_generator import generate_pairing_payload, generate_qr_code_image_bytes
from app.clipboard.clipboard_manager import ClipboardManager
from app.clipboard.auto_paste import AutoPaster
from app.server.ws_handler import WebSocketHandler

class PairRequest(BaseModel):
    pin: str
    device_name: str

class UnpairRequest(BaseModel):
    token: str

def create_app(db: DatabaseManager, auth_mgr: AuthManager, clip_mgr: ClipboardManager, paster: AutoPaster) -> FastAPI:
    app = FastAPI(title="SnapClip Desktop Agent", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    ws_handler = WebSocketHandler(auth_mgr, clip_mgr, paster)

    @app.get("/api/info")
    def get_info():
        local_ip = auth_mgr.get_local_ip()
        pin = auth_mgr.get_pairing_pin()
        pc_name = socket.gethostname()
        return {
            "pc_name": pc_name,
            "local_ip": local_ip,
            "port": 8765,
            "pin": pin,
            "paired_devices": db.get_paired_devices()
        }

    @app.get("/api/qr")
    def get_qr_code():
        local_ip = auth_mgr.get_local_ip()
        pin = auth_mgr.get_pairing_pin()
        pc_name = socket.gethostname()
        payload_str = generate_pairing_payload(local_ip, 8765, pin, pc_name)
        img_bytes = generate_qr_code_image_bytes(payload_str)
        return Response(content=img_bytes, media_type="image/png")

    @app.post("/api/pair")
    def pair_device(req: PairRequest):
        token = auth_mgr.verify_pin_and_create_token(req.pin, req.device_name)
        if not token:
            raise HTTPException(status_code=400, detail="Invalid pairing PIN code")
        
        return {
            "status": "ok",
            "token": token,
            "pc_name": socket.gethostname()
        }

    @app.post("/api/unpair")
    def unpair_device(req: UnpairRequest):
        if req.token:
            db.remove_paired_device(req.token)
        return {
            "status": "ok",
            "message": "Device unpaired successfully"
        }

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket, token: str = ""):
        await ws_handler.handle_connection(websocket, token)

    return app

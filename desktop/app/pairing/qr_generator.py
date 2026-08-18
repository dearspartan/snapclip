import qrcode
import json
import io
from typing import Dict, Any

def generate_pairing_payload(ip: str, port: int, pin: str, pc_name: str) -> str:
    payload = {
        "ip": ip,
        "port": port,
        "pin": pin,
        "pc_name": pc_name
    }
    return json.dumps(payload)

def generate_qr_code_image_bytes(payload_str: str) -> bytes:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(payload_str)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

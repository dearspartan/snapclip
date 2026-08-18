import secrets
import socket
from typing import Tuple, Optional
from app.storage.database import DatabaseManager

class AuthManager:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_local_ip(self) -> str:
        """Helper to discover LAN IP address of this Windows machine."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Doesn't actually connect, just routes to determine outbound interface IP
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def get_pairing_pin(self) -> str:
        return self.db.get_or_create_pin()

    def verify_pin_and_create_token(self, pin: str, device_name: str) -> Optional[str]:
        current_pin = self.get_pairing_pin()
        if pin and pin.strip() == current_pin.strip():
            token = f"snapclip_{secrets.token_urlsafe(32)}"
            self.db.register_paired_device(token, device_name)
            return token
        return None

    def validate_token(self, token: str) -> bool:
        return self.db.is_token_valid(token)

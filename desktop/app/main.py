import uvicorn
import threading
import logging
import time
import sys
import os
import io

# In PyInstaller windowed/GUI mode, sys.stdout and sys.stderr are None
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

# Ensure package imports work regardless of cwd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.storage.database import DatabaseManager
from app.pairing.auth import AuthManager
from app.clipboard.clipboard_manager import ClipboardManager
from app.clipboard.auto_paste import AutoPaster
from app.server.api import create_app
from app.tray.tray_icon import SystemTrayManager
from app.ui.pairing_window import PairingWindow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("snapclip.main")

def main():
    logger.info("Starting SnapClip Windows Desktop Agent V1...")

    # Initialize Managers
    db = DatabaseManager()
    auth_mgr = AuthManager(db)
    clip_mgr = ClipboardManager()
    auto_paster = AutoPaster()

    # Create FastAPI app
    app = create_app(db, auth_mgr, clip_mgr, auto_paster)

    # Server Thread
    server_config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8765,
        log_level="warning",
        log_config=None,
        use_colors=False
    )
    server = uvicorn.Server(server_config)

    def run_server():
        server.run()

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    ip = auth_mgr.get_local_ip()
    pin = auth_mgr.get_pairing_pin()
    logger.info(f"SnapClip Agent running at http://{ip}:8765 | WebSocket ws://{ip}:8765/ws")
    logger.info(f"Current Pairing PIN: {pin}")

    # UI Window instance
    pairing_ui = PairingWindow(db, auth_mgr)

    def show_ui():
        # Schedule UI show on main thread
        threading.Thread(target=pairing_ui.show, daemon=True).start()

    def stop_all():
        logger.info("Stopping SnapClip Desktop Agent...")
        server.should_exit = True

    # Run System Tray on main thread (or launcher)
    tray = SystemTrayManager(auth_mgr, show_ui_callback=show_ui, stop_server_callback=stop_all)
    
    # Show initial pairing UI on first launch
    threading.Thread(target=pairing_ui.show, daemon=True).start()
    
    tray.run()

if __name__ == "__main__":
    main()

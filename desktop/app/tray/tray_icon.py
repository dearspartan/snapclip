import pystray
from PIL import Image, ImageDraw
import threading
import sys
from app.pairing.auth import AuthManager
from app.config.autostart import is_autostart_enabled, set_autostart

def create_tray_icon_image():
    # Draw a 64x64 blue clipboard icon with a check mark
    img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Clipboard background pill shape
    draw.rounded_rectangle((10, 8, 54, 56), radius=8, fill="#0284c7")
    # Clip top handle
    draw.rounded_rectangle((24, 4, 40, 14), radius=3, fill="#0369a1")
    # Paper inside
    draw.rectangle((16, 18, 48, 50), fill="#ffffff")
    # Checkmark inside
    draw.line((22, 34, 30, 42), fill="#0284c7", width=4)
    draw.line((30, 42, 42, 26), fill="#0284c7", width=4)
    return img

class SystemTrayManager:
    def __init__(self, auth_mgr: AuthManager, show_ui_callback, stop_server_callback):
        self.auth_mgr = auth_mgr
        self.show_ui_callback = show_ui_callback
        self.stop_server_callback = stop_server_callback
        self.icon = None

    def run(self):
        local_ip = self.auth_mgr.get_local_ip()
        image = create_tray_icon_image()

        menu = pystray.Menu(
            pystray.MenuItem(f"● SnapClip Running ({local_ip})", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Show Pairing Info & QR", self._on_show_ui),
            pystray.MenuItem("Start with Windows", self._on_toggle_autostart, checked=lambda item: is_autostart_enabled()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit SnapClip", self._on_exit)
        )

        self.icon = pystray.Icon("SnapClip", image, "SnapClip Agent", menu)
        self.icon.run()

    def _on_show_ui(self, icon, item):
        if self.show_ui_callback:
            self.show_ui_callback()

    def _on_toggle_autostart(self, icon, item):
        current = is_autostart_enabled()
        set_autostart(not current)

    def _on_exit(self, icon, item):
        if self.icon:
            self.icon.stop()
        if self.stop_server_callback:
            self.stop_server_callback()
        sys.exit(0)

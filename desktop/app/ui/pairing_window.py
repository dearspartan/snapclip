import tkinter as tk
from tkinter import ttk, messagebox
import io
import os
import socket
from PIL import Image, ImageTk
from app.pairing.auth import AuthManager
from app.pairing.qr_generator import generate_pairing_payload, generate_qr_code_image_bytes
from app.config.autostart import set_autostart, is_autostart_enabled
from app.storage.database import DatabaseManager

class PairingWindow:
    def __init__(self, db: DatabaseManager, auth_mgr: AuthManager):
        self.db = db
        self.auth_mgr = auth_mgr
        self.root = None

    def show(self):
        if self.root is not None:
            try:
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()
                return
            except tk.TclError:
                self.root = None

        self.root = tk.Tk()
        self.root.title("SnapClip Desktop Agent")
        self.root.geometry("450x580")
        self.root.resizable(False, False)

        # Apply dark/light theme styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f8fafc")
        style.configure("TLabel", background="#f8fafc", foreground="#1e293b", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#0284c7")
        style.configure("Pin.TLabel", font=("Segoe UI", 24, "bold"), foreground="#0369a1", background="#e0f2fe")

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # App Header
        header = ttk.Label(main_frame, text="SnapClip Desktop Agent", style="Header.TLabel")
        header.pack(anchor=tk.W, pady=(0, 5))

        status_lbl = ttk.Label(main_frame, text="● Server Running", font=("Segoe UI", 10, "bold"), foreground="#16a34a")
        status_lbl.pack(anchor=tk.W, pady=(0, 15))

        # Local IP Info Box
        ip_addr = self.auth_mgr.get_local_ip()
        info_frame = ttk.LabelFrame(main_frame, text=" Connection Info ", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(info_frame, text=f"Computer Name: {socket.gethostname()}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Local LAN IP: {ip_addr}:8765").pack(anchor=tk.W)

        # PIN Box
        pin_val = self.auth_mgr.get_pairing_pin()
        pin_frame = ttk.LabelFrame(main_frame, text=" Pairing Code ", padding=10)
        pin_frame.pack(fill=tk.X, pady=(0, 15))

        pin_lbl = ttk.Label(pin_frame, text=f"  {pin_val}  ", style="Pin.TLabel")
        pin_lbl.pack(pady=5)

        # QR Code Image
        qr_payload = generate_pairing_payload(ip_addr, 8765, pin_val, socket.gethostname())
        qr_bytes = generate_qr_code_image_bytes(qr_payload)
        pil_img = Image.open(io.BytesIO(qr_bytes)).resize((180, 180))
        self.qr_photo = ImageTk.PhotoImage(pil_img)

        qr_lbl = ttk.Label(main_frame, image=self.qr_photo)
        qr_lbl.pack(pady=(0, 15))

        # Settings
        self.autostart_var = tk.BooleanVar(value=is_autostart_enabled())
        autostart_cb = ttk.Checkbutton(
            main_frame, 
            text="Start SnapClip automatically with Windows", 
            variable=self.autostart_var,
            command=self._on_toggle_autostart
        )
        autostart_cb.pack(anchor=tk.W, pady=(0, 10))

        # Hide window on close instead of destroying process
        self.root.protocol("WM_DELETE_WINDOW", self.hide)
        self.root.mainloop()

    def _on_toggle_autostart(self):
        val = self.autostart_var.get()
        set_autostart(val)

    def hide(self):
        if self.root:
            self.root.withdraw()

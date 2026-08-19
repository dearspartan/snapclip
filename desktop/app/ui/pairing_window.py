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
                self.refresh_devices()
                return
            except tk.TclError:
                self.root = None

        self.root = tk.Tk()
        self.root.title("SnapClip Desktop Agent")
        self.root.geometry("480x700")
        self.root.resizable(False, False)

        # Apply styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f8fafc")
        style.configure("TLabel", background="#f8fafc", foreground="#1e293b", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#0284c7")
        style.configure("Pin.TLabel", font=("Segoe UI", 22, "bold"), foreground="#0369a1", background="#e0f2fe")

        main_frame = ttk.Frame(self.root, padding=16)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # App Header
        header = ttk.Label(main_frame, text="SnapClip Desktop Agent", style="Header.TLabel")
        header.pack(anchor=tk.W, pady=(0, 2))

        status_lbl = ttk.Label(main_frame, text="● Server Running", font=("Segoe UI", 10, "bold"), foreground="#16a34a")
        status_lbl.pack(anchor=tk.W, pady=(0, 10))

        # Local IP Info Box
        ip_addr = self.auth_mgr.get_local_ip()
        info_frame = ttk.LabelFrame(main_frame, text=" Connection Info ", padding=8)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(info_frame, text=f"Computer Name: {socket.gethostname()}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Local LAN IP: {ip_addr}:8765").pack(anchor=tk.W)

        # Content Split Frame (PIN & QR Code)
        qr_pin_frame = ttk.Frame(main_frame)
        qr_pin_frame.pack(fill=tk.X, pady=(0, 10))

        # PIN Box
        self.pin_val = self.auth_mgr.get_pairing_pin()
        pin_frame = ttk.LabelFrame(qr_pin_frame, text=" 6-Digit PIN ", padding=8)
        pin_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=(0, 5))

        self.pin_lbl = ttk.Label(pin_frame, text=f" {self.pin_val} ", style="Pin.TLabel")
        self.pin_lbl.pack(pady=10)

        # QR Code Image
        self.qr_frame = ttk.LabelFrame(qr_pin_frame, text=" QR Scan ", padding=4)
        self.qr_frame.pack(side=tk.RIGHT)

        self._update_qr_image(ip_addr, self.pin_val)
        self.qr_lbl = ttk.Label(self.qr_frame, image=self.qr_photo)
        self.qr_lbl.pack()

        # Paired Devices List Box
        devices_frame = ttk.LabelFrame(main_frame, text=" Connected / Paired Devices ", padding=8)
        devices_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.device_listbox = tk.Listbox(
            devices_frame, 
            height=4, 
            font=("Segoe UI", 9), 
            selectmode=tk.SINGLE,
            bg="#ffffff",
            fg="#1e293b",
            highlightthickness=1,
            highlightcolor="#0284c7"
        )
        self.device_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 5))

        scrollbar = ttk.Scrollbar(devices_frame, orient="vertical", command=self.device_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.device_listbox.config(yscrollcommand=scrollbar.set)

        # Device Action Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        unpair_btn = tk.Button(
            btn_frame, 
            text="Disconnect Selected Device", 
            command=self._on_unpair_selected,
            bg="#ef4444", 
            fg="#ffffff", 
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            activebackground="#dc2626",
            activeforeground="#ffffff",
            padx=8,
            pady=4
        )
        unpair_btn.pack(side=tk.LEFT, padx=(0, 5))

        unpair_all_btn = tk.Button(
            btn_frame, 
            text="Unpair All Devices", 
            command=self._on_unpair_all,
            bg="#64748b", 
            fg="#ffffff", 
            font=("Segoe UI", 9),
            relief="flat",
            activebackground="#475569",
            activeforeground="#ffffff",
            padx=8,
            pady=4
        )
        unpair_all_btn.pack(side=tk.RIGHT)

        # Settings
        self.autostart_var = tk.BooleanVar(value=is_autostart_enabled())
        autostart_cb = ttk.Checkbutton(
            main_frame, 
            text="Start SnapClip automatically with Windows", 
            variable=self.autostart_var,
            command=self._on_toggle_autostart
        )
        autostart_cb.pack(anchor=tk.W, pady=(0, 5))

        # Initial device populate
        self.refresh_devices()

        # Hide window on close instead of destroying process
        self.root.protocol("WM_DELETE_WINDOW", self.hide)
        self.root.mainloop()

    def _update_qr_image(self, ip_addr: str, pin_val: str):
        qr_payload = generate_pairing_payload(ip_addr, 8765, pin_val, socket.gethostname())
        qr_bytes = generate_qr_code_image_bytes(qr_payload)
        pil_img = Image.open(io.BytesIO(qr_bytes)).resize((130, 130))
        self.qr_photo = ImageTk.PhotoImage(pil_img)

    def refresh_devices(self):
        if not self.root:
            return
        self.device_listbox.delete(0, tk.END)
        self.paired_devices_cache = self.db.get_paired_devices()
        if not self.paired_devices_cache:
            self.device_listbox.insert(tk.END, "  No devices paired yet. Scan QR code above!")
        else:
            for dev in self.paired_devices_cache:
                d_name = dev.get("device_name", "Unknown Phone")
                l_seen = dev.get("last_seen", "")
                self.device_listbox.insert(tk.END, f"📱 {d_name} (Last Active: {l_seen})")

    def _on_unpair_selected(self):
        sel = self.device_listbox.curselection()
        if not sel or not self.paired_devices_cache:
            messagebox.showinfo("Disconnect Device", "Please select a paired device from the list first.")
            return

        index = sel[0]
        if index < len(self.paired_devices_cache):
            target_device = self.paired_devices_cache[index]
            token = target_device.get("token")
            name = target_device.get("device_name", "Device")
            if token:
                self.db.remove_paired_device(token)
                messagebox.showinfo("Device Disconnected", f"Successfully disconnected and unpaired '{name}'.")
                self.refresh_devices()

    def _on_unpair_all(self):
        if messagebox.askyesno("Unpair All Devices", "Are you sure you want to disconnect and unpair all mobile devices?"):
            self.db.clear_all_paired_devices()
            new_pin = self.auth_mgr.db.rotate_pin()
            self.pin_lbl.config(text=f" {new_pin} ")
            self._update_qr_image(self.auth_mgr.get_local_ip(), new_pin)
            self.qr_lbl.config(image=self.qr_photo)
            self.refresh_devices()
            messagebox.showinfo("Unpaired All", "All devices unpaired and a new PIN code has been generated!")

    def _on_toggle_autostart(self):
        val = self.autostart_var.get()
        set_autostart(val)

    def hide(self):
        if self.root:
            self.root.withdraw()

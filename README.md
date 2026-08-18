# SnapClip — V1

> **One tap. Right there.**

[![Beginner User Guide](https://img.shields.io/badge/Documentation-Beginner's%20User%20Guide-blue.svg)](docs/USER_GUIDE.md)

📖 **[Read the Complete Beginner's User Guide](docs/USER_GUIDE.md)** for step-by-step setup, QR pairing, and usage instructions.

SnapClip is a polished, local-first cross-device utility that allows users to store custom text snippets on their Android phone and send them to their Windows PC with a single tap. 

Upon tapping a snippet on the phone, SnapClip transmits the text over the local network via WebSockets, writes it directly into the Windows system clipboard, and automatically performs a `Ctrl + V` keyboard paste into whatever application is currently active.

---

## 1. Core Workflow

```text
              SNAPCLIP WORKFLOW
        
        📱 Android Phone App
                 │
                 │ Single Tap "Email" Snippet
                 ▼
          📡 Local Wi-Fi WebSocket
                 │
                 ▼
       💻 Windows Desktop Agent
                 │
                 ▼
          📋 System Clipboard
                 │
                 ▼
         Synthetic Ctrl + V
                 │
                 ▼
     Currently Focused Application
```

---

## 2. Architecture & Tech Stack

### Mobile Application (`mobile/`)
* **Framework**: Flutter (Dart 3.x)
* **Local Storage**: `sqflite` (SQLite database for Snippet CRUD, Categories, Search indexing)
* **State Management**: `flutter_riverpod`
* **Networking**: `web_socket_channel` (Auto-reconnecting WebSocket connection with Ping/Pong heartbeat)
* **Security**: `flutter_secure_storage` (Android Keystore token persistence)
* **QR Scanner**: `mobile_scanner`

### Windows Desktop Agent (`desktop/`)
* **Runtime**: Python 3.11+
* **Server**: `FastAPI` + `uvicorn` (Asynchronous HTTP pairing & WebSocket server engine)
* **Clipboard Controller**: `pyperclip` / `win32clipboard`
* **Auto-Paster**: Win32 `SendInput` ctypes injection (with `pynput` fallback) for instant low-latency `Ctrl + V` simulation
* **System Tray & GUI**: `pystray` + `Pillow` notification icon + `tkinter` pairing info window
* **Database**: `sqlite3` (Local storage for PIN, auth token hashes, paired device info)
* **Auto-Start**: Windows Registry (`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`) integration

---

## 3. Communication & Security Protocol

SnapClip uses an authenticated local WebSocket communication model:

1. **Pairing**: Desktop generates a 6-digit random PIN & QR code payload.
2. **Handshake**: Phone sends `POST http://<PC_IP>:8765/api/pair` containing the PIN and device name.
3. **Token Issuance**: Desktop validates PIN and returns a cryptographically secure 256-bit token.
4. **Authentication**: Phone connects to `ws://<PC_IP>:8765/ws?token=<SECURE_TOKEN>`. Unauthenticated WebSocket connections are rejected.

### Protocol Payloads

#### Paste Request (Phone -> PC)
```json
{
  "type": "paste",
  "request_id": "req_8f9a2b",
  "text": "user@example.com"
}
```

#### Paste Result (PC -> Phone)
```json
{
  "type": "paste_result",
  "request_id": "req_8f9a2b",
  "success": true
}
```

#### Heartbeat
```json
// Ping (Phone -> PC)
{ "type": "ping" }

// Pong (PC -> Phone)
{ "type": "pong" }
```

---

## 4. Setup & Running Instructions

### Running Windows Desktop Agent

1. Open PowerShell / CMD in `desktop/`:
   ```bash
   cd desktop
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Run the agent:
   ```bash
   python app/main.py
   ```
3. A pairing window will pop up showing the LAN IP, 6-digit PIN code, and QR code. The app will run in the Windows system tray.

### Running Android App

1. Ensure Flutter SDK is installed and configured.
2. Open terminal in `mobile/`:
   ```bash
   cd mobile
   flutter pub get
   flutter run
   ```
3. Tap the status badge in the top app bar to scan the PC's QR code or enter the IP & PIN manually.

---

## 5. Future Roadmap

### SnapClip V2
* Clipboard history synchronization
* Temporary clipboard auto-clear
* Multi-computer switching
* Import/export JSON snippet backup

### SnapClip V3
* Dynamic template placeholders (`Hello {name}, your code is {code}`)
* Quick desktop launcher widget
* Browser extensions & iOS support

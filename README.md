# SnapClip — V1

> **One tap. Right there.**

SnapClip is a polished, local-first cross-device utility that allows users to store custom text snippets on their Android phone and send them to their Windows PC with a single tap. 

Upon tapping a snippet on the phone, SnapClip transmits the text over the local network via WebSockets, writes it directly into the Windows system clipboard, and automatically performs a `Ctrl + V` keyboard paste into whatever application is currently active.

---

## ⚡ Direct Downloads (No Setup Needed)

| Platform | Download Link | Description |
| :--- | :--- | :--- |
| 💻 **Windows PC Agent** | [**`SnapClip-Desktop-Agent.exe`**](releases/SnapClip-Desktop-Agent.exe) | 1-Click standalone `.exe` (No Python required) |
| 📱 **Android App** | [**`SnapClip-Android.apk`**](releases/SnapClip-Android.apk) | Direct `.apk` installer for Android phone |

---

## 📖 Beginner's User Guide

Read the complete **[Beginner's Step-by-Step Guide](docs/USER_GUIDE.md)** for pairing instructions, category management, autostart configuration, and troubleshooting.

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

## 2. Tech Stack

### Mobile Application (`mobile/`)
* **Framework**: Flutter (Dart 3.x)
* **Local Storage**: `sqflite` (SQLite database for Snippet CRUD, Categories, Search indexing)
* **State Management**: `flutter_riverpod`
* **Networking**: `web_socket_channel` (Auto-reconnecting WebSocket connection with Ping/Pong heartbeat)
* **Security**: `flutter_secure_storage` (Android Keystore token persistence)
* **QR Scanner**: `mobile_scanner`

### Windows Desktop Agent (`desktop/`)
* **Runtime**: Python 3.11+ (Compiled to standalone `.exe`)
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

---

## 4. Running from Source (Developer Setup)

### Windows Agent Source
```powershell
cd desktop
.\venv\Scripts\python.exe app\main.py
```

### Android App Source
```bash
cd mobile
flutter pub get
flutter run
```

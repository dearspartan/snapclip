# 📖 SnapClip — Complete Beginner's User Guide

> **One tap. Right there.**  
> *The complete step-by-step guide to setting up, pairing, and mastering SnapClip for seamless Phone-to-PC text pasting over Local Wi-Fi.*

---

## 📌 Table of Contents

1. [Overview & Core Concept](#-overview--core-concept)
2. [System Prerequisites](#-system-prerequisites)
3. [First-Time Setup Guide](#-first-time-setup-guide)
   - [Step 1: Launch the Windows Desktop Agent](#step-1-launch-the-windows-desktop-agent)
   - [Step 2: Install & Open the Android App](#step-2-install--open-the-android-app)
   - [Step 3: Pair Devices (QR Code or PIN)](#step-3-pair-devices-qr-code-or-pin)
4. [Day-to-Day Usage Guide](#-day-to-day-usage-guide)
   - [Creating Snippets](#creating-snippets)
   - [Pasting Snippets with a Single Tap](#pasting-snippets-with-a-single-tap)
   - [Organizing with Categories & Favorites](#organizing-with-categories--favorites)
   - [Instant Search](#instant-search)
   - [Editing & Deleting Snippets](#editing--deleting-snippets)
5. [Windows Agent & System Tray Features](#-windows-agent--system-tray-features)
   - [Background Execution](#background-execution)
   - [Start Automatically with Windows](#start-automatically-with-windows)
6. [Security & Privacy Model](#-security--privacy-model)
7. [Troubleshooting & FAQ](#-troubleshooting--faq)

---

## 🎯 Overview & Core Concept

**SnapClip** is a utility designed for maximum speed. It eliminates the frustration of emailing text snippets to yourself, opening messaging apps just to copy links, or manually retyping passwords and addresses onto your computer.

### How It Works

```text
📱 Android App                   📡 Local Wi-Fi                  💻 Windows PC
┌────────────────┐             ┌──────────────┐            ┌────────────────┐
│  Tap "Email"   ├────────────►│  WebSocket   ├───────────►│ Copy & Paste   │
│    Snippet     │             │ Protocol /ws │            │  via Ctrl + V  │
└────────────────┘             └──────────────┘            └───────┬────────┘
                                                                   │
                                                                   ▼
                                                         Currently Active Field
                                                         Email: [ user@example.com ]
```

When you tap a snippet on your Android phone, SnapClip instantly transmits it over your local Wi-Fi network directly into your Windows computer's clipboard and automatically presses **Ctrl + V**. The text appears wherever your mouse cursor is currently focused on your PC.

---

## 💻 System Prerequisites

Before getting started, ensure you have:

* **Windows PC**: Windows 10 or Windows 11.
* **Android Phone**: Android 8.0 (Oreo) or newer.
* **Network**: Both PC and Android phone **must be connected to the same Wi-Fi / Local Area Network (LAN)**.

> [!IMPORTANT]
> **No Internet Connection Required!** SnapClip works entirely offline over your local router. Your snippets are never sent to external servers or cloud accounts.

---

## 🚀 First-Time Setup Guide

### Step 1: Launch the Windows Desktop Agent

1. Download or clone the SnapClip repository onto your Windows computer.
2. Open **PowerShell** or **Command Prompt** inside the `desktop` folder:
   ```powershell
   cd L:\Code\projects\snapclip\desktop
   ```
3. Run the desktop agent application:
   ```powershell
   .\venv\Scripts\python.exe app\main.py
   ```
4. A setup window will appear on your desktop screen displaying:
   * **Server Status**: `● Server Running`
   * **Local LAN IP**: e.g., `192.168.1.25:8765`
   * **Pairing Code**: A 6-digit PIN (e.g., `482931`)
   * **QR Code**: A scannable pairing code

```text
┌─────────────────────────────────────────┐
│ SnapClip Desktop Agent                  │
├─────────────────────────────────────────┤
│ ● Server Running                        │
│                                         │
│ Connection Info                         │
│ Computer Name: SnapClip-PC              │
│ Local LAN IP: 192.168.1.25:8765         │
│                                         │
│ Pairing Code                            │
│ ┌─────────────────────────────────────┐ │
│ │               482931                │ │
│ └─────────────────────────────────────┘ │
│                                         │
│        [ QR Code Image Here ]           │
│                                         │
│ ☑ Start SnapClip automatically with Win │
└─────────────────────────────────────────┘
```

---

### Step 2: Install & Open the Android App

1. Launch the **SnapClip** app on your Android device.
2. On first launch, look at the top-right header badge: it will show **`○ Offline`**.
3. Tap the **`○ Offline`** badge to open the **Connect to PC** screen.

---

### Step 3: Pair Devices (QR Code or PIN)

You can pair your phone with your PC in two easy ways:

#### Option A: Scan QR Code (Recommended)
1. In the app, select the **Scan QR Code** tab.
2. Grant camera permissions if prompted.
3. Point your phone's camera at the QR code displayed on your Windows computer screen.
4. The app will automatically connect and save your secure pairing credentials!

#### Option B: Manual Setup
1. Switch to the **Manual Setup** tab on your phone.
2. Enter your computer's **Local LAN IP** (shown on the PC agent window, e.g., `192.168.1.25`).
3. Type the **6-digit Pairing Code** (e.g., `482931`).
4. Tap **Connect Computer**.

```text
✓ Success Indicator
Once paired, the status badge in the app header turns green:
● SnapClip-PC
```

---

## 📱 Day-to-Day Usage Guide

### Creating Snippets

1. Tap the blue **`[+] Add Snippet`** button at the bottom right of the phone screen.
2. Fill in the details:
   * **Snippet Name**: A recognizable title (e.g., `Work Email`, `GitHub Token`, `Home Address`).
   * **Category**: Choose a category (`Personal`, `Work`, `College`, `Development`, `Forms`, `Other`).
   * **Text Snippet**: Type or paste the content. Multiline text and Unicode characters (e.g., `₹500`, `é`, `こんにちは`) are fully supported.
   * **Mark as Favorite** *(Optional)*: Toggle to place this snippet at the top of your home screen.
3. Tap **Save**.

---

### Pasting Snippets with a Single Tap

This is the primary action in SnapClip:

1. On your Windows PC, place your cursor inside any active input field where you want text to appear (e.g., Notepad, Chrome search bar, Word document, VS Code editor).
2. On your Android phone, **tap the snippet card once**.
3. **Result**: 
   * A notification bar appears on your phone: `Pasted "Work Email" to SnapClip-PC!`.
   * The text automatically pastes into your PC application instantly!

```text
📱 Phone                              💻 PC Screen
┌──────────────┐                      ┌───────────────────────────┐
│ ✉ Email      │                      │ Form                      │
│ user@ex...   │ ──── Single Tap ───► │ Email: [ user@example.com]│
└──────────────┘                      └───────────────────────────┘
```

---

### Organizing with Categories & Favorites

* **Favorites Section**: Snippets marked with a star ⭐ appear in a quick horizontal scroll list near the top of the screen for ultra-fast access.
* **Category Filter Chips**: Tap any category pill (`Personal`, `Work`, `Development`, etc.) below the search bar to filter your list. Tap `All` to reset the view.

---

### Instant Search

Type keywords into the **Search Snippets** field. The list updates instantly as you type, matching against:
* Snippet titles
* Text content
* Category names

---

### Editing & Deleting Snippets

* **Long Press** on any snippet card to open the action menu:
  * ⭐ **Add / Remove from Favorites**
  * ✏️ **Edit Snippet**
  * 🗑️ **Delete Snippet** *(Requires confirmation)*

---

## ⚙️ Windows Agent & System Tray Features

### Background Execution

When you close the SnapClip window on Windows, the application **does not stop**. It minimizes silently to the **Windows System Tray** (notification area near the clock).

Look for the blue clipboard icon in your system tray:

```text
System Tray Menu Options:
─────────────────────────
● SnapClip Running (192.168.1.25)
─────────────────────────
Show Pairing Info & QR
Start with Windows
─────────────────────────
Exit SnapClip
```

* **Right-click the tray icon** to reopen the pairing window, toggle autostart, or exit the application completely.

---

### Start Automatically with Windows

To ensure SnapClip is always ready whenever you turn on your PC:
1. Open the SnapClip PC window (or right-click the system tray icon).
2. Check **`☑ Start SnapClip automatically with Windows`**.
3. SnapClip will start silently in the background on system boot.

---

## 🔒 Security & Privacy Model

SnapClip is designed with security and privacy as first principles:

* **100% Local Communication**: All communication stays strictly inside your local Wi-Fi router. No external servers or cloud accounts are used.
* **Secure Token Authentication**: During pairing, SnapClip generates a random 256-bit cryptographic token stored in your phone's hardware-backed Keystore (`flutter_secure_storage`). Unauthenticated devices cannot send messages to your PC.
* **Strict Command Isolation**: The Windows desktop agent **only accepts text paste commands**. It will never execute terminal commands, scripts, or system code sent over network messages.

---

## ❓ Troubleshooting & FAQ

### Q1: The status badge says "Offline" or "Connecting..."
* **Check Wi-Fi**: Ensure both your phone and PC are connected to the **same Wi-Fi network**.
* **Check Windows Firewall**: If Windows Defender Firewall displays a popup when starting SnapClip for the first time, click **Allow Access** for Private Networks.
* **Verify PC IP**: If your router assigned your PC a new local IP address, tap the status badge on your phone and re-pair using the new QR code or IP.

---

### Q2: I tap a snippet on my phone, but text does not appear on my PC
1. **Active Focus**: Ensure your cursor is clicked and actively blinking inside a text field on your PC before tapping the snippet on your phone.
2. **Administrator Windows**: Some elevated administrator applications (e.g., Task Manager running as Admin) block synthetic input from non-admin apps. If needed, run the SnapClip Desktop Agent as Administrator.

---

### Q3: How do I pair a new computer or unpair my phone?
* On your Android phone, go to **Connect to PC** screen -> tap **Unpair** or scan a new PC QR code.

---

### Q4: Does SnapClip support multiline text, emojis, and foreign languages?
* **Yes!** SnapClip fully supports multiline text blocks, special symbols (`!@#$%^&*()`), emojis, and Unicode languages (`Hindi`, `Japanese`, `Arabic`, `Spanish`, `German`, etc.).

---

## 📄 License & Roadmap

* **Version**: SnapClip V1.0.0
* **Architecture**: Local-First Phone-to-PC Utility
* **Roadmap**: Planned V2 features include multi-computer support, temporary clipboard history, and JSON snippet import/export.

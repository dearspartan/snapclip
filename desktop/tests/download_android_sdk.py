import urllib.request
import zipfile
import os
import subprocess
import ssl

SDK_DIR = r"L:\android-sdk"
TOOLS_URL = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
ZIP_PATH = r"L:\commandlinetools.zip"

print(f"[SDK] Downloading Android command line tools from {TOOLS_URL}...")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(TOOLS_URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=ctx) as resp, open(ZIP_PATH, "wb") as f:
    f.write(resp.read())

print("[SDK] Extracting commandlinetools...")
os.makedirs(os.path.join(SDK_DIR, "cmdline-tools"), exist_ok=True)
with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
    zip_ref.extractall(os.path.join(SDK_DIR, "cmdline-tools"))

# Move extracted 'cmdline-tools' folder to 'latest'
src = os.path.join(SDK_DIR, "cmdline-tools", "cmdline-tools")
dst = os.path.join(SDK_DIR, "cmdline-tools", "latest")
if os.path.exists(src) and not os.path.exists(dst):
    os.rename(src, dst)

print(f"[SDK] Android SDK Command Line Tools set up at {dst}")
if os.path.exists(ZIP_PATH):
    os.remove(ZIP_PATH)

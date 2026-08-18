import urllib.request
import zipfile
import os
import ssl

JDK_DIR = r"L:\jdk-17"
JDK_URL = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.10%2B7/OpenJDK17U-jdk_x64_windows_hotspot_17.0.10_7.zip"
ZIP_PATH = r"L:\openjdk17.zip"

print(f"[JDK] Downloading OpenJDK 17 from {JDK_URL}...")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(JDK_URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=ctx) as resp, open(ZIP_PATH, "wb") as f:
    f.write(resp.read())

print("[JDK] Extracting OpenJDK 17...")
os.makedirs(JDK_DIR, exist_ok=True)
with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
    zip_ref.extractall(r"L:\jdk_temp")

# Find extracted inner directory (jdk-17.0.10+7)
items = os.listdir(r"L:\jdk_temp")
if items:
    inner = os.path.join(r"L:\jdk_temp", items[0])
    for f in os.listdir(inner):
        src_f = os.path.join(inner, f)
        dst_f = os.path.join(JDK_DIR, f)
        if not os.path.exists(dst_f):
            os.rename(src_f, dst_f)

print(f"[JDK] OpenJDK 17 set up at {JDK_DIR}")
if os.path.exists(ZIP_PATH):
    os.remove(ZIP_PATH)

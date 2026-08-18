import subprocess
import os

SDKMANAGER = r"L:\android-sdk\cmdline-tools\latest\bin\sdkmanager.bat"
ENV = os.environ.copy()
ENV["JAVA_HOME"] = r"L:\jdk-17"
ENV["ANDROID_HOME"] = r"L:\android-sdk"
ENV["ANDROID_SDK_ROOT"] = r"L:\android-sdk"
ENV["PATH"] = r"L:\jdk-17\bin;" + ENV.get("PATH", "")

print("[SDK] Accepting Android SDK licenses...")
proc = subprocess.Popen([SDKMANAGER, "--licenses", "--sdk_root=L:\\android-sdk"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV, text=True)
stdout, stderr = proc.communicate(input="y\ny\ny\ny\ny\ny\ny\ny\n")
print(stdout[:500])

print("[SDK] Installing platforms;android-34, build-tools;34.0.0, platform-tools...")
proc = subprocess.Popen([SDKMANAGER, "--install", "platforms;android-34", "build-tools;34.0.0", "platform-tools", "--sdk_root=L:\\android-sdk"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV, text=True)
stdout, stderr = proc.communicate(input="y\ny\ny\n")
print(stdout[:500])
print("[SDK] Android SDK package installation complete!")

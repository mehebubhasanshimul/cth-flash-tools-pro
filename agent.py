#!/usr/bin/env python3
"""CTH local device agent. Read-only ADB/Fastboot queries only."""
import os, shutil, subprocess
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Restrict browser requests to local web origins; agent binds to loopback by default.
CORS(app, resources={r"/health": {"origins": "*"}, r"/api/*": {"origins": "*"}})
TIMEOUT = 12

def tool_path(name):
    env_name = "ADB_PATH" if name == "adb" else "FASTBOOT_PATH"
    custom = os.environ.get(env_name)
    if custom and os.path.isfile(custom):
        return custom
    found = shutil.which(name)
    return found

def execute(tool, args):
    path = tool_path(tool)
    if not path:
        return f"{tool} পাওয়া যায়নি। Android SDK Platform-Tools ইনস্টল করে PATH সেট করো।"
    try:
        p = subprocess.run([path] + args, capture_output=True, text=True, timeout=TIMEOUT, shell=False)
        output = (p.stdout or "") + (p.stderr or "")
        return output.strip() or f"কোনো আউটপুট নেই (exit code {p.returncode})"
    except subprocess.TimeoutExpired:
        return "সময় শেষ: ডিভাইস সংযোগ ও অনুমতি পরীক্ষা করো।"
    except Exception as e:
        return f"চালানো যায়নি: {type(e).__name__}: {e}"

@app.get("/health")
def health():
    return jsonify(ok=True, service="CTH Local Agent", mode="read-only")

@app.post("/api/adb_devices")
def adb_devices():
    return jsonify(output=execute("adb", ["devices", "-l"]))

@app.post("/api/adb_info")
def adb_info():
    # Read-only queries; no shell input, no arbitrary user-provided command.
    chunks = []
    for label, args in [
        ("ADB devices", ["devices", "-l"]),
        ("Model", ["-s", "DEVICE_PLACEHOLDER", "shell", "getprop", "ro.product.model"]),
    ]:
        if label == "ADB devices":
            chunks.append(label + ":\n" + execute("adb", args))
    # Query each connected device using a fixed, read-only command sequence.
    path = tool_path("adb")
    if path:
        try:
            p = subprocess.run([path, "devices"], capture_output=True, text=True, timeout=TIMEOUT, shell=False)
            ids = [line.split()[0] for line in p.stdout.splitlines()[1:] if line.strip() and "\tdevice" in line]
            if not ids:
                chunks.append("ডিভাইস তথ্য: অনুমোদিত ADB ডিভাইস পাওয়া যায়নি। ফোনে USB debugging অনুমোদন করো।")
            for serial in ids[:5]:
                chunks.append(f"\n[{serial}]")
                for prop in ("ro.product.manufacturer", "ro.product.model", "ro.build.version.release"):
                    chunks.append(prop + ": " + execute("adb", ["-s", serial, "shell", "getprop", prop]))
        except Exception as e:
            chunks.append(f"তথ্য পড়া যায়নি: {e}")
    return jsonify(output="\n".join(chunks))

@app.post("/api/fastboot_devices")
def fastboot_devices():
    return jsonify(output=execute("fastboot", ["devices"]))

if __name__ == "__main__":
    # Loopback only: do not expose the local command agent to the public internet.
    print("CTH Local Agent: http://127.0.0.1:8765")
    print("Read-only mode. Press Ctrl+C to stop.")
    app.run(host="127.0.0.1", port=8765, debug=False)

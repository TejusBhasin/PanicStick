#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="$HOME/Library/Application Support/PanicStick/app"
DATA_DIR="$HOME/Library/Application Support/PanicStick"
PLIST="$HOME/Library/LaunchAgents/org.panicstick.listener.plist"
LABEL="org.panicstick.listener"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 was not found. Install Python 3 from https://www.python.org/downloads/macos/ and run this installer again."
    open "https://www.python.org/downloads/macos/" || true
    read -r -p "Press Return to close this window."
    exit 1
fi

mkdir -p "$APP_DIR" "$HOME/Library/LaunchAgents" "$DATA_DIR"
cp "$ROOT_DIR/mac/panicstick.py" "$APP_DIR/panicstick.py"
cp "$ROOT_DIR/requirements.txt" "$APP_DIR/requirements.txt"

if [ ! -x "$APP_DIR/.venv/bin/python" ]; then
    python3 -m venv "$APP_DIR/.venv"
fi

"$APP_DIR/.venv/bin/python" -m pip install --upgrade pip
"$APP_DIR/.venv/bin/python" -m pip install -r "$APP_DIR/requirements.txt"

echo
echo "Opening PanicStick setup. Leave notification-only selected for your first test."
"$APP_DIR/.venv/bin/python" "$APP_DIR/panicstick.py" --setup

# If setup was cancelled, save the safe notification-only configuration.
if [ ! -f "$DATA_DIR/config.json" ]; then
    "$APP_DIR/.venv/bin/python" - "$DATA_DIR/config.json" <<'PY'
import json, sys
with open(sys.argv[1], "w", encoding="utf-8") as stream:
    json.dump({"version": 1, "on_insertion": True, "on_button_hold": False,
               "actions": [{"id": "notify"}], "selected_apps": [],
               "vm_apps": [], "shortcut_name": ""}, stream, indent=2)
    stream.write("\n")
PY
fi

python3 - "$PLIST" "$APP_DIR" "$DATA_DIR" "$LABEL" <<'PY'
import os
import plistlib
import sys

plist_path, app_dir, data_dir, label = sys.argv[1:]
python_path = os.path.join(app_dir, ".venv", "bin", "python")
program = os.path.join(app_dir, "panicstick.py")
payload = {
    "Label": label,
    "ProgramArguments": [python_path, program],
    "RunAtLoad": True,
    "KeepAlive": True,
    "StandardOutPath": os.path.join(data_dir, "panicstick.log"),
    "StandardErrorPath": os.path.join(data_dir, "panicstick.log"),
}
with open(plist_path, "wb") as stream:
    plistlib.dump(payload, stream)
PY

launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"

echo
echo "PanicStick is installed. The helper starts when you sign in."
echo "When you plug in a Pico, a confirmation window appears before selected actions run."
echo "Choose No to cancel. To change your choices later, run PanicStick setup again."
read -r -p "Press Return to close this window."

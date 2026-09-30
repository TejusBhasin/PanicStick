#!/bin/bash
set -euo pipefail

PLIST="$HOME/Library/LaunchAgents/org.panicstick.listener.plist"
APP_DIR="$HOME/Library/Application Support/PanicStick/app"

launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
rm -f "$PLIST"
rm -rf "$APP_DIR"

echo "PanicStick's login helper has been removed."
echo "Your saved settings and event log were kept in ~/Library/Application Support/PanicStick."
read -r -p "Press Return to close this window."

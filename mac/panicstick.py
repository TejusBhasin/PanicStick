#!/usr/bin/env python3
"""PanicStick macOS USB serial listener: notify and log; no destructive actions."""
import argparse
import json
import logging
import signal
import subprocess
import sys
import time
from pathlib import Path

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    print("Missing pySerial. Install dependencies with: python3 -m pip install -r requirements.txt", file=sys.stderr)
    raise SystemExit(2)

PROTOCOL = "panicstick"
VERSION = 1
MIN_HOLD_MS = 2000
MAX_LINE_BYTES = 4096
LOG_PATH = Path.home() / "Library" / "Application Support" / "PanicStick" / "events.jsonl"


def choose_port(requested):
    if requested:
        return requested
    ports = list(list_ports.comports())
    candidates = [
        port.device for port in ports
        if any(word in " ".join(filter(None, [port.description, port.product, port.manufacturer])).lower()
               for word in ("pico", "panicstick", "rp2"))
    ]
    if len(candidates) == 1:
        return candidates[0]
    if not ports:
        raise RuntimeError("No serial ports found. Connect the Pico with a USB data cable.")
    available = "\n".join(f"  {p.device}: {p.description or p.product or 'serial device'}" for p in ports)
    if candidates:
        available += "\nPossible Pico ports: " + ", ".join(candidates)
    raise RuntimeError("Could not safely choose one Pico serial port. Available ports:\n" + available +
                       "\nPass the intended device with --port.")


def notify(title, message):
    # Notifications are informational and contain no user-controlled shell text.
    if sys.platform != "darwin":
        print(f"{title}: {message}")
        return
    try:
        subprocess.run(
            ["osascript", "-e",
             f'display notification "{message}" with title "{title}"'],
            check=False, capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        print(f"{title}: {message}")


def append_event(event):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, sort_keys=True) + "\n")


def validate(message):
    if not isinstance(message, dict):
        return False
    if message.get("protocol") != PROTOCOL or message.get("version") != VERSION:
        return False
    event = message.get("event")
    if event == "hello":
        return True
    if event == "released":
        hold_ms = message.get("hold_ms")
        return isinstance(hold_ms, int) and not isinstance(hold_ms, bool) and hold_ms >= 0
    if event != "trigger":
        return False
    hold_ms = message.get("hold_ms")
    event_id = message.get("event_id")
    return (
        isinstance(hold_ms, int) and not isinstance(hold_ms, bool)
        and MIN_HOLD_MS <= hold_ms <= 60_000
        and isinstance(event_id, str) and 1 <= len(event_id) <= 32
        and event_id.isalnum()
    )


def run(port_name):
    port = serial.Serial(port_name, baudrate=115200, timeout=1, write_timeout=1)
    seen_ids = set()
    logging.info("Connected to %s. USB connection alone does not trigger a response.", port_name)
    notify("PanicStick ready", "Connected. Hold the hardware button for 2 seconds to log a trigger.")
    try:
        while True:
            raw = port.readline(MAX_LINE_BYTES + 1)
            if not raw:
                continue
            if len(raw) > MAX_LINE_BYTES or not raw.endswith(b"\n"):
                logging.warning("Ignored overlong or incomplete serial line.")
                continue
            try:
                message = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                logging.warning("Ignored malformed serial message.")
                continue
            if not validate(message):
                logging.warning("Ignored message that did not match protocol v%d.", VERSION)
                continue

            event_type = message["event"]
            if event_type == "hello":
                logging.info("Pico online: %s (firmware %s)", message.get("device", "device"),
                             message.get("firmware", "unknown"))
                continue
            if event_type == "released":
                continue

            event_id = message["event_id"]
            if event_id in seen_ids:
                continue
            seen_ids.add(event_id)
            if len(seen_ids) > 512:
                seen_ids.clear()
                seen_ids.add(event_id)

            record = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "event": "trigger",
                "event_id": event_id,
                "hold_ms": message["hold_ms"],
                "action": "notification_only",
            }
            append_event(record)
            logging.warning("Physical trigger received after %d ms. Logged; no system settings changed.",
                            message["hold_ms"])
            notify("PanicStick triggered", "Physical button held. Trigger recorded; no system settings changed.")
    finally:
        port.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", help="USB serial device path (auto-detected when unambiguous)")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        run(choose_port(args.port))
    except KeyboardInterrupt:
        logging.info("Stopped.")
    except (RuntimeError, serial.SerialException, OSError) as exc:
        logging.error("%s", exc)
        raise SystemExit(1)


if __name__ == "__main__":
    main()

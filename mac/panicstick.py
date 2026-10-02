#!/usr/bin/env python3
"""PanicStick macOS companion. Plug-in and button actions always require review."""
import argparse
import json
import logging
import os
import plistlib
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

from panicstick_core import EventIdCache, normalize_config, ordered_actions, validate_message

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    print("PanicStick needs pySerial. Use the beginner install guide.", file=sys.stderr)
    raise SystemExit(2)

PROTOCOL = "panicstick"
VERSION = 1
MIN_HOLD_MS = 2000
MAX_LINE_BYTES = 4096
DATA_DIR = Path.home() / "Library" / "Application Support" / "PanicStick"
CONFIG_PATH = DATA_DIR / "config.json"
LOG_PATH = DATA_DIR / "events.jsonl"
SKIP_PROCESSES = {"Finder", "System Events", "Dock", "loginwindow", "WindowManager"}
SEEN_TRIGGER_IDS = EventIdCache(512)
STOP = threading.Event()
EVENTS = queue.Queue()

ACTION_LABELS = {
    "quit_all_apps": "Quit all open apps (apps may ask to save unsaved work)",
    "quit_selected_apps": "Quit selected apps",
    "disable_wifi": "Turn Wi-Fi off",
    "disable_bluetooth": "Turn Bluetooth off (requires blueutil)",
    "disable_ssh": "Turn off incoming SSH / Remote Login (admin password prompt)",
    "open_sharing_settings": "Open Sharing settings to turn off Screen Sharing manually",
    "quit_vm_apps": "Quit selected virtual-machine apps (does not stop headless VMs)",
    "run_shortcut": "Run a Shortcut you made in the Shortcuts app",
    "quit_terminal": "Quit Terminal",
    "power_off": "Shut down the Mac (always runs last)",
    "notify": "Show a PanicStick notification",
}
ACTION_ORDER = {
    "notify": 0,
    "run_shortcut": 10,
    "open_sharing_settings": 80,
    "disable_wifi": 30,
    "disable_bluetooth": 31,
    "disable_ssh": 32,
    "quit_selected_apps": 50,
    "quit_vm_apps": 51,
    "quit_all_apps": 60,
    "quit_terminal": 90,
    "power_off": 100,
}
DEFAULT_CONFIG = {
    "version": 1,
    "confirmation_mode": "before_run",
    "confirm_before": ["power_off"],
    "on_insertion": True,
    "on_button_hold": False,
    "actions": [{"id": "notify"}],
    "selected_apps": [],
    "vm_apps": [],
    "shortcut_name": "",
}


def notify(title, message):
    if sys.platform != "darwin":
        print(f"{title}: {message}")
        return
    try:
        subprocess.run(
            ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
            check=False, capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        print(f"{title}: {message}")


def ensure_private_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        os.chmod(DATA_DIR, 0o700)
    except OSError as exc:
        logging.warning("Could not restrict settings-folder permissions: %s", exc)


def append_event(event):
    ensure_private_data_dir()
    with LOG_PATH.open("a", encoding="utf-8") as stream:
        os.chmod(LOG_PATH, 0o600)
        stream.write(json.dumps(event, sort_keys=True) + "\n")


def load_config():
    if not CONFIG_PATH.exists():
        return normalize_config(DEFAULT_CONFIG, DEFAULT_CONFIG, ACTION_LABELS)
    try:
        with CONFIG_PATH.open(encoding="utf-8") as stream:
            config = json.load(stream)
        return normalize_config(config, DEFAULT_CONFIG, ACTION_LABELS)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        logging.error("Could not read setup settings (%s). Keeping safe notification-only defaults.", exc)
        return normalize_config(DEFAULT_CONFIG, DEFAULT_CONFIG, ACTION_LABELS)


def save_config(config):
    ensure_private_data_dir()
    config = normalize_config(config, DEFAULT_CONFIG, ACTION_LABELS)
    temporary = CONFIG_PATH.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        os.chmod(temporary, 0o600)
        json.dump(config, stream, indent=2)
        stream.write("\n")
    temporary.replace(CONFIG_PATH)


def setup_wizard():
    """Beginner-friendly visual setup; cancelling preserves safe defaults."""
    try:
        import tkinter as tk
        from tkinter import messagebox
    except ImportError:
        raise RuntimeError("This Python installation does not include the macOS Tk interface.")

    config = load_config()
    root = tk.Tk()
    root.title("PanicStick setup")
    root.geometry("760x900")
    root.minsize(680, 760)
    root.columnconfigure(0, weight=1)

    heading = tk.Label(root, text="Choose what PanicStick should do",
                       font=("Helvetica", 19, "bold"), anchor="w")
    heading.grid(row=0, column=0, sticky="ew", padx=24, pady=(22, 6))
    tk.Label(
        root,
        text=("Choose confirmation before each run or unattended mode with optional checkpoints. "
              "If someone takes over the Mac, a prompt may be blocked and you may not be able to confirm. "
              "USB insertion triggers actions only when explicitly enabled."),
        justify="left", wraplength=650, anchor="w",
    ).grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 14))

    insertion = tk.BooleanVar(value=bool(config.get("on_insertion", True)))
    button = tk.BooleanVar(value=bool(config.get("on_button_hold", False)))
    tk.Checkbutton(root, text="Ask me to run these actions when I plug in the Pico",
                   variable=insertion).grid(row=2, column=0, sticky="w", padx=24)
    tk.Checkbutton(root, text="Also ask when I hold the physical button for 2 seconds",
                   variable=button).grid(row=3, column=0, sticky="w", padx=24, pady=(0, 12))

    mode = tk.StringVar(value=config.get("confirmation_mode", "before_run"))
    tk.Label(root, text="Confirmation mode:", anchor="w").grid(row=4, column=0, sticky="w", padx=24)
    tk.Radiobutton(root, text="Ask before each run (recommended)", variable=mode, value="before_run").grid(row=5, column=0, sticky="w", padx=24)
    tk.Radiobutton(root, text="Run without a start prompt (unattended)", variable=mode, value="unattended").grid(row=6, column=0, sticky="w", padx=24)
    tk.Label(root, text="Optional checkpoints: ask immediately before selected actions", anchor="w").grid(row=7, column=0, sticky="w", padx=24)
    checkpoints = tk.Listbox(root, selectmode="multiple", height=4, exportselection=False)
    checkpoints.grid(row=8, column=0, sticky="ew", padx=24)
    defaults = {item.get("id") for item in config.get("actions", [])}
    choices = {}
    row = 9
    checkpoint_ids = []
    for action_id, label in ACTION_LABELS.items():
        var = tk.BooleanVar(value=action_id in defaults)
        choices[action_id] = var
        tk.Checkbutton(root, text=label, variable=var, anchor="w").grid(
            row=row, column=0, sticky="w", padx=24, pady=1
        )
        row += 1
        checkpoint_ids.append(action_id)
        checkpoints.insert("end", f"Confirm before: {label}")
        if action_id in config.get("confirm_before", []):
            checkpoints.selection_set(len(checkpoint_ids) - 1)

    tk.Label(root, text="App names for the two app choices (comma-separated; for example Safari, Mail):",
             anchor="w", wraplength=650).grid(row=row, column=0, sticky="ew", padx=24, pady=(12, 2))
    app_entry = tk.Entry(root)
    app_entry.insert(0, ", ".join(config.get("selected_apps", [])))
    app_entry.grid(row=row + 1, column=0, sticky="ew", padx=24)

    tk.Label(root, text="Virtual-machine apps to quit (comma-separated; for example UTM, VMware Fusion):",
             anchor="w", wraplength=650).grid(row=row + 2, column=0, sticky="ew", padx=24, pady=(10, 2))
    vm_entry = tk.Entry(root)
    vm_entry.insert(0, ", ".join(config.get("vm_apps", [])))
    vm_entry.grid(row=row + 3, column=0, sticky="ew", padx=24)

    tk.Label(root, text="Exact Shortcut name (check it in the Shortcuts app):", anchor="w").grid(
        row=row + 4, column=0, sticky="ew", padx=24, pady=(10, 2)
    )
    shortcut_entry = tk.Entry(root)
    shortcut_entry.insert(0, config.get("shortcut_name", ""))
    shortcut_entry.grid(row=row + 5, column=0, sticky="ew", padx=24)

    result = {"saved": False}

    def save():
        actions = [{"id": action_id} for action_id, var in choices.items() if var.get()]
        if choices["quit_selected_apps"].get() and not app_entry.get().strip():
            messagebox.showerror("App names needed", "Enter at least one app name for “Quit selected apps.”", parent=root)
            return
        if choices["quit_vm_apps"].get() and not vm_entry.get().strip():
            messagebox.showerror("App names needed", "Enter the virtual-machine app names to quit.", parent=root)
            return
        if choices["run_shortcut"].get() and not shortcut_entry.get().strip():
            messagebox.showerror("Shortcut name needed", "Enter the exact name of your Shortcut.", parent=root)
            return
        if not actions:
            messagebox.showerror("Choose an action", "Select at least one action.", parent=root)
            return
        config.update({
            "confirmation_mode": mode.get(),
            "confirm_before": [checkpoint_ids[index] for index in checkpoints.curselection()],
            "on_insertion": insertion.get(),
            "on_button_hold": button.get(),
            "actions": actions,
            "selected_apps": [s.strip() for s in app_entry.get().split(",") if s.strip()],
            "vm_apps": [s.strip() for s in vm_entry.get().split(",") if s.strip()],
            "shortcut_name": shortcut_entry.get().strip(),
        })
        try:
            config = normalize_config(config, DEFAULT_CONFIG, ACTION_LABELS)
        except ValueError as exc:
            messagebox.showerror("Settings need a change", str(exc), parent=root)
            return
        if not config["on_insertion"] and not config["on_button_hold"]:
            if not messagebox.askyesno("No trigger selected", "Save anyway? The app will wait without running actions.",
                                       default=messagebox.NO, parent=root):
                return
        save_config(config)
        result["saved"] = True
        messagebox.showinfo("Setup saved", f"Settings saved in:\n{CONFIG_PATH}", parent=root)
        root.destroy()

    buttons = tk.Frame(root)
    buttons.grid(row=row + 6, column=0, sticky="e", padx=24, pady=18)
    tk.Button(buttons, text="Cancel", command=root.destroy).pack(side="right", padx=(8, 0))
    tk.Button(buttons, text="Save settings", command=save, default="active").pack(side="right")
    root.mainloop()
    return result["saved"]


def validate(message):
    return validate_message(
        message, protocol=PROTOCOL, version=VERSION,
        minimum_hold_ms=MIN_HOLD_MS, maximum_hold_ms=60_000,
    )


def applescript_string(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def ask_to_run(source, config):
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        labels = [action_prompt_line(item, config)
                  for item in ordered_actions(config["actions"], ACTION_ORDER)]
        details = "\n".join(f"• {label}" for label in labels)
        ok = messagebox.askyesno(
            "PanicStick confirmation",
            f"PanicStick was {source}. Run these actions now?\n\n{details}\n\n"
            "Choose No to cancel. Unsaved work may be affected by app closing.",
            default=messagebox.NO, parent=root,
        )
        root.destroy()
        return ok
    except Exception as exc:
        logging.error("Could not show the confirmation window; actions cancelled: %s", exc)
        return False


def ask_action_checkpoint(action, config):
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        ok = messagebox.askyesno("PanicStick checkpoint",
            f"Continue with this step?\\n\\n{action_prompt_line(action, config)}\\n\\nChoose No to stop later actions.",
            default=messagebox.NO, parent=root)
        root.destroy()
        return ok
    except Exception as exc:
        logging.error("Could not show the checkpoint; later actions cancelled: %s", exc)
        return False


def action_prompt_line(action, config):
    action_id = action["id"]
    label = ACTION_LABELS.get(action_id, action_id)
    if action_id == "quit_selected_apps":
        return f"{label}: {', '.join(config.get('selected_apps', []))}"
    if action_id == "quit_vm_apps":
        return f"{label}: {', '.join(config.get('vm_apps', []))}"
    if action_id == "run_shortcut":
        return f"{label}: {config.get('shortcut_name', '')}"
    return label


def run_osascript(script, timeout=30):
    return subprocess.run(["osascript", "-e", script], check=True,
                          capture_output=True, text=True, timeout=timeout)


def wifi_device():
    result = subprocess.run(["networksetup", "-listallhardwareports"], check=True,
                            capture_output=True, text=True, timeout=10)
    blocks = re.split(r"\n\s*\n", result.stdout)
    for block in blocks:
        if re.search(r"Hardware Port:\s*(Wi-Fi|AirPort)", block, re.I):
            match = re.search(r"Device:\s*(\S+)", block)
            if match:
                return match.group(1)
    raise RuntimeError("Could not find the Mac's Wi-Fi interface.")


def quit_app(name):
    target = applescript_string(name)
    script = (
        f"tell application \"System Events\"\n"
        f"if exists (application process {target}) then\n"
        f"tell application {target} to quit\n"
        "end if\nend tell"
    )
    run_osascript(script)


def quit_all_apps():
    script = """
set skipApps to {"Finder", "System Events", "Dock", "loginwindow", "WindowManager"}
tell application "System Events" to set appNames to name of every application process whose background only is false
repeat with appRef in appNames
    set appName to contents of appRef
    if appName is not in skipApps then
        try
            tell application appName to quit
        end try
    end if
end repeat
"""
    run_osascript(script, timeout=120)


def run_shortcut(config):
    name = config.get("shortcut_name", "").strip()
    if not name:
        raise RuntimeError("No Shortcut name is saved. Open PanicStick setup first.")
    if not shutil.which("shortcuts"):
        raise RuntimeError("The macOS shortcuts command was not found.")
    subprocess.run(["shortcuts", "run", name], check=True,
                   capture_output=True, text=True, timeout=300)
    return "Shortcut completed."


def disable_ssh():
    command = "/usr/sbin/systemsetup -setremotelogin off"
    script = f'do shell script "{command}" with administrator privileges'
    run_osascript(script, timeout=120)


def execute_action(action, config):
    action_id = action["id"]
    if action_id == "notify":
        notify("PanicStick", "Your configured trigger was received.")
    elif action_id == "run_shortcut":
        output = run_shortcut(config)
        if output:
            logging.info("Shortcut result: %s", output[:500])
    elif action_id == "disable_wifi":
        subprocess.run(["networksetup", "-setairportpower", wifi_device(), "off"],
                       check=True, capture_output=True, text=True, timeout=30)
    elif action_id == "disable_bluetooth":
        if not shutil.which("blueutil"):
            raise RuntimeError("Bluetooth action needs blueutil. Install it first or uncheck this action.")
        subprocess.run(["blueutil", "--power", "0"], check=True, capture_output=True,
                       text=True, timeout=30)
    elif action_id == "disable_ssh":
        disable_ssh()
    elif action_id == "open_sharing_settings":
        subprocess.run(["open", "x-apple.systempreferences:com.apple.Sharing-Settings.extension"],
                       check=True, timeout=15)
    elif action_id == "quit_selected_apps":
        for name in config.get("selected_apps", []):
            quit_app(name)
    elif action_id == "quit_vm_apps":
        for name in config.get("vm_apps", []):
            quit_app(name)
    elif action_id == "quit_all_apps":
        quit_all_apps()
    elif action_id == "quit_terminal":
        quit_app("Terminal")
    elif action_id == "power_off":
        run_osascript('tell application "System Events" to shut down', timeout=60)
    else:
        raise RuntimeError(f"Unsupported action: {action_id}")


def handle_trigger(source, message, config):
    if source == "USB insertion" and not config.get("on_insertion", True):
        return
    if source == "button hold" and not config.get("on_button_hold", False):
        return
    event_id = message.get("event_id") or f"{source}-{time.time_ns()}"
    if not SEEN_TRIGGER_IDS.add(event_id):
        logging.info("Ignored a duplicate trigger event.")
        return

    if config.get("confirmation_mode", "before_run") == "before_run" and not ask_to_run(source, config):
        append_event({"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                      "event": "cancelled", "source": source, "event_id": event_id})
        logging.info("%s action run cancelled by user.", source)
        return

    record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event": "trigger",
        "source": source,
        "event_id": event_id,
        "hold_ms": message.get("hold_ms"),
        "actions": [item["id"] for item in config["actions"]],
    }
    append_event(record)

    ordered = ordered_actions(config["actions"], ACTION_ORDER)
    for action in ordered:
        if action["id"] in config.get("confirm_before", []):
            if not ask_action_checkpoint(action, config):
                append_event({"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                              "event": "checkpoint_cancelled", "source": source,
                              "event_id": event_id, "before_action": action["id"]})
                break
        try:
            execute_action(action, config)
            logging.info("Completed action: %s", action["id"])
        except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
            logging.error("Action %s failed: %s", action["id"], exc)
            notify("PanicStick action needs attention", f"{ACTION_LABELS.get(action['id'], action['id'])} failed.")
            # Do not continue a partially completed sequence after any failure.
            break


def pico_ports():
    found = {}
    for port in list_ports.comports():
        description = " ".join(filter(None, [port.description, port.product, port.manufacturer])).lower()
        if any(word in description for word in ("pico", "panicstick", "rp2", "micropython")):
            found[port.device] = port
        elif getattr(port, "vid", None) == 0x2E8A:
            # Raspberry Pi USB vendor; still require a per-run user confirmation before actions.
            found[port.device] = port
    return found


def read_device(port_name, config):
    try:
        with serial.Serial(port_name, baudrate=115200, timeout=1, write_timeout=1) as device:
            logging.info("Listening to %s.", port_name)
            while not STOP.is_set():
                raw = device.readline(4097)
                if not raw:
                    continue
                if len(raw) > MAX_LINE_BYTES or not raw.endswith(b"\n"):
                    logging.warning("Ignored an overlong or incomplete serial line from %s.", port_name)
                    continue
                try:
                    message = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    logging.warning("Ignored malformed serial data from %s.", port_name)
                    continue
                if not validate(message):
                    logging.warning("Ignored a message that did not match protocol v%d.", VERSION)
                    continue
                if message.get("event") == "hello":
                    logging.info("Pico online: %s.", message.get("device", "Pico"))
                elif message.get("event") == "trigger":
                    # Keep all confirmation dialogs on the main thread.
                    EVENTS.put(message)
    except (serial.SerialException, OSError) as exc:
        if not STOP.is_set():
            logging.info("Serial connection %s ended: %s", port_name, exc)


def monitor(config):
    initially_connected = pico_ports()
    known = set(initially_connected)
    for name in known:
        threading.Thread(target=read_device, args=(name, config), daemon=True).start()
    if known:
        logging.info("Pico already connected at startup; no insertion action will run. Unplug and reconnect to trigger it.")
    else:
        logging.info("Waiting for a Pico. USB insertion will ask before running configured actions.")

    while not STOP.is_set():
        current = pico_ports()
        connected = set(current)
        for name in connected - known:
            logging.info("Pico connected on %s.", name)
            threading.Thread(target=read_device, args=(name, config), daemon=True).start()
            handle_trigger("USB insertion", {"event_id": f"insert-{time.time_ns()}"}, config)
        known = connected
        while True:
            try:
                message = EVENTS.get_nowait()
            except queue.Empty:
                break
            handle_trigger("button hold", message, config)
        STOP.wait(0.25)


def doctor():
    """Print a read-only readiness check; never starts or runs an action."""
    try:
        import tkinter  # noqa: F401
        has_tk = True
    except ImportError:
        has_tk = False

    required = [
        ("macOS", sys.platform == "darwin"),
        ("Python 3.9 or newer", sys.version_info >= (3, 9)),
        ("Tk setup window", has_tk),
        ("pySerial", serial is not None),
    ]
    optional = [
        ("Pico connected", bool(pico_ports())),
        ("Shortcuts command", bool(shutil.which("shortcuts"))),
        ("blueutil for Bluetooth action", bool(shutil.which("blueutil"))),
    ]
    for label, ready in required:
        print("{}  {}".format("OK" if ready else "MISSING", label))
    for label, ready in optional:
        print("{}  {}".format("OK" if ready else "OPTIONAL", label))
    return 0 if all(ready for _, ready in required) else 1


def show_recent_log(limit=20):
    """Print a small tail of the local event log without changing it."""
    if not LOG_PATH.is_file():
        print("No PanicStick events have been logged yet.")
        return
    try:
        with LOG_PATH.open(encoding="utf-8") as stream:
            lines = stream.readlines()
    except OSError as exc:
        print(f"Could not read the PanicStick log: {exc}", file=sys.stderr)
        return
    print("".join(lines[-limit:]), end="")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--setup", action="store_true", help="open the visual setup screen")
    parser.add_argument("--doctor", action="store_true", help="check setup readiness without running actions")
    parser.add_argument("--show-log", action="store_true", help="show the latest 20 local event-log entries")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ensure_private_data_dir()
    if args.doctor:
        return doctor()
    if args.show_log:
        show_recent_log()
        return 0
    if args.setup:
        try:
            setup_wizard()
        except RuntimeError as exc:
            logging.error("%s", exc)
            raise SystemExit(1)
        return
    if not CONFIG_PATH.exists():
        logging.info("First run: opening PanicStick setup.")
        try:
            if not setup_wizard():
                save_config(dict(DEFAULT_CONFIG))
        except RuntimeError as exc:
            logging.error("%s", exc)
            raise SystemExit(1)
    config = load_config()
    try:
        monitor(config)
    except KeyboardInterrupt:
        STOP.set()
        logging.info("PanicStick listener stopped.")


if __name__ == "__main__":
    main()

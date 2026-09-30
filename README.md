# PanicStick

A Raspberry Pi Pico 2 (non-W) button device and macOS companion for a deliberate, physical emergency-response trigger.

> **Safety model:** Plugging the Pico into USB never runs a response. The firmware sends a trigger only after the button on GP14 has been held for two seconds. The Mac companion's default response is a local notification and an event-log entry. It does not change network settings, quit apps, hide files or windows, or shut down the Mac.

This is an initial prototype. Test with non-critical data and a spare Mac account before relying on it.

## Project layout

- `pico/main.py` — MicroPython firmware for Raspberry Pi Pico 2.
- `mac/panicstick.py` — macOS USB serial listener; Python 3 plus pySerial.
- `docs/protocol.md` — newline-delimited JSON protocol.
- `docs/testing.md` — bench and end-to-end test checklist.
- `requirements.txt` — host dependency.

## Hardware

- Raspberry Pi Pico 2 (non-W)
- Normally-open momentary pushbutton between **GP14** and **GND**
- Optional LED on GP25 (the onboard LED, if exposed by the installed MicroPython build)

The firmware enables the GPIO's internal pull-up. Do not connect the button to 3V3. No external power supply is needed when connected to USB.

## Install firmware

1. Install a Pico 2 compatible MicroPython UF2 from the official Raspberry Pi downloads page.
2. Hold **BOOTSEL** while connecting the Pico to USB, then copy the UF2 file to the mounted **RPI-RP2** drive. The Pico will reboot as a USB serial device.
3. In Thonny (or another MicroPython editor), select the Pico 2 interpreter and save `pico/main.py` to the device as `main.py`.
4. Wire the button from GP14 to GND. Open the serial REPL and confirm the device starts without errors.

At startup, the Pico announces a hello message. That message is informational only and cannot trigger a Mac action.

## Install and run the macOS companion

From the project directory:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python mac/panicstick.py
```

The listener attempts to select a connected USB serial device whose description or USB product name contains “Pico” or “PanicStick”. If it cannot decide safely, it prints the available ports; pass one explicitly:

```sh
python mac/panicstick.py --port /dev/cu.usbmodemXXXX
```

The app prints connection and trigger events, displays a macOS notification when available, and appends JSON Lines to `~/Library/Application Support/PanicStick/events.jsonl`. Use Ctrl-C to stop it. No launch agent or background persistence is installed.

## Trigger behavior

1. Connect the Pico. USB insertion only produces a hello message.
2. Hold the button for at least two seconds.
3. The LED flashes and the Pico emits one trigger event. Releasing the button rearms it.
4. The Mac listener checks the protocol version, event name, hold duration, and event identifier before recording the trigger.

A valid trigger only creates a local notification and log entry. This is reversible and does not interrupt work.

## Optional or future actions

This initial release deliberately does **not** disable networking, quit applications, hide desktop items/windows, or shut down the Mac. If these actions are added later, each must be disabled by default and require a clear, per-trigger macOS confirmation. Do not configure an automatic sequence that can lock you out of the computer or interrupt unsaved work.

Locking the screen is also not part of this first release. Keep your normal Mac security settings enabled.

## Troubleshooting

- **No serial port:** Check the USB cable supports data, reinstall Pico 2 MicroPython, and inspect the port list printed by the listener.
- **No trigger:** Check the button is between GP14 and GND, confirm `main.py` is running, and hold the button continuously for two seconds.
- **Listener reports invalid data:** Confirm the same protocol version is used by the firmware and host. See `docs/protocol.md`.
- **No notification:** Event logging still works. macOS may suppress notifications for the Python terminal host; check System Settings → Notifications or watch the terminal output.

## Development

See [docs/protocol.md](docs/protocol.md) and [docs/testing.md](docs/testing.md). The host listener can be tested with a serial loopback or a USB serial emulator before connecting the button.

## License

MIT. See [LICENSE](LICENSE).

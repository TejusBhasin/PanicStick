# Bench and end-to-end checks

Use a non-critical Mac account and save open work before testing. The listener's expected behavior is logging and notification only.

## Firmware bench check

1. Install the Pico 2 MicroPython firmware and copy `pico/main.py` to the board as `main.py`.
2. Open the REPL/serial output. Confirm one `hello` JSON line appears after startup.
3. Connect GP14 to GND briefly. Confirm no `trigger` line appears.
4. Hold GP14 to GND continuously for at least two seconds. Confirm exactly one `trigger` line with `hold_ms >= 2000`.
5. Keep holding. Confirm no second trigger appears.
6. Release and press again for two seconds. Confirm one new trigger appears.

## Host check

1. Install `requirements.txt` in a virtual environment.
2. Connect the Pico and run `python mac/panicstick.py`. If detection is ambiguous, rerun with `--port` and the serial path printed in the error.
3. Confirm connection produces a ready notification only.
4. Tap the button briefly. Confirm no trigger event is logged.
5. Hold for two seconds. Confirm one trigger notification and one JSON object in `~/Library/Application Support/PanicStick/events.jsonl`.
6. Confirm the Mac remains connected to the network, open apps remain open, and files/windows are unchanged.
7. Press Ctrl-C and reconnect. Confirm serial insertion by itself does not produce a trigger log record.

## Protocol validation

The listener rejects wrong protocol names/versions, unknown events, triggers shorter than two seconds, malformed JSON, oversized lines, and invalid event IDs. For bench testing without hardware, feed newline-terminated JSON messages into a USB serial emulator or a serial loopback pair.

Record the Pico model, MicroPython build, macOS version, and test results before demonstrating the prototype.

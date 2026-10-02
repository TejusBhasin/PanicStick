# Bench and end-to-end checks

Use a non-critical Mac account and save open work before testing. First test with notification-only selected.

## Firmware bench check

1. Install Pico 2 MicroPython. In Thonny, copy pico/button_monitor.py onto the board as button_monitor.py, then copy pico/main.py as main.py.
2. Open the serial REPL. Confirm one hello JSON line appears.
3. Connect GP14 to GND briefly. Confirm no trigger line appears.
4. Hold GP14 to GND continuously for at least two seconds. Confirm exactly one trigger line with hold_ms >= 2000.
5. Keep holding. Confirm no second trigger appears.
6. Release, then hold again for two seconds. Confirm one new trigger appears.

## Automated checks

From the repository folder, run `python3 -m unittest discover -v` and `python3 -m compileall -q mac pico tests`. On a Mac, also run `bash -n mac/install.command mac/uninstall.command`. The GitHub Actions workflow runs these checks on macOS and Ubuntu and keeps the test output in its run summary and downloadable artifact. These automated checks do not replace the physical Pico and Mac steps below.

## Mac setup and insertion check

1. Run mac/install.command, leave notification-only selected, and save settings.
2. Confirm the helper is running after installation.
3. Unplug the Pico, wait five seconds, and plug it back in.
4. Confirm the action confirmation appears. Choose No and verify no configured action runs.
5. Repeat and choose Run. Confirm only the selected notification/log action runs.
6. Confirm the event appears in ~/Library/Application Support/PanicStick/events.jsonl.
7. Restart the Mac with the Pico unplugged. Sign in, then plug it in. Confirm arrival is detected.
8. Start the helper with the Pico already connected. Confirm it does not run insertion actions at startup; unplug and reconnect to trigger.
9. If enabled, hold the button for two seconds and confirm the button-trigger flow.

## Action ordering and cancellation

On a test Mac with disposable apps and saved files:

1. Configure a harmless test Shortcut plus a later action such as Wi-Fi off.
2. Confirm the Shortcut completes before Wi-Fi changes.
3. Configure Terminal quit and a test Shortcut; confirm the Shortcut runs before Terminal is asked to quit.
4. Configure shutdown only after reviewing all options. Confirm two prompts appear and declining the second leaves the Mac on.
5. Simulate an unavailable selected tool (for example, remove blueutil) and confirm the run stops instead of continuing with later actions.
6. Restore connectivity and reopen apps manually after testing.

Do not test shutdown, Wi-Fi, Bluetooth, or app quitting while important work is open.

## Protocol validation

The listener rejects wrong protocol names/versions, unknown events, triggers shorter than two seconds, malformed JSON, overlong lines, and invalid event IDs. Test with a serial emulator or loopback before connecting a button.


## Read-only preview

After saving settings, run `panicstick.py --preview` to print the enabled triggers, confirmation mode, action order, and checkpoints. This command does not connect to the Pico or execute any action.

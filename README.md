# PanicStick

A physical button accessory for a Raspberry Pi Pico 2 (non-W) and a macOS companion.

The Mac companion can ask before running selected actions when the Pico is plugged in. A two-second physical button hold can be enabled as an additional trigger. **Plugging in the device never silently runs an action:** the Mac displays the configured action list and requires a click on **Run**; choosing **No** cancels it. Notification-only mode is the safe default.

> Prototype warning: some choices can close apps, disconnect the Mac, or shut it down. Read the action descriptions, keep your work saved, and test with notification-only mode first.

## Start here

If you are new to coding or hardware, follow the step-by-step [Beginner Install Guide](docs/install-for-beginners.md). It explains the Pico wiring, firmware setup, Mac setup, and first safe test without assuming Git knowledge.

## What is included

- pico/main.py: MicroPython firmware for the Pico 2.
- mac/panicstick.py: Mac companion, setup window, USB arrival monitor, action confirmation, and event log.
- mac/install.command and mac/uninstall.command: install or remove the per-user Mac login helper.
- docs/protocol.md: USB serial protocol.
- docs/testing.md: bench and end-to-end checklist.
- docs/install-for-beginners.md: beginner setup guide.

## Supported setup choices

- Show a notification.
- Quit all apps or named apps (apps may ask about unsaved work).
- Turn off Wi-Fi.
- Turn off Bluetooth when the optional blueutil utility is installed.
- Turn off incoming SSH / Remote Login (macOS administrator prompt).
- Open Sharing settings so you can turn off Screen Sharing manually.
- Quit named virtual-machine apps. This does not stop headless VMs.
- Run a named Shortcut from the Shortcuts app.
- Quit Terminal.
- Shut down the Mac.

Every configured set is shown in a confirmation window for each trigger. Shutdown gets an additional confirmation and always runs last. Shortcuts run before connectivity changes or apps close, so a later step cannot prevent the Shortcut from starting. If an action fails, remaining actions are skipped. Screen Sharing and headless virtual machines require manual steps or a user-created Shortcut; PanicStick does not claim it can reliably toggle those settings itself.

## Hardware

- Raspberry Pi Pico 2 (non-W)
- Normally-open momentary button between GP14 and GND
- USB data cable

The Pico's internal pull-up is used. Do not connect the button to 3V3.

## Open source and packaging

PanicStick is licensed under MIT (see [LICENSE](LICENSE)), and this repository is public so anyone can browse, fork, and contribute.

You do not need a package or release while developing. A GitHub ZIP plus the installer is enough for early testers. For a simple public release, publish a signed and notarized macOS app or installer package; signing requires an Apple Developer ID. This repository currently provides an install script and does not yet ship a signed app.

## Development

See the USB [protocol](docs/protocol.md) and [test checklist](docs/testing.md). Do not enable disruptive actions until the notification-only flow works on the actual Mac.

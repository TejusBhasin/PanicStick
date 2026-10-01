# PanicStick

A physical emergency-response button accessory built around a Raspberry Pi Pico 2 (non-W) and a macOS companion.

When the Pico is inserted, the Mac can show the configured action list and ask before running it. A two-second hold of the physical button is an optional second trigger. **USB insertion never silently runs actions:** the user must click **Run** in the Mac confirmation window. Notification-only is the safest first setup.

> Prototype warning: some optional choices can close apps, disconnect the Mac, or shut it down. Save your work and test notification-only first.

## Start here

If you are new to coding or hardware, follow the step-by-step [Beginner Install Guide](docs/install-for-beginners.md). It includes setup, testing, and recovery steps.

## What's included

- `pico/main.py`: MicroPython firmware for Pico 2.
- `mac/panicstick.py`: setup window, USB arrival monitor, confirmations, actions, and event log.
- `mac/install.command` / `mac/uninstall.command`: per-user Mac login helper installer and remover.
- `cad/panicstick_case.scad`: editable OpenSCAD enclosure design.
- `cad/printable/panicstick_base.stl` and `panicstick_lid.stl`: separate print-ready parts.
- `cad/fit_gauge.scad`: optional printer-clearance coupon.
- `cad/panicstick-dimensions.svg`: flat 2D case drawing, with no perspective or 3D rendering.
- `docs/cad-printing.md`: beginner printing and assembly guide; `docs/button-wiring.svg`: GP14 wiring picture.
- `docs/protocol.md`: USB protocol; `docs/testing.md`: bench and end-to-end checklist.

## Actions

The setup window lets you choose notifications, quit all apps or selected apps, Wi-Fi, Bluetooth (optional blueutil), incoming SSH/Remote Login, manual Sharing settings, named virtual-machine apps, a named Shortcuts app shortcut, Terminal, and power off.

Each triggered sequence asks the user to confirm. Shortcuts run before connectivity changes or apps close. Shutdown runs last and gets its own second confirmation. Screen Sharing and headless virtual machines require manual steps or a user-authored Shortcut. If an action fails, later actions are skipped.

## Hardware

- Raspberry Pi Pico 2 (non-W)
- Normally-open momentary switch between GP14 and GND
- USB Micro-B data cable to connect the Pico to the Mac
- Optional printed enclosure, four M2 × 8 mm screws

Do not connect the button to 3V3. The onboard pull-up is used. The enclosure is nominally 62 × 31 × 16.4 mm including the raised button guard. Its opening fits the Pico's Micro-USB-B connector; use a data-capable cable, not a charge-only cable. See the [flat 2D dimension drawing](cad/panicstick-dimensions.svg) and [print guide](docs/cad-printing.md).

## Open source and distribution

The entire project is openly available under the MIT License (see [LICENSE](LICENSE)). You can browse, download, modify, and fork the code and CAD files.

You do not need a package or release while developing or testing. A GitHub ZIP and the installer are enough for early testers. A tagged GitHub release is useful when you want to pin a stable version; a signed and notarized macOS app/package is a later convenience, not required to run the current prototype.

## Development

Read the [USB protocol](docs/protocol.md), [testing checklist](docs/testing.md), and [case printing guide](docs/cad-printing.md). Start with notification-only mode and confirm the full insert → review → Run/Cancel flow on your own Mac.

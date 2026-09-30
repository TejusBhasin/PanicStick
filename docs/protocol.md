# PanicStick USB protocol v1

Pico 2 USB CDC serial at 115200 baud. Each message is one UTF-8 JSON object followed by LF. The host ignores malformed, oversized, unsupported-version, and unknown-event messages. No host action is associated with opening a serial port or receiving a hello message.

## Messages from device to host

Startup announcement:

```json
{"protocol":"panicstick","version":1,"event":"hello","device":"Pico 2","firmware":"1.0.0","button_gpio":14}
```

One trigger is emitted only after a debounced GP14 press remains active for at least 2000 ms:

```json
{"protocol":"panicstick","version":1,"event":"trigger","hold_ms":2000,"event_id":"123456"}
```

On release after a trigger:

```json
{"protocol":"panicstick","version":1,"event":"released","hold_ms":2531}
```

The firmware emits at most one trigger per press. A stable release rearms it. `event_id` is unique within a device boot session and lets the host ignore duplicate trigger messages.

## Electrical behavior

GP14 uses the internal pull-up; wire a normally-open button between GP14 and GND. Pressed reads LOW. Firmware debounces for 35 ms and requires a two-second hold. The LED indicates a press and flashes when the trigger is emitted.

## Host behavior

The macOS listener validates protocol name, version, event type, hold duration, and event ID. It records accepted triggers in JSON Lines and shows an informational notification. No message executes a shell command, changes network configuration, closes applications, hides files/windows, or shuts down the Mac.

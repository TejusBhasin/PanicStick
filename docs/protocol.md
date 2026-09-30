# PanicStick USB protocol v1

The Pico sends UTF-8 JSON lines over USB CDC serial at 115200 baud. Each message ends with LF. The Mac companion ignores malformed, oversized, unsupported-version, and unknown-event messages.

USB connection is a separate host-side trigger configured in the Mac app. The firmware's startup hello is informational; it is never treated as a button press.

## Device messages

Startup announcement:

    {"protocol":"panicstick","version":1,"event":"hello","device":"Pico 2","firmware":"1.0.0","button_gpio":14}

After GP14 has remained pressed for at least 2000 ms:

    {"protocol":"panicstick","version":1,"event":"trigger","hold_ms":2000,"event_id":"123456"}

On release after a trigger:

    {"protocol":"panicstick","version":1,"event":"released","hold_ms":2531}

The firmware emits at most one trigger per press. A debounced release rearms the button. Event IDs are used to ignore duplicate trigger lines during a connection.

## Electrical behavior

GP14 uses the internal pull-up; wire a normally-open button between GP14 and GND. Pressed reads LOW. Firmware debounces for 35 ms and requires a two-second hold.

## Host behavior

The Mac companion can act on either a newly detected USB connection or a button-hold message, depending on the user's setup. A connection is matched using Pico/RP2 USB identification hints. At app startup, devices already attached are not treated as new insertions; unplug and reconnect to create a fresh arrival event.

For every configured action except a plain notification, the companion presents the action list and requires an affirmative confirmation. The power-off action asks a second time and is ordered last. If a step fails, later steps are skipped. The event log is stored locally in JSON Lines format.

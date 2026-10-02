# PanicStick USB protocol v1

The Pico 2 sends one UTF-8 JSON object per line over USB CDC serial at 115200 baud. Each line ends with LF. The Mac ignores malformed, oversized, unsupported-version, and unknown-event messages.

USB connection is a separate host-side trigger controlled by the user's setup. The Pico's startup hello is informational; it is never treated as a button press. The Mac still displays a confirmation before running a configured action list.

## Device messages

Startup announcement:

    {"protocol":"panicstick","version":1,"event":"hello","device":"Pico 2","firmware":"1.0.0","button_gpio":14}

After GP14 has remained pressed for at least 2000 ms:

    {"protocol":"panicstick","version":1,"event":"trigger","hold_ms":2000,"event_id":"123456"}

On release after a trigger:

    {"protocol":"panicstick","version":1,"event":"released","hold_ms":2531}

## Validation rules

- Protocol name and version must match exactly.
- A trigger hold must be an integer from 2000 through 60000 ms. Booleans are not accepted as integers.
- A trigger event ID must be 1–32 ASCII letters, digits, underscores, or hyphens.
- A hello device name is limited to 64 characters; firmware label to 32; button GPIO to 0–29.
- A release message must have a non-negative integer hold time.
- The USB listener reads at most 4096 bytes per line.
- Trigger IDs are held in a bounded FIFO cache, so repeats are ignored without allowing unbounded memory growth.

The firmware emits only one trigger per press. A debounced release rearms the button. The Mac host assigns its own event ID to an insertion event; it does not accept a USB hello as a trigger.

## Electrical behavior

GP14 uses the internal pull-up. Connect a normally-open momentary button between GP14 and GND; pressed reads LOW. The firmware debounces for 35 ms and requires a two-second hold. It continues polling while its LED gives feedback.

## Host behavior

The Mac companion identifies Pico/RP2 serial devices. At app startup, already-connected devices are not treated as fresh insertion events; unplug and reconnect to create a new arrival event.

The action review defaults to Cancel. The selected Shortcut runs before connectivity changes and app quitting. Shutdown requires a second confirmation and always runs last. A failed action stops the remaining sequence. The companion stores its JSON Lines event log locally in the user's PanicStick support folder.

# PanicStick firmware for Raspberry Pi Pico 2 (non-W), MicroPython.
# Button: GP14 to GND. The internal pull-up is enabled.
# USB insertion only sends "hello"; it never triggers an action.
import json
import sys
import time
from machine import Pin

BUTTON_GPIO = 14
LED_GPIO = 25
HOLD_MS = 2000
DEBOUNCE_MS = 35

button = Pin(BUTTON_GPIO, Pin.IN, Pin.PULL_UP)
try:
    led = Pin("LED", Pin.OUT)
except (TypeError, ValueError):
    # Pico 2 boards/builds that expose the onboard LED as GP25.
    led = Pin(LED_GPIO, Pin.OUT)


def emit(event, **fields):
    message = {"protocol": "panicstick", "version": 1, "event": event}
    message.update(fields)
    print(json.dumps(message), flush=True)


emit("hello", device="Pico 2", firmware="1.0.0", button_gpio=BUTTON_GPIO)

pressed_at = None
debounced_pressed = False
triggered = False
last_raw = button.value()
raw_changed_at = time.ticks_ms()

while True:
    now = time.ticks_ms()
    raw = button.value()

    if raw != last_raw:
        last_raw = raw
        raw_changed_at = now

    if time.ticks_diff(now, raw_changed_at) >= DEBOUNCE_MS:
        is_pressed = raw == 0
        if is_pressed and not debounced_pressed:
            debounced_pressed = True
            pressed_at = now
            triggered = False
            led.value(1)
        elif not is_pressed and debounced_pressed:
            debounced_pressed = False
            held_ms = time.ticks_diff(now, pressed_at) if pressed_at is not None else 0
            if triggered:
                emit("released", hold_ms=held_ms)
            pressed_at = None
            triggered = False
            led.value(0)

    if debounced_pressed and not triggered and pressed_at is not None:
        held_ms = time.ticks_diff(now, pressed_at)
        if held_ms >= HOLD_MS:
            triggered = True
            # Unique enough for de-duplication during one connection; regenerated on reboot.
            event_id = str(time.ticks_us())
            emit("trigger", hold_ms=held_ms, event_id=event_id)
            for _ in range(3):
                led.value(0)
                time.sleep_ms(80)
                led.value(1)
                time.sleep_ms(80)
            led.value(1)

    time.sleep_ms(5)

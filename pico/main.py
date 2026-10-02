# PanicStick firmware for Raspberry Pi Pico 2 (non-W), MicroPython.
# Button: GP14 to GND. The internal pull-up is enabled.
# USB insertion only sends "hello"; it never triggers an action.
import json
import sys
import time
from machine import Pin
from button_monitor import ButtonMonitor

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

monitor = ButtonMonitor(hold_ms=HOLD_MS, debounce_ms=DEBOUNCE_MS)
blink_until = None
blink_next = None
blink_on = False

while True:
    now = time.ticks_ms()
    event = monitor.update(button.value(), now, time.ticks_diff)
    if event and event[0] == "trigger":
        emit("trigger", hold_ms=event[1], event_id=str(time.ticks_us()))
        blink_until = time.ticks_add(now, 480)
        blink_next = now
        blink_on = False
    elif event and event[0] == "released":
        emit("released", hold_ms=event[1])

    if blink_until is not None and time.ticks_diff(now, blink_until) < 0:
        if time.ticks_diff(now, blink_next) >= 0:
            blink_on = not blink_on
            led.value(1 if blink_on else 0)
            blink_next = time.ticks_add(now, 80)
    else:
        blink_until = None
        led.value(1 if monitor.pressed else 0)

    time.sleep_ms(5)

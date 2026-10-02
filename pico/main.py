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
while True:
    event = monitor.update(button.value(), time.ticks_ms(), time.ticks_diff)
    if event and event[0] == "trigger":
        held_ms = event[1]
        event_id = str(time.ticks_us())
        emit("trigger", hold_ms=held_ms, event_id=event_id)
        for _ in range(3):
            led.value(0)
            time.sleep_ms(80)
            led.value(1)
            time.sleep_ms(80)
        led.value(1)
    elif event and event[0] == "released":
        led.value(0)
        emit("released", hold_ms=event[1])
    elif monitor.pressed:
        led.value(1)
    time.sleep_ms(5)

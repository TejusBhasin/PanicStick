"""Debounced, hold-to-trigger button state machine for MicroPython and CPython."""

class ButtonMonitor:
    def __init__(self, hold_ms=2000, debounce_ms=35):
        if hold_ms < 1 or debounce_ms < 1:
            raise ValueError("hold and debounce times must be positive")
        self.hold_ms = hold_ms
        self.debounce_ms = debounce_ms
        self.last_raw = 1
        self.raw_changed_at = 0
        self.pressed = False
        self.pressed_at = None
        self.triggered = False

    def update(self, raw_value, now_ms, ticks_diff):
        """Return (event_name, held_ms) when a stable state transition occurs."""
        raw_value = 1 if raw_value else 0
        if raw_value != self.last_raw:
            self.last_raw = raw_value
            self.raw_changed_at = now_ms
        if ticks_diff(now_ms, self.raw_changed_at) < self.debounce_ms:
            return None

        is_pressed = raw_value == 0
        if is_pressed and not self.pressed:
            self.pressed = True
            self.pressed_at = now_ms
            self.triggered = False
        elif not is_pressed and self.pressed:
            held_ms = ticks_diff(now_ms, self.pressed_at)
            self.pressed = False
            self.pressed_at = None
            was_triggered = self.triggered
            self.triggered = False
            if was_triggered:
                return ("released", held_ms)
            return None

        if self.pressed and not self.triggered:
            held_ms = ticks_diff(now_ms, self.pressed_at)
            if held_ms >= self.hold_ms:
                self.triggered = True
                return ("trigger", held_ms)
        return None

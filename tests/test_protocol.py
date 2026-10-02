import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mac"))
from panicstick_core import validate_message


def packet(event="trigger", **fields):
    return {"protocol": "panicstick", "version": 1, "event": event, **fields}


class ProtocolTests(unittest.TestCase):
    def test_valid_hold_trigger(self):
        self.assertTrue(validate_message(packet(hold_ms=2000, event_id="1234")))

    def test_rejects_short_hold(self):
        self.assertFalse(validate_message(packet(hold_ms=1999, event_id="1")))

    def test_rejects_unknown_version_event_and_bad_identifier(self):
        self.assertFalse(validate_message({**packet(hold_ms=2000, event_id="x"), "version": 2}))
        self.assertFalse(validate_message(packet("run-command", hold_ms=2000, event_id="x")))
        self.assertFalse(validate_message(packet(hold_ms=2000, event_id="../bad")))

    def test_rejects_bool_as_integer_and_unbounded_lines(self):
        self.assertFalse(validate_message(packet(hold_ms=True, event_id="x")))
        self.assertFalse(validate_message(packet(hold_ms=60001, event_id="x")))

    def test_hello_and_release_are_informational(self):
        self.assertTrue(validate_message(packet("hello", device="Pico 2", firmware="1.0.0", button_gpio=14)))
        self.assertTrue(validate_message(packet("released", hold_ms=2510)))
        self.assertFalse(validate_message(packet("hello", device="x" * 65)))

    def test_rejects_non_objects(self):
        for value in (None, [], "trigger", 3):
            self.assertFalse(validate_message(value))


if __name__ == "__main__":
    unittest.main()

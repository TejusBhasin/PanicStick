import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pico"))
from button_monitor import ButtonMonitor


def diff(now, before):
    return now - before


class ButtonMonitorTests(unittest.TestCase):
    def test_short_press_does_not_trigger(self):
        monitor = ButtonMonitor()
        monitor.update(0, 10, diff)
        monitor.update(0, 45, diff)
        monitor.update(1, 100, diff)
        monitor.update(1, 135, diff)
        self.assertFalse(monitor.triggered)

    def test_requires_stable_press_then_full_hold(self):
        monitor = ButtonMonitor()
        self.assertIsNone(monitor.update(0, 10, diff))
        self.assertIsNone(monitor.update(0, 44, diff))
        self.assertIsNone(monitor.update(0, 45, diff))
        self.assertIsNone(monitor.update(0, 2044, diff))
        self.assertEqual(monitor.update(0, 2045, diff), ("trigger", 2000))

    def test_emits_once_until_release_rearms(self):
        monitor = ButtonMonitor()
        monitor.update(0, 0, diff)
        monitor.update(0, 35, diff)
        self.assertEqual(monitor.update(0, 2035, diff), ("trigger", 2000))
        self.assertIsNone(monitor.update(0, 5000, diff))
        self.assertEqual(monitor.update(1, 5001, diff), ("released", 5001))
        monitor.update(1, 5036, diff)
        monitor.update(0, 5040, diff)
        monitor.update(0, 5075, diff)
        self.assertIsNone(monitor.update(0, 7074, diff))
        self.assertEqual(monitor.update(0, 7075, diff), ("trigger", 2000))

    def test_wrap_safe_tick_difference_is_supported(self):
        monitor = ButtonMonitor(hold_ms=20, debounce_ms=5)
        def wrap_diff(now, before):
            return (now - before) % 100
        monitor.update(0, 90, wrap_diff)
        monitor.update(0, 95, wrap_diff)
        self.assertIsNone(monitor.update(0, 9, wrap_diff))
        self.assertEqual(monitor.update(0, 15, wrap_diff), ("trigger", 20))


if __name__ == "__main__":
    unittest.main()

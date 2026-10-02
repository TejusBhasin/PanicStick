import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mac"))
from panicstick_core import ordered_actions

ORDER = {"notify": 0, "run_shortcut": 10, "disable_wifi": 30,
         "quit_terminal": 90, "power_off": 100}


class OrderingTests(unittest.TestCase):
    def test_shortcut_precedes_changes_and_shutdown_is_last(self):
        actions = [{"id": "power_off"}, {"id": "disable_wifi"},
                   {"id": "run_shortcut"}, {"id": "quit_terminal"}]
        self.assertEqual([item["id"] for item in ordered_actions(actions, ORDER)],
                         ["run_shortcut", "disable_wifi", "quit_terminal", "power_off"])

    def test_sort_is_stable_for_same_priority(self):
        actions = [{"id": "disable_wifi"}, {"id": "disable_wifi"}]
        self.assertEqual(ordered_actions(actions, ORDER), actions)


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mac"))
from panicstick_core import normalize_config

DEFAULTS = {
    "version": 1, "on_insertion": True, "on_button_hold": False,
    "actions": [{"id": "notify"}], "selected_apps": [], "vm_apps": [], "shortcut_name": "",
}
ALLOWED = {"notify", "run_shortcut", "power_off", "quit_selected_apps"}


class ConfigurationTests(unittest.TestCase):
    def test_returns_independent_safe_default_copy(self):
        first = normalize_config(DEFAULTS, DEFAULTS, ALLOWED)
        first["actions"].clear()
        self.assertEqual(DEFAULTS["actions"], [{"id": "notify"}])

    def test_rejects_non_objects_versions_and_unknown_actions(self):
        for value in ([], None, "settings"):
            with self.assertRaises(ValueError):
                normalize_config(value, DEFAULTS, ALLOWED)
        for value in ({**DEFAULTS, "version": 99},
                      {**DEFAULTS, "actions": [{"id": "shell"}]}):
            with self.assertRaises(ValueError):
                normalize_config(value, DEFAULTS, ALLOWED)

    def test_deduplicates_actions_and_app_names(self):
        config = {**DEFAULTS, "actions": [{"id": "notify"}, {"id": "notify"}],
                  "selected_apps": [" Safari ", "Safari"]}
        result = normalize_config(config, DEFAULTS, ALLOWED)
        self.assertEqual(result["actions"], [{"id": "notify"}])
        self.assertEqual(result["selected_apps"], ["Safari"])

    def test_rejects_wrong_types_and_control_characters(self):
        for config in ({**DEFAULTS, "on_insertion": 1},
                       {**DEFAULTS, "selected_apps": ["Mail\nInjected"]},
                       {**DEFAULTS, "vm_apps": ["x" * 121]},
                       {**DEFAULTS, "shortcut_name": 9}):
            with self.assertRaises(ValueError):
                normalize_config(config, DEFAULTS, ALLOWED)


if __name__ == "__main__":
    unittest.main()

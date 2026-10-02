import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mac"))
from panicstick_core import preview_workflow

ORDER = {"notify": 0, "run_shortcut": 10, "disable_wifi": 30,
         "quit_all_apps": 60, "power_off": 100}
LABELS = {"notify": "Notification", "run_shortcut": "Run Shortcut",
          "disable_wifi": "Turn Wi-Fi off", "quit_all_apps": "Quit all apps",
          "power_off": "Shut down Mac"}


class PreviewWorkflowTests(unittest.TestCase):
    def test_preview_reports_modes_triggers_order_and_checkpoints(self):
        config = {
            "confirmation_mode": "unattended", "on_insertion": True,
            "on_button_hold": False,
            "actions": [{"id": "power_off"}, {"id": "disable_wifi"}, {"id": "run_shortcut"}],
            "confirm_before": ["disable_wifi", "power_off"],
            "shortcut_name": "My Shortcut", "selected_apps": [], "vm_apps": [],
        }
        preview = preview_workflow(config, LABELS, ORDER)
        self.assertIn("Confirmation: unattended", preview)
        self.assertIn("Triggers: USB insertion", preview)
        self.assertLess(preview.index("My Shortcut"), preview.index("Turn Wi-Fi off"))
        self.assertLess(preview.index("Turn Wi-Fi off"), preview.index("Shut down Mac"))
        self.assertIn("Confirmation checkpoint immediately before this step", preview)
        self.assertTrue(preview.endswith("Preview only: no actions were run."))

    def test_preview_reports_no_enabled_trigger(self):
        config = {"confirmation_mode": "before_run", "on_insertion": False,
                  "on_button_hold": False, "actions": [{"id": "notify"}],
                  "confirm_before": [], "selected_apps": [], "vm_apps": [],
                  "shortcut_name": ""}
        self.assertIn("Triggers: none enabled", preview_workflow(config, LABELS, ORDER))


if __name__ == "__main__":
    unittest.main()

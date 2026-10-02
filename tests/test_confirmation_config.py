import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mac"))
from panicstick_core import normalize_config
DEFAULTS={"version":1,"confirmation_mode":"before_run","confirm_before":["power_off"],"on_insertion":True,"on_button_hold":False,"actions":[{"id":"notify"}],"selected_apps":[],"vm_apps":[],"shortcut_name":""}
ALLOWED={"notify","run_shortcut","power_off","quit_selected_apps","disable_wifi"}
class CheckpointConfigTests(unittest.TestCase):
 def test_modes_and_checkpoint(self):
  c={**DEFAULTS,"confirmation_mode":"unattended","actions":[{"id":"run_shortcut"},{"id":"disable_wifi"}],"confirm_before":["disable_wifi"]}
  out=normalize_config(c,DEFAULTS,ALLOWED)
  self.assertEqual(out["confirmation_mode"],"unattended")
  self.assertEqual(out["confirm_before"],["disable_wifi"])
 def test_unselected_checkpoint_removed(self):
  self.assertEqual(normalize_config(DEFAULTS,DEFAULTS,ALLOWED)["confirm_before"],[])
 def test_invalid_mode_or_checkpoint(self):
  for patch in ({"confirmation_mode":"x"},{"confirm_before":"disable_wifi"},{"confirm_before":["shell"]}):
   with self.assertRaises(ValueError): normalize_config({**DEFAULTS,**patch},DEFAULTS,ALLOWED)
if __name__=="__main__": unittest.main()

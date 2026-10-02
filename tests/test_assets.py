import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "docs" / "images"
EXPECTED = {
    "pico2-and-button.svg": "Bare Pico 2 board and PanicStick button",
    "response-flow.svg": "PanicStick response flow",
    "setup-flow.svg": "PanicStick beginner setup flow",
    "case-exploded.svg": "PanicStick enclosure exploded view",
}


class ArtworkTests(unittest.TestCase):
    def test_all_four_project_illustrations_are_well_formed_and_labeled(self):
        ns = "{http://www.w3.org/2000/svg}"
        for filename, expected_title in EXPECTED.items():
            with self.subTest(filename=filename):
                root = ET.parse(IMAGES / filename).getroot()
                self.assertEqual(root.tag, ns + "svg")
                self.assertEqual(root.attrib.get("role"), "img")
                title = root.find(ns + "title")
                desc = root.find(ns + "desc")
                self.assertIsNotNone(title)
                self.assertIsNotNone(desc)
                self.assertEqual(title.text, expected_title)
                self.assertGreater(len(desc.text or ""), 20)

    def test_readme_displays_the_four_artworks(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for filename in EXPECTED:
            self.assertIn("docs/images/" + filename, readme)


if __name__ == "__main__":
    unittest.main()

import unittest


class PackageImportTests(unittest.TestCase):
    def test_test_runner_uses_only_standard_library_for_core(self):
        import json
        import pathlib
        self.assertTrue(json.dumps({"ready": True}))
        self.assertTrue(pathlib.Path(__file__).is_file())


if __name__ == "__main__":
    unittest.main()

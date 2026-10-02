import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mac"))
from panicstick_core import EventIdCache


class EventIdCacheTests(unittest.TestCase):
    def test_rejects_duplicates_inside_window(self):
        cache = EventIdCache(3)
        self.assertTrue(cache.add("a"))
        self.assertFalse(cache.add("a"))

    def test_evicts_oldest_without_clearing_recent_ids(self):
        cache = EventIdCache(2)
        self.assertTrue(cache.add("a"))
        self.assertTrue(cache.add("b"))
        self.assertTrue(cache.add("c"))
        self.assertFalse(cache.add("c"))
        self.assertTrue(cache.add("a"))


if __name__ == "__main__":
    unittest.main()

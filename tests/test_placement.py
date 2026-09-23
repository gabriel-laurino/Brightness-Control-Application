import unittest

from PySide6.QtCore import QRect

from app.placement import safe_bottom, taskbar_rectangles


class PlacementTests(unittest.TestCase):
    def test_visible_bottom_taskbar(self):
        screen = QRect(0, 0, 3440, 1440)
        bar = QRect(0, 1392, 3440, 48)
        self.assertEqual(safe_bottom(screen, screen, [bar]), 1380)

    def test_auto_hide_taskbar_reserves_its_full_height(self):
        screen = QRect(0, 0, 3440, 1440)
        bar = QRect(0, 1438, 3440, 48)
        self.assertEqual(safe_bottom(screen, screen, [bar]), 1380)

    def test_unrelated_or_top_taskbar_does_not_reduce_bottom(self):
        screen = QRect(0, 0, 3440, 1440)
        bars = [QRect(3440, 1080, 1920, 48), QRect(0, 0, 3440, 48)]
        self.assertEqual(safe_bottom(screen, screen, bars), 1428)

    def test_real_taskbar_probe_returns_rectangles(self):
        self.assertTrue(taskbar_rectangles())


if __name__ == "__main__":
    unittest.main()

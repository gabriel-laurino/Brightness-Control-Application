"""Regression checks for the daily tray-popup behavior."""
import os
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QRect, Qt  # noqa: E402
from PySide6.QtGui import QCloseEvent  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from app.config import ConfigStore  # noqa: E402
from app.ui import MainWindow, SettingsDialog  # noqa: E402


class QuietTray:
    def geometry(self):
        return QRect()

    def showMessage(self, *_args):
        raise AssertionError("Closing the popup must never post a system notification")


class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setQuitOnLastWindowClosed(False)

    def test_live_popup_is_tool_window_and_closes_silently(self):
        config = Path(__file__).resolve().parents[1] / "data" / "config.json"
        with patch.object(MainWindow, "_create_tray", return_value=QuietTray()), \
             patch.object(MainWindow, "_refresh_monitors"):
            window = MainWindow(ConfigStore(config), Path("unused.ps1"), runner=None)
        try:
            self.assertTrue(window.windowFlags() & Qt.WindowType.Tool)
            event = QCloseEvent()
            window.closeEvent(event)
            self.assertFalse(event.isAccepted())
            self.assertTrue(window.isHidden())
        finally:
            window.clock.stop()
            window.monitor_timer.stop()
            window.executor.shutdown(wait=False, cancel_futures=True)

    def test_language_picker_switches_between_two_exclusive_choices(self):
        config = Path(__file__).resolve().parents[1] / "data" / "config.json"
        dialog = SettingsDialog(ConfigStore(config).load(), [], None)
        dialog.language_buttons["EN"].click()
        self.assertTrue(dialog.language_buttons["EN"].isChecked())
        self.assertFalse(dialog.language_buttons["PT"].isChecked())
        dialog._validate()
        self.assertEqual(dialog.language, "EN")


if __name__ == "__main__":
    unittest.main()

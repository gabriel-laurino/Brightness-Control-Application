"""Regression checks for the daily tray-popup behavior."""
import os
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QRect, Qt  # noqa: E402
from PySide6.QtGui import QCloseEvent  # noqa: E402
from PySide6.QtWidgets import QApplication, QSystemTrayIcon  # noqa: E402

from app.config import BrightnessConfig, ConfigStore  # noqa: E402
from app.ui import MainWindow, ScheduleHourInput, SettingsDialog  # noqa: E402


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

    def test_tray_clicks_queue_one_reopen_after_callback(self):
        config = Path(__file__).resolve().parents[1] / "data" / "config.json"
        with patch.object(MainWindow, "_create_tray", return_value=QuietTray()), \
             patch.object(MainWindow, "_refresh_monitors"):
            window = MainWindow(ConfigStore(config), Path("unused.ps1"), runner=None)
        try:
            with patch.object(window, "_show_from_tray") as reopen:
                window._on_tray_activated(QSystemTrayIcon.ActivationReason.Trigger)
                window._on_tray_activated(QSystemTrayIcon.ActivationReason.DoubleClick)
                self.assertEqual(reopen.call_count, 0)
                self.app.processEvents()
                reopen.assert_called_once_with()
        finally:
            window.clock.stop()
            window.monitor_timer.stop()
            window.executor.shutdown(wait=False, cancel_futures=True)

    def test_placement_failure_does_not_prevent_reopening(self):
        config = Path(__file__).resolve().parents[1] / "data" / "config.json"
        with patch.object(MainWindow, "_create_tray", return_value=QuietTray()), \
             patch.object(MainWindow, "_refresh_monitors"):
            window = MainWindow(ConfigStore(config), Path("unused.ps1"), runner=None)
        try:
            with patch.object(window, "_place_near_tray", side_effect=OSError("probe unavailable")), \
                 patch("app.ui.logging.exception"):
                window._show_from_tray()
            self.assertTrue(window.isVisible())
        finally:
            window.hide()
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
        self.assertEqual(dialog.starts, (6, 11, 17, 22))

    def test_english_editor_converts_am_pm_without_changing_stored_hours(self):
        for hour, expected_number, period in ((0, 12, "AM"), (6, 6, "AM"), (12, 12, "PM"), (17, 5, "PM"), (23, 11, "PM")):
            with self.subTest(hour=hour):
                editor = ScheduleHourInput(hour, "EN", "Test")
                self.assertEqual(editor.spin12.value(), expected_number)
                self.assertTrue(editor.meridiem_buttons[period].isChecked())
                self.assertEqual(editor.hour(), hour)
                editor.set_language("PT")
                self.assertEqual(editor.spin24.value(), hour)
                editor.set_language("EN")
                self.assertEqual(editor.hour(), hour)
        editor = ScheduleHourInput(0, "EN", "Test")
        editor.meridiem_buttons["PM"].click()
        self.assertEqual(editor.hour(), 12)
        editor.spin12.setValue(5)
        self.assertEqual(editor.hour(), 17)

    def test_english_popup_shows_am_pm_in_all_time_ranges(self):
        config_path = Path(__file__).resolve().parents[1] / "data" / "config.json"
        config = ConfigStore(config_path).load()
        english = BrightnessConfig("EN", config.levels, config.starts, config.raw)
        with patch.object(ConfigStore, "load", return_value=english), \
             patch.object(MainWindow, "_create_tray", return_value=QuietTray()), \
             patch.object(MainWindow, "_refresh_monitors"):
            window = MainWindow(ConfigStore(config_path), Path("unused.ps1"), runner=None)
        try:
            self.assertEqual(window.cards["B1"].time_label.text(), "6:00 AM — 11:00 AM")
            self.assertEqual(window.cards["B3"].time_label.text(), "5:00 PM — 10:00 PM")
            self.assertIn("AM", window.cards["B4"].time_label.text())
            self.assertIn("AM", window.current_period_label.text() + " ".join(card.time_label.text() for card in window.cards.values()))
            self.assertEqual(window.top_badge.text(), "●  ACTIVE")
            window._worker_status(False, "offline")
            self.assertEqual(window.top_badge.text(), "●  ERROR")
            window._worker_status(True, "")
            self.assertEqual(window.top_badge.text(), "●  ACTIVE")
        finally:
            window.clock.stop()
            window.monitor_timer.stop()
            window.executor.shutdown(wait=False, cancel_futures=True)


if __name__ == "__main__":
    unittest.main()

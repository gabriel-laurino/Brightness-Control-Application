import json
import tempfile
import unittest
from pathlib import Path

from app.config import BrightnessConfig, ConfigStore, format_hour


def sample():
    return {
        "Language": "PT",
        "BrightnessLevels": {"B1": 30, "B2": 50, "B3": 30, "B4": 60},
        "Schedule": {
            "MorningStart": 6, "MorningEnd": 11,
            "AfternoonStart": 11, "AfternoonEnd": 17,
            "EveningStart": 17, "EveningEnd": 22,
            "NightStart": 22, "NightEnd": 6,
        },
        "FutureSetting": {"preserved": True},
    }


class ConfigTests(unittest.TestCase):
    def test_localized_hour_boundaries_and_ranges(self):
        self.assertEqual(format_hour(0, "EN"), "12:00 AM")
        self.assertEqual(format_hour(11, "EN"), "11:00 AM")
        self.assertEqual(format_hour(12, "EN"), "12:00 PM")
        self.assertEqual(format_hour(17, "EN"), "5:00 PM")
        self.assertEqual(format_hour(23, "EN"), "11:00 PM")
        self.assertEqual(format_hour(0, "PT"), "00:00")
        config = BrightnessConfig.from_dict({**sample(), "Language": "EN"})
        self.assertEqual(config.time_range("B1"), "6:00 AM — 11:00 AM")
        self.assertEqual(config.time_range("B3"), "5:00 PM — 10:00 PM")
        self.assertEqual(config.time_range("B3", compact=True), "5 PM — 10 PM")
        self.assertEqual(config.time_range("B4"), "10:00 PM — 6:00 AM")
        self.assertEqual(config.as_dict()["Schedule"]["EveningStart"], 17)

    def test_every_hour_has_one_expected_period(self):
        config = BrightnessConfig.from_dict(sample())
        periods = [config.current_period(hour) for hour in range(24)]
        self.assertEqual(periods[:6], ["B4"] * 6)
        self.assertEqual(periods[6:11], ["B1"] * 5)
        self.assertEqual(periods[11:17], ["B2"] * 6)
        self.assertEqual(periods[17:22], ["B3"] * 5)
        self.assertEqual(periods[22:], ["B4"] * 2)

    def test_invalid_brightness_and_schedule_fail_closed(self):
        data = sample()
        data["BrightnessLevels"]["B3"] = 101
        with self.assertRaises(ValueError):
            BrightnessConfig.from_dict(data)
        data = sample()
        data["Schedule"]["AfternoonStart"] = 6
        with self.assertRaises(ValueError):
            BrightnessConfig.from_dict(data)
        data = sample()
        data["Schedule"]["NightEnd"] = 7
        with self.assertRaises(ValueError):
            BrightnessConfig.from_dict(data)

    def test_atomic_save_retains_rollback_and_unknown_fields(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            original = sample()
            path.write_text(json.dumps(original), encoding="utf-8")
            store = ConfigStore(path)
            config = store.load()
            config.levels["B4"] = 42
            store.save(config)
            self.assertEqual(store.load().levels["B4"], 42)
            self.assertEqual(store.load().as_dict()["FutureSetting"], {"preserved": True})
            self.assertEqual(json.loads(path.with_suffix(".json.bak").read_text(encoding="utf-8")), original)


if __name__ == "__main__":
    unittest.main()

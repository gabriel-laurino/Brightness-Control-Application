"""Validated, atomic persistence for the existing config.json format."""
from __future__ import annotations

import copy
import json
import os
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

PERIODS = ("B1", "B2", "B3", "B4")
START_KEYS = ("MorningStart", "AfternoonStart", "EveningStart", "NightStart")
END_KEYS = ("MorningEnd", "AfternoonEnd", "EveningEnd", "NightEnd")


def format_hour(hour: int, language: str, compact: bool = False) -> str:
    """Display a stored 24-hour schedule value in the selected language."""
    if not 0 <= hour <= 23:
        raise ValueError("Hour must be 0..23.")
    if language == "PT":
        return f"{hour:02d}:00"
    if language == "EN":
        return f"{hour % 12 or 12}{'' if compact else ':00'} {'AM' if hour < 12 else 'PM'}"
    raise ValueError("Language must be PT or EN.")


@dataclass
class BrightnessConfig:
    language: str
    levels: dict[str, int]
    starts: tuple[int, int, int, int]
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "BrightnessConfig":
        if not isinstance(data, dict):
            raise ValueError("Configuration must be a JSON object.")
        language = data.get("Language", "PT")
        if language not in ("PT", "EN"):
            raise ValueError("Language must be PT or EN.")
        levels_data = data.get("BrightnessLevels")
        schedule = data.get("Schedule")
        if not isinstance(levels_data, dict) or not isinstance(schedule, dict):
            raise ValueError("BrightnessLevels and Schedule are required objects.")
        levels = {}
        for key in PERIODS:
            value = levels_data.get(key)
            if type(value) is not int or not 0 <= value <= 100:
                raise ValueError(f"{key} must be an integer from 0 to 100.")
            levels[key] = value
        starts = []
        for key in START_KEYS:
            value = schedule.get(key)
            if type(value) is not int or not 0 <= value <= 23:
                raise ValueError(f"{key} must be an hour from 0 to 23.")
            starts.append(value)
        if starts != sorted(set(starts)):
            raise ValueError("The four periods must have unique, increasing start hours.")
        expected_ends = (starts[1], starts[2], starts[3], starts[0])
        for key, expected in zip(END_KEYS, expected_ends):
            if schedule.get(key) != expected:
                raise ValueError(f"{key} must match the next period's start hour.")
        return cls(language, levels, tuple(starts), copy.deepcopy(data))

    def as_dict(self) -> dict:
        data = copy.deepcopy(self.raw)
        data["Language"] = self.language
        data["BrightnessLevels"] = {**data.get("BrightnessLevels", {}), **self.levels}
        schedule = dict(data.get("Schedule", {}))
        for key, value in zip(START_KEYS, self.starts):
            schedule[key] = value
        for key, value in zip(END_KEYS, (*self.starts[1:], self.starts[0])):
            schedule[key] = value
        data["Schedule"] = schedule
        return data

    def current_period(self, hour: int) -> str:
        if not 0 <= hour <= 23:
            raise ValueError("Hour must be 0..23.")
        for index in range(3, -1, -1):
            if hour >= self.starts[index]:
                return PERIODS[index]
        return "B4"  # Night wraps over midnight.

    def time_range(self, key: str, compact: bool = False) -> str:
        index = PERIODS.index(key)
        end = self.starts[(index + 1) % 4]
        return f"{format_hour(self.starts[index], self.language, compact)} — {format_hour(end, self.language, compact)}"


class ConfigStore:
    def __init__(self, path: Path):
        self.path = Path(path)

    def load(self) -> BrightnessConfig:
        with self.path.open("r", encoding="utf-8") as stream:
            return BrightnessConfig.from_dict(json.load(stream))

    def save(self, config: BrightnessConfig) -> None:
        validated = BrightnessConfig.from_dict(config.as_dict())
        payload = json.dumps(validated.as_dict(), ensure_ascii=False, indent=4) + "\n"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", newline="\n", dir=self.path.parent,
                prefix=".config-", suffix=".tmp", delete=False,
            ) as stream:
                temp_name = stream.name
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            if self.path.exists():
                shutil.copy2(self.path, self.path.with_suffix(".json.bak"))
            os.replace(temp_name, self.path)
        finally:
            if temp_name and os.path.exists(temp_name):
                os.unlink(temp_name)

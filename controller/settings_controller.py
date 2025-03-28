# controllers/settings_controller.py

from tkinter import messagebox
from views.settings_view import SettingsView
from services.log_service import LogService


class SettingsController:
    def __init__(self, parent_window, config_manager, brightness_controller):
        self.log_service = LogService()
        self.config_manager = config_manager
        self.model = self.config_manager.load_config()
        self.language_code = self.model.get("Language", "EN")
        self.lang_strings = self.config_manager.load_language_strings(
            self.language_code
        )
        self.view = SettingsView(parent_window, self)
        self.view.set_controller(self)
        self.brightness_controller = brightness_controller
        self.log_service.log_info("SettingsController initialized.")

    def apply_settings(self, schedule, language_code):
        try:
            # Validate schedule
            if not self.validate_schedule(schedule):
                raise ValueError(
                    self.lang_strings.get(
                        "MSG_26",
                        "The defined times overlap or are in an invalid order.",
                    )
                )

            # Update model with new schedule and language
            self.log_service.log_info("Schedule validation passed.")
            self.model["Language"] = language_code
            self.model["Schedule"] = schedule

            self.config_manager.config["Language"] = language_code
            self.config_manager.config["Schedule"] = schedule

            self.config_manager.save_config()

            # Update the Brightness View and Settings View with the new configuration
            self.brightness_controller.update_brightness_view()
            self.view.close()
            self.log_service.log_info(
                "Brightness view updated with new schedule and brightness levels."
            )

        except ValueError as e:
            self.log_service.log_error(f"ValueError during settings application: {e}")
            error_message = str(e)
            messagebox.showerror(
                self.lang_strings.get("MSG_07", "Error"), error_message
            )

    def validate_schedule(self, schedule):
        self.log_service.log_debug("Validating the provided schedule.")
        # Validate that the time intervals do not overlap and are correctly ordered
        periods = [
            ("MorningStart", "MorningEnd"),
            ("AfternoonStart", "AfternoonEnd"),
            ("EveningStart", "EveningEnd"),
            ("NightStart", "NightEnd"),
        ]

        intervals = []
        wrap_around_count = 0

        for start, end in periods:
            if start not in schedule or end not in schedule:
                self.log_service.log_warning(
                    f"Schedule missing start or end for period: {start}, {end}"
                )
                return False
            start_time = schedule[start]
            end_time = schedule[end]

            if not (0 <= start_time <= 24) or not (0 <= end_time <= 24):
                self.log_service.log_warning(
                    f"Schedule times out of bounds for period: {start} - {end}"
                )
                return False

            if start_time < end_time:
                intervals.append((start_time, end_time))
            elif start_time > end_time:
                wrap_around_count += 1
                if wrap_around_count > 1:
                    self.log_service.log_warning(
                        "Multiple wrap-around periods detected."
                    )
                    return False
                intervals.append((start_time, 24))
                intervals.append((0, end_time))
            else:
                self.log_service.log_warning(
                    f"Start time equals end time for period: {start} - {end}"
                )
                return False

        if wrap_around_count > 1:
            self.log_service.log_warning("More than one wrap-around period detected.")
            return False

        intervals_sorted = sorted(intervals, key=lambda x: x[0])
        self.log_service.log_debug(f"Sorted intervals: {intervals_sorted}")

        for i in range(len(intervals_sorted) - 1):
            current_end = intervals_sorted[i][1]
            next_start = intervals_sorted[i + 1][0]
            if current_end > next_start:
                self.log_service.log_warning(
                    f"Overlap detected between intervals: {intervals_sorted[i]} and {intervals_sorted[i + 1]}"
                )
                return False

        self.log_service.log_info("Schedule validation passed.")
        return True

    def convert_to_24_hour(self, hour, ampm):
        self.log_service.log_debug(f"Converting {hour} {ampm} to 24-hour format.")
        if ampm.upper() == "AM":
            if hour == 12:
                return 0
            else:
                return hour
        elif ampm.upper() == "PM":
            if hour == 12:
                return 12
            else:
                return hour + 12
        else:
            self.log_service.log_error(f"Invalid AM/PM specifier: {ampm}")
            return hour

    def convert_to_12_hour(self, hour_24):
        self.log_service.log_debug(
            f"Converting {hour_24} from 24-hour to 12-hour format."
        )
        if hour_24 == 0:
            return 12, "AM"
        elif 1 <= hour_24 <= 11:
            return hour_24, "AM"
        elif hour_24 == 12:
            return 12, "PM"
        elif 13 <= hour_24 <= 23:
            return hour_24 - 12, "PM"
        else:
            self.log_service.log_error(f"Invalid hour value: {hour_24}")
            return hour_24, "AM"

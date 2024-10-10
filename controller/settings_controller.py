# controller/settings_controller.py

import logging
from views.settings_view import SettingsView
from tkinter import messagebox

class SettingsController:
    def __init__(self, parent_window, config_manager):
        # Load configuration and set language before creating the view
        self.config_manager = config_manager
        self.model = config_manager.config
        self.language_code = self.model.get("Language", "EN")
        self.lang_strings = config_manager.load_language_strings(self.language_code)
        
        # Instantiate the view with the already configured controller
        self.view = SettingsView(parent_window, self)
        self.view.set_controller(self)
        
        logging.info("SettingsController initialized.")

    def apply_settings(self, schedule, language_code):
        try:
            logging.info("Applying settings with schedule and language code.")
            # Validate the data
            if not self.validate_schedule(schedule):
                raise ValueError("The defined times overlap or are in an invalid order.")

            # Update the model
            self.model["Schedule"] = schedule
            self.model["Language"] = language_code
            self.config_manager.save_config()
            logging.info("Configuration model updated with new schedule and language.")

            # Update the language strings
            self.lang_strings = self.config_manager.load_language_strings(language_code)
            logging.info("Language strings reloaded based on the new language code.")

            # Update the view and close the settings window
            self.view.close()
            logging.info("Settings view closed after applying settings.")

        except ValueError as e:
            error_message = str(e)
            logging.error(f"Error applying settings: {error_message}")
            if "integers" in error_message.lower():
                error_text = self.lang_strings.get("MSG_06", "All values must be integers!")
            else:
                error_text = error_message
            messagebox.showerror(
                self.lang_strings.get("MSG_07", "Error"),
                error_text
            )

    def validate_schedule(self, schedule):
        logging.debug("Validating the provided schedule.")
        # Validate that the time intervals do not overlap and are correctly ordered
        periods = [
            ("MorningStart", "MorningEnd"),
            ("AfternoonStart", "AfternoonEnd"),
            ("EveningStart", "EveningEnd"),
            ("NightStart", "NightEnd")
        ]

        intervals = []
        wrap_around_count = 0

        for start, end in periods:
            if start not in schedule or end not in schedule:
                logging.warning(f"Schedule missing start or end for period: {start}, {end}")
                return False
            start_time = schedule[start]
            end_time = schedule[end]

            if not (0 <= start_time <= 24) or not (0 <= end_time <= 24):
                logging.warning(f"Schedule times out of bounds for period: {start} - {end}")
                return False

            if start_time < end_time:
                intervals.append((start_time, end_time))
            elif start_time > end_time:
                wrap_around_count += 1
                if wrap_around_count > 1:
                    logging.warning("Multiple wrap-around periods detected.")
                    return False
                intervals.append((start_time, 24))
                intervals.append((0, end_time))
            else:
                logging.warning(f"Start time equals end time for period: {start} - {end}")
                return False

        if wrap_around_count > 1:
            logging.warning("More than one wrap-around period detected.")
            return False

        intervals_sorted = sorted(intervals, key=lambda x: x[0])
        logging.debug(f"Sorted intervals: {intervals_sorted}")

        for i in range(len(intervals_sorted) - 1):
            current_end = intervals_sorted[i][1]
            next_start = intervals_sorted[i + 1][0]
            if current_end > next_start:
                logging.warning(f"Overlap detected between intervals: {intervals_sorted[i]} and {intervals_sorted[i + 1]}")
                return False

        logging.info("Schedule validation passed.")
        return True

    def convert_to_24_hour(self, hour, ampm):
        logging.debug(f"Converting {hour} {ampm} to 24-hour format.")
        # Convert 12-hour format to 24-hour format
        if ampm.upper() == 'AM':
            if hour == 12:
                return 0
            else:
                return hour
        elif ampm.upper() == 'PM':
            if hour == 12:
                return 12
            else:
                return hour + 12
        else:
            logging.error(f"Invalid AM/PM specifier: {ampm}")
            return hour

    def convert_to_12_hour(self, hour_24):
        logging.debug(f"Converting {hour_24} from 24-hour to 12-hour format.")
        # Convert 24-hour format to 12-hour format
        if hour_24 == 0:
            return 12, 'AM'
        elif 1 <= hour_24 <= 11:
            return hour_24, 'AM'
        elif hour_24 == 12:
            return 12, 'PM'
        elif 13 <= hour_24 <= 23:
            return hour_24 - 12, 'PM'
        else:
            logging.error(f"Invalid hour value: {hour_24}")
            return hour_24, 'AM'

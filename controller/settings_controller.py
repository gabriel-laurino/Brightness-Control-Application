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

    def apply_settings(self, schedule, language_code):
        try:
            # Validate the data
            if not self.validate_schedule(schedule):
                raise ValueError("The defined times overlap or are in an invalid order.")

            # Update the model
            self.model["Schedule"] = schedule
            self.model["Language"] = language_code
            self.config_manager.save_config()

            # Update the language strings
            self.lang_strings = self.config_manager.load_language_strings(language_code)

            # Update the view and close the settings window
            self.view.close()

        except ValueError as e:
            error_message = str(e)
            if "inteiros" in error_message.lower() or "integers" in error_message.lower():
                error_text = self.lang_strings.get("MSG_06", "All values must be integers!")
            else:
                error_text = error_message
            messagebox.showerror(
                self.lang_strings.get("MSG_07", "Error"),
                error_text
            )

    def validate_schedule(self, schedule):
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
                return False
            start_time = schedule[start]
            end_time = schedule[end]

            if not (0 <= start_time <= 24) or not (0 <= end_time <= 24):
                return False

            if start_time < end_time:
                intervals.append((start_time, end_time))
            elif start_time > end_time:
                wrap_around_count += 1
                if wrap_around_count > 1:
                    return False
                intervals.append((start_time, 24))
                intervals.append((0, end_time))
            else:
                return False

        if wrap_around_count > 1:
            return False

        intervals_sorted = sorted(intervals, key=lambda x: x[0])

        for i in range(len(intervals_sorted) - 1):
            current_end = intervals_sorted[i][1]
            next_start = intervals_sorted[i + 1][0]
            if current_end > next_start:
                return False

        return True

    def convert_to_24_hour(self, hour, ampm):
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
            return hour

    def convert_to_12_hour(self, hour_24):
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
            return hour_24, 'AM'
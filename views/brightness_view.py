import tkinter as tk
from views.view_helper import ViewHelper
from model.data_model import ConfigManager

config_manager = ConfigManager()

class BrightnessView:
    def __init__(self, lang_strings, window):
        self.window = window
        self.helper = ViewHelper(self.window)
        self.entries = {}
        self.success_label = None
        self.lang_strings = lang_strings
        self.widgets_to_update = {}

        # Set up the window
        self.helper.setup_window(width=320, height=300, bg_color="#2E2E2E")

    def create_widgets(self, brightness_levels):
        self.create_title()
        self.create_separator()
        self.create_brightness_inputs(brightness_levels)
        self.create_buttons()

    def create_title(self):
        # Create title label
        self.title_label = self.helper.create_label(
            text=self.lang_strings.get("MSG_04", "Brightness Settings"),
            x=20,
            y=10,
            font=("Segoe UI", 14, "bold"),
            bg="#2E2E2E",
            fg="white"
        )
        self.widgets_to_update['title_label'] = self.title_label

    def create_separator(self):
        # Create a separator
        self.helper.create_separator(x=20, y=50, width=280, height=2, bg="#444444")

    def create_brightness_inputs(self, brightness_levels):
        # Load the current configuration to get time schedules
        config = config_manager.load_config()
        schedule = config.get("Schedule", {})

        # Define brightness periods with time schedules
        periods = [
            {
                "label_key": "MSG_20",
                "default_name": "Morning",
                "key": "B1",
                "start_key": "MorningStart",
                "end_key": "MorningEnd",
                "y_pos": 60
            },
            {
                "label_key": "MSG_21",
                "default_name": "Afternoon",
                "key": "B2",
                "start_key": "AfternoonStart",
                "end_key": "AfternoonEnd",
                "y_pos": 100
            },
            {
                "label_key": "MSG_22",
                "default_name": "Evening",
                "key": "B3",
                "start_key": "EveningStart",
                "end_key": "EveningEnd",
                "y_pos": 140
            },
            {
                "label_key": "MSG_23",
                "default_name": "Night",
                "key": "B4",
                "start_key": "NightStart",
                "end_key": "NightEnd",
                "y_pos": 180
            },
        ]

        for period in periods:
            self.create_brightness_input(period, brightness_levels, schedule)

    def create_brightness_input(self, period, brightness_levels, schedule):
        # Set period name and time range
        period_name = self.lang_strings.get(period["label_key"], period["default_name"])
        start_time = schedule.get(period["start_key"], "")
        end_time = schedule.get(period["end_key"], "")

        if self.lang_strings.get("Language", "EN") == "EN":
            # Convert to 12-hour format with AM/PM
            start_hour_12, start_ampm = self.convert_to_12_hour_format(start_time)
            end_hour_12, end_ampm = self.convert_to_12_hour_format(end_time)

            if start_hour_12 and end_hour_12:
                label_text = f"{period_name} ({start_hour_12} {start_ampm} - {end_hour_12} {end_ampm}):"
            else:
                label_text = f"{period_name} ():"
        else:
            # Keep in 24-hour format
            label_text = f"{period_name} ({start_time}h - {end_time}h):"

        # Create label and input for brightness level
        label_widget = self.helper.create_label(
            text=label_text,
            x=40,
            y=period["y_pos"],
            font=("Segoe UI", 10),
            bg="#2E2E2E",
            fg="white"
        )
        self.widgets_to_update[f'label_{period["key"]}'] = label_widget

        entry = self.helper.create_entry(
            x=220,
            y=period["y_pos"],
            initial_value=brightness_levels.get(period["key"], "")
        )
        self.entries[period["key"]] = entry

    def create_buttons(self):
        # Create Apply button
        self.apply_button = self.helper.create_apply_button(
            text=self.lang_strings.get("MSG_08", "Apply")
        )
        self.apply_button.place(x=100, y=230)
        self.widgets_to_update['apply_button'] = self.apply_button

        # Create Minimize button
        self.minimize_button = self.helper.create_rounded_button(
            text="-",
            width=25,
            height=25,
            bg_color="#555555",
            fg_color="white",
            font=("Segoe UI", 12, "bold")
        )
        self.minimize_button.place(x=250, y=10)
        self.widgets_to_update['minimize_button'] = self.minimize_button

        # Create Close button
        self.close_button = self.helper.create_rounded_button(
            text="X",
            width=25,
            height=25,
            bg_color="#555555",
            fg_color="white",
            font=("Segoe UI", 12, "bold")
        )
        self.close_button.place(x=285, y=10)
        self.widgets_to_update['close_button'] = self.close_button

        # Create Settings button
        self.settings_button = self.helper.create_rounded_button(
            text="⚙",
            width=25,
            height=25,
            bg_color="#555555",
            fg_color="white",
            font=("Segoe UI", 12)
        )
        self.settings_button.place(x=215, y=10)
        self.widgets_to_update['settings_button'] = self.settings_button

    def update_language(self):
        # Load updated language strings
        config = config_manager.load_config()
        self.lang_strings = ConfigManager().load_language_strings(config.get("Language", "EN"))

        # Update title label
        self.widgets_to_update['title_label'].config(
            text=self.lang_strings.get("MSG_04", "Brightness Settings")
        )

        # Update brightness level labels
        schedule = config.get("Schedule", {})
        periods = [
            {
                "key": "B1",
                "label_key": "MSG_20",
                "default_name": "Morning",
                "start_key": "MorningStart",
                "end_key": "MorningEnd"
            },
            {
                "key": "B2",
                "label_key": "MSG_21",
                "default_name": "Afternoon",
                "start_key": "AfternoonStart",
                "end_key": "AfternoonEnd"
            },
            {
                "key": "B3",
                "label_key": "MSG_22",
                "default_name": "Evening",
                "start_key": "EveningStart",
                "end_key": "EveningEnd"
            },
            {
                "key": "B4",
                "label_key": "MSG_23",
                "default_name": "Night",
                "start_key": "NightStart",
                "end_key": "NightEnd"
            },
        ]

        for period in periods:
            period_name = self.lang_strings.get(period["label_key"], period["default_name"])
            start_time = schedule.get(period["start_key"], "")
            end_time = schedule.get(period["end_key"], "")

            if self.lang_strings.get("Language", "EN") == "EN":
                # Convert to 12-hour format
                start_hour_12, start_ampm = self.convert_to_12_hour_format(start_time)
                end_hour_12, end_ampm = self.convert_to_12_hour_format(end_time)

                if start_hour_12 and end_hour_12:
                    label_text = f"{period_name} ({start_hour_12} {start_ampm} - {end_hour_12} {end_ampm}):"
                else:
                    label_text = f"{period_name} ():"
            else:
                # Keep in 24-hour format
                label_text = f"{period_name} ({start_time}h - {end_time}h):"

            self.widgets_to_update[f'label_{period["key"]}'].config(text=label_text)

        # Update Apply button text
        try:
            self.apply_button.itemconfig(self.apply_button.text_id, text=self.lang_strings.get("MSG_08", "Apply"))
        except AttributeError:
            self.apply_button.config(text=self.lang_strings.get("MSG_08", "Apply"))

    def show_success_message(self):
        # Show success message for saving settings
        if self.success_label:
            self.success_label.destroy()

        self.success_label = self.helper.create_label(
            text=self.lang_strings.get("MSG_10", "Success! Settings saved."),
            x=20,
            y=270,
            font=("Segoe UI", 10, "bold"),
            bg="#2E2E2E",
            fg="#32CD32"
        )

        self.window.after(3000, self.success_label.destroy)

    def withdraw_window(self):
        self.window.withdraw()

    def deiconify_window(self):
        self.window.deiconify()

    def mainloop(self):
        self.window.mainloop()

    def convert_to_12_hour_format(self, hour_24):
        # Convert 24-hour format to 12-hour format
        if hour_24 is None:
            return "", ""
        
        try:
            hour = int(hour_24)
        except (ValueError, TypeError):
            return "", ""

        if hour == 0:
            return 12, 'AM'
        elif 1 <= hour < 12:
            return hour, 'AM'
        elif hour == 12:
            return 12, 'PM'
        elif 13 <= hour < 24:
            return hour - 12, 'PM'
        else:
            return hour, 'AM'

# views/settings_view.py

import tkinter as tk
from views.view_helper import ViewHelper
from tkinter import messagebox


class Tooltip:
    def __init__(self, widget, text="widget info"):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove window decorations
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#FFFFE0",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 10),
        )
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw:
            tw.destroy()


class SettingsView:
    def __init__(self, parent_window, controller):
        self.controller = controller
        self.window = tk.Toplevel(parent_window)
        self.helper = ViewHelper(self.window)
        self.entries = {}
        self.parent_window = parent_window

        # Variable to store the selected language code
        self.language_var = tk.StringVar(value=self.controller.language_code)

        # Register the validation function with %P (proposed value) and %W (widget name)
        self.vcmd = (self.window.register(self.validate_time_input), "%P", "%W")

        # Window configuration
        self.helper.setup_window(width=470, height=400, bg_color="#2E2E2E")

        # Create widgets
        self.create_widgets()

    def set_controller(self, controller):
        self.controller = controller

    def validate_time_input(self, proposed_value, widget_name):

        widget = self.window.nametowidget(widget_name)

        if proposed_value == "":
            widget.config(bg="#3A3A3A")  # Default color
            if hasattr(widget, "tooltip"):
                widget.tooltip.hide_tooltip()
            return True

        try:
            value = int(proposed_value)
        except ValueError:
            widget.config(bg="#FFCCCC")  # Error color
            if not hasattr(widget, "tooltip"):
                widget.tooltip = Tooltip(widget, "Please enter a valid integer.")
            return False

        language_code = self.language_var.get()

        if language_code == "EN":
            is_valid = 0 <= value <= 12
        elif language_code == "PT":
            is_valid = 0 <= value <= 24
        else:
            is_valid = False

        if is_valid:
            widget.config(bg="#3A3A3A")  # Default color
            if hasattr(widget, "tooltip"):
                widget.tooltip.hide_tooltip()
        else:
            widget.config(bg="#FFCCCC")  # Error color
            if not hasattr(widget, "tooltip"):
                if language_code == "EN":
                    error_msg = "Please enter a value between 0 and 12."
                else:
                    error_msg = "Please enter a value between 0 and 24."
                widget.tooltip = Tooltip(widget, error_msg)

        return is_valid

    def create_widgets(self):
        # Title
        self.title_label = self.helper.create_label(
            text=self.controller.lang_strings.get("MSG_15", "Time Settings"),
            x=20,
            y=10,
            font=("Segoe UI", 14, "bold"),
            bg="#2E2E2E",
            fg="white",
        )

        # Separator
        self.helper.create_separator(x=20, y=50, width=430, height=2, bg="#444444")

        # Available languages list
        languages = [("EN", "English"), ("PT", "Português")]

        # Map code to name and name to code
        self.code_to_name = {code: name for code, name in languages}
        self.name_to_code = {name: code for code, name in languages}

        # Add language selection
        self.language_label = self.helper.create_label(
            text=self.controller.lang_strings.get("MSG_24", "Language:"),
            x=20,
            y=250,
            font=("Segoe UI", 10),
            bg="#2E2E2E",
            fg="white",
        )

        # Create custom buttons for language selection
        x_position = 100
        self.language_buttons = {}
        for lang_code, lang_name in languages:
            button = self.helper.create_rounded_button(
                text=lang_name,
                width=100,
                height=30,
                bg_color="#3A3A3A",
                fg_color="white",
                font=("Segoe UI", 10),
            )
            button.place(x=x_position, y=250)
            # Bind the button with the language code
            button.bind(
                "<Button-1>", lambda event, code=lang_code: self.select_language(code)
            )
            self.language_buttons[lang_code] = button  # Store the button with its code
            x_position += 120

        # Highlight the selected language button
        self.highlight_selected_language()

        # Set time settings
        self.settings = [
            {
                "label": self.controller.lang_strings.get(
                    "MSG_16", "Morning (Start - End):"
                ),
                "msg_id": "MSG_16",
                "default_label": "Morning (Start - End):",
                "start_key": "MorningStart",
                "end_key": "MorningEnd",
                "y_pos": 70,
            },
            {
                "label": self.controller.lang_strings.get(
                    "MSG_17", "Afternoon (Start - End):"
                ),
                "msg_id": "MSG_17",
                "default_label": "Afternoon (Start - End):",
                "start_key": "AfternoonStart",
                "end_key": "AfternoonEnd",
                "y_pos": 110,
            },
            {
                "label": self.controller.lang_strings.get(
                    "MSG_18", "Evening (Start - End):"
                ),
                "msg_id": "MSG_18",
                "default_label": "Evening (Start - End):",
                "start_key": "EveningStart",
                "end_key": "EveningEnd",
                "y_pos": 150,
            },
            {
                "label": self.controller.lang_strings.get(
                    "MSG_19", "Night (Start - End):"
                ),
                "msg_id": "MSG_19",
                "default_label": "Night (Start - End):",
                "start_key": "NightStart",
                "end_key": "NightEnd",
                "y_pos": 190,
            },
        ]

        self.time_labels = []
        self.create_time_inputs()

        # Apply button
        self.apply_button = self.helper.create_apply_button(
            text=self.controller.lang_strings.get("MSG_08", "Apply")
        )
        self.apply_button.place(x=175, y=330)
        self.apply_button.bind("<Button-1>", self.on_apply)

        # Close Button
        self.close_button = self.helper.create_rounded_button(
            text="X",
            width=25,
            height=25,
            bg_color="#555555",
            fg_color="white",
            font=("Segoe UI", 12, "bold"),
        )
        self.close_button.place(x=435, y=10)  # Adjust position to the new width
        self.close_button.bind("<Button-1>", lambda event: self.close())

    def on_apply(self, event):
        schedule = {}
        language_code = self.language_var.get()

        for setting in self.settings:
            start_key = setting["start_key"]
            end_key = setting["end_key"]

            start_time_str = self.entries[start_key].get()
            end_time_str = self.entries[end_key].get()

            if start_time_str == "" or end_time_str == "":
                messagebox.showerror(
                    self.controller.lang_strings.get("MSG_07", "Error"),
                    self.controller.lang_strings.get(
                        "MSG_06", "All values must be integers!"
                    ),
                )
                return

            try:
                start_time = int(start_time_str)
                end_time = int(end_time_str)
            except ValueError:
                messagebox.showerror(
                    self.controller.lang_strings.get("MSG_07", "Error"),
                    self.controller.lang_strings.get(
                        "MSG_06", "All values must be integers!"
                    ),
                )
                return

            if language_code == "EN":
                # Get AM/PM from buttons
                start_ampm = self.entries[start_key + "_ampm"].get()
                end_ampm = self.entries[end_key + "_ampm"].get()
                # Delegate conversion to the Controller
                start_time_24 = self.controller.convert_to_24_hour(
                    start_time, start_ampm
                )
                end_time_24 = self.controller.convert_to_24_hour(end_time, end_ampm)
            else:
                # Assume 24-hour format
                start_time_24 = start_time
                end_time_24 = end_time

            schedule[start_key] = start_time_24
            schedule[end_key] = end_time_24

        # Delegate applying settings to the Controller
        self.controller.apply_settings(schedule, language_code)

    def create_time_inputs(self):
        # Destroy existing time widgets if any
        if hasattr(self, "time_input_widgets"):
            for widget in self.time_input_widgets:
                widget.destroy()
        self.time_input_widgets = []
        self.entries = {}
        self.time_labels = []

        # Get the current language
        selected_language_code = self.language_var.get()

        # Load current settings
        schedule = self.controller.model.get("Schedule", {})

        # Define constants for button width and padding
        BUTTON_WIDTH = 36
        BUTTON_HEIGHT = 30
        BUTTON_PADDING = 10

        # Create time fields
        for setting in self.settings:
            y_pos = setting["y_pos"]
            # Update label text if language has changed
            label_text = self.controller.lang_strings.get(
                setting["msg_id"], setting["default_label"]
            )
            label_widget = self.helper.create_label(
                text=label_text,
                x=20,
                y=y_pos,
                font=("Segoe UI", 10),
                bg="#2E2E2E",
                fg="white",
            )
            self.time_labels.append(label_widget)
            self.time_input_widgets.append(label_widget)

            if selected_language_code == "EN":
                # Get stored times and convert to 12-hour format
                start_time_24 = schedule.get(setting["start_key"], "")
                end_time_24 = schedule.get(setting["end_key"], "")

                if start_time_24 != "":
                    start_time_12, start_ampm = self.controller.convert_to_12_hour(
                        start_time_24
                    )
                else:
                    start_time_12, start_ampm = "", "AM"
                if end_time_24 != "":
                    end_time_12, end_ampm = self.controller.convert_to_12_hour(
                        end_time_24
                    )
                else:
                    end_time_12, end_ampm = "", "AM"

                # Entry field for start time with validation
                entry_start = self.helper.create_entry(
                    x=165,
                    y=y_pos,
                    initial_value=str(start_time_12),
                    width=5,
                    validate="key",
                    validatecommand=self.vcmd,
                )
                self.entries[setting["start_key"]] = entry_start
                self.time_input_widgets.append(entry_start)

                # AM/PM selection buttons for start time
                am_button = self.helper.create_rounded_button(
                    text="AM",
                    width=BUTTON_WIDTH,
                    height=BUTTON_HEIGHT,
                    bg_color="#3A3A3A",
                    fg_color="white",
                    font=("Segoe UI", 10),
                    command=lambda key=setting["start_key"]: self.set_ampm(key, "AM"),
                )
                am_button.place(x=210, y=y_pos - 4)
                pm_button = self.helper.create_rounded_button(
                    text="PM",
                    width=BUTTON_WIDTH,
                    height=BUTTON_HEIGHT,
                    bg_color="#3A3A3A",
                    fg_color="white",
                    font=("Segoe UI", 10),
                    command=lambda key=setting["start_key"]: self.set_ampm(key, "PM"),
                )
                pm_button.place(x=210 + BUTTON_WIDTH + BUTTON_PADDING, y=y_pos - 4)

                # Store button references for future updates
                self.entries[setting["start_key"] + "_ampm"] = tk.StringVar(
                    value=start_ampm
                )
                self.entries[setting["start_key"] + "_am_button"] = am_button
                self.entries[setting["start_key"] + "_pm_button"] = pm_button
                self.time_input_widgets.extend([am_button, pm_button])

                # Initialize button color based on current selection
                self.update_ampm_buttons(setting["start_key"], start_ampm)

                # Entry field for end time with validation
                entry_end = self.helper.create_entry(
                    x=330,
                    y=y_pos,
                    initial_value=str(end_time_12),
                    width=5,
                    validate="key",
                    validatecommand=self.vcmd,
                )
                self.entries[setting["end_key"]] = entry_end
                self.time_input_widgets.append(entry_end)

                # AM/PM selection buttons for end time
                am_button_end = self.helper.create_rounded_button(
                    text="AM",
                    width=BUTTON_WIDTH,
                    height=BUTTON_HEIGHT,
                    bg_color="#3A3A3A",
                    fg_color="white",
                    font=("Segoe UI", 10),
                    command=lambda key=setting["end_key"]: self.set_ampm(key, "AM"),
                )
                am_button_end.place(x=375, y=y_pos - 4)
                pm_button_end = self.helper.create_rounded_button(
                    text="PM",
                    width=BUTTON_WIDTH,
                    height=BUTTON_HEIGHT,
                    bg_color="#3A3A3A",
                    fg_color="white",
                    font=("Segoe UI", 10),
                    command=lambda key=setting["end_key"]: self.set_ampm(key, "PM"),
                )
                pm_button_end.place(x=375 + BUTTON_WIDTH + BUTTON_PADDING, y=y_pos - 4)

                # Store button references for future updates
                self.entries[setting["end_key"] + "_ampm"] = tk.StringVar(
                    value=end_ampm
                )
                self.entries[setting["end_key"] + "_am_button"] = am_button_end
                self.entries[setting["end_key"] + "_pm_button"] = pm_button_end
                self.time_input_widgets.extend([am_button_end, pm_button_end])

                # Initialize button color based on current selection
                self.update_ampm_buttons(setting["end_key"], end_ampm)

            else:
                # For other languages (e.g., Portuguese), use 24-hour format
                entry_start = self.helper.create_entry(
                    x=220,
                    y=y_pos,
                    initial_value=str(schedule.get(setting["start_key"], "")),
                    width=5,
                    validate="key",
                    validatecommand=self.vcmd,
                )

                self.entries[setting["start_key"]] = entry_start
                self.time_input_widgets.append(entry_start)

                entry_end = self.helper.create_entry(
                    x=300,
                    y=y_pos,
                    initial_value=str(schedule.get(setting["end_key"], "")),
                    width=5,
                    validate="key",
                    validatecommand=self.vcmd,
                )
                self.entries[setting["end_key"]] = entry_end
                self.time_input_widgets.append(entry_end)

    def select_language(self, lang_code):
        self.language_var.set(lang_code)
        self.highlight_selected_language()
        self.controller.language_code = lang_code
        self.controller.lang_strings = (
            self.controller.config_manager.load_language_strings(lang_code)
        )
        self.update_language()

    def highlight_selected_language(self):
        selected_code = self.language_var.get()
        for code, button in self.language_buttons.items():
            if code == selected_code:
                # Change the appearance of the selected button
                try:
                    button.config(bg="#5A5A5A")  # Change background color
                except tk.TclError:
                    pass  # Ignore if button doesn't have this attribute
            else:
                try:
                    button.config(bg="#3A3A3A")
                except tk.TclError:
                    pass

    def update_language(self):
        # Update widget texts
        self.title_label.config(
            text=self.controller.lang_strings.get("MSG_15", "Time Settings")
        )
        self.language_label.config(
            text=self.controller.lang_strings.get("MSG_24", "Language:")
        )

        # Update labels for time fields
        for setting, label_widget in zip(self.settings, self.time_labels):
            label_text = self.controller.lang_strings.get(
                setting["msg_id"], setting["default_label"]
            )
            label_widget.config(text=label_text)

        # Update text for the Apply button
        try:
            self.apply_button.itemconfig(
                self.apply_button.text_id,
                text=self.controller.lang_strings.get("MSG_08", "Apply"),
            )
        except AttributeError:
            # If apply_button doesn't have text_id, use config
            self.apply_button.config(
                text=self.controller.lang_strings.get("MSG_08", "Apply")
            )

        # Recreate time fields to reflect language changes
        self.create_time_inputs()

    def close(self):
        self.window.destroy()

    def convert_to_24_hour(self, hour, ampm):
        return self.controller.convert_to_24_hour(hour, ampm)

    def convert_to_12_hour(self, hour_24):
        return self.controller.convert_to_12_hour(hour_24)

    def set_ampm(self, key, value):
        self.entries[key + "_ampm"].set(value)
        self.update_ampm_buttons(key, value)

    def update_ampm_buttons(self, key, value):
        am_button = self.entries.get(key + "_am_button")
        pm_button = self.entries.get(key + "_pm_button")
        if am_button and pm_button:
            if value == "AM":
                self.helper.set_button_bg(am_button, "#5A5A5A")
                self.helper.set_button_bg(pm_button, "#3A3A3A")
            else:
                self.helper.set_button_bg(am_button, "#3A3A3A")
                self.helper.set_button_bg(pm_button, "#5A5A5A")

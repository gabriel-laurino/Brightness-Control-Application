# controllers/brightness_controller.py

import logging
from tkinter import messagebox
from controller.settings_controller import SettingsController
from model.data_model import ConfigManager
from views.brightness_view import BrightnessView
from services.tray_service import TrayService


class BrightnessController:
    def __init__(self, root, powershell_service):
        self.root = root
        self.powershell_service = powershell_service
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        self.brightness_levels = self.config.get("BrightnessLevels", {})
        self.language = self.config.get("Language", "EN")
        self.lang_strings = self.config_manager.load_language_strings(self.language)
        self.schedule = self.config.get("Schedule", {})

        # Initialize TrayService
        self.tray_service = TrayService(
            show_window_callback=self.show_window_from_tray,
            exit_app_callback=self.exit_app_from_tray,
            lang_strings=self.lang_strings,
        )
        self.tray_service.create_tray_icon()

        # Initialize View
        self.view = BrightnessView(self.lang_strings, self.root, self)
        self.view.create_widgets(self.brightness_levels, self.schedule)
        self.view.window.protocol("WM_DELETE_WINDOW", self.exit_app_from_tray)

        logging.info("BrightnessController initialized.")

    def update_brightness_view(self):
        self.config = self.config_manager.load_config()
        self.schedule = self.config.get("Schedule", {})
        self.brightness_levels = self.config.get("BrightnessLevels", {})
        self.view.update_brightness_inputs(self.schedule)
        self.view.update_language(self.lang_strings, self.schedule)
        logging.info("Brightness view updated with new schedule and brightness levels.")

    def run(self):
        logging.info("Running the main Tkinter loop.")
        self.view.mainloop()

    def apply_settings(self):
        try:
            new_brightness_levels = {
                key: int(entry.get()) for key, entry in self.view.entries.items()
            }
            self.brightness_levels = new_brightness_levels
            self.config["BrightnessLevels"] = new_brightness_levels
            if self.config_manager.save_brightness_settings(new_brightness_levels):
                self.view.show_success_message()
                logging.info("Brightness settings saved successfully.")
                self.update_brightness_view()
            else:
                messagebox.showerror(
                    self.lang_strings.get("MSG_07", "Error"),
                    self.lang_strings.get("MSG_11", "Failed to save settings."),
                )
                logging.error("Failed to save brightness settings.")
        except ValueError:
            messagebox.showerror(
                self.lang_strings.get("MSG_07", "Error"),
                self.lang_strings.get("MSG_06", "All values must be integers!"),
            )
            logging.error("Invalid values entered for brightness levels.")

    def minimize_to_tray(self):
        logging.info("Minimizing window to tray.")
        self.view.withdraw_window()
        self.tray_service.create_tray_icon()

    def show_window_from_tray(self):
        logging.info("Showing window from tray.")
        self.view.deiconify_window()
        self.tray_service.hide_tray_icon()

    def exit_app_from_tray(self):
        logging.info("Exiting the application from tray.")
        self.exit_application()

    def exit_application(self):
        logging.info("Finalizing the application.")
        self.tray_service.destroy_tray_icon()
        self.powershell_service.stop_powershell()
        self.root.quit()
        self.root.destroy()

    def open_settings(self):
        settings_controller = SettingsController(
            self.view.window, self.config_manager, self
        )
        self.view.window.wait_window(settings_controller.view.window)
        updated_language = self.config_manager.config.get("Language", "EN")
        updated_lang_strings = self.config_manager.load_language_strings(
            updated_language
        )
        self.lang_strings = updated_lang_strings
        self.schedule = self.config.get("Schedule", {})
        self.view.update_language(self.lang_strings, self.schedule)
        self.tray_service.update_tray_icon(lang_strings=self.lang_strings)
        logging.info("Language and settings updated.")

    def convert_to_12_hour_format(self, hour_24):
        # Convert 24-hour format to 12-hour format.
        try:
            hour = int(hour_24)
        except (ValueError, TypeError):
            logging.error(f"Invalid hour value for conversion: {hour_24}")
            return "", ""

        if hour == 0:
            return 12, "AM"
        elif 1 <= hour < 12:
            return hour, "AM"
        elif hour == 12:
            return 12, "PM"
        elif 13 <= hour < 24:
            return hour - 12, "PM"
        else:
            logging.error(f"Hour value out of range for conversion: {hour}")
            return hour, "AM"

# controllers/brightness_controller.py

import os
from tkinter import messagebox
from controller.settings_controller import SettingsController
from model.data_model import ConfigManager
from views.brightness_view import BrightnessView
from services.tray_service import TrayService


def start_gui():
    config_manager = ConfigManager()
    config = config_manager.config
    brightness_levels = config.get("BrightnessLevels", {})
    language = config.get("Language", "EN")

    lang_strings = config_manager.load_language_strings(language)

    view = BrightnessView(lang_strings)
    view.create_widgets(brightness_levels)

    def apply_settings():
        try:
            new_brightness_levels = {
                key: int(entry.get()) for key, entry in view.entries.items()
            }
            config["BrightnessLevels"] = new_brightness_levels
            config_manager.save_config()
            view.show_success_message()
        except ValueError:
            messagebox.showerror(
                lang_strings.get("MSG_07", "Error"),
                lang_strings.get("MSG_06", "All values must be integers!")
            )

    def minimize_to_tray():
        view.withdraw_window()
        tray_service.create_tray_icon()

    def show_window_from_tray():
        view.deiconify_window()
        tray_service.hide_tray_icon()

    def exit_app_from_tray():
        exit_application()

    def exit_application():
        if view.window:
            view.window.quit()
            view.window.destroy()
        tray_service.destroy_tray_icon()
        os._exit(0)

    def open_settings():
        settings_controller = SettingsController(view.window, config_manager)
        view.window.wait_window(settings_controller.view.window)
        updated_language = config_manager.config.get("Language", "EN")
        updated_lang_strings = config_manager.load_language_strings(updated_language)
        view.lang_strings = updated_lang_strings
        view.update_language()
        tray_service.update_tray_icon(lang_strings=updated_lang_strings)

    tray_service = TrayService(
        show_window_callback=show_window_from_tray,
        exit_app_callback=exit_app_from_tray,
        lang_strings=lang_strings
    )

    view.apply_button.bind("<Button-1>", lambda event: apply_settings())
    view.minimize_button.bind("<Button-1>", lambda event: minimize_to_tray())
    view.close_button.bind("<Button-1>", lambda event: exit_app_from_tray())
    view.settings_button.bind("<Button-1>", lambda event: open_settings())

    tray_service.create_tray_icon()

    view.window.protocol("WM_DELETE_WINDOW", exit_app_from_tray)
    view.mainloop()

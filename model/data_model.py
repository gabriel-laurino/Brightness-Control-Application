# model/data_model.py

import os
import json
import logging


class ConfigManager:
    def __init__(self):
        # Determine the project root directory based on the current working directory
        self.project_root = os.getcwd()

        # Absolute paths for config.json and lang.json
        self.CONFIG_PATH = os.path.join(self.project_root, "data", "config.json")
        self.LANG_PATH = os.path.join(self.project_root, "data", "lang.json")
        self.DEFAULT_LANG = "EN"

        # Load the configuration upon initialization
        self.config = self.load_config()

    def load_config(self):
        # Load configuration from config.json or return default values if the file is missing
        try:
            with open(self.CONFIG_PATH, "r", encoding="utf-8") as config_file:
                logging.info(f"Loading configuration from {self.CONFIG_PATH}")
                return json.load(config_file)
        except FileNotFoundError:
            logging.warning(
                f"Configuration file not found at {self.CONFIG_PATH}. Using default settings."
            )
            # Return default settings if config.json is not found
            return {
                "Language": self.DEFAULT_LANG,
                "BrightnessLevels": {"B1": 30, "B2": 40, "B3": 15, "B4": 10},
                "Schedule": {
                    "MorningStart": 6,
                    "MorningEnd": 11,
                    "AfternoonStart": 11,
                    "AfternoonEnd": 17,
                    "EveningStart": 17,
                    "EveningEnd": 23,
                    "NightStart": 23,
                    "NightEnd": 6,
                },
            }

    def save_config(self):
        # Save the current configuration to config.json
        try:
            os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)
            with open(self.CONFIG_PATH, "w", encoding="utf-8") as config_file:
                json.dump(self.config, config_file, indent=4)
            logging.info(f"Configuration saved to {self.CONFIG_PATH}")
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")

    def load_language_strings(self, language_code=None):
        # Load language strings from lang.json or use the default language if not found
        language_code = language_code or self.config.get("Language", self.DEFAULT_LANG)
        try:
            with open(self.LANG_PATH, "r", encoding="utf-8") as lang_file:
                logging.info(f"Loading language strings from {self.LANG_PATH}")
                lang_data = json.load(lang_file)
                return lang_data.get(language_code, lang_data[self.DEFAULT_LANG])
        except FileNotFoundError:
            logging.warning(
                f"Language file not found at {self.LANG_PATH}. Using default English strings."
            )
            # Return default English strings if lang.json is missing
            return {
                "MSG_01": "Brightness adjusted to",
                "MSG_02": "internally mapped to",
                "MSG_03": "Configuration file 'config.json' not found.",
                "MSG_04": "Brightness Settings",
                "MSG_05": "Morning (6 AM - 11 AM):",
                "MSG_06": "Afternoon (11 AM - 5 PM):",
                "MSG_07": "Evening (5 PM - 11 PM):",
                "MSG_08": "Night (11 PM - 6 AM):",
                "MSG_09": "Apply",
                "MSG_10": "Success! Settings saved.",
                "MSG_11": "Error: All values must be integers!",
                "MSG_12": "Open",
                "MSG_13": "Exit",
            }

    def save_brightness_settings(self, new_brightness_levels):
        try:
            logging.debug("Attempting to save new brightness settings.")
            # Update "BrightnessLevels" in the current configuration
            self.config["BrightnessLevels"] = new_brightness_levels

            # Save the updated configuration
            self.save_config()
            logging.info("Brightness settings saved successfully.")
            return True
        except Exception as e:
            logging.error(f"Failed to save brightness settings: {e}")
            return False

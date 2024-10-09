# model/data_model.py
import os
import json

class ConfigManager:
    CONFIG_PATH = os.path.join("data", "config.json")
    LANG_PATH = os.path.join("data", "lang.json")
    DEFAULT_LANG = "EN"

    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.CONFIG_PATH, "r", encoding="utf-8") as config_file:
                return json.load(config_file)
        except FileNotFoundError:
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
                    "NightEnd": 6
                }
            }

    def save_config(self):
        os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)
        with open(self.CONFIG_PATH, "w", encoding="utf-8") as config_file:
            json.dump(self.config, config_file, indent=4)

    def load_language_strings(self, language):
        try:
            with open(self.LANG_PATH, "r", encoding="utf-8") as lang_file:
                lang_data = json.load(lang_file)
                return lang_data.get(language, lang_data[self.DEFAULT_LANG])
        except FileNotFoundError:
            # Retorna strings padrão em inglês se o arquivo não for encontrado
            return {
                "MSG_01": "Brightness adjusted to",
                "MSG_02": "internally mapped to",
                "MSG_03": "Configuration file 'config.json' not found.",
                "MSG_04": "Brightness Settings",
                "MSG_05": "Morning (6 AM - 11 AM):",
                "MSG_06": "Afternoon (11 AM - 5 PM):",
                "MSG_07": "Night (5 PM - 11 PM):",
                "MSG_08": "Midnight (11 PM - 6 AM):",
                "MSG_09": "Apply",
                "MSG_10": "Success! Settings saved.",
                "MSG_11": "Error: All values must be integers!",
                "MSG_12": "Open",
                "MSG_13": "Exit"
            }

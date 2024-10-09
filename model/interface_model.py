import threading
import tkinter as tk
import ctypes
from PIL import Image, ImageDraw
import pystray
import json

class InterfaceModel:
    def __init__(self, window):
        self.window = window
        self.tray_icon = None
        self.tray_thread = None

    def setup_window(self, width=320, height=300, bg_color="#2E2E2E", topmost=True, corner_radius=20):
        # General window configuration
        self.window.overrideredirect(True)
        self.window.geometry(f"{width}x{height}")
        self.window.configure(bg=bg_color)
        self.window.resizable(False, False)
        self.window.attributes("-topmost", topmost)

        # Position window in bottom right corner
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_pos = screen_width - width - 10
        y_pos = screen_height - height - 60
        self.window.geometry(f"{width}x{height}+{x_pos}+{y_pos}")

        # Apply rounded corners to the window
        self.apply_rounded_region(radius=corner_radius)

    def create_rounded_button(self, text, width, height, bg_color="#1E90FF", fg_color="white", font=("Segoe UI", 10, "bold"), command=None):
        # Creates a rounded button using a Canvas widget
        btn_canvas = tk.Canvas(self.window, width=width, height=height, bg=self.window["bg"], highlightthickness=0)
        radius = 10
        rect_id = self.round_rectangle(btn_canvas, 0, 0, width, height, radius, fill=bg_color, outline="")
        text_id = btn_canvas.create_text(width / 2, height / 2, text=text, fill=fg_color, font=font)
        btn_canvas.tag_lower(rect_id)
        btn_canvas.bind("<Button-1>", lambda event: command())
        return btn_canvas

    def apply_button(self, text="Apply", command=None):
        # Standard apply button
        return self.create_rounded_button(text, width=120, height=35, bg_color="#1E90FF", fg_color="white", command=command)

    def close_button(self, text="X", command=None):
        # Standard close button
        return self.create_rounded_button(text, width=25, height=25, bg_color="#555555", fg_color="white", command=command)

    def create_label(self, text, x, y, font=("Segoe UI", 10), bg="#2E2E2E", fg="white"):
        # Reusable label creation
        label = tk.Label(self.window, text=text, bg=bg, fg=fg, font=font)
        label.place(x=x, y=y)
        return label

    def create_separator(self, x, y, width=280, height=2, bg="#444444"):
        # Reusable separator creation
        separator = tk.Frame(self.window, bg=bg)
        separator.place(x=x, y=y, width=width, height=height)
        return separator

    def round_rectangle(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        # Create a rectangle with rounded corners
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def apply_rounded_region(self, radius=20):
        # Apply rounded region to the window
        hwnd = self.window.winfo_id()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        hRgn = ctypes.windll.gdi32.CreateRoundRectRgn(0, 0, width + 1, height + 1, radius, radius)
        ctypes.windll.user32.SetWindowRgn(hwnd, hRgn, True)

    def load_language_strings(self, config_path='data/config.json', lang_path='data/lang.json', default_lang="EN"):
        # Load language from config.json
        with open(config_path, 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
            language = config.get("Language", default_lang)

        # Load language strings from lang.json
        with open(lang_path, 'r', encoding='utf-8') as lang_file:
            lang_data = json.load(lang_file)
            
        return lang_data.get(language, lang_data[default_lang])

    def withdraw_window(self):
        # Minimize the window to tray
        self.window.withdraw()

    def deiconify_window(self):
        # Restore the window from tray
        self.window.deiconify()

    def create_tray_icon(self, show_window_callback, exit_app_callback, icon_text="Brightness Control", lang_strings=None):
        if lang_strings is None:
            lang_strings = self.load_language_strings()

        if self.tray_icon is None:
            # Create the tray icon only if it doesn't exist
            image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.ellipse((8, 8, 56, 56), fill="yellow", outline="orange", width=3)

            # Use translated strings for the tray menu
            self.tray_icon = pystray.Icon(icon_text, image, icon_text, menu=pystray.Menu(
                pystray.MenuItem(lang_strings.get("MSG_13", "Open"), show_window_callback, default=True),
                pystray.MenuItem(lang_strings.get("MSG_14", "Exit"), exit_app_callback)
            ))

            # Run the tray icon in a separate thread
            self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self.tray_thread.start()
        else:
            # If the tray icon already exists, make it visible
            self.tray_icon.visible = True

    def destroy_tray_icon(self):
        # Destroy the tray icon safely
        if self.tray_icon:
            self.tray_icon.visible = False
            self.tray_icon.stop()
            self.tray_icon = None

            # Wait for the tray thread to stop
            if self.tray_thread and self.tray_thread.is_alive():
                self.tray_thread.join(timeout=1)
            self.tray_thread = None

    def hide_tray_icon(self):
        # Hide the tray icon
        if self.tray_icon:
            self.tray_icon.visible = False

    def set_tray_icon_visibility(self, visible):
        # Set visibility of the tray icon
        if self.tray_icon:
            self.tray_icon.visible = visible
            
    def save_brightness_settings(self, new_brightness_levels):
        try:
            # Load existing config.json
            with open('data/config.json', 'r', encoding='utf-8') as config_file:
                config = json.load(config_file)

            # Update "BrightnessLevels" in config.json
            config["BrightnessLevels"] = new_brightness_levels

            # Save changes to config.json
            with open('data/config.json', 'w', encoding='utf-8') as config_file:
                json.dump(config, config_file, indent=4)
            return True
        except Exception as e:
            return False

    def create_entry(self, x, y, initial_value=""):
        # Create a reusable entry widget
        entry = tk.Entry(self.window, width=5, relief="flat", justify='center', font=("Segoe UI", 10))
        entry.place(x=x, y=y)
        entry.insert(0, initial_value)
        entry.configure(bg="#3A3A3A", fg="white", insertbackground="white",
                        highlightbackground="#5A5A5A", highlightthickness=1)
        return entry

    def create_brightness_settings_widgets(self, lang_strings, brightness_levels):
        # Create brightness settings widgets
        self.create_label(
            text=lang_strings.get("MSG_04", "Brightness Settings"),
            x=20,
            y=10,
            font=("Segoe UI", 14, "bold")
        )

        self.create_separator(x=20, y=50, width=280, height=2)

        # Labels and entries for brightness levels
        settings = [
            {"label": lang_strings.get("MSG_05", "Morning (6h-11h):"), "key": "B1", "y_pos": 60},
            {"label": lang_strings.get("MSG_06", "Afternoon (11h-17h):"), "key": "B2", "y_pos": 100},
            {"label": lang_strings.get("MSG_07", "Evening (17h-23h):"), "key": "B3", "y_pos": 140},
            {"label": lang_strings.get("MSG_08", "Night (23h-6h):"), "key": "B4", "y_pos": 180},
        ]

        entries = {}
        for setting in settings:
            self.create_label(
                text=setting["label"], x=40, y=setting["y_pos"], font=("Segoe UI", 10)
            )
            entry = self.create_entry(x=220, y=setting["y_pos"], initial_value=brightness_levels.get(setting["key"], ""))
            entries[setting["key"]] = entry

        return entries

    def minimize_to_tray(self, show_window_callback, exit_app_callback):
        # Minimize window and create tray icon
        self.withdraw_window()
        self.create_tray_icon(show_window_callback, exit_app_callback)

    def restore_window(self):
        # Restore window and hide tray icon
        self.deiconify_window()
        self.hide_tray_icon()

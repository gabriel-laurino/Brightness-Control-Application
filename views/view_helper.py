# views/view_helper.py

import tkinter as tk
import ctypes

class ViewHelper:
    def __init__(self, window):
        self.window = window
        self.tray_icon = None
        self.tray_thread = None

    def setup_window(
        self,
        width=320,
        height=300,
        bg_color="#2E2E2E",
        topmost=True,
        corner_radius=20
    ):

        self.window.overrideredirect(True)
        self.window.geometry(f"{width}x{height}")
        self.window.configure(bg=bg_color)
        self.window.resizable(False, False)
        self.window.attributes("-topmost", topmost)

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_pos = screen_width - width - 10
        y_pos = screen_height - height - 60
        self.window.geometry(f"{width}x{height}+{x_pos}+{y_pos}")
        
        self.window.update_idletasks()

        self.apply_rounded_region(radius=corner_radius)

    def apply_rounded_region(self, radius=20):
 
        hwnd = self.window.winfo_id()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        hRgn = ctypes.windll.gdi32.CreateRoundRectRgn(
            0, 0, width + 1, height + 1, radius, radius
        )
        ctypes.windll.user32.SetWindowRgn(hwnd, hRgn, True)

    def create_rounded_button(
        self,
        text,
        width,
        height,
        bg_color="#1E90FF",
        fg_color="white",
        font=("Segoe UI", 10, "bold"),
        command=None
    ):

        btn_canvas = tk.Canvas(
            self.window,
            width=width,
            height=height,
            bg=self.window["bg"],
            highlightthickness=0,
            cursor="hand2"
        )
        radius = 10
        rect_id = self.round_rectangle(
            btn_canvas, 0, 0, width, height, radius, fill=bg_color, outline=""
        )
        text_id = btn_canvas.create_text(
            width / 2, height / 2, text=text, fill=fg_color, font=font
        )
        btn_canvas.tag_lower(rect_id)
        if command:
            btn_canvas.bind("<Button-1>", lambda event: command())
        btn_canvas.rect_id = rect_id
        btn_canvas.text_id = text_id
        return btn_canvas

    def set_button_bg(self, button, color):

        button.itemconfig(button.rect_id, fill=color)

    def create_apply_button(self, text="Apply", command=None):
 
        return self.create_rounded_button(
            text=text,
            width=120,
            height=35,
            bg_color="#1E90FF",
            fg_color="white",
            font=("Segoe UI", 10, "bold"),
            command=command
        )

    def create_close_button(self, text="X", command=None):
 
        return self.create_rounded_button(
            text=text,
            width=25,
            height=25,
            bg_color="#555555",
            fg_color="white",
            font=("Segoe UI", 10, "bold"),
            command=command
        )

    def create_label(
        self,
        text,
        x,
        y,
        font=("Segoe UI", 10),
        bg="#2E2E2E",
        fg="white"
    ):

        label = tk.Label(
            self.window,
            text=text,
            bg=bg,
            fg=fg,
            font=font
        )
        label.place(x=x, y=y)
        return label

    def create_separator(
        self,
        x,
        y,
        width=280,
        height=2,
        bg="#444444"
    ):

        separator = tk.Frame(
            self.window,
            bg=bg
        )
        separator.place(x=x, y=y, width=width, height=height)
        return separator

    def round_rectangle(
        self,
        canvas,
        x1,
        y1,
        x2,
        y2,
        radius=25,
        **kwargs
    ):

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
        return canvas.create_polygon(
            points,
            **kwargs,
            smooth=True
        )

    def create_entry(self, x, y, initial_value="", width=5, validate=None, validatecommand=None, **kwargs):
        entry = tk.Entry(
            self.window,
            width=width,
            relief="flat",
            justify='center',
            font=("Segoe UI", 10),
            bg="#3A3A3A",
            fg="white",
            insertbackground="white",
            highlightbackground="#5A5A5A",
            highlightthickness=1,
            validate=validate,
            validatecommand=validatecommand,
            **kwargs
        )
        entry.place(x=x, y=y)
        entry.insert(0, initial_value)
        return entry

    def create_brightness_settings_widgets(
        self,
        lang_strings,
        brightness_levels
    ):

        self.create_label(
            text=lang_strings.get("MSG_04", "Brightness Settings"),
            x=20,
            y=10,
            font=("Segoe UI", 14, "bold"),
            bg=self.window["bg"],
            fg="white"
        )

        self.create_separator(x=20, y=50, width=280, height=2)

        # Labels and entries for brightness levels
        settings = [
            {
                "label": lang_strings.get("MSG_05", "Morning (6h-11h):"),
                "key": "B1",
                "y_pos": 60
            },
            {
                "label": lang_strings.get("MSG_06", "Afternoon (11h-17h):"),
                "key": "B2",
                "y_pos": 100
            },
            {
                "label": lang_strings.get("MSG_07", "Evening (17h-23h):"),
                "key": "B3",
                "y_pos": 140
            },
            {
                "label": lang_strings.get("MSG_08", "Night (23h-6h):"),
                "key": "B4",
                "y_pos": 180
            },
        ]

        entries = {}
        for setting in settings:
            self.create_label(
                text=setting["label"],
                x=40,
                y=setting["y_pos"],
                font=("Segoe UI", 10),
                bg=self.window["bg"],
                fg="white"
            )
            entry = self.create_entry(
                x=220,
                y=setting["y_pos"],
                initial_value=str(brightness_levels.get(setting["key"], "")),
                width=5
            )
            entries[setting["key"]] = entry

        return entries

    def create_icon_button(
        self,
        text,
        x,
        y,
        command=None
    ):

        button = self.create_rounded_button(
            text=text,
            width=25,
            height=25,
            bg_color="#555555",
            fg_color="white",
            font=("Segoe UI", 12),
            command=command
        )
        button.place(x=x, y=y)
        return button
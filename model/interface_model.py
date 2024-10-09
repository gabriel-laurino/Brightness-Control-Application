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
        # Configurações gerais da janela
        self.window.overrideredirect(True)
        self.window.geometry(f"{width}x{height}")
        self.window.configure(bg=bg_color)
        self.window.resizable(False, False)
        self.window.attributes("-topmost", topmost)

        # Posicionar a janela no canto inferior direito da tela
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_pos = screen_width - width - 10
        y_pos = screen_height - height - 60
        self.window.geometry(f"{width}x{height}+{x_pos}+{y_pos}")

        # Atualizar a janela para garantir que as dimensões estão corretas
        self.window.update_idletasks()

        # Criar uma região com cantos arredondados
        self.apply_rounded_region(radius=corner_radius)

    def create_rounded_button(self, text, width, height, bg_color="#1E90FF", fg_color="white", font=("Segoe UI", 10, "bold"), command=None):
        # Cria um botão com bordas arredondadas usando Canvas
        btn_canvas = tk.Canvas(self.window, width=width, height=height, bg=self.window["bg"], highlightthickness=0)
        radius = 10
        rect_id = self.round_rectangle(btn_canvas, 0, 0, width, height, radius, fill=bg_color, outline="")
        text_id = btn_canvas.create_text(width / 2, height / 2, text=text, fill=fg_color, font=font)
        btn_canvas.tag_lower(rect_id)
        btn_canvas.bind("<Button-1>", lambda event: command())  # Associar o comando ao clique
        return btn_canvas

    def apply_button(self, text="Aplicar", command=None):
        # Botão padrão de aplicar
        return self.create_rounded_button(text, width=120, height=35, bg_color="#1E90FF", fg_color="white", command=command)

    def close_button(self, text="X", command=None):
        # Botão padrão de fechar
        return self.create_rounded_button(text, width=25, height=25, bg_color="#555555", fg_color="white", command=command)

    def create_label(self, text, x, y, font=("Segoe UI", 10), bg="#2E2E2E", fg="white"):
        # Cria um Label reutilizável
        label = tk.Label(self.window, text=text, bg=bg, fg=fg, font=font)
        label.place(x=x, y=y)
        return label

    def create_separator(self, x, y, width=280, height=2, bg="#444444"):
        # Cria um separador reutilizável
        separator = tk.Frame(self.window, bg=bg)
        separator.place(x=x, y=y, width=width, height=height)
        return separator

    def round_rectangle(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
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
        # Aplicar cantos arredondados à janela
        hwnd = self.window.winfo_id()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        hRgn = ctypes.windll.gdi32.CreateRoundRectRgn(0, 0, width + 1, height + 1, radius, radius)
        ctypes.windll.user32.SetWindowRgn(hwnd, hRgn, True)

    def load_language_strings(self, config_path='data/config.json', lang_path='data/lang.json', default_lang="EN"):
        # Carregar o idioma do config.json
        with open(config_path, 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
            language = config.get("Language", default_lang)  # Padrão para "EN" se não for definido

        # Carregar as strings de idioma do lang.json com base na língua, usando UTF-8
        with open(lang_path, 'r', encoding='utf-8') as lang_file:
            lang_data = json.load(lang_file)
            
        return lang_data.get(language, lang_data[default_lang])  # Retorna "EN" se o idioma não for encontrado

    def withdraw_window(self):
        # Método para ocultar a janela (minimizar para a bandeja)
        self.window.withdraw()

    def deiconify_window(self):
        # Método para restaurar a janela a partir da bandeja
        self.window.deiconify()

    def create_tray_icon(self, show_window_callback, exit_app_callback, icon_text="Brightness Control", lang_strings=None):
        if lang_strings is None:
            lang_strings = self.load_language_strings()

        if self.tray_icon is None:
            # Criar o ícone da bandeja apenas se ele não existir
            image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.ellipse((8, 8, 56, 56), fill="yellow", outline="orange", width=3)

            # Use as mensagens traduzidas para o menu da bandeja
            self.tray_icon = pystray.Icon(icon_text, image, icon_text, menu=pystray.Menu(
                pystray.MenuItem(lang_strings.get("MSG_13", "Open"), show_window_callback, default=True),
                pystray.MenuItem(lang_strings.get("MSG_14", "Exit"), exit_app_callback)
            ))

            # Executar o tray icon em um thread separado para evitar bloquear a interface do Tkinter
            self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self.tray_thread.start()
        else:
            # Se o ícone já existe, apenas torná-lo visível
            self.tray_icon.visible = True

    def destroy_tray_icon(self):
        if self.tray_icon:
            # Remover visibilidade e parar o ícone da bandeja
            self.tray_icon.visible = False
            self.tray_icon.stop()  # Para o tray icon corretamente
            self.tray_icon = None

            # Aguardar o encerramento da thread do tray icon
            if self.tray_thread and self.tray_thread.is_alive():
                self.tray_thread.join(timeout=1)
            self.tray_thread = None

    def hide_tray_icon(self):
        if self.tray_icon:
            self.tray_icon.visible = False

    def set_tray_icon_visibility(self, visible):
        if self.tray_icon:
            self.tray_icon.visible = visible
            
    def save_brightness_settings(self, new_brightness_levels):
        try:
            # Carregar o arquivo config.json existente
            with open('data/config.json', 'r', encoding='utf-8') as config_file:
                config = json.load(config_file)

            # Atualizar apenas a seção "BrightnessLevels" no arquivo config.json
            config["BrightnessLevels"] = new_brightness_levels

            # Salvar as alterações no arquivo config.json
            with open('data/config.json', 'w', encoding='utf-8') as config_file:
                json.dump(config, config_file, indent=4)
            return True
        except Exception as e:
            return False

    def create_entry(self, x, y, initial_value=""):
        # Cria um Entry reutilizável com as configurações padrão
        entry = tk.Entry(self.window, width=5, relief="flat", justify='center', font=("Segoe UI", 10))
        entry.place(x=x, y=y)
        entry.insert(0, initial_value)
        entry.configure(bg="#3A3A3A", fg="white", insertbackground="white",
                        highlightbackground="#5A5A5A", highlightthickness=1)
        return entry

    def create_brightness_settings_widgets(self, lang_strings, brightness_levels):
        # Criação dos widgets de configurações de brilho
        self.create_label(
            text=lang_strings.get("MSG_04", "Configurações de Brilho"),
            x=20,
            y=10,
            font=("Segoe UI", 14, "bold")
        )

        self.create_separator(x=20, y=50, width=280, height=2)

        # Labels e Entries
        settings = [
            {"label": lang_strings.get("MSG_05", "Manhã (6h-11h):"), "key": "B1", "y_pos": 60},
            {"label": lang_strings.get("MSG_06", "Tarde (11h-17h):"), "key": "B2", "y_pos": 100},
            {"label": lang_strings.get("MSG_07", "Noite (17h-23h):"), "key": "B3", "y_pos": 140},
            {"label": lang_strings.get("MSG_08", "Madrugada (23h-6h):"), "key": "B4", "y_pos": 180},
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
        # Minimizar a janela e criar ícone na bandeja
        self.withdraw_window()
        self.create_tray_icon(show_window_callback, exit_app_callback)

    def restore_window(self):
        # Restaurar a janela e ocultar o ícone da bandeja
        self.deiconify_window()
        self.hide_tray_icon()

# views/settings_view.py

import tkinter as tk
from views.view_helper import ViewHelper
from tkinter import messagebox

class Tooltip:
    def __init__(self, widget, text='widget info'):
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
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#FFFFE0", relief='solid', borderwidth=1,
                         font=("Segoe UI", 10))
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

        # Variável para armazenar o código do idioma selecionado
        self.language_var = tk.StringVar(value=self.controller.language_code)

        # Registrar a função de validação com %P (proposed value) e %W (widget name)
        self.vcmd = (self.window.register(self.validate_time_input), '%P', '%W')

        # Configuração da janela
        self.helper.setup_window(width=470, height=400, bg_color="#2E2E2E")

        # Criar widgets
        self.create_widgets()

    def set_controller(self, controller):
        self.controller = controller

    def validate_time_input(self, proposed_value, widget_name):

        widget = self.window.nametowidget(widget_name)

        if proposed_value == "":
            widget.config(bg="#3A3A3A")  # Cor padrão
            if hasattr(widget, 'tooltip'):
                widget.tooltip.hide_tooltip()
            return True

        try:
            value = int(proposed_value)
        except ValueError:
            widget.config(bg="#FFCCCC")  # Cor de erro
            if not hasattr(widget, 'tooltip'):
                widget.tooltip = Tooltip(widget, "Por favor, insira um número inteiro válido.")
            return False

        language_code = self.language_var.get()

        if language_code == "EN":
            is_valid = 0 <= value <= 12
        elif language_code == "PT":
            is_valid = 0 <= value <= 24
        else:
            is_valid = False

        if is_valid:
            widget.config(bg="#3A3A3A")  # Cor padrão
            if hasattr(widget, 'tooltip'):
                widget.tooltip.hide_tooltip()
        else:
            widget.config(bg="#FFCCCC")  # Cor de erro
            if not hasattr(widget, 'tooltip'):
                if language_code == "EN":
                    error_msg = "Please enter a value between 0 and 12."
                else:
                    error_msg = "Por favor, insira um valor entre 0 e 24."
                widget.tooltip = Tooltip(widget, error_msg)

        return is_valid

    def create_widgets(self):
        # Título
        self.title_label = self.helper.create_label(
            text=self.controller.lang_strings.get("MSG_15", "Time Settings"),
            x=20,
            y=10,
            font=("Segoe UI", 14, "bold"),
            bg="#2E2E2E",
            fg="white"
        )

        # Separador
        self.helper.create_separator(x=20, y=50, width=430, height=2, bg="#444444")

        # Lista de idiomas disponíveis
        languages = [("EN", "English"), ("PT", "Português")]

        # Mapear código para nome e nome para código
        self.code_to_name = {code: name for code, name in languages}
        self.name_to_code = {name: code for code, name in languages}

        # Adicionar seleção de idioma
        self.language_label = self.helper.create_label(
            text=self.controller.lang_strings.get("MSG_24", "Language:"),
            x=20,
            y=250,
            font=("Segoe UI", 10),
            bg="#2E2E2E",
            fg="white"
        )

        # Criar botões personalizados para seleção de idioma
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
            # Bind do botão com o código do idioma
            button.bind("<Button-1>", lambda event, code=lang_code: self.select_language(code))
            self.language_buttons[lang_code] = button  # Armazenar o botão com o código
            x_position += 120

        # Destacar o botão do idioma selecionado
        self.highlight_selected_language()

        # Definir configurações de horário
        self.settings = [
            {
                "label": self.controller.lang_strings.get("MSG_16", "Morning (Start - End):"),
                "msg_id": "MSG_16",
                "default_label": "Morning (Start - End):",
                "start_key": "MorningStart",
                "end_key": "MorningEnd",
                "y_pos": 70
            },
            {
                "label": self.controller.lang_strings.get("MSG_17", "Afternoon (Start - End):"),
                "msg_id": "MSG_17",
                "default_label": "Afternoon (Start - End):",
                "start_key": "AfternoonStart",
                "end_key": "AfternoonEnd",
                "y_pos": 110
            },
            {
                "label": self.controller.lang_strings.get("MSG_18", "Evening (Start - End):"),
                "msg_id": "MSG_18",
                "default_label": "Evening (Start - End):",
                "start_key": "EveningStart",
                "end_key": "EveningEnd",
                "y_pos": 150
            },
            {
                "label": self.controller.lang_strings.get("MSG_19", "Night (Start - End):"),
                "msg_id": "MSG_19",
                "default_label": "Night (Start - End):",
                "start_key": "NightStart",
                "end_key": "NightEnd",
                "y_pos": 190
            }
        ]

        self.time_labels = []
        self.create_time_inputs()

        # Botão Aplicar
        self.apply_button = self.helper.create_apply_button(
            text=self.controller.lang_strings.get("MSG_08", "Apply")
        )
        self.apply_button.place(x=175, y=330)
        self.apply_button.bind("<Button-1>", self.on_apply)

        # Botão Fechar
        self.close_button = self.helper.create_rounded_button(
            text="X",
            width=25,
            height=25,
            bg_color="#555555",
            fg_color="white",
            font=("Segoe UI", 12, "bold")
        )
        self.close_button.place(x=435, y=10)  # Ajustar posição para a nova largura
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
                    self.controller.lang_strings.get("MSG_06", "All values must be integers!")
                )
                return

            try:
                start_time = int(start_time_str)
                end_time = int(end_time_str)
            except ValueError:
                messagebox.showerror(
                    self.controller.lang_strings.get("MSG_07", "Error"),
                    self.controller.lang_strings.get("MSG_06", "All values must be integers!")
                )
                return

            if language_code == 'EN':
                # Obter AM/PM dos botões
                start_ampm = self.entries[start_key + '_ampm'].get()
                end_ampm = self.entries[end_key + '_ampm'].get()
                # Delegar a conversão para o Controller
                start_time_24 = self.controller.convert_to_24_hour(start_time, start_ampm)
                end_time_24 = self.controller.convert_to_24_hour(end_time, end_ampm)
            else:
                # Assumir formato de 24 horas
                start_time_24 = start_time
                end_time_24 = end_time

            schedule[start_key] = start_time_24
            schedule[end_key] = end_time_24

        # Delegar a aplicação das configurações para o Controller
        self.controller.apply_settings(schedule, language_code)

    def create_time_inputs(self):
        # Destruir os widgets de horário existentes, se houver
        if hasattr(self, 'time_input_widgets'):
            for widget in self.time_input_widgets:
                widget.destroy()
        self.time_input_widgets = []
        self.entries = {}
        self.time_labels = [] 

        # Obter o idioma atual
        selected_language_code = self.language_var.get()

        # Carregar configurações atuais
        schedule = self.controller.model.get("Schedule", {})

        # Definir constantes para largura dos botões e espaçamento
        BUTTON_WIDTH = 36 
        BUTTON_HEIGHT = 30
        BUTTON_PADDING = 10 

        # Criar os campos de horário
        for setting in self.settings:
            y_pos = setting["y_pos"]
            # Atualizar o texto do label caso o idioma tenha mudado
            label_text = self.controller.lang_strings.get(
                setting["msg_id"], setting["default_label"])
            label_widget = self.helper.create_label(
                text=label_text,
                x=20,
                y=y_pos,
                font=("Segoe UI", 10),
                bg="#2E2E2E",
                fg="white"
            )
            self.time_labels.append(label_widget)
            self.time_input_widgets.append(label_widget)

            if selected_language_code == 'EN':
                # Obter os horários armazenados e converter para o formato de 12 horas
                start_time_24 = schedule.get(setting["start_key"], "")
                end_time_24 = schedule.get(setting["end_key"], "")

                if start_time_24 != "":
                    start_time_12, start_ampm = self.controller.convert_to_12_hour(start_time_24)
                else:
                    start_time_12, start_ampm = "", "AM"
                if end_time_24 != "":
                    end_time_12, end_ampm = self.controller.convert_to_12_hour(end_time_24)
                else:
                    end_time_12, end_ampm = "", "AM"

                # Campo de entrada para o horário de início com validação
                entry_start = self.helper.create_entry(
                    x=165,
                    y=y_pos,
                    initial_value=str(start_time_12),
                    width=5,
                    validate='key',
                    validatecommand=self.vcmd
                )
                self.entries[setting["start_key"]] = entry_start
                self.time_input_widgets.append(entry_start)

                # Seleção de AM/PM para o horário de início
                # Criar botões personalizados para AM e PM
                am_button = self.helper.create_rounded_button(
                    text='AM',
                    width=BUTTON_WIDTH,
                    height=BUTTON_HEIGHT,
                    bg_color="#3A3A3A",
                    fg_color="white",
                    font=("Segoe UI", 10),
                    command=lambda key=setting["start_key"]: self.set_ampm(key, 'AM')
                )
                am_button.place(x=210, y=y_pos-4)
                pm_button = self.helper.create_rounded_button(
                    text='PM',
                    width=BUTTON_WIDTH,
                    height=BUTTON_HEIGHT,
                    bg_color="#3A3A3A",
                    fg_color="white",
                    font=("Segoe UI", 10),
                    command=lambda key=setting["start_key"]: self.set_ampm(key, 'PM')
                )
                pm_button.place(x=210 + BUTTON_WIDTH + BUTTON_PADDING, y=y_pos-4)

                # Armazenar referências dos botões para atualização futura
                self.entries[setting["start_key"] + '_ampm'] = tk.StringVar(value=start_ampm)
                self.entries[setting["start_key"] + '_am_button'] = am_button
                self.entries[setting["start_key"] + '_pm_button'] = pm_button
                self.time_input_widgets.extend([am_button, pm_button])

                # Inicializar a cor dos botões com base na seleção atual
                self.update_ampm_buttons(setting["start_key"], start_ampm)

                # Campo de entrada para o horário de fim com validação
                entry_end = self.helper.create_entry(
                    x=330,
                    y=y_pos,
                    initial_value=str(end_time_12),
                    width=5,
                    validate='key',
                    validatecommand=self.vcmd
                )
                self.entries[setting["end_key"]] = entry_end
                self.time_input_widgets.append(entry_end)

                # Seleção de AM/PM para o horário de fim
                am_button_end = self.helper.create_rounded_button(
                    text='AM',
                    width=BUTTON_WIDTH,
                    height=BUTTON_HEIGHT,
                    bg_color="#3A3A3A",
                    fg_color="white",
                    font=("Segoe UI", 10),
                    command=lambda key=setting["end_key"]: self.set_ampm(key, 'AM')
                )
                am_button_end.place(x=375, y=y_pos-4)
                pm_button_end = self.helper.create_rounded_button(
                    text='PM',
                    width=BUTTON_WIDTH,
                    height=BUTTON_HEIGHT,
                    bg_color="#3A3A3A",
                    fg_color="white",
                    font=("Segoe UI", 10),
                    command=lambda key=setting["end_key"]: self.set_ampm(key, 'PM')
                )
                pm_button_end.place(x=375 + BUTTON_WIDTH + BUTTON_PADDING, y=y_pos-4)

                # Armazenar referências dos botões para atualização futura
                self.entries[setting["end_key"] + '_ampm'] = tk.StringVar(value=end_ampm)
                self.entries[setting["end_key"] + '_am_button'] = am_button_end
                self.entries[setting["end_key"] + '_pm_button'] = pm_button_end
                self.time_input_widgets.extend([am_button_end, pm_button_end])

                # Inicializar a cor dos botões com base na seleção atual
                self.update_ampm_buttons(setting["end_key"], end_ampm)

            else:
                # Para outros idiomas (por exemplo, português), usar o formato de 24 horas
                entry_start = self.helper.create_entry(
                    x=220,
                    y=y_pos,
                    initial_value=str(schedule.get(setting["start_key"], "")),
                    width=5,
                    validate='key',
                    validatecommand=self.vcmd
                )
                self.entries[setting["start_key"]] = entry_start
                self.time_input_widgets.append(entry_start)

                entry_end = self.helper.create_entry(
                    x=300,
                    y=y_pos,
                    initial_value=str(schedule.get(setting["end_key"], "")),
                    width=5,
                    validate='key',
                    validatecommand=self.vcmd
                )
                self.entries[setting["end_key"]] = entry_end
                self.time_input_widgets.append(entry_end)

    def select_language(self, lang_code):
        self.language_var.set(lang_code)
        self.highlight_selected_language()
        self.controller.language_code = lang_code
        self.controller.lang_strings = self.controller.config_manager.load_language_strings(lang_code)
        self.update_language()

    def highlight_selected_language(self):
        selected_code = self.language_var.get()
        for code, button in self.language_buttons.items():
            if code == selected_code:
                # Mudar a aparência do botão selecionado
                try:
                    button.config(bg="#5A5A5A")  # Alterar a cor de fundo
                except tk.TclError:
                    pass  # Caso o botão não tenha esse atributo
            else:
                try:
                    button.config(bg="#3A3A3A")
                except tk.TclError:
                    pass

    def update_language(self):
        # Atualizar os textos dos widgets
        self.title_label.config(text=self.controller.lang_strings.get("MSG_15", "Time Settings"))
        self.language_label.config(text=self.controller.lang_strings.get("MSG_24", "Language:"))

        # Atualizar os labels dos campos de horário
        for setting, label_widget in zip(self.settings, self.time_labels):
            label_text = self.controller.lang_strings.get(setting["msg_id"], setting["default_label"])
            label_widget.config(text=label_text)

        # Atualizar o texto do botão Aplicar
        try:
            self.apply_button.itemconfig(self.apply_button.text_id, text=self.controller.lang_strings.get("MSG_08", "Apply"))
        except AttributeError:
            # Se apply_button não tiver text_id, use config
            self.apply_button.config(text=self.controller.lang_strings.get("MSG_08", "Apply"))

        # Recriar os campos de horário para refletir as mudanças de idioma
        self.create_time_inputs()

    def close(self):
        self.window.destroy()

    def convert_to_24_hour(self, hour, ampm):

        return self.controller.convert_to_24_hour(hour, ampm)

    def convert_to_12_hour(self, hour_24):

        return self.controller.convert_to_12_hour(hour_24)

    def set_ampm(self, key, value):
        self.entries[key + '_ampm'].set(value)
        self.update_ampm_buttons(key, value)

    def update_ampm_buttons(self, key, value):
        am_button = self.entries.get(key + '_am_button')
        pm_button = self.entries.get(key + '_pm_button')
        if am_button and pm_button:
            if value == 'AM':
                self.helper.set_button_bg(am_button, "#5A5A5A")
                self.helper.set_button_bg(pm_button, "#3A3A3A")
            else:
                self.helper.set_button_bg(am_button, "#3A3A3A")
                self.helper.set_button_bg(pm_button, "#5A5A5A")

---

# Brightness Control Application

This application allows users to manage system brightness levels through an intuitive graphical interface. It includes features such as multilingual support, configuration management, and system tray integration for easy access and control.

## Project Overview

The project is structured following the **MVC (Model-View-Controller)** pattern, ensuring a clear separation of concerns and facilitating maintenance and scalability.

### Technologies Used:

- **Tkinter**: For creating the graphical user interface.
- **pystray**: For integrating the application with the system tray.
- **Pillow**: For handling images used in the tray icon.
- **JSON**: For storing and managing language strings and configurations.

### Features:

- **Brightness Control**: Allows adjusting brightness levels for different times of the day (Morning, Afternoon, Evening, Night).
- **Multilingual Support**: Facilitates internationalization and customization of the interface.
- **System Tray Integration**: Provides quick access to main functionalities via the system tray icon.
- **Configuration Management**: Stores user preferences persistently.
- **Data Validation**: Ensures user inputs are valid and consistent.

## Project Structure

```bash
.
├── controllers
│   └── brightness_controller.py    # Main controller managing brightness logic
├── model
│   ├── config_manager.py           # Manages loading and saving configurations
│   └── language_manager.py         # Manages loading and updating language strings
├── services
│   └── tray_service.py             # Service for managing the system tray icon
├── views
│   ├── brightness_view.py          # Main graphical interface for brightness control
│   └── view_helper.py              # Assists in creating and managing UI widgets
├── languages
│   ├── lang_en.json                # Language strings for English
│   └── lang_pt.json                # Language strings for Portuguese
├── main
│   └── main.py                     # Entry point of the application
├── README.md                       # Project documentation (this file)
└── requirements.txt                # List of project dependencies
```

### Key Files:

- **brightness_controller.py**: Controls the interaction between the GUI, services, and models.
- **config_manager.py**: Loads and saves user configurations.
- **language_manager.py**: Loads language strings and notifies subscribed views about language changes.
- **tray_service.py**: Manages the system tray icon, including click events and context menus.
- **brightness_view.py**: Defines and updates the graphical interface elements related to brightness control.
- **view_helper.py**: Provides helper methods for consistent widget creation.
- **lang_en.json & lang_pt.json**: Contain translations for supported languages.
- **main.py**: Initializes and starts the application.

## Prerequisites

Ensure you have the following tools installed on your machine:

- **Python 3.10+**
- **Pip** (Python package manager)

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/brightness-control-app.git
   cd brightness-control-app
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Required Packages:

- `pystray`
- `Pillow`

## Language Management

Language files are located in the `languages/` directory. To add a new language:

1. **Create a New JSON File** following the naming pattern `lang_<language_code>.json`, for example, `lang_es.json` for Spanish.

2. **Add Translations** corresponding to the existing keys in the language files.

   ```json
   {
       "MSG_04": "Configuraciones de Brillo",
       "MSG_06": "¡Todos los valores deben ser enteros!",
       "MSG_07": "Error",
       "MSG_08": "Aplicar",
       "MSG_10": "¡Éxito! Configuraciones guardadas.",
       "MSG_12": "Abrir",
       "MSG_13": "Salir",
       "MSG_20": "Mañana",
       "MSG_21": "Tarde",
       "MSG_22": "Noche",
       "MSG_23": "Medianoche",
       "Language": "ES"
   }
   ```

## Usage

### Step 1: Run the Application

Execute the main script to start the application:

```bash
python main/main.py
```

### Step 2: Adjust Brightness Levels

- **Main Interface**: Allows adjusting brightness levels for different times of the day.
- **Buttons**:
  - **Apply**: Saves the settings and applies the brightness levels.
  - **Minimize**: Minimizes the application to the system tray.
  - **Close**: Completely exits the application.
  - **Settings**: Opens the settings window for advanced adjustments (such as changing the language).

### Step 3: Interact with the System Tray

- **Left Click** on the tray icon to restore the main window.
- **Right Click** on the tray icon to access the context menu with options like "Open" and "Exit".

### Step 4: Change Language

1. Click on the **Settings** button (⚙) in the main interface.
2. Select the desired language.
3. Changes will be automatically applied to the interface and the tray menu.

## Configuration Management

User configurations, including brightness levels and selected language, are persistently stored via the `ConfigManager`. This ensures preferences are maintained across sessions.

## Error Handling

The application includes error handling for:

- **Invalid Inputs**: Ensures brightness levels are valid integers.
- **Language Loading Issues**: Notifies the user if language strings cannot be loaded.
- **Tray Icon Failures**: Safely manages the creation and destruction of the tray icon.

## Contributing

Feel free to fork this project and submit pull requests for improvements or new features. Please ensure your code is clean and follows the existing code style.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

```plaintext
# requirements.txt

pystray==0.19.3
Pillow==9.5.0
```
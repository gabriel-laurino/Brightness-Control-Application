---

# Brightness Control Application

This application allows users to manage SDR brightness levels on HDR-enabled screens in Windows 11. It includes features such as multilingual support, configuration management, and system tray integration for easy access and control.

## Project Overview

The project is structured following the **MVC (Model-View-Controller)** pattern, ensuring a clear separation of concerns and facilitating maintenance and scalability;

**The project is in Alpha and is still in the development process, many things could be wrong, especially in the division of class tasks and code organization.**

### Technologies Used:

- **Tkinter**: For creating the graphical user interface.
- **pystray**: For integrating the application with the system tray.
- **Pillow**: For handling images used in the tray icon.
- **JSON**: For storing and managing language strings and configurations.
- **PowerShell**: For executing brightness adjustments on the system through automation scripts.
- **Portable Python**: Bundled with all necessary dependencies, eliminating the need for separate installations.

### Features:

- **SDR Brightness Control**: Adjusts SDR brightness levels on HDR-enabled displays in Windows 11.
- **Multilingual Support**: English and Portuguese are supported, with language configuration stored in a single `lang.json` file.
- **System Tray Integration**: Provides quick access to main functionalities via the system tray icon.
- **Configuration Management**: Stores user preferences, such as brightness levels and time-based adjustments, persistently.
- **Data Validation**: Ensures user inputs are valid and consistent.
- **Automated Brightness Adjustment**: Adjusts brightness automatically based on user-defined schedules using PowerShell.

## Project Structure

```bash
.
├── controller
│   ├── settings_controller.py      # Manages settings logic and updates configurations
│   ├── adjust_brightness.ps1       # PowerShell script to automate brightness changes based on time
│   └── brightness_controller.py    # Main controller managing brightness logic and interaction with the view
├── model
│   └── data_model.py               # Manages loading and saving data configurations (config.json)
├── services
│   ├── powershell_service.py       # Service for managing the Shell script
│   └── tray_service.py             # Service for managing the system tray icon
├── views
│   ├── brightness_view.py          # Main graphical interface for brightness control
│   ├── settings_view.py            # Settings graphical interface for configuring options
│   └── view_helper.py              # Assists in creating and managing UI widgets
├── data
│   ├── config.json                 # Stores user configurations (brightness levels, schedules, language)
│   └── lang.json                   # Language strings for English and Portuguese
├── main
│   └── main.py                     # Entry point of the application
├── python                          # Folder with all necessary dependencies to run the application (Portable Python)
├── README.md                       # Project documentation (this file)
├── LICENSE                         # Project license file (MIT)
├── Run.vbs                         # VBScript to completely launch the application
└── requirements.txt                # List of project dependencies
```

### Key Files:

- **brightness_controller.py**: Controls the interaction between the GUI, services, and models.
- **settings_controller.py**: Manages the logic behind adjusting settings (e.g., schedule, language) and updating configurations.
- **adjust_brightness.ps1**: A PowerShell script that automatically adjusts brightness levels based on the defined schedule.
- **tray_service.py**: Manages the system tray icon, including handling click events and context menus.
- **brightness_view.py**: Defines and updates the graphical interface elements related to brightness control.
- **view_helper.py**: Provides helper methods for creating consistent widgets across views.
- **config.json**: Stores user settings such as brightness levels, time-based schedules, and the selected language.
- **lang.json**: Contains translations for supported languages (English and Portuguese).

## Usage

### Step 1: Download the latest Release and run the Application

Double click the `Run.vbs` file to start the application.

### Step 2: Adjust Brightness Levels

- **ADVICE**: Please use values between 0 and 100. Currently, there is no validation to limit the numbers to a maximum of 100, which can make your screen VERY bright.

- **Main Interface**: Allows adjusting SDR brightness levels for different times of the day (Morning, Afternoon, Evening, Night).
- **Buttons**:
  - **Apply**: Saves the settings and applies the brightness levels.
  - **Minimize**: Minimizes the application to the system tray.
  - **Close**: Completely exits the application.
  - **Settings**: Opens the settings window for advanced adjustments (such as changing the language or configuring brightness schedules).

### Step 3: Interact with the System Tray

- **Left Click** on the tray icon to restore the main window.
- **Right Click** on the tray icon to access the context menu with options like "Open" and "Exit".

### Step 4: Automate Brightness Adjustment

To automate brightness changes based on time:
1. Configure the time schedule in the **Settings** window.
2. The `adjust_brightness.ps1` script will handle the automatic adjustments based on the defined times in the `config.json` file.

### Step 5: Adjust Language

1. Open the **Settings** window via the settings button (⚙).
2. Select either English or Portuguese from the available options.
3. Changes will be automatically applied to the interface and the tray menu.

### For Devs: 

## If you prefer to just clone the repository and not download the Release, the python folder will not be present in your project, so you will need python 3.12 installed and the necessary dependencies.

## Configuration Management

The application stores user settings, including brightness levels, time schedules, and selected language, in the `config.json` file located in the `data/` directory. This ensures that user preferences persist across sessions.

## Error Handling

The application includes error handling for:

- **Invalid Inputs**: Ensures brightness levels are valid integers.
- **Language Loading Issues**: Notifies the user if language strings cannot be loaded from `lang.json`.
- **Tray Icon Failures**: Safely manages the creation and destruction of the tray icon.
- **PowerShell Execution Issues**: Handles errors related to the automatic execution of the PowerShell script for brightness adjustment.

## Contributing

Feel free to fork this project and submit pull requests for improvements or new features. Please ensure your code is clean and follows the existing code style.

## License

<<<<<<< HEAD
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
=======
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
>>>>>>> b35fd3f0c7463b9b5a401659957c89cdfbf4180d

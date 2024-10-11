import os
import sys

# Setup paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.chdir(project_root)

# Agora que o sys.path foi atualizado, importe o LogService
from services.log_service import LogService

# Initialize logging service
log_service = LogService()

# Set Python Path (embedded or system)
log_service.set_embedded_python_path()

try:
    from tkinter import Tk
except ImportError as e:
    log_service.log_error(
        "Tkinter is required but not found. Please install it or use the embedded Python."
    )
    sys.exit(1)

from controller.brightness_controller import BrightnessController
from services.powershell_service import PowerShellService

def main():
    try:
        # Define the absolute path to the PowerShell script
        script_path = os.path.join(project_root, "controller", "adjust_brightness.ps1")

        # Initialize PowerShellService
        powershell_service = PowerShellService(script_path)
        powershell_service.start_powershell()
        powershell_service.start_monitoring()

        # Initialize Tkinter root
        root = Tk()

        # Initialize BrightnessController with root and PowerShellService
        controller = BrightnessController(root, powershell_service)

        # Run the application
        controller.run()

    except Exception as e:
        log_service.log_error(f"An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        if "powershell_service" in locals() and powershell_service:
            powershell_service.stop_powershell()
            
        log_service.finalize_log_file()

if __name__ == "__main__":
    main()

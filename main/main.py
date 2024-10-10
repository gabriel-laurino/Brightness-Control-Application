import logging
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.chdir(project_root)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Logs will be displayed in the console
    ]
)

# Determine if the embedded Python directory exists
script_dir = os.path.dirname(os.path.abspath(__file__))
python_dir = os.path.abspath(os.path.join(script_dir, '..', 'python'))
dll_dir = os.path.join(python_dir, 'DLLs')

# If the embedded Python exists, configure PATH and sys.path
if os.path.exists(python_dir):
    logging.info("Using embedded Python.")
    os.environ['PATH'] = dll_dir + os.pathsep + os.environ.get('PATH', '')
    sys.path.insert(0, dll_dir)
else:
    logging.info("Using system Python.")

# Now import tkinter
try:
    from tkinter import Tk, Label
except ImportError as e:
    logging.error("Tkinter is required but not found. Please install it or use the embedded Python.")
    sys.exit(1)

from controller.brightness_controller import BrightnessController
from services.powershell_service import PowerShellService

def main():
    # Define the absolute path to the PowerShell script
    script_path = os.path.join(project_root, "controller", "adjust_brightness.ps1")
    
    # Initialize PowerShellService
    powershell_service = PowerShellService(script_path)
    powershell_service.start_powershell()
    
    # Initialize Tkinter root
    root = Tk()
    
    # Initialize BrightnessController with root and PowerShellService
    controller = BrightnessController(root, powershell_service)
    
    # Run the application
    controller.run()

if __name__ == "__main__":
    main()

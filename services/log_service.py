import logging
import os
import sys
import shutil
from datetime import datetime
import time
from logging.handlers import RotatingFileHandler


class LogService:

    # Log configuration parameters
    create_log_file = True
    log_level = logging.DEBUG  # INFO | ERROR | WARNING | DEBUG | CRITICAL

    def __init__(self, log_level=log_level, log_to_file=create_log_file):
        self.log_file_path = "running_app.log"
        # Configure logging settings
        self.setup_logging(log_level, log_to_file)

    def setup_logging(self, log_level, log_to_file):
        handlers = [logging.StreamHandler()]

        # Use RotatingFileHandler instead of FileHandler
        if log_to_file:
            rotating_handler = RotatingFileHandler(
                self.log_file_path,
                maxBytes=5 * 1024 * 1024,
                backupCount=5,
            )
            handlers.append(rotating_handler)

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=handlers,
        )
        self.log_info("Logging service initialized.")

    def set_embedded_python_path(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        python_dir = os.path.abspath(os.path.join(script_dir, "..", "python"))
        dll_dir = os.path.join(python_dir, "DLLs")

        if os.path.exists(python_dir):
            self.log_info("Using embedded Python.")
            os.environ["PATH"] = dll_dir + os.pathsep + os.environ.get("PATH", "")
            if dll_dir not in sys.path:
                sys.path.insert(0, dll_dir)
        else:
            self.log_info("Using system Python.")

    def log_info(self, message):
        logging.info(message)

    def log_error(self, message):
        logging.error(message)

    def log_warning(self, message):
        logging.warning(message)

    def log_debug(self, message):
        logging.debug(message)

    def log_critical(self, message):
        logging.critical(message)

    def finalize_log_file(self):
        try:
            # Close all logging handlers to release the file
            root_logger = logging.getLogger()
            handlers = root_logger.handlers[:]
            for handler in handlers:
                handler.close()
                root_logger.removeHandler(handler)

            # Wait briefly to ensure that the file is fully released
            time.sleep(0.5)

            # Check if the log file exists before renaming
            if os.path.exists(self.log_file_path):
                # Create the logs directory if it doesn't exist
                logs_dir = os.path.join(
                    os.path.abspath(os.path.dirname(__file__)), "..", "logs"
                )
                if not os.path.exists(logs_dir):
                    os.makedirs(logs_dir)

                # Format the current date and time for the filename
                timestamp = datetime.now().strftime("%d-%m-%y_%H-%M")
                new_log_filename = f"{timestamp}_app.log"
                new_log_path = os.path.join(logs_dir, new_log_filename)

                shutil.move(self.log_file_path, new_log_path)
                print(f"Log file saved as: {new_log_path}")
            else:
                print("No running log file found to finalize.")
        except Exception as e:
            logging.error(f"Unexpected error occurred while finalizing log file: {e}")

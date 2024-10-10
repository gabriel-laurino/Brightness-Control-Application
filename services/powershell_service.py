import os
import subprocess
import signal
import atexit
import logging


class PowerShellService:
    def __init__(self, script_path):
        self.script_path = script_path
        self.powershell_process = None
        self._stopped = False
        atexit.register(self.stop_powershell)
        logging.info(f"PowerShellService initialized with script: {self.script_path}")

    def start_powershell(self):
        if self.powershell_process is None:
            logging.info(f"Starting PowerShell with script: {self.script_path}")
            try:
                self.powershell_process = subprocess.Popen(
                    [
                        "powershell.exe",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        self.script_path,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW,  # This flag prevents the window from opening
                )
                logging.info(
                    f"PowerShell process started with PID: {self.powershell_process.pid}"
                )
            except Exception as e:
                logging.error(f"Failed to start PowerShell: {e}")

    def stop_powershell(self):
        if self._stopped:
            return
        self._stopped = True
        if self.powershell_process:
            logging.info(
                f"Attempting to terminate PowerShell process with PID: {self.powershell_process.pid}"
            )
            self.powershell_process.terminate()
            try:
                self.powershell_process.wait(timeout=5)
                logging.info(
                    f"PowerShell process with PID {self.powershell_process.pid} terminated successfully."
                )
            except subprocess.TimeoutExpired:
                logging.warning(
                    f"Timeout expired. Forcing termination of PowerShell process with PID: {self.powershell_process.pid}"
                )
                try:
                    os.kill(self.powershell_process.pid, signal.SIGKILL)
                    logging.info(
                        f"PowerShell process with PID {self.powershell_process.pid} was forcefully terminated."
                    )
                except Exception as e:
                    logging.error(f"Failed to forcefully terminate the process: {e}")
            self.powershell_process = None
        else:
            logging.info("No PowerShell process is running to terminate.")

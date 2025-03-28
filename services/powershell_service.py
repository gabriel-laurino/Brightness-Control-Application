import os
import subprocess
import signal
import atexit
import logging
import threading
import time


class PowerShellService:
    def __init__(self, script_path):
        self.script_path = script_path
        self.powershell_process = None
        self._stopped = False
        self._stop_requested = threading.Event()
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
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                logging.info(
                    f"PowerShell process started with PID: {self.powershell_process.pid}"
                )
            except Exception as e:
                logging.error(f"Failed to start PowerShell: {e}")

    def stop_powershell(self):
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

    def monitor_powershell(self):
        while not self._stopped:
            if self.powershell_process:
                return_code = self.powershell_process.poll()
                if return_code is not None:
                    logging.error(
                        f"PowerShell process with PID {self.powershell_process.pid} exited with return code {return_code}"
                    )
                    self.powershell_process = None
                    # Restart the PowerShell process
                    logging.info("Attempting to restart PowerShell process.")
                    self.start_powershell()
                else:
                    logging.debug(
                        f"PowerShell process with PID {self.powershell_process.pid} is still running."
                    )
            else:
                logging.info("No PowerShell process is running. Starting a new one.")
                self.start_powershell()

            time.sleep(3)

    def start_monitoring(self):
        monitoring_thread = threading.Thread(
            target=self.monitor_powershell, daemon=True
        )
        monitoring_thread.start()
        logging.info("Started monitoring PowerShell process.")

        stop_thread = threading.Thread(
            target=self._stop_powershell_every_60s, daemon=True
        )
        stop_thread.start()
        logging.info("Started auto-stop thread for PowerShell process.")

    def _stop_powershell_every_60s(self):
        # Start a thread to restart the process every 60 seconds (To fix a little problem with de PS not changing the brightness after a while)
        while not self._stopped:
            time.sleep(60)
            if not self._stopped:
                logging.info("Stopping PowerShell process to ensure periodic refresh.")
                self.stop_powershell()

                time.sleep(2)

                self._stopped = False
                self._stop_requested.clear()

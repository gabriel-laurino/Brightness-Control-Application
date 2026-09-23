"""Owns exactly one hidden PowerShell brightness worker."""
from __future__ import annotations

import logging
import subprocess
import time
from pathlib import Path

from PySide6.QtCore import QObject, QTimer, Signal


class BrightnessRunner(QObject):
    status_changed = Signal(bool, str)

    def __init__(self, script: Path, log_path: Path, parent=None):
        super().__init__(parent)
        self.script = Path(script)
        self.log_path = Path(log_path)
        self.process: subprocess.Popen | None = None
        self.log_stream = None
        self.started_at = 0.0
        self.retry_at = 0.0
        self.failures = 0
        self.stopping = False
        self.timer = QTimer(self)
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self._poll)

    def start(self) -> None:
        self.stopping = False
        self._launch()
        self.timer.start()

    def _launch(self) -> None:
        if self.stopping or self.process is not None:
            return
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_stream = self.log_path.open("ab", buffering=0)
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = subprocess.SW_HIDE
        try:
            self.process = subprocess.Popen(
                ["powershell.exe", "-NoLogo", "-NoProfile", "-NonInteractive",
                 "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-File", str(self.script)],
                stdin=subprocess.DEVNULL, stdout=self.log_stream, stderr=subprocess.STDOUT,
                startupinfo=startup, creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except Exception as exc:
            logging.exception("Could not start brightness worker")
            self.log_stream.close()
            self.log_stream = None
            self.failures += 1
            self.retry_at = time.monotonic() + min(60, 3 * 2 ** min(self.failures, 4))
            self.status_changed.emit(False, str(exc))
            return
        self.started_at = time.monotonic()
        self.status_changed.emit(True, "")
        logging.info("Brightness worker started with PID %s", self.process.pid)

    def _poll(self) -> None:
        if self.stopping:
            return
        now = time.monotonic()
        if self.process is None:
            if now >= self.retry_at:
                self._launch()
            return
        return_code = self.process.poll()
        if return_code is not None:
            logging.error("Brightness worker exited with code %s", return_code)
            self._close_stream()
            self.process = None
            self.failures += 1
            self.retry_at = now + min(60, 3 * 2 ** min(self.failures, 4))
            self.status_changed.emit(False, f"PowerShell exited ({return_code})")
        elif now - self.started_at >= 60:
            # Preserve the existing installation's 60-second refresh workaround.
            self._terminate()
            self.failures = 0
            self.retry_at = now + 2

    def _close_stream(self) -> None:
        if self.log_stream is not None:
            self.log_stream.close()
            self.log_stream = None

    def _terminate(self) -> None:
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
            logging.info("Brightness worker stopped")
            self.process = None
        self._close_stream()

    def stop(self) -> None:
        self.stopping = True
        self.timer.stop()
        self._terminate()

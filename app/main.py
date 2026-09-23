"""Entrypoint for the modern desktop application."""
from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication

from app.config import ConfigStore
from app.instance import InstanceLock
from app.runner import BrightnessRunner
from app.ui import MainWindow, icon


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Brightness Control Application v2.0.1")
    parser.add_argument("--preview", action="store_true", help="Show the UI without starting the brightness worker or writing settings")
    parser.add_argument("--config", type=Path, help="Use an existing config.json (useful for safe previews)")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    config_path = args.config or root / "data" / "config.json"
    log_dir = root / "logs"
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[RotatingFileHandler(log_dir / "studio.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8")],
    )
    app = QApplication(sys.argv[:1])
    app.setApplicationName("Brightness Control Application v2.0.1")
    app.setWindowIcon(icon())
    app.setQuitOnLastWindowClosed(False)
    server = None
    instance_lock = None
    if not args.preview:
        instance_name = f"BrightnessControlApplication-v2-{os.getlogin()}"
        instance_lock = InstanceLock(instance_name)
        if not instance_lock.acquired:
            # A mutex, not QLocalServer.listen(), is the authority on Windows:
            # named pipes can have more than one server instance with one name.
            # Give the owner a moment to finish creating its reopen channel.
            for _attempt in range(12):
                socket = QLocalSocket()
                socket.connectToServer(instance_name)
                if socket.waitForConnected(200):
                    socket.write(b"show")
                    socket.waitForBytesWritten(300)
                    instance_lock.close()
                    return 0
                time.sleep(0.1)
            logging.error("Another brightness instance owns the lock but did not accept the reopen request")
            instance_lock.close()
            return 1
        server = QLocalServer()
        if not server.listen(instance_name):
            # A stale server name may remain after an abnormal exit.
            QLocalServer.removeServer(instance_name)
            if not server.listen(instance_name):
                instance_lock.close()
                raise RuntimeError("Could not create the single-instance channel.")
    script = root / "controller" / "adjust_brightness_v2.ps1"
    runner = None if args.preview else BrightnessRunner(script, log_dir / "brightness-worker.log")
    try:
        try:
            window = MainWindow(ConfigStore(config_path), script, runner=runner, preview=args.preview)
        except Exception:
            logging.exception("Could not initialize Brightness Control Application v2.0.1")
            raise
        if server is not None:
            def show_existing():
                socket = server.nextPendingConnection()
                if socket is not None:
                    window._show_from_tray()
                    socket.disconnectFromServer()
            server.newConnection.connect(show_existing)
        window.show()
        return app.exec()
    finally:
        if instance_lock is not None:
            instance_lock.close()


if __name__ == "__main__":
    raise SystemExit(main())

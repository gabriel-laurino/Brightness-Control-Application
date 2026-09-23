"""Export the code-drawn sun icon for Windows shortcuts and releases."""
from __future__ import annotations

import struct
from pathlib import Path

from PySide6.QtCore import QBuffer, QIODevice
from PySide6.QtWidgets import QApplication

from app.ui import icon


def main() -> None:
    QApplication([])
    pixmap = icon().pixmap(64, 64)
    data = QBuffer()
    data.open(QIODevice.OpenModeFlag.WriteOnly)
    if not pixmap.save(data, "PNG"):
        raise RuntimeError("Could not render the sun icon")
    png = bytes(data.data())
    header = struct.pack("<HHH", 0, 1, 1)
    image = struct.pack("<BBBBHHII", 64, 64, 0, 0, 1, 32, len(png), 22)
    destination = Path(__file__).resolve().parents[1] / "assets" / "sun.ico"
    destination.parent.mkdir(exist_ok=True)
    destination.write_bytes(header + image + png)
    print(destination)


if __name__ == "__main__":
    main()

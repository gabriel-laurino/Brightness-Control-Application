"""Read-only bridge to Windows' per-display HDR state."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path


def discover_monitors(script: Path) -> list[dict]:
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = subprocess.SW_HIDE
    result = subprocess.run(
        ["powershell.exe", "-NoLogo", "-NoProfile", "-NonInteractive",
         "-ExecutionPolicy", "Bypass", "-File", str(script), "-ListMonitors", "-Json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=15, startupinfo=startup, creationflags=subprocess.CREATE_NO_WINDOW,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"Monitor probe failed ({result.returncode}).")
    payload = json.loads(result.stdout)
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list) or any(not isinstance(item, dict) for item in payload):
        raise ValueError("Unexpected monitor probe response.")
    return payload

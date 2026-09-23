# Brightness Control Application v2.0.1

A compact Windows tray app for scheduling the SDR-content brightness boost on HDR displays. The daily control remains a small, borderless popup: click the tray icon, adjust the four periods, and save. It does not occupy the Windows taskbar, and closing the popup silently returns it to the tray. **Ajustes / Settings** opens the detailed schedule, language, and display-status panel.

The current version uses PySide6 for the interface and a separate PowerShell worker for display changes. The original Tkinter application and its `controller/adjust_brightness.ps1` are retained in the repository as the legacy version; the critical original script has not been modified.

The schedule remains stored as 24-hour integers for compatibility. Portuguese displays 24-hour times; English shows 12-hour times with AM/PM in both the tray popup and schedule editor. Switching languages in the editor preserves the selected hours.

## Safety boundary

- `adjust_brightness_v2.ps1` discovers connected display paths, checks whether HDR is *currently active*, and maps each verified HDR display to its Windows `HMONITOR`. SDR displays are excluded. If no HDR target can be verified, no display is changed.
- The existing 0–100 to 1.0–6.0 boost mapping and DWM ordinal 171 are preserved. The DWM call is undocumented, so this remains Windows-version-sensitive; do not change its signature or mapping without testing on real hardware.
- The app does not enable HDR, change monitor modes, open a network port, or send settings to a server.
- `data/config.json` is validated before saving. Writes are atomic and create `data/config.json.bak` for rollback.

## Run locally (Python 3.12 on Windows)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-v2.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

To inspect the interface without starting the brightness worker or writing settings:

```powershell
.\.venv\Scripts\python.exe -m app.main --preview
```

For normal operation, run `Run.v2.ps1` or `pythonw.exe -m app.main` from this folder. The process keeps one worker alive and reopens the existing popup when invoked again. A normal app exit is available from the tray menu. Closing the popup only hides it to the tray.

The `-ListMonitors` switch is read-only:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\controller\adjust_brightness_v2.ps1 -ListMonitors
```

`-RunOnce` **does change brightness** and should only be used to test a known-good level on the actual displays.

## Layout

- `app/config.py`: validation, period calculation, atomic persistence, and rollback copy.
- `app/monitor.py`: read-only monitor-status probe.
- `app/runner.py`: lifecycle and health monitoring for the PowerShell worker.
- `app/ui.py`: compact popup, detailed settings, tray interaction, and custom-painted sliders.
- `app/main.py`: startup and single-instance handling.
- `controller/HdrDisplayTopology.cs`: Windows display topology / HDR state mapping.
- `controller/adjust_brightness_v2.ps1`: guarded multi-HDR adjustment.
- `main/`, `views/`, `model/`, `services/`, and `controller/adjust_brightness.ps1`: preserved legacy application.

## Recovery

The new version can be removed from startup and the original `Run.ps1` shortcut restored without altering legacy source. Restore `data/config.json.bak` if a settings edit must be rolled back. Do not run the old and new brightness workers together because they would compete for the same HDR setting.

Licensed under [MIT](LICENSE).

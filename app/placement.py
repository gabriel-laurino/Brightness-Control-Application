"""Keep the tray popup clear of the Windows taskbar, including auto-hide bars."""
from __future__ import annotations

import ctypes
from ctypes import wintypes

from PySide6.QtCore import QRect


def taskbar_rectangles() -> list[QRect]:
    """Read Shell taskbar bounds; no desktop or window state is changed."""
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    enum_windows = user32.EnumWindows
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    enum_windows.argtypes = [callback_type, wintypes.LPARAM]
    enum_windows.restype = wintypes.BOOL
    get_class = user32.GetClassNameW
    get_class.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    get_class.restype = ctypes.c_int
    get_rect = user32.GetWindowRect
    get_rect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    get_rect.restype = wintypes.BOOL

    bars: list[QRect] = []

    @callback_type
    def visit(handle, _parameter):
        name = ctypes.create_unicode_buffer(64)
        get_class(handle, name, len(name))
        if name.value not in ("Shell_TrayWnd", "Shell_SecondaryTrayWnd"):
            return True
        bounds = wintypes.RECT()
        if get_rect(handle, ctypes.byref(bounds)):
            bars.append(QRect(bounds.left, bounds.top, bounds.right - bounds.left, bounds.bottom - bounds.top))
        return True

    enum_windows(visit, 0)
    return bars


def safe_bottom(screen: QRect, available: QRect, bars: list[QRect], gap: int = 12) -> int:
    """Return an exclusive bottom edge above any bottom taskbar on this screen."""
    reserve = 0
    for bar in bars:
        horizontal_overlap = max(0, min(screen.right(), bar.right()) - max(screen.left(), bar.left()) + 1)
        near_bottom = abs(bar.top() - screen.bottom()) <= 80
        if horizontal_overlap >= screen.width() * 0.4 and bar.width() > bar.height() * 3 and near_bottom:
            # Auto-hide taskbars can report a rect almost fully below the screen.
            reserve = max(reserve, min(bar.height(), 80))
    return min(available.bottom() + 1, screen.bottom() + 1 - reserve) - gap

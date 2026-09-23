"""Windows session-scoped lock for the one brightness worker invariant."""
from __future__ import annotations

import ctypes
from ctypes import wintypes


class InstanceLock:
    def __init__(self, name: str):
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._close = kernel32.CloseHandle
        self._close.argtypes = [wintypes.HANDLE]
        self._close.restype = wintypes.BOOL
        create = kernel32.CreateMutexW
        create.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
        create.restype = wintypes.HANDLE
        self._handle = create(None, False, f"Local\\{name}")
        if not self._handle:
            raise OSError(ctypes.get_last_error(), "Could not acquire application instance lock")
        self.acquired = ctypes.get_last_error() != 183  # ERROR_ALREADY_EXISTS

    def close(self) -> None:
        if self._handle:
            self._close(self._handle)
            self._handle = None

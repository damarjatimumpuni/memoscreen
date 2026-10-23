"""Windows session helpers: locking the workstation and detecting its state."""

import ctypes
import sys

# GetUserObjectInformation request for the desktop name.
_UOI_NAME = 2
# Access right that allows opening the currently displayed desktop.
_DESKTOP_SWITCHDESKTOP = 0x0100
# Desktop the shell switches to while the session is locked.
_LOCKED_DESKTOP = "winlogon"

_user32 = None


def _get_user32():
    """Return the user32 library with the prototypes we need."""
    global _user32
    if _user32 is None:
        from ctypes import wintypes

        lib = ctypes.WinDLL("user32", use_last_error=True)
        lib.LockWorkStation.restype = wintypes.BOOL
        lib.OpenInputDesktop.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        lib.OpenInputDesktop.restype = wintypes.HANDLE
        lib.GetUserObjectInformationW.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
        ]
        lib.GetUserObjectInformationW.restype = wintypes.BOOL
        lib.CloseDesktop.argtypes = [wintypes.HANDLE]
        lib.CloseDesktop.restype = wintypes.BOOL
        _user32 = lib
    return _user32


def lock_workstation() -> bool:
    """Lock the Windows session, the same way Win+L does.

    Returns True when the workstation was locked.
    """
    if sys.platform != "win32":
        return False
    try:
        return bool(_get_user32().LockWorkStation())
    except (AttributeError, OSError, ValueError):
        return False


def is_workstation_locked() -> bool:
    """Return True while the session is locked.

    While the session is locked, the input desktop is the Winlogon one
    instead of the normal shell desktop.
    """
    if sys.platform != "win32":
        return False
    try:
        lib = _get_user32()
        desktop = lib.OpenInputDesktop(0, False, _DESKTOP_SWITCHDESKTOP)
        if not desktop:
            return True
        try:
            needed = ctypes.c_ulong(0)
            lib.GetUserObjectInformationW(desktop, _UOI_NAME, None, 0, ctypes.byref(needed))
            buffer = ctypes.create_unicode_buffer(needed.value)
            lib.GetUserObjectInformationW(
                desktop, _UOI_NAME, buffer, needed.value, ctypes.byref(needed)
            )
            return buffer.value.lower() == _LOCKED_DESKTOP
        finally:
            lib.CloseDesktop(desktop)
    except (AttributeError, OSError, ValueError):
        return False

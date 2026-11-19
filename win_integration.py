from __future__ import annotations

import os
import sys
import webbrowser
from pathlib import Path
from typing import Iterable, Optional

try:
    import winreg
except ImportError:  # pragma: no cover - non-Windows fallback
    winreg = None  # type: ignore

from config import GOOGLE_MIME_TYPES

CONTEXT_MENU_KEY_NAME = "OpenInGoogle"


def get_launch_command() -> str:
    if getattr(sys, "frozen", False):
        exe_path = Path(sys.executable).resolve()
        return f'"{exe_path}" "%1"'

    python_exe = Path(sys.executable).resolve()
    pythonw = python_exe.with_name("pythonw.exe")
    runner = pythonw if pythonw.exists() else python_exe
    main_script = Path(__file__).resolve().with_name("OpenInGoogle.py")
    return f'"{runner}" "{main_script}" "%1"'


def get_icon_path() -> Optional[str]:
    if getattr(sys, "frozen", False):
        return f'"{Path(sys.executable).resolve()}",0'
    return None


def _shell_subkey(ext: str) -> str:
    ext = ext if ext.startswith(".") else f".{ext}"
    return rf"Software\Classes\SystemFileAssociations\{ext.lower()}\shell\{CONTEXT_MENU_KEY_NAME}"


def register_context_menu(
    extensions: Iterable[str],
    menu_label: str = "Google で開く (OpenInGoogle)",
) -> None:
    if winreg is None:
        raise RuntimeError("Windows registry integration is only supported on Windows.")

    command = get_launch_command()
    icon = get_icon_path()

    for ext in extensions:
        subkey = _shell_subkey(ext)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, subkey) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, menu_label)
            if icon:
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"{subkey}\command") as cmd_key:
            winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, command)


def _delete_tree(root: int, subkey: str) -> None:
    if winreg is None:
        return
    try:
        with winreg.OpenKey(root, subkey, 0, winreg.KEY_ALL_ACCESS) as key:
            while True:
                try:
                    child = winreg.EnumKey(key, 0)
                    _delete_tree(root, rf"{subkey}\{child}")
                except OSError:
                    break
        winreg.DeleteKey(root, subkey)
    except FileNotFoundError:
        pass


def unregister_context_menu(extensions: Iterable[str] = GOOGLE_MIME_TYPES.keys()) -> None:
    if winreg is None:
        return
    for ext in extensions:
        _delete_tree(winreg.HKEY_CURRENT_USER, _shell_subkey(ext))


def is_context_menu_registered(extensions: Iterable[str] = (".docx", ".xlsx", ".pptx")) -> bool:
    if winreg is None:
        return False
    for ext in extensions:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _shell_subkey(ext)):
                return True
        except FileNotFoundError:
            continue
    return False


def open_windows_default_apps() -> None:
    if os.name == "nt":
        os.startfile("ms-settings:defaultapps")  # type: ignore[attr-defined]
    else:
        webbrowser.open("https://support.microsoft.com/windows")

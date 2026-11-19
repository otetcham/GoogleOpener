from __future__ import annotations

import ctypes
import os
import shutil
import sys
import webbrowser
from pathlib import Path
from typing import Dict, Iterable, Optional

try:
    import winreg
except ImportError:  # pragma: no cover - non-Windows fallback
    winreg = None  # type: ignore

from config import GOOGLE_MIME_TYPES, ICONS_DIR

CONTEXT_MENU_KEY_NAME = "OpenInGoogle"

EXTENSION_ICON_MAP: Dict[str, str] = {
    ".doc": "docs.ico",
    ".docx": "docs.ico",
    ".rtf": "docs.ico",
    ".odt": "docs.ico",
    ".xls": "sheets.ico",
    ".xlsx": "sheets.ico",
    ".xlsm": "sheets.ico",
    ".ods": "sheets.ico",
    ".csv": "sheets.ico",
    ".ppt": "slides.ico",
    ".pptx": "slides.ico",
    ".odp": "slides.ico",
}


def _bundle_icons_dir() -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / "assets" / "icons"


def deploy_icons() -> Path:
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    src_dir = _bundle_icons_dir()
    for icon_name in ("docs.ico", "sheets.ico", "slides.ico"):
        src = src_dir / icon_name
        if src.exists():
            shutil.copy2(src, ICONS_DIR / icon_name)
    return ICONS_DIR


def get_icon_for_extension(ext: str) -> Optional[str]:
    ext = ext.lower() if ext.startswith(".") else f".{ext.lower()}"
    icon_name = EXTENSION_ICON_MAP.get(ext)
    if icon_name:
        deployed = deploy_icons() / icon_name
        if deployed.exists():
            return f'"{deployed}",0'
    if getattr(sys, "frozen", False):
        return f'"{Path(sys.executable).resolve()}",0'
    return None


def get_launch_command() -> str:
    if getattr(sys, "frozen", False):
        exe_path = Path(sys.executable).resolve()
        return f'"{exe_path}" "%1"'

    python_exe = Path(sys.executable).resolve()
    pythonw = python_exe.with_name("pythonw.exe")
    runner = pythonw if pythonw.exists() else python_exe
    main_script = Path(__file__).resolve().with_name("OpenInGoogle.py")
    return f'"{runner}" "{main_script}" "%1"'


def notify_shell_assoc_changed() -> None:
    if os.name == "nt":
        try:
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
        except Exception:
            pass


def _shell_subkey(ext: str) -> str:
    ext = ext if ext.startswith(".") else f".{ext}"
    return rf"Software\Classes\SystemFileAssociations\{ext.lower()}\shell\{CONTEXT_MENU_KEY_NAME}"


def register_file_icons(extensions: Iterable[str] = GOOGLE_MIME_TYPES.keys()) -> None:
    if winreg is None:
        raise RuntimeError("Windows registry integration is only supported on Windows.")

    deploy_icons()
    command = get_launch_command()

    for ext in extensions:
        ext_norm = ext.lower() if ext.startswith(".") else f".{ext.lower()}"
        prog_id = f"OpenInGoogle{ext_norm}"
        icon_val = get_icon_for_extension(ext_norm)

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}\shell\open\command") as cmd_key:
            winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, command)

        if icon_val:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}\DefaultIcon") as icon_key:
                winreg.SetValueEx(icon_key, "", 0, winreg.REG_SZ, icon_val)

            # Also update context menu icon if already registered
            ctx_subkey = _shell_subkey(ext_norm)
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, ctx_subkey, 0, winreg.KEY_SET_VALUE) as ctx_key:
                    winreg.SetValueEx(ctx_key, "Icon", 0, winreg.REG_SZ, icon_val)
            except FileNotFoundError:
                pass

    notify_shell_assoc_changed()


def register_context_menu(
    extensions: Iterable[str],
    menu_label: str = "Google で開く (OpenInGoogle)",
) -> None:
    if winreg is None:
        raise RuntimeError("Windows registry integration is only supported on Windows.")

    deploy_icons()
    command = get_launch_command()

    for ext in extensions:
        ext_norm = ext.lower() if ext.startswith(".") else f".{ext.lower()}"
        subkey = _shell_subkey(ext_norm)
        icon = get_icon_for_extension(ext_norm)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, subkey) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, menu_label)
            if icon:
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"{subkey}\command") as cmd_key:
            winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, command)

    notify_shell_assoc_changed()


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
    notify_shell_assoc_changed()


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

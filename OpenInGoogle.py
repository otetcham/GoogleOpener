from __future__ import annotations

import os
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Optional

from cache_db import CacheDB
from config import (
    APPDATA_DIR,
    APP_NAME,
    GOOGLE_API_LIBRARY_URL,
    GOOGLE_CLOUD_CONSOLE_URL,
    GOOGLE_CREDENTIALS_URL,
    HELP_FILE,
    AppSettings,
    load_settings,
)
from drive_client import UICallbacks, process_file_open
from gui_settings import SettingsWindow
from i18n import t
from win_integration import register_context_menu, unregister_context_menu


def ensure_help_file(lang: str = "ja") -> None:
    APPDATA_DIR.mkdir(parents=True, exist_ok=True)
    text = t(
        "help_text",
        lang,
        app_dir=APPDATA_DIR,
        console_url=GOOGLE_CLOUD_CONSOLE_URL,
        api_url=GOOGLE_API_LIBRARY_URL,
        cred_url=GOOGLE_CREDENTIALS_URL,
    )
    HELP_FILE.write_text(text, encoding="utf-8")


def show_box(title: str, message: str, error: bool = False) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        if error:
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)
        root.destroy()
    except Exception:
        print(f"{title}\n{message}")


def ask_yes_no(title: str, message: str) -> bool:
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        result = messagebox.askyesno(title, message)
        root.destroy()
        return bool(result)
    except Exception:
        print(f"{title}\n{message}")
        return False


def ask_yes_no_cancel(title: str, message: str) -> Optional[bool]:
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        result = messagebox.askyesnocancel(title, message)
        root.destroy()
        return result
    except Exception:
        print(f"{title}\n{message}")
        return None


def open_credentials_folder(lang: str = "ja") -> None:
    ensure_help_file(lang)
    try:
        os.startfile(str(APPDATA_DIR))  # type: ignore[attr-defined]
    except Exception:
        webbrowser.open(str(APPDATA_DIR))


def open_text_file_in_notepad(path: Path) -> None:
    try:
        subprocess.Popen(["notepad.exe", str(path)])
    except Exception:
        try:
            os.startfile(str(path))  # type: ignore[attr-defined]
        except Exception:
            webbrowser.open(str(path))


def open_setup_guide(lang: str = "ja") -> None:
    ensure_help_file(lang)
    open_text_file_in_notepad(HELP_FILE)


def open_google_cloud_pages() -> None:
    webbrowser.open(GOOGLE_CLOUD_CONSOLE_URL)
    webbrowser.open(GOOGLE_API_LIBRARY_URL)
    webbrowser.open(GOOGLE_CREDENTIALS_URL)


def run_credentials_setup_prompt(lang: str = "ja") -> None:
    ensure_help_file(lang)
    open_credentials_folder(lang)
    open_setup_guide(lang)

    msg = t("setup_prompt_msg", lang, app_dir=APPDATA_DIR)
    if ask_yes_no(t("setup_prompt_title", lang), msg):
        open_google_cloud_pages()


def open_office_file(file_path: str, settings: Optional[AppSettings] = None) -> None:
    active_settings = settings or load_settings()
    ensure_help_file(active_settings.language)
    cache_db = CacheDB()
    callbacks = UICallbacks(
        ask_yes_no=ask_yes_no,
        ask_yes_no_cancel=ask_yes_no_cancel,
        on_missing_credentials=lambda: run_credentials_setup_prompt(active_settings.language),
    )
    process_file_open(
        file_path=file_path,
        settings=active_settings,
        cache_db=cache_db,
        callbacks=callbacks,
        open_browser=True,
    )


def open_settings_gui() -> None:
    window = SettingsWindow(
        open_file_callback=lambda p: open_office_file(p, load_settings()),
        open_setup_guide_callback=open_setup_guide,
        open_appdata_callback=lambda: open_credentials_folder(load_settings().language),
    )
    window.run()


def main() -> int:
    settings = load_settings()
    lang = settings.language
    ensure_help_file(lang)

    if len(sys.argv) >= 2:
        arg = sys.argv[1]
        if arg == "--open-credentials-folder":
            open_credentials_folder(lang)
            return 0
        if arg == "--setup-credentials":
            run_credentials_setup_prompt(lang)
            return 0
        if arg == "--open-google-cloud-setup":
            open_google_cloud_pages()
            return 0
        if arg == "--settings":
            open_settings_gui()
            return 0
        if arg == "--register-context-menu":
            register_context_menu(settings.enabled_extensions)
            return 0
        if arg == "--unregister-context-menu":
            unregister_context_menu()
            return 0

        try:
            open_office_file(arg, settings)
            return 0
        except Exception as exc:
            show_box(t("app_title", lang), str(exc), error=True)
            return 1

    open_settings_gui()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

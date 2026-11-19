from __future__ import annotations

import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Callable, Dict

from cache_db import CacheDB
from config import (
    APPDATA_DIR,
    CREDENTIALS_FILE,
    DUPLICATE_MODE_ALWAYS_NEW,
    DUPLICATE_MODE_ASK,
    DUPLICATE_MODE_OPEN_OR_NEW,
    DUPLICATE_MODE_OPEN_OR_UPDATE,
    GOOGLE_CLOUD_CONSOLE_URL,
    GOOGLE_MIME_TYPES,
    TOKEN_FILE,
    AppSettings,
    load_settings,
    save_settings,
)
from drive_client import get_drive_service, sign_out
from i18n import t
from win_integration import (
    is_context_menu_registered,
    open_windows_default_apps,
    register_context_menu,
    unregister_context_menu,
)


class SettingsWindow:
    def __init__(
        self,
        open_file_callback: Callable[[str], None],
        open_setup_guide_callback: Callable[[str], None],
        open_appdata_callback: Callable[[], None],
    ) -> None:
        self.open_file_callback = open_file_callback
        self.open_setup_guide_callback = open_setup_guide_callback
        self.open_appdata_callback = open_appdata_callback

        self.settings: AppSettings = load_settings()
        self.cache_db = CacheDB()

        self.root = tk.Tk()
        self.root.geometry("760x620")
        self.root.minsize(700, 560)

        self._build_ui()

    def _tr(self, key: str, **kwargs) -> str:
        return t(key, self.settings.language, **kwargs)

    def _clear_root(self) -> None:
        for widget in self.root.winfo_children():
            widget.destroy()

    def _build_ui(self) -> None:
        self._clear_root()
        self.root.title(self._tr("app_title"))

        container = ttk.Frame(self.root, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(container)
        notebook.pack(fill=tk.BOTH, expand=True)

        tab_general = ttk.Frame(notebook, padding=12)
        tab_upload = ttk.Frame(notebook, padding=12)
        tab_windows = ttk.Frame(notebook, padding=12)

        notebook.add(tab_general, text=self._tr("tab_general"))
        notebook.add(tab_upload, text=self._tr("tab_upload"))
        notebook.add(tab_windows, text=self._tr("tab_windows"))

        self._build_general_tab(tab_general)
        self._build_upload_tab(tab_upload)
        self._build_windows_tab(tab_windows)

        footer = ttk.Frame(container, padding=(0, 10, 0, 0))
        footer.pack(fill=tk.X)

        ttk.Button(
            footer,
            text=self._tr("btn_open_file"),
            command=self._on_choose_and_open_file,
        ).pack(side=tk.LEFT)

        ttk.Button(
            footer,
            text=self._tr("btn_save_settings"),
            command=self._on_save_settings,
        ).pack(side=tk.RIGHT)

    def _build_general_tab(self, parent: ttk.Frame) -> None:
        acct_frame = ttk.LabelFrame(parent, text=self._tr("account_section"), padding=10)
        acct_frame.pack(fill=tk.X, pady=(0, 10))

        self.cred_status_var = tk.StringVar()
        self.token_status_var = tk.StringVar()
        self._refresh_auth_status()

        ttk.Label(acct_frame, textvariable=self.cred_status_var).pack(anchor=tk.W, pady=2)
        ttk.Label(acct_frame, textvariable=self.token_status_var).pack(anchor=tk.W, pady=(2, 8))

        btn_row1 = ttk.Frame(acct_frame)
        btn_row1.pack(fill=tk.X, pady=4)
        ttk.Button(btn_row1, text=self._tr("btn_auth_now"), command=self._on_auth_now).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(btn_row1, text=self._tr("btn_logout"), command=self._on_logout).pack(
            side=tk.LEFT, padx=(0, 6)
        )

        btn_row2 = ttk.Frame(acct_frame)
        btn_row2.pack(fill=tk.X, pady=4)
        ttk.Button(
            btn_row2,
            text=self._tr("btn_setup_guide"),
            command=lambda: self.open_setup_guide_callback(self.settings.language),
        ).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(
            btn_row2,
            text=self._tr("btn_open_appdata"),
            command=self.open_appdata_callback,
        ).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(
            btn_row2,
            text=self._tr("btn_open_gcloud"),
            command=lambda: webbrowser.open(GOOGLE_CLOUD_CONSOLE_URL),
        ).pack(side=tk.LEFT)

        lang_frame = ttk.Frame(parent, padding=(0, 8))
        lang_frame.pack(fill=tk.X)
        ttk.Label(lang_frame, text=self._tr("lang_label")).pack(side=tk.LEFT, padx=(0, 8))
        self.lang_var = tk.StringVar(value=self.settings.language)
        ttk.Radiobutton(
            lang_frame, text=self._tr("lang_ja"), variable=self.lang_var, value="ja"
        ).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Radiobutton(
            lang_frame, text=self._tr("lang_en"), variable=self.lang_var, value="en"
        ).pack(side=tk.LEFT)

    def _build_upload_tab(self, parent: ttk.Frame) -> None:
        folder_frame = ttk.Frame(parent)
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(folder_frame, text=self._tr("drive_folder_label")).pack(anchor=tk.W)
        self.drive_folder_var = tk.StringVar(value=self.settings.drive_folder_name)
        ttk.Entry(folder_frame, textvariable=self.drive_folder_var, width=48).pack(
            anchor=tk.W, pady=(4, 0)
        )

        dup_frame = ttk.LabelFrame(parent, text=self._tr("dup_mode_label"), padding=10)
        dup_frame.pack(fill=tk.X, pady=(0, 10))

        self.dup_mode_var = tk.StringVar(value=self.settings.duplicate_mode)
        modes = [
            (DUPLICATE_MODE_OPEN_OR_UPDATE, "dup_mode_open_or_update"),
            (DUPLICATE_MODE_OPEN_OR_NEW, "dup_mode_open_or_new"),
            (DUPLICATE_MODE_ASK, "dup_mode_ask"),
            (DUPLICATE_MODE_ALWAYS_NEW, "dup_mode_always_new"),
        ]
        for val, key in modes:
            ttk.Radiobutton(
                dup_frame, text=self._tr(key), variable=self.dup_mode_var, value=val
            ).pack(anchor=tk.W, pady=2)

        self.match_hash_var = tk.BooleanVar(value=self.settings.match_by_hash_across_paths)
        ttk.Checkbutton(
            dup_frame, text=self._tr("match_hash_label"), variable=self.match_hash_var
        ).pack(anchor=tk.W, pady=(6, 0))

        opt_frame = ttk.Frame(parent)
        opt_frame.pack(fill=tk.X, pady=(0, 8))

        self.convert_var = tk.BooleanVar(value=self.settings.convert_to_google_format)
        ttk.Checkbutton(
            opt_frame, text=self._tr("convert_format_label"), variable=self.convert_var
        ).pack(anchor=tk.W, pady=2)

        self.confirm_upload_var = tk.BooleanVar(value=self.settings.confirm_before_upload)
        ttk.Checkbutton(
            opt_frame, text=self._tr("confirm_upload_label"), variable=self.confirm_upload_var
        ).pack(anchor=tk.W, pady=2)

        excl_frame = ttk.Frame(parent)
        excl_frame.pack(fill=tk.BOTH, expand=True)
        excl_header = ttk.Frame(excl_frame)
        excl_header.pack(fill=tk.X)
        ttk.Label(excl_header, text=self._tr("excluded_folders_label")).pack(side=tk.LEFT)
        ttk.Button(
            excl_header, text=self._tr("btn_add_excluded"), command=self._on_add_excluded_folder
        ).pack(side=tk.RIGHT)

        self.excluded_text = tk.Text(excl_frame, height=4, width=60)
        self.excluded_text.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        if self.settings.excluded_folders:
            self.excluded_text.insert("1.0", "\n".join(self.settings.excluded_folders))

    def _build_windows_tab(self, parent: ttk.Frame) -> None:
        win_frame = ttk.LabelFrame(parent, text=self._tr("win_integration_section"), padding=10)
        win_frame.pack(fill=tk.X, pady=(0, 8))

        self.ctx_status_var = tk.StringVar()
        self._refresh_ctx_status()
        ttk.Label(win_frame, textvariable=self.ctx_status_var).pack(anchor=tk.W, pady=(0, 6))

        btn_row = ttk.Frame(win_frame)
        btn_row.pack(fill=tk.X)
        ttk.Button(
            btn_row, text=self._tr("btn_register_ctx"), command=self._on_register_ctx
        ).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(
            btn_row, text=self._tr("btn_unregister_ctx"), command=self._on_unregister_ctx
        ).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(
            btn_row, text=self._tr("btn_open_default_apps"), command=open_windows_default_apps
        ).pack(side=tk.LEFT)

        ext_frame = ttk.LabelFrame(parent, text=self._tr("extensions_section"), padding=8)
        ext_frame.pack(fill=tk.X, pady=(0, 8))

        self.ext_vars: Dict[str, tk.BooleanVar] = {}
        all_exts = list(GOOGLE_MIME_TYPES.keys())
        for idx, ext in enumerate(all_exts):
            var = tk.BooleanVar(value=(ext in self.settings.enabled_extensions))
            self.ext_vars[ext] = var
            cb = ttk.Checkbutton(ext_frame, text=ext, variable=var)
            cb.grid(row=idx // 6, column=idx % 6, sticky=tk.W, padx=8, pady=2)

        hist_frame = ttk.LabelFrame(parent, text=self._tr("history_section"), padding=8)
        hist_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("file", "updated", "path")
        self.history_tree = ttk.Treeview(hist_frame, columns=columns, show="headings", height=6)
        self.history_tree.heading("file", text=self._tr("col_file"))
        self.history_tree.heading("updated", text=self._tr("col_status"))
        self.history_tree.heading("path", text=self._tr("col_path"))
        self.history_tree.column("file", width=160)
        self.history_tree.column("updated", width=140)
        self.history_tree.column("path", width=360)
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        self.history_tree.bind("<Double-1>", lambda _e: self._on_open_selected_history())

        hist_btns = ttk.Frame(hist_frame, padding=(0, 6, 0, 0))
        hist_btns.pack(fill=tk.X)
        ttk.Button(
            hist_btns,
            text=self._tr("btn_open_selected_history"),
            command=self._on_open_selected_history,
        ).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(
            hist_btns,
            text=self._tr("btn_clear_history"),
            command=self._on_clear_history,
        ).pack(side=tk.RIGHT)

        self._history_links: Dict[str, str] = {}
        self._refresh_history()

    def _refresh_auth_status(self) -> None:
        if CREDENTIALS_FILE.exists():
            self.cred_status_var.set(self._tr("cred_status_ok"))
        else:
            self.cred_status_var.set(self._tr("cred_status_missing"))

        if TOKEN_FILE.exists():
            self.token_status_var.set(self._tr("token_status_ok"))
        else:
            self.token_status_var.set(self._tr("token_status_missing"))

    def _refresh_ctx_status(self) -> None:
        if is_context_menu_registered():
            self.ctx_status_var.set(self._tr("context_menu_status_on"))
        else:
            self.ctx_status_var.set(self._tr("context_menu_status_off"))

    def _refresh_history(self) -> None:
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        self._history_links.clear()

        for idx, entry in enumerate(self.cache_db.list_recent(50)):
            iid = f"row_{idx}"
            name = Path(entry.local_path).name
            self.history_tree.insert("", tk.END, iid=iid, values=(name, entry.updated_at, entry.local_path))
            self._history_links[iid] = entry.web_view_link

    def _collect_settings_from_ui(self) -> AppSettings:
        raw_excluded = self.excluded_text.get("1.0", tk.END).splitlines()
        excluded = [line.strip() for line in raw_excluded if line.strip()]
        enabled_exts = [ext for ext, var in self.ext_vars.items() if var.get()]

        return AppSettings(
            language=self.lang_var.get(),
            drive_folder_name=self.drive_folder_var.get().strip(),
            duplicate_mode=self.dup_mode_var.get(),
            match_by_hash_across_paths=self.match_hash_var.get(),
            convert_to_google_format=self.convert_var.get(),
            confirm_before_upload=self.confirm_upload_var.get(),
            show_duplicate_notice=self.settings.show_duplicate_notice,
            excluded_folders=excluded,
            enabled_extensions=enabled_exts,
        )

    def _on_save_settings(self) -> None:
        old_lang = self.settings.language
        self.settings = self._collect_settings_from_ui()
        save_settings(self.settings)
        messagebox.showinfo(self._tr("settings_saved_title"), self._tr("settings_saved_msg"))
        if self.settings.language != old_lang:
            self._build_ui()

    def _on_add_excluded_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            current = self.excluded_text.get("1.0", tk.END).strip()
            new_text = f"{current}\n{folder}" if current else folder
            self.excluded_text.delete("1.0", tk.END)
            self.excluded_text.insert("1.0", new_text)

    def _on_auth_now(self) -> None:
        try:
            get_drive_service(
                lang=self.settings.language,
                on_missing_credentials=lambda: self.open_setup_guide_callback(self.settings.language),
            )
            self._refresh_auth_status()
            messagebox.showinfo(self._tr("app_title"), self._tr("auth_success_msg"))
        except Exception as exc:
            messagebox.showerror(self._tr("app_title"), str(exc))

    def _on_logout(self) -> None:
        if messagebox.askyesno(self._tr("app_title"), self._tr("logout_confirm")):
            sign_out()
            self._refresh_auth_status()
            messagebox.showinfo(self._tr("app_title"), self._tr("logout_done"))

    def _on_register_ctx(self) -> None:
        try:
            exts = [ext for ext, var in self.ext_vars.items() if var.get()]
            register_context_menu(exts)
            self._refresh_ctx_status()
            messagebox.showinfo(self._tr("app_title"), self._tr("ctx_registered_msg"))
        except Exception as exc:
            messagebox.showerror(self._tr("app_title"), str(exc))

    def _on_unregister_ctx(self) -> None:
        try:
            unregister_context_menu()
            self._refresh_ctx_status()
            messagebox.showinfo(self._tr("app_title"), self._tr("ctx_unregistered_msg"))
        except Exception as exc:
            messagebox.showerror(self._tr("app_title"), str(exc))

    def _on_open_selected_history(self) -> None:
        selected = self.history_tree.selection()
        if not selected:
            return
        link = self._history_links.get(selected[0])
        if link:
            webbrowser.open(link)

    def _on_clear_history(self) -> None:
        self.cache_db.clear()
        self._refresh_history()
        messagebox.showinfo(self._tr("app_title"), self._tr("history_cleared_msg"))

    def _on_choose_and_open_file(self) -> None:
        self.settings = self._collect_settings_from_ui()
        save_settings(self.settings)
        exts_pattern = " ".join(f"*{e}" for e in self.settings.enabled_extensions) or "*.*"
        file_path = filedialog.askopenfilename(
            title=self._tr("choose_file_title"),
            filetypes=[
                (self._tr("supported_files_filter"), exts_pattern),
                (self._tr("all_files_filter"), "*.*"),
            ],
        )
        if not file_path:
            return
        try:
            self.open_file_callback(file_path)
            self._refresh_auth_status()
            self._refresh_history()
        except Exception as exc:
            messagebox.showerror(self._tr("app_title"), str(exc))

    def run(self) -> None:
        self.root.mainloop()

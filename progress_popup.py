from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Callable, Optional

from drive_client import OperationCancelledError, UICallbacks
from i18n import t


def run_with_progress_popup(
    file_path: str,
    worker_fn: Callable[[UICallbacks], None],
    lang: str = "ja",
    on_missing_credentials: Optional[Callable[[], None]] = None,
    parent: Optional[tk.Misc] = None,
) -> None:
    """Display a bottom-left topmost progress popup while running worker_fn."""
    owns_root = parent is None
    win: tk.Tk | tk.Toplevel = tk.Tk() if owns_root else tk.Toplevel(parent)
    win.title(t("app_title", lang))
    win.overrideredirect(True)
    win.attributes("-topmost", True)

    width = 370
    height = 128
    screen_h = win.winfo_screenheight()
    x_pos = 16
    y_pos = max(16, screen_h - height - 64)
    win.geometry(f"{width}x{height}+{x_pos}+{y_pos}")

    outer = tk.Frame(win, bg="#ffffff", highlightbackground="#2563eb", highlightthickness=2)
    outer.pack(fill=tk.BOTH, expand=True)

    header = tk.Frame(outer, bg="#f8fafc", padx=10, pady=6)
    header.pack(fill=tk.X)

    tk.Label(
        header,
        text=t("app_title", lang),
        font=("Yu Gothic UI", 9, "bold"),
        bg="#f8fafc",
        fg="#1e293b",
    ).pack(side=tk.LEFT)

    file_name = Path(file_path).name
    if len(file_name) > 28:
        file_name = file_name[:25] + "..."
    tk.Label(
        header,
        text=file_name,
        font=("Yu Gothic UI", 9),
        bg="#f8fafc",
        fg="#475569",
    ).pack(side=tk.RIGHT)

    body = tk.Frame(outer, bg="#ffffff", padx=12, pady=8)
    body.pack(fill=tk.BOTH, expand=True)

    status_var = tk.StringVar(value=t("progress_preparing", lang))
    tk.Label(
        body,
        textvariable=status_var,
        font=("Yu Gothic UI", 9),
        bg="#ffffff",
        fg="#0f172a",
        anchor=tk.W,
    ).pack(fill=tk.X, pady=(0, 6))

    pbar = ttk.Progressbar(body, mode="indeterminate", maximum=100)
    pbar.pack(fill=tk.X, pady=(0, 8))
    pbar.start(12)

    cancel_event = threading.Event()
    ui_queue: queue.Queue = queue.Queue()
    worker_error: list[BaseException] = []
    is_indeterminate = [True]

    def on_cancel() -> None:
        cancel_event.set()
        status_var.set(t("progress_cancelling", lang))
        cancel_btn.config(state=tk.DISABLED)

    footer = tk.Frame(body, bg="#ffffff")
    footer.pack(fill=tk.X)
    cancel_btn = ttk.Button(footer, text=t("btn_cancel", lang), command=on_cancel)
    cancel_btn.pack(side=tk.RIGHT)

    def ask_yes_no_threadsafe(title: str, msg: str) -> bool:
        ev = threading.Event()
        box: list[bool] = [False]
        ui_queue.put(("ask_yes_no", title, msg, ev, box))
        ev.wait()
        return box[0]

    def ask_yes_no_cancel_threadsafe(title: str, msg: str) -> Optional[bool]:
        ev = threading.Event()
        box: list[Optional[bool]] = [None]
        ui_queue.put(("ask_yes_no_cancel", title, msg, ev, box))
        ev.wait()
        return box[0]

    def missing_creds_threadsafe() -> None:
        if on_missing_credentials is None:
            return
        ev = threading.Event()
        ui_queue.put(("missing_creds", ev))
        ev.wait()

    def on_progress(msg: str, percent: Optional[float]) -> None:
        if not cancel_event.is_set():
            ui_queue.put(("progress", msg, percent))

    callbacks = UICallbacks(
        ask_yes_no=ask_yes_no_threadsafe,
        ask_yes_no_cancel=ask_yes_no_cancel_threadsafe,
        on_missing_credentials=missing_creds_threadsafe,
        on_progress=on_progress,
        is_cancelled=cancel_event.is_set,
    )

    def worker() -> None:
        try:
            worker_fn(callbacks)
        except OperationCancelledError:
            pass
        except BaseException as exc:
            worker_error.append(exc)
        finally:
            ui_queue.put(("done",))

    def poll_queue() -> None:
        try:
            while True:
                item = ui_queue.get_nowait()
                kind = item[0]
                if kind == "progress":
                    _, msg, pct = item
                    status_var.set(msg)
                    if pct is None:
                        if not is_indeterminate[0]:
                            pbar.config(mode="indeterminate")
                            pbar.start(12)
                            is_indeterminate[0] = True
                    else:
                        if is_indeterminate[0]:
                            pbar.stop()
                            pbar.config(mode="determinate")
                            is_indeterminate[0] = False
                        pbar["value"] = pct
                elif kind == "ask_yes_no":
                    _, title, msg, ev, box = item
                    box[0] = bool(messagebox.askyesno(title, msg, parent=win))
                    ev.set()
                elif kind == "ask_yes_no_cancel":
                    _, title, msg, ev, box = item
                    box[0] = messagebox.askyesnocancel(title, msg, parent=win)
                    ev.set()
                elif kind == "missing_creds":
                    _, ev = item
                    try:
                        if on_missing_credentials:
                            on_missing_credentials()
                    finally:
                        ev.set()
                elif kind == "done":
                    win.destroy()
                    return
        except queue.Empty:
            pass
        win.after(50, poll_queue)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    win.after(50, poll_queue)
    if owns_root:
        win.mainloop()
    else:
        win.wait_window()

    if worker_error:
        raise worker_error[0]

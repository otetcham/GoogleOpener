from __future__ import annotations

import copy
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

APP_NAME = "OpenInGoogle"
APP_DISPLAY_NAME = "GoogleOpener"
APP_VERSION = "2.3.0"
GITHUB_REPO = "otetcham/OpenInGoogle-V2-Apocrypha"

APPDATA_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / APP_NAME
APPDATA_DIR.mkdir(parents=True, exist_ok=True)

CREDENTIALS_FILE = APPDATA_DIR / "credentials.json"
TOKEN_FILE = APPDATA_DIR / "token.json"
SETTINGS_FILE = APPDATA_DIR / "settings.json"
CACHE_DB_FILE = APPDATA_DIR / "cache.db"
HELP_FILE = APPDATA_DIR / "SAVE_YOUR_GOOGLE_CREDENTIALS_HERE.txt"
ICONS_DIR = APPDATA_DIR / "icons"

GOOGLE_CLOUD_CONSOLE_URL = "https://console.cloud.google.com/"
GOOGLE_API_LIBRARY_URL = "https://console.cloud.google.com/apis/library/drive.googleapis.com"
GOOGLE_CREDENTIALS_URL = "https://console.cloud.google.com/apis/credentials"

GOOGLE_MIME_TYPES: Dict[str, str] = {
    ".docx": "application/vnd.google-apps.document",
    ".doc": "application/vnd.google-apps.document",
    ".rtf": "application/vnd.google-apps.document",
    ".odt": "application/vnd.google-apps.document",
    ".xlsx": "application/vnd.google-apps.spreadsheet",
    ".xls": "application/vnd.google-apps.spreadsheet",
    ".xlsm": "application/vnd.google-apps.spreadsheet",
    ".ods": "application/vnd.google-apps.spreadsheet",
    ".csv": "application/vnd.google-apps.spreadsheet",
    ".pptx": "application/vnd.google-apps.presentation",
    ".ppt": "application/vnd.google-apps.presentation",
    ".odp": "application/vnd.google-apps.presentation",
}

DEFAULT_ENABLED_EXTENSIONS: List[str] = [
    ".docx",
    ".doc",
    ".rtf",
    ".odt",
    ".xlsx",
    ".xls",
    ".xlsm",
    ".ods",
    ".csv",
    ".pptx",
    ".ppt",
    ".odp",
]

DUPLICATE_MODE_OPEN_OR_NEW = "open_if_unchanged_else_new"
DUPLICATE_MODE_OPEN_OR_UPDATE = "open_if_unchanged_else_update"
DUPLICATE_MODE_ASK = "always_ask"
DUPLICATE_MODE_ALWAYS_NEW = "always_new"

VALID_DUPLICATE_MODES = {
    DUPLICATE_MODE_OPEN_OR_NEW,
    DUPLICATE_MODE_OPEN_OR_UPDATE,
    DUPLICATE_MODE_ASK,
    DUPLICATE_MODE_ALWAYS_NEW,
}


@dataclass
class AppSettings:
    language: str = "ja"
    drive_folder_name: str = "OpenInGoogle"
    duplicate_mode: str = DUPLICATE_MODE_OPEN_OR_UPDATE
    match_by_hash_across_paths: bool = True
    convert_to_google_format: bool = True
    confirm_before_upload: bool = False
    show_duplicate_notice: bool = True
    excluded_folders: List[str] = field(default_factory=list)
    enabled_extensions: List[str] = field(default_factory=lambda: list(DEFAULT_ENABLED_EXTENSIONS))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "language": self.language,
            "drive_folder_name": self.drive_folder_name,
            "duplicate_mode": self.duplicate_mode,
            "match_by_hash_across_paths": self.match_by_hash_across_paths,
            "convert_to_google_format": self.convert_to_google_format,
            "confirm_before_upload": self.confirm_before_upload,
            "show_duplicate_notice": self.show_duplicate_notice,
            "excluded_folders": list(self.excluded_folders),
            "enabled_extensions": list(self.enabled_extensions),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppSettings":
        defaults = cls()
        lang = data.get("language", defaults.language)
        if lang not in ("ja", "en"):
            lang = defaults.language

        dup_mode = data.get("duplicate_mode", defaults.duplicate_mode)
        if dup_mode not in VALID_DUPLICATE_MODES:
            dup_mode = defaults.duplicate_mode

        raw_exts = data.get("enabled_extensions", defaults.enabled_extensions)
        if isinstance(raw_exts, list):
            exts = [e.lower() for e in raw_exts if isinstance(e, str) and e.lower() in GOOGLE_MIME_TYPES]
        else:
            exts = list(defaults.enabled_extensions)

        raw_excluded = data.get("excluded_folders", defaults.excluded_folders)
        if isinstance(raw_excluded, list):
            excluded = [str(p).strip() for p in raw_excluded if isinstance(p, str) and str(p).strip()]
        else:
            excluded = []

        return cls(
            language=lang,
            drive_folder_name=str(data.get("drive_folder_name", defaults.drive_folder_name)).strip(),
            duplicate_mode=dup_mode,
            match_by_hash_across_paths=bool(data.get("match_by_hash_across_paths", defaults.match_by_hash_across_paths)),
            convert_to_google_format=bool(data.get("convert_to_google_format", defaults.convert_to_google_format)),
            confirm_before_upload=bool(data.get("confirm_before_upload", defaults.confirm_before_upload)),
            show_duplicate_notice=bool(data.get("show_duplicate_notice", defaults.show_duplicate_notice)),
            excluded_folders=excluded,
            enabled_extensions=exts,
        )


def load_settings(settings_file: Path = SETTINGS_FILE) -> AppSettings:
    if not settings_file.exists():
        return AppSettings()
    try:
        raw = json.loads(settings_file.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            return AppSettings.from_dict(raw)
    except Exception:
        pass
    return AppSettings()


def save_settings(settings: AppSettings, settings_file: Path = SETTINGS_FILE) -> None:
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    payload = copy.deepcopy(settings.to_dict())
    settings_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

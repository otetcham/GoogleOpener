from __future__ import annotations

import os
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from cache_db import CacheDB, CacheEntry, compute_sha256, normalize_local_path
from config import (
    CREDENTIALS_FILE,
    DUPLICATE_MODE_ALWAYS_NEW,
    DUPLICATE_MODE_ASK,
    DUPLICATE_MODE_OPEN_OR_NEW,
    DUPLICATE_MODE_OPEN_OR_UPDATE,
    GOOGLE_MIME_TYPES,
    TOKEN_FILE,
    AppSettings,
)
from i18n import t

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


@dataclass
class OpenResult:
    action: str  # "opened_existing", "updated_existing", "uploaded_new"
    file_id: str
    web_view_link: str


@dataclass
class UICallbacks:
    ask_yes_no: Callable[[str, str], bool]
    ask_yes_no_cancel: Callable[[str, str], Optional[bool]]
    on_missing_credentials: Callable[[], None]


def sign_out() -> None:
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()


def get_drive_service(
    lang: str = "ja",
    on_missing_credentials: Optional[Callable[[], None]] = None,
):
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                if on_missing_credentials:
                    on_missing_credentials()
                raise FileNotFoundError(
                    t("err_credentials_missing", lang, cred_file=CREDENTIALS_FILE)
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    return build("drive", "v3", credentials=creds)


def _escape_drive_query(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def get_or_create_folder(service, folder_name: str) -> str:
    folder_name = folder_name.strip()
    if not folder_name:
        return ""

    escaped = _escape_drive_query(folder_name)
    query = (
        f"name = '{escaped}' "
        "and mimeType = 'application/vnd.google-apps.folder' "
        "and trashed = false"
    )
    res = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)",
        pageSize=1,
    ).execute()
    files = res.get("files", [])
    if files:
        return files[0]["id"]

    created = service.files().create(
        body={
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        },
        fields="id",
    ).execute()
    return created["id"]


def verify_remote_file(service, file_id: str) -> Optional[str]:
    if not file_id:
        return None
    try:
        meta = service.files().get(
            fileId=file_id,
            fields="id, trashed, webViewLink",
        ).execute()
        if meta.get("trashed"):
            return None
        return meta.get("webViewLink")
    except HttpError:
        return None


def upload_new_file(
    service,
    path: Path,
    target_mime_type: Optional[str],
    folder_id: str = "",
) -> Tuple[str, str]:
    media = MediaFileUpload(str(path), resumable=True)
    metadata: dict = {
        "name": path.stem if target_mime_type else path.name,
    }
    if target_mime_type:
        metadata["mimeType"] = target_mime_type
    if folder_id:
        metadata["parents"] = [folder_id]

    created = service.files().create(
        body=metadata,
        media_body=media,
        fields="id, name, webViewLink",
    ).execute()

    file_id = created.get("id", "")
    link = created.get("webViewLink", "")
    return file_id, link


def update_existing_file(
    service,
    file_id: str,
    path: Path,
) -> Tuple[str, str]:
    media = MediaFileUpload(str(path), resumable=True)
    updated = service.files().update(
        fileId=file_id,
        media_body=media,
        fields="id, name, webViewLink",
    ).execute()
    return updated.get("id", file_id), updated.get("webViewLink", "")


def is_in_excluded_folder(path: Path, excluded_folders: list[str]) -> bool:
    if not excluded_folders:
        return False
    norm_file = os.path.normcase(str(path.resolve()))
    for raw_folder in excluded_folders:
        if not raw_folder.strip():
            continue
        norm_dir = os.path.normcase(str(Path(raw_folder).expanduser().resolve()))
        try:
            if os.path.commonpath([norm_file, norm_dir]) == norm_dir:
                return True
        except ValueError:
            # Different drive letters on Windows
            continue
    return False


def process_file_open(
    file_path: str,
    settings: AppSettings,
    cache_db: CacheDB,
    callbacks: UICallbacks,
    open_browser: bool = True,
) -> Optional[OpenResult]:
    lang = settings.language
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(t("err_file_not_found", lang, path=path))

    ext = path.suffix.lower()
    if ext not in GOOGLE_MIME_TYPES or ext not in settings.enabled_extensions:
        raise ValueError(t("err_unsupported_ext", lang, ext=ext))

    if is_in_excluded_folder(path, settings.excluded_folders):
        raise PermissionError(t("err_excluded_folder", lang, path=path))

    if settings.confirm_before_upload:
        confirmed = callbacks.ask_yes_no(
            t("app_title", lang),
            t("confirm_upload_msg", lang, name=path.name, path=path),
        )
        if not confirmed:
            return None

    service = get_drive_service(lang=lang, on_missing_credentials=callbacks.on_missing_credentials)
    norm_path = normalize_local_path(path)
    stat = path.stat()
    sha256 = compute_sha256(path)
    target_mime = GOOGLE_MIME_TYPES[ext] if settings.convert_to_google_format else None

    # Duplicate check
    cached_entry: Optional[CacheEntry] = None
    matched_same_content = False

    if settings.duplicate_mode != DUPLICATE_MODE_ALWAYS_NEW:
        by_path = cache_db.get_by_path(norm_path)
        if by_path:
            cached_entry = by_path
            matched_same_content = (by_path.sha256 == sha256)
        elif settings.match_by_hash_across_paths:
            by_hash = cache_db.get_by_hash(sha256)
            if by_hash:
                cached_entry = by_hash
                matched_same_content = True

    if cached_entry:
        remote_link = verify_remote_file(service, cached_entry.drive_file_id)
        if not remote_link:
            cache_db.delete_by_file_id(cached_entry.drive_file_id)
            cached_entry = None
        else:
            if matched_same_content:
                should_open_existing = True
                if settings.duplicate_mode == DUPLICATE_MODE_ASK:
                    choice = callbacks.ask_yes_no_cancel(
                        t("app_title", lang),
                        t("confirm_existing_msg", lang, name=path.name),
                    )
                    if choice is None:
                        return None
                    should_open_existing = bool(choice)

                if should_open_existing:
                    cache_db.upsert(
                        CacheEntry(
                            local_path=norm_path,
                            sha256=sha256,
                            file_size=stat.st_size,
                            mtime=stat.st_mtime,
                            drive_file_id=cached_entry.drive_file_id,
                            web_view_link=remote_link,
                            drive_folder_id=cached_entry.drive_folder_id,
                        )
                    )
                    if open_browser:
                        webbrowser.open(remote_link)
                    return OpenResult("opened_existing", cached_entry.drive_file_id, remote_link)
            else:
                # Same path, modified content
                should_update = False
                if settings.duplicate_mode == DUPLICATE_MODE_OPEN_OR_UPDATE:
                    should_update = True
                elif settings.duplicate_mode == DUPLICATE_MODE_OPEN_OR_NEW:
                    should_update = False
                elif settings.duplicate_mode == DUPLICATE_MODE_ASK:
                    choice = callbacks.ask_yes_no_cancel(
                        t("app_title", lang),
                        t("confirm_update_msg", lang),
                    )
                    if choice is None:
                        return None
                    should_update = bool(choice)

                if should_update:
                    updated_id, updated_link = update_existing_file(
                        service, cached_entry.drive_file_id, path
                    )
                    link = updated_link or remote_link
                    cache_db.upsert(
                        CacheEntry(
                            local_path=norm_path,
                            sha256=sha256,
                            file_size=stat.st_size,
                            mtime=stat.st_mtime,
                            drive_file_id=updated_id,
                            web_view_link=link,
                            drive_folder_id=cached_entry.drive_folder_id,
                        )
                    )
                    if open_browser:
                        webbrowser.open(link)
                    return OpenResult("updated_existing", updated_id, link)

    # Upload as a new file
    folder_id = get_or_create_folder(service, settings.drive_folder_name)
    file_id, link = upload_new_file(service, path, target_mime, folder_id=folder_id)
    if not link:
        raise RuntimeError(t("err_no_link", lang))

    cache_db.upsert(
        CacheEntry(
            local_path=norm_path,
            sha256=sha256,
            file_size=stat.st_size,
            mtime=stat.st_mtime,
            drive_file_id=file_id,
            web_view_link=link,
            drive_folder_id=folder_id,
        )
    )
    if open_browser:
        webbrowser.open(link)
    return OpenResult("uploaded_new", file_id, link)

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from cache_db import CacheDB, CacheEntry, compute_sha256, normalize_local_path
from config import (
    DUPLICATE_MODE_ALWAYS_NEW,
    DUPLICATE_MODE_ASK,
    DUPLICATE_MODE_OPEN_OR_NEW,
    DUPLICATE_MODE_OPEN_OR_UPDATE,
    AppSettings,
    load_settings,
    save_settings,
)
from drive_client import OperationCancelledError, UICallbacks, process_file_open
from i18n import t
from updater import is_update_available, parse_version
from win_integration import EXTENSION_ICON_MAP


class TestConfigAndI18n(unittest.TestCase):
    def test_settings_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            settings_path = Path(tmp) / "settings.json"
            original = AppSettings(
                language="en",
                drive_folder_name="MyDocs",
                duplicate_mode=DUPLICATE_MODE_ASK,
                confirm_before_upload=True,
                excluded_folders=[r"C:\Secret"],
                enabled_extensions=[".docx", ".xlsx"],
            )
            save_settings(original, settings_path)
            loaded = load_settings(settings_path)
            self.assertEqual(loaded.language, "en")
            self.assertEqual(loaded.drive_folder_name, "MyDocs")
            self.assertEqual(loaded.duplicate_mode, DUPLICATE_MODE_ASK)
            self.assertTrue(loaded.confirm_before_upload)
            self.assertEqual(loaded.excluded_folders, [r"C:\Secret"])
            self.assertEqual(loaded.enabled_extensions, [".docx", ".xlsx"])

    def test_i18n_lookup(self) -> None:
        self.assertIn("GoogleOpener", t("app_title", "ja"))
        self.assertIn("GoogleOpener", t("app_title", "en"))

    def test_updater_version_comparison(self) -> None:
        self.assertEqual(parse_version("v2.2.0"), (2, 2, 0))
        self.assertTrue(is_update_available("v2.3.0", "2.2.0"))
        self.assertFalse(is_update_available("v2.2.0", "2.2.0"))
        self.assertFalse(is_update_available("v2.1.0", "2.2.0"))

    def test_icon_mapping_covers_office_types(self) -> None:
        self.assertEqual(EXTENSION_ICON_MAP[".docx"], "docs.ico")
        self.assertEqual(EXTENSION_ICON_MAP[".xlsx"], "sheets.ico")
        self.assertEqual(EXTENSION_ICON_MAP[".pptx"], "slides.ico")


class TestDuplicateCheckAndUpload(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_dir.name)
        self.db = CacheDB(self.root / "cache.db")
        self.sample_file = self.root / "report.docx"
        self.sample_file.write_bytes(b"dummy docx content v1")
        self.callbacks = UICallbacks(
            ask_yes_no=lambda _t, _m: True,
            ask_yes_no_cancel=lambda _t, _m: True,
            on_missing_credentials=lambda: None,
        )

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    @patch("drive_client.get_drive_service")
    @patch("drive_client.get_or_create_folder", return_value="folder_1")
    @patch("drive_client.upload_new_file", return_value=("file_1", "https://docs.google.com/document/d/file_1/edit"))
    @patch("drive_client.verify_remote_file", return_value="https://docs.google.com/document/d/file_1/edit")
    def test_upload_new_then_open_existing_when_unchanged(
        self,
        mock_verify: MagicMock,
        mock_upload: MagicMock,
        _mock_folder: MagicMock,
        _mock_service: MagicMock,
    ) -> None:
        settings = AppSettings(duplicate_mode=DUPLICATE_MODE_OPEN_OR_UPDATE)

        res1 = process_file_open(str(self.sample_file), settings, self.db, self.callbacks, open_browser=False)
        self.assertIsNotNone(res1)
        self.assertEqual(res1.action, "uploaded_new")
        self.assertEqual(mock_upload.call_count, 1)

        res2 = process_file_open(str(self.sample_file), settings, self.db, self.callbacks, open_browser=False)
        self.assertIsNotNone(res2)
        self.assertEqual(res2.action, "opened_existing")
        self.assertEqual(mock_upload.call_count, 1)
        mock_verify.assert_called_once_with(_mock_service.return_value, "file_1")

    @patch("drive_client.get_drive_service")
    @patch("drive_client.update_existing_file", return_value=("file_1", "https://docs.google.com/document/d/file_1/edit"))
    @patch("drive_client.verify_remote_file", return_value="https://docs.google.com/document/d/file_1/edit")
    def test_update_existing_when_file_modified(
        self,
        _mock_verify: MagicMock,
        mock_update: MagicMock,
        _mock_service: MagicMock,
    ) -> None:
        self.db.upsert(
            CacheEntry(
                local_path=normalize_local_path(self.sample_file),
                sha256=compute_sha256(self.sample_file),
                file_size=self.sample_file.stat().st_size,
                mtime=self.sample_file.stat().st_mtime,
                drive_file_id="file_1",
                web_view_link="https://docs.google.com/document/d/file_1/edit",
            )
        )
        # Modify file content
        self.sample_file.write_bytes(b"dummy docx content v2 modified")
        settings = AppSettings(duplicate_mode=DUPLICATE_MODE_OPEN_OR_UPDATE)

        res = process_file_open(str(self.sample_file), settings, self.db, self.callbacks, open_browser=False)
        self.assertIsNotNone(res)
        self.assertEqual(res.action, "updated_existing")
        self.assertEqual(mock_update.call_count, 1)

    @patch("drive_client.get_drive_service")
    @patch("drive_client.get_or_create_folder", return_value="folder_1")
    @patch("drive_client.upload_new_file", return_value=("file_2", "https://docs.google.com/document/d/file_2/edit"))
    @patch("drive_client.verify_remote_file", return_value=None)
    def test_reupload_when_remote_deleted(
        self,
        _mock_verify: MagicMock,
        mock_upload: MagicMock,
        _mock_folder: MagicMock,
        _mock_service: MagicMock,
    ) -> None:
        self.db.upsert(
            CacheEntry(
                local_path=normalize_local_path(self.sample_file),
                sha256=compute_sha256(self.sample_file),
                file_size=self.sample_file.stat().st_size,
                mtime=self.sample_file.stat().st_mtime,
                drive_file_id="deleted_file",
                web_view_link="https://docs.google.com/document/d/deleted_file/edit",
            )
        )
        settings = AppSettings(duplicate_mode=DUPLICATE_MODE_OPEN_OR_NEW)

        res = process_file_open(str(self.sample_file), settings, self.db, self.callbacks, open_browser=False)
        self.assertIsNotNone(res)
        self.assertEqual(res.action, "uploaded_new")
        self.assertEqual(res.file_id, "file_2")
        self.assertEqual(mock_upload.call_count, 1)

    def test_excluded_folder_blocked(self) -> None:
        settings = AppSettings(excluded_folders=[str(self.root)])
        with self.assertRaises(PermissionError):
            process_file_open(str(self.sample_file), settings, self.db, self.callbacks, open_browser=False)

    @patch("drive_client.get_drive_service")
    @patch("drive_client.get_or_create_folder", return_value="folder_1")
    @patch("drive_client.upload_new_file", return_value=("file_3", "https://docs.google.com/document/d/file_3/edit"))
    def test_always_new_ignores_cache(
        self,
        mock_upload: MagicMock,
        _mock_folder: MagicMock,
        _mock_service: MagicMock,
    ) -> None:
        self.db.upsert(
            CacheEntry(
                local_path=normalize_local_path(self.sample_file),
                sha256=compute_sha256(self.sample_file),
                file_size=self.sample_file.stat().st_size,
                mtime=self.sample_file.stat().st_mtime,
                drive_file_id="file_1",
                web_view_link="https://docs.google.com/document/d/file_1/edit",
            )
        )
        settings = AppSettings(duplicate_mode=DUPLICATE_MODE_ALWAYS_NEW)
        res = process_file_open(str(self.sample_file), settings, self.db, self.callbacks, open_browser=False)
        self.assertIsNotNone(res)
        self.assertEqual(res.action, "uploaded_new")
        self.assertEqual(mock_upload.call_count, 1)

    @patch("drive_client.get_drive_service")
    def test_cancel_aborts_before_upload(self, mock_service: MagicMock) -> None:
        progress_events: list[tuple[str, float | None]] = []
        callbacks = UICallbacks(
            ask_yes_no=lambda _t, _m: True,
            ask_yes_no_cancel=lambda _t, _m: True,
            on_missing_credentials=lambda: None,
            on_progress=lambda msg, pct: progress_events.append((msg, pct)),
            is_cancelled=lambda: True,
        )
        settings = AppSettings()
        with self.assertRaises(OperationCancelledError):
            process_file_open(str(self.sample_file), settings, self.db, callbacks, open_browser=False)
        self.assertEqual(mock_service.call_count, 0)
        self.assertGreaterEqual(len(progress_events), 1)


if __name__ == "__main__":
    unittest.main()

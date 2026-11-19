from __future__ import annotations

import hashlib
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, List, Optional

from config import CACHE_DB_FILE


def normalize_local_path(path: Path) -> str:
    return os.path.normcase(str(path.resolve()))


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass
class CacheEntry:
    local_path: str
    sha256: str
    file_size: int
    mtime: float
    drive_file_id: str
    web_view_link: str
    drive_folder_id: str = ""
    updated_at: str = ""


class CacheDB:
    def __init__(self, db_path: Path = CACHE_DB_FILE) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS file_cache (
                    local_path TEXT PRIMARY KEY,
                    sha256 TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    mtime REAL NOT NULL,
                    drive_file_id TEXT NOT NULL,
                    web_view_link TEXT NOT NULL,
                    drive_folder_id TEXT NOT NULL DEFAULT '',
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_file_cache_sha256 ON file_cache (sha256)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_file_cache_updated ON file_cache (updated_at DESC)"
            )

    @staticmethod
    def _row_to_entry(row: sqlite3.Row) -> CacheEntry:
        return CacheEntry(
            local_path=row["local_path"],
            sha256=row["sha256"],
            file_size=int(row["file_size"]),
            mtime=float(row["mtime"]),
            drive_file_id=row["drive_file_id"],
            web_view_link=row["web_view_link"],
            drive_folder_id=row["drive_folder_id"],
            updated_at=row["updated_at"],
        )

    def get_by_path(self, local_path: str) -> Optional[CacheEntry]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM file_cache WHERE local_path = ?",
                (local_path,),
            ).fetchone()
            return self._row_to_entry(row) if row else None

    def get_by_hash(self, sha256: str) -> Optional[CacheEntry]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM file_cache WHERE sha256 = ? ORDER BY updated_at DESC LIMIT 1",
                (sha256,),
            ).fetchone()
            return self._row_to_entry(row) if row else None

    def upsert(self, entry: CacheEntry) -> None:
        now_iso = entry.updated_at or datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO file_cache (
                    local_path, sha256, file_size, mtime,
                    drive_file_id, web_view_link, drive_folder_id, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(local_path) DO UPDATE SET
                    sha256 = excluded.sha256,
                    file_size = excluded.file_size,
                    mtime = excluded.mtime,
                    drive_file_id = excluded.drive_file_id,
                    web_view_link = excluded.web_view_link,
                    drive_folder_id = excluded.drive_folder_id,
                    updated_at = excluded.updated_at
                """,
                (
                    entry.local_path,
                    entry.sha256,
                    entry.file_size,
                    entry.mtime,
                    entry.drive_file_id,
                    entry.web_view_link,
                    entry.drive_folder_id,
                    now_iso,
                ),
            )

    def delete_by_file_id(self, drive_file_id: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM file_cache WHERE drive_file_id = ?",
                (drive_file_id,),
            )

    def list_recent(self, limit: int = 50) -> List[CacheEntry]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM file_cache ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [self._row_to_entry(r) for r in rows]

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM file_cache")

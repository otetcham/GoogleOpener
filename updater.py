from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from config import APP_NAME, APP_VERSION, GITHUB_REPO


@dataclass
class ReleaseInfo:
    tag_name: str
    html_url: str
    asset_name: str
    asset_url: str
    is_installer: bool
    body: str = ""


def parse_version(version_str: str) -> Tuple[int, ...]:
    cleaned = version_str.strip().lstrip("vV")
    nums = re.findall(r"\d+", cleaned.split("-")[0])
    if not nums:
        return (0, 0, 0)
    return tuple(int(n) for n in nums[:4])


def is_update_available(latest_tag: str, current_version: str = APP_VERSION) -> bool:
    return parse_version(latest_tag) > parse_version(current_version)


def fetch_latest_release(repo: str = GITHUB_REPO, timeout: int = 10) -> ReleaseInfo:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{APP_NAME}/{APP_VERSION}",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    tag_name = str(data.get("tag_name", ""))
    html_url = str(data.get("html_url", f"https://github.com/{repo}/releases"))
    body = str(data.get("body", ""))
    assets = data.get("assets", [])

    exe_asset: Optional[dict] = None
    installer_asset: Optional[dict] = None
    for asset in assets:
        name = str(asset.get("name", ""))
        lower = name.lower()
        if lower == "openingoogle.exe":
            exe_asset = asset
        elif lower.endswith(".exe") and "setup" in lower:
            installer_asset = asset

    chosen = exe_asset or installer_asset
    if not chosen:
        raise RuntimeError("No Windows executable asset found in the latest GitHub release.")

    return ReleaseInfo(
        tag_name=tag_name,
        html_url=html_url,
        asset_name=str(chosen["name"]),
        asset_url=str(chosen["browser_download_url"]),
        is_installer=(chosen is installer_asset),
        body=body,
    )


def download_asset(url: str, dest_path: Path, timeout: int = 60) -> Path:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": f"{APP_NAME}/{APP_VERSION}"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp, dest_path.open("wb") as out:
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            out.write(chunk)
    return dest_path


def download_and_apply_update(release: ReleaseInfo) -> Tuple[bool, Path]:
    """Download the release asset and launch updater if running as frozen exe.

    Returns (should_exit_app, downloaded_path).
    """
    download_dir = Path(tempfile.gettempdir()) / f"{APP_NAME}_update"
    dest_file = download_dir / release.asset_name
    download_asset(release.asset_url, dest_file)

    is_frozen = getattr(sys, "frozen", False)
    if not is_frozen:
        return False, dest_file

    if release.is_installer:
        subprocess.Popen([str(dest_file)], close_fds=True)
        return True, dest_file

    current_exe = Path(sys.executable).resolve()
    bat_path = download_dir / "apply_update.bat"
    bat_content = (
        "@echo off\r\n"
        "timeout /t 2 /nobreak > nul\r\n"
        f'move /y "{dest_file}" "{current_exe}" > nul\r\n'
        f'start "" "{current_exe}" --apply-icons\r\n'
        f'start "" "{current_exe}" --settings\r\n'
        'del "%~f0"\r\n'
    )
    bat_path.write_text(bat_content, encoding="utf-8")

    creationflags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW
    subprocess.Popen(
        ["cmd.exe", "/c", str(bat_path)],
        creationflags=creationflags,
        close_fds=True,
    )
    return True, dest_file

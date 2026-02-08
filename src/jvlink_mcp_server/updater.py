"""Auto-update and version checking for jvlink-mcp-server."""

import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

GITHUB_OWNER = "miyamamoto"
GITHUB_REPO = "jvlink-mcp-server"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"

PROJECT_ROOT = Path(__file__).parent.parent.parent
UPDATE_CHECK_FILE = PROJECT_ROOT / ".update_check.json"


def get_current_version() -> str:
    """Get current version from git tag or pyproject.toml."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    try:
        toml_path = PROJECT_ROOT / "pyproject.toml"
        if toml_path.exists():
            for line in toml_path.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("version"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    except Exception:
        pass

    return "unknown"


def _normalize_version(v: str) -> list[int]:
    """Normalize version string to list of ints."""
    v = v.lstrip("v")
    parts = []
    for p in v.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return parts


def _version_newer(latest: str, current: str) -> bool:
    """Return True if latest is newer than current."""
    try:
        return _normalize_version(latest) > _normalize_version(current)
    except Exception:
        return latest != current


def check_for_updates() -> Optional[dict]:
    """Check GitHub for latest release.

    Returns dict with latest_version, current_version, update_available, html_url
    or None on failure.
    """
    import urllib.request
    import urllib.error

    current = get_current_version()

    # Try releases/latest first
    try:
        url = f"{GITHUB_API_URL}/releases/latest"
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/vnd.github.v3+json", "User-Agent": GITHUB_REPO},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            latest = data.get("tag_name", "unknown")
            return {
                "latest_version": latest,
                "current_version": current,
                "update_available": _version_newer(latest, current),
                "html_url": data.get("html_url", ""),
                "release_name": data.get("name", ""),
                "body": data.get("body", ""),
            }
    except urllib.error.HTTPError as e:
        if e.code != 404:
            logger.debug("GitHub API error: %s", e.code)
            return None
    except Exception as e:
        logger.debug("Failed to check releases: %s", e)
        return None

    # Fallback: check tags
    try:
        url = f"{GITHUB_API_URL}/tags?per_page=1"
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/vnd.github.v3+json", "User-Agent": GITHUB_REPO},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data:
                latest = data[0].get("name", "unknown")
                return {
                    "latest_version": latest,
                    "current_version": current,
                    "update_available": _version_newer(latest, current),
                    "html_url": f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases",
                    "release_name": "",
                    "body": "",
                }
    except Exception as e:
        logger.debug("Failed to check tags: %s", e)

    return None


def should_check_updates(interval_hours: int = 24) -> bool:
    """Return True if enough time has passed since last check."""
    try:
        if not UPDATE_CHECK_FILE.exists():
            return True
        data = json.loads(UPDATE_CHECK_FILE.read_text(encoding="utf-8"))
        return (time.time() - data.get("last_check", 0)) > (interval_hours * 3600)
    except Exception:
        return True


def save_update_check_time():
    """Save the current time as last update check."""
    try:
        UPDATE_CHECK_FILE.parent.mkdir(parents=True, exist_ok=True)
        UPDATE_CHECK_FILE.write_text(
            json.dumps({"last_check": time.time(), "checked_at": datetime.now(timezone.utc).isoformat()}),
            encoding="utf-8",
        )
    except Exception:
        pass


def perform_update(confirmed: bool = False) -> dict:
    """Perform update: git pull + uv sync (or pip install -e .).

    Args:
        confirmed: Trueの場合のみ実際にアップデートを実行。
                   Falseの場合は確認メッセージを返す。

    Returns dict with success, message, and details.
    """
    results = {"success": False, "steps": []}

    # Step 1: Check for updates first
    info = check_for_updates()
    if info is None:
        results["message"] = "アップデートの確認に失敗しました"
        return results

    if not info["update_available"]:
        results["success"] = True
        results["message"] = f"最新バージョン {info['current_version']} です。アップデートは不要です。"
        return results

    results["from_version"] = info["current_version"]
    results["to_version"] = info["latest_version"]

    # 確認が未完了の場合は確認メッセージを返す
    if not confirmed:
        results["message"] = (
            f"アップデートが利用可能です: {info['current_version']} → {info['latest_version']}\n"
            "実行するには confirmed=True を指定してください。\n"
            "注意: git pull と依存関係の更新が実行され、サーバーの再起動が必要になります。"
        )
        results["requires_confirmation"] = True
        return results

    # Step 2: git pull
    try:
        result = subprocess.run(
            ["git", "pull", "--ff-only", "origin", "master"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=60,
        )
        if result.returncode != 0:
            results["message"] = f"git pull 失敗: {result.stderr.strip()}"
            results["steps"].append({"git_pull": "failed", "error": result.stderr.strip()})
            return results
        results["steps"].append({"git_pull": "success", "output": result.stdout.strip()})
    except Exception as e:
        results["message"] = f"git pull エラー: {e}"
        return results

    # Step 3: uv sync or pip install -e .
    try:
        # Try uv first
        result = subprocess.run(
            ["uv", "sync"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=120,
        )
        if result.returncode == 0:
            results["steps"].append({"uv_sync": "success"})
        else:
            raise FileNotFoundError("uv sync failed")
    except (FileNotFoundError, Exception):
        # Fallback to pip
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", "."],
                capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=120,
            )
            if result.returncode != 0:
                results["message"] = f"pip install 失敗: {result.stderr.strip()}"
                return results
            results["steps"].append({"pip_install": "success"})
        except Exception as e:
            results["message"] = f"依存関係の更新に失敗: {e}"
            return results

    results["success"] = True
    results["message"] = (
        f"アップデート完了: {info['current_version']} → {info['latest_version']}\n"
        "サーバーを再起動してください。"
    )
    return results


def startup_update_check() -> Optional[str]:
    """Check for updates on startup. Returns notice string or None."""
    if not should_check_updates():
        return None

    try:
        info = check_for_updates()
        save_update_check_time()
        if info and info.get("update_available"):
            return (
                f"🔄 アップデートがあります: {info['current_version']} → {info['latest_version']}\n"
                f"check_update ツールで詳細を確認、update_server ツールで更新できます。"
            )
    except Exception:
        pass
    return None

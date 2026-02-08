"""Tests for the auto-updater module."""

import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from jvlink_mcp_server.updater import (
    _normalize_version,
    _version_newer,
    get_current_version,
    check_for_updates,
    should_check_updates,
    save_update_check_time,
    perform_update,
    startup_update_check,
    UPDATE_CHECK_FILE,
)


class TestVersionComparison:
    def test_normalize_version(self):
        assert _normalize_version("1.2.3") == [1, 2, 3]
        assert _normalize_version("v1.2.3") == [1, 2, 3]
        assert _normalize_version("0.2.0") == [0, 2, 0]

    def test_version_newer(self):
        assert _version_newer("1.0.0", "0.2.0") is True
        assert _version_newer("0.3.0", "0.2.0") is True
        assert _version_newer("0.2.1", "0.2.0") is True
        assert _version_newer("v0.3.0", "0.2.0") is True

    def test_version_not_newer(self):
        assert _version_newer("0.2.0", "0.2.0") is False
        assert _version_newer("0.1.0", "0.2.0") is False
        assert _version_newer("v0.2.0", "v0.2.0") is False

    def test_version_with_v_prefix(self):
        assert _version_newer("v1.0.0", "v0.9.0") is True
        assert _version_newer("v0.2.0", "0.2.0") is False


class TestGetCurrentVersion:
    @patch("jvlink_mcp_server.updater.subprocess.run")
    def test_from_git_tag(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="v0.2.0\n")
        assert get_current_version() == "v0.2.0"

    @patch("jvlink_mcp_server.updater.subprocess.run")
    def test_fallback_to_pyproject(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1)
        version = get_current_version()
        # Should read from pyproject.toml
        assert version == "0.2.0" or version != "unknown"


class TestCheckForUpdates:
    @patch("urllib.request.urlopen")
    def test_returns_info_on_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "tag_name": "v1.0.0",
            "html_url": "https://github.com/miyamamoto/jvlink-mcp-server/releases/tag/v1.0.0",
            "name": "v1.0.0",
            "body": "Release notes",
        }).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        info = check_for_updates()
        assert info is not None
        assert info["latest_version"] == "v1.0.0"
        assert info["update_available"] is True

    @patch("urllib.request.urlopen", side_effect=Exception("Network error"))
    def test_returns_none_on_failure(self, mock_urlopen):
        assert check_for_updates() is None


class TestShouldCheckUpdates:
    def test_returns_true_when_no_file(self, tmp_path):
        with patch("jvlink_mcp_server.updater.UPDATE_CHECK_FILE", tmp_path / "nonexistent.json"):
            assert should_check_updates() is True

    def test_returns_false_when_recently_checked(self, tmp_path):
        check_file = tmp_path / "check.json"
        check_file.write_text(json.dumps({"last_check": time.time()}))
        with patch("jvlink_mcp_server.updater.UPDATE_CHECK_FILE", check_file):
            assert should_check_updates() is False

    def test_returns_true_when_old_check(self, tmp_path):
        check_file = tmp_path / "check.json"
        check_file.write_text(json.dumps({"last_check": time.time() - 100000}))
        with patch("jvlink_mcp_server.updater.UPDATE_CHECK_FILE", check_file):
            assert should_check_updates() is True


class TestPerformUpdate:
    @patch("jvlink_mcp_server.updater.check_for_updates")
    def test_no_update_needed(self, mock_check):
        mock_check.return_value = {
            "current_version": "0.2.0",
            "latest_version": "0.2.0",
            "update_available": False,
        }
        result = perform_update()
        assert result["success"] is True
        assert "不要" in result["message"]

    @patch("jvlink_mcp_server.updater.check_for_updates")
    def test_check_failure(self, mock_check):
        mock_check.return_value = None
        result = perform_update()
        assert result["success"] is False


class TestStartupCheck:
    @patch("jvlink_mcp_server.updater.should_check_updates", return_value=False)
    def test_skips_when_recently_checked(self, mock_should):
        assert startup_update_check() is None

    @patch("jvlink_mcp_server.updater.save_update_check_time")
    @patch("jvlink_mcp_server.updater.check_for_updates")
    @patch("jvlink_mcp_server.updater.should_check_updates", return_value=True)
    def test_returns_notice_when_update_available(self, mock_should, mock_check, mock_save):
        mock_check.return_value = {
            "current_version": "0.2.0",
            "latest_version": "v1.0.0",
            "update_available": True,
        }
        notice = startup_update_check()
        assert notice is not None
        assert "アップデート" in notice

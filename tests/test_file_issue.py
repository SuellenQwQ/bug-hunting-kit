"""Tests for file_issue.py — the CLI issue filer.

No network, no git: everything is monkeypatched.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import file_issue  # noqa: E402


def test_get_token_from_env(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "  abc123  ")
    assert file_issue.get_token() == "abc123"


def test_get_token_missing_exits(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    # git 缺失时走 sys.exit 分支
    import subprocess as sp

    def fake_run(*a, **k):
        raise FileNotFoundError("no git")

    monkeypatch.setattr(sp, "run", fake_run)
    with pytest.raises(SystemExit):
        file_issue.get_token()


def test_main_posts_issue(tmp_path, monkeypatch, capsys):
    body_file = tmp_path / "issue.md"
    body_file.write_text("# hello\nworld", encoding="utf-8")
    monkeypatch.setenv("GITHUB_TOKEN", "tok123")
    monkeypatch.setattr(
        sys, "argv",
        ["file_issue.py", "--repo", "a/b", "--title", "T", "--body-file", str(body_file)],
    )

    captured = {}

    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps({"number": 7, "html_url": "https://x/7"}).encode()

    def fake_urlopen(req, timeout=None):
        captured["req"] = req
        return FakeResp()

    monkeypatch.setattr(file_issue.urllib.request, "urlopen", fake_urlopen)
    file_issue.main()

    req = captured["req"]
    assert req.full_url == "https://api.github.com/repos/a/b/issues"
    assert req.get_method() == "POST"
    assert json.loads(req.data) == {"title": "T", "body": "# hello\nworld"}
    assert req.get_header("Authorization") == "token tok123"
    out = capsys.readouterr().out
    assert "CREATED: 7" in out
    assert "https://x/7" in out


def test_main_reads_stdin(monkeypatch, capsys):
    import io

    monkeypatch.setenv("GITHUB_TOKEN", "tok")
    monkeypatch.setattr(sys, "argv", ["file_issue.py", "--repo", "a/b", "--title", "T"])
    monkeypatch.setattr(sys, "stdin", io.StringIO("body from stdin"))

    captured = {}

    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b'{"number": 1, "html_url": "u"}'

    monkeypatch.setattr(
        file_issue.urllib.request, "urlopen",
        lambda req, timeout=None: (captured.setdefault("req", req), FakeResp())[1],
    )
    file_issue.main()
    assert json.loads(captured["req"].data)["body"] == "body from stdin"


def test_main_rejects_empty_body(tmp_path, monkeypatch):
    body_file = tmp_path / "empty.md"
    body_file.write_text("   \n", encoding="utf-8")
    monkeypatch.setattr(
        sys, "argv",
        ["file_issue.py", "--repo", "a/b", "--title", "T", "--body-file", str(body_file)],
    )
    with pytest.raises(SystemExit):
        file_issue.main()

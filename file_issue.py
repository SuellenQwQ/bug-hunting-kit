#!/usr/bin/env python3
"""File a GitHub issue from the command line.

Credentials: env var GITHUB_TOKEN, or the stored git credential
(git credential fill). Stdlib only, Python 3.8+.

Usage:
  python file_issue.py --repo owner/repo --title "Title" --body-file issue.md
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


def get_token() -> str:
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        return tok.strip()
    try:
        out = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True, text=True, timeout=30,
        ).stdout
    except FileNotFoundError:
        sys.exit("git not found; set GITHUB_TOKEN instead.")
    for line in out.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1].strip()
    sys.exit("No stored GitHub credential. Set GITHUB_TOKEN or push once via git.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Create a GitHub issue")
    ap.add_argument("--repo", required=True, help="owner/repo")
    ap.add_argument("--title", required=True)
    ap.add_argument("--body-file", help="markdown file; omit to read stdin")
    args = ap.parse_args()

    body = open(args.body_file, encoding="utf-8").read() if args.body_file else sys.stdin.read()
    if not body.strip():
        sys.exit("empty body")

    payload = json.dumps({"title": args.title, "body": body}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/repos/%s/issues" % args.repo,
        data=payload,
        headers={
            "Authorization": "token %s" % get_token(),
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "bug-hunting-kit",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            d = json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit("GitHub %s: %s" % (e.code, e.read().decode("utf-8", "replace")))
    print("CREATED:", d["number"])
    print("URL:", d["html_url"])


if __name__ == "__main__":
    main()

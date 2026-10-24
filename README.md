# bug-hunting-kit 🐛

[![CI](https://github.com/SuellenQwQ/bug-hunting-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/SuellenQwQ/bug-hunting-kit/actions/workflows/ci.yml)

The toolkit behind my daily habit: **read one open-source project, file one verified issue.**

## What's inside

| File | Purpose |
|---|---|
| `file_issue.py` | File a GitHub issue from the CLI (stdlib only). Reads `GITHUB_TOKEN` or the stored git credential. |
| `METHODOLOGY.md` | The bug patterns I hunt for, ranked by hit rate, each born from a real find. |

## Usage

```bash
python file_issue.py --repo owner/repo --title "fix: ..." --body-file issue.md
```

## Ground rules

1. Never file what you cannot reproduce or prove from the code path.
2. Quote the exact source lines (file + line number) in the issue.
3. Always propose the one-line fix.
4. Check open issues first; link related ones.
5. Match the maintainer's language.

## Track record

22 real bugs found across 22 repos (1 PR + 21 issues), every one with a minimal
repro or a line-level code-path proof.

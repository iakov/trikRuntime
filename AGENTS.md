# AGENTS.md — Entry Point for AI Assistants

This project is the **TRIK Runtime** — a Qt5/C++14 firmware for the TRIK
educational robotics controller.

## Where to start

Read `TRIK_RUNTIME.md` first. It covers architecture, build system,
conventions, CI pipelines, and the translation workflow. Everything an agent
needs is in that document.

## Key files

| Purpose | File |
|---------|------|
| Main reference | `TRIK_RUNTIME.md` |
| Project README | `README.md` |
| Changelog | `resources/changelog.txt` |
| Qt project config | `trikRuntime.pro` |
| Shared build config | `global.pri` |
| Code style | `.clang-format` |

## Rules for agents

1. **No ephemeral data in docs** — never write build timestamps, machine paths,
   or temp directories. Use `.tmp/` for local scratch files. Never use `/tmp`
   or system temp.
2. **UTF-8 everywhere** — all source and config files are UTF-8.
3. **Python tools** — use `uv` with local `.venv/`, never system pip or pipx.
4. **Never commit secrets** — API keys, passwords, tokens go in `.env` or
   environment variables only.
5. **Minimal diffs** — prefer targeted edits over rewrites.
6. **No generated documentation** — never create `.md` files unless explicitly
   requested.
7. **mdformat + markdownlint** — all markdown must pass `scripts/mdformat.sh`.
8. **PR descriptions via files** — never pass PR bodies or commit messages
   inline in PowerShell shell commands. Write to `.tmp/pr_<number>_body.md` and
   use `--body-file .tmp/pr_<number>_body.md` (for `gh`) or `-F
   .tmp/<filename>` (for `git`) to avoid backtick/escape corruption.
#!/bin/bash
# Run mdformat and markdownlint on all .md files in the project.
# Uses uv-managed local .venv — never system pip.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"
cd "${PROJECT_DIR}"

mkdir -p .tmp

uv venv --seed 2>/dev/null || true
uv pip install mdformat mdl 2>/dev/null || true

echo "=== mdformat ==="
uv run mdformat --check .mdformat *.md docs/*.md 2>&1 || {
    echo "mdformat failed. To fix: uv run mdformat .mdformat *.md docs/*.md"
    exit 1
}

echo "=== markdownlint ==="
uv run mdl --style scripts/mdl_style.rb *.md docs/*.md 2>&1 || {
    echo "markdownlint failed."
    exit 1
}

echo "All markdown checks passed."
#!/usr/bin/env python3
"""
Build wrapper for trikRuntime.

Sets up PATH for MinGW + Qt and runs qmake + mingw32-make.
Usage:
    uv run python .tmp/build_wrapper.py          # qmake + build
    uv run python .tmp/build_wrapper.py --qmake  # qmake only
    uv run python .tmp/build_wrapper.py --clean  # full rebuild
"""

import argparse
import os
import platform
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# --- Configuration (discovered paths) ---
# Qt 5.15 MinGW 8.1 32-bit (primary target)
QT5_DIR = r"C:\Qt\5.15.2\mingw81_32"
# Qt 6.7.3 MinGW 64-bit (future target)
QT6_DIR = r"C:\Qt\6.7.3\mingw_64"
# MinGW 8.1 toolchain (bundled with Qt)
MINGW_DIR = r"C:\Qt\Tools\mingw810_32"
# MSYS2 utilities
MSYS2_USR = r"C:\msys64\usr"

BUILD_DIR = REPO / ".tmp" / "build"


def build_env(qt_ver: str = "5.15") -> dict:
    env = os.environ.copy()

    if qt_ver == "5.15":
        qt_bin = f"{QT5_DIR}\\bin"
    elif qt_ver == "6.7":
        qt_bin = f"{QT6_DIR}\\bin"
    else:
        raise ValueError(f"Unknown Qt version: {qt_ver}")

    # PATH order: MinGW tools → Qt bin → MSYS2 utils → system
    paths = [
        f"{MINGW_DIR}\\bin",
        qt_bin,
        f"{MSYS2_USR}\\bin",
        env.get("PATH", ""),
    ]
    env["PATH"] = ";".join(paths)

    if qt_ver == "5.15":
        env["QMAKE_SPEC"] = "win32-g++"
    else:
        env["QMAKE_SPEC"] = "win32-g++"

    return env


def run_qmake(env: dict, build_dir: Path, clean: bool = False):
    if clean and build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)

    spec = env.get("QMAKE_SPEC", "win32-g++")
    qmake = shutil.which("qmake", path=env["PATH"])
    if not qmake:
        print("ERROR: qmake not found on PATH")
        sys.exit(1)

    # Auto-detect Python version
    import re
    py_ver = ""
    py_path = shutil.which("python", path=env["PATH"])
    if py_path:
        result = subprocess.run([py_path, "--version"], capture_output=True, text=True)
        m = re.search(r"3\.\d+", result.stdout)
        if m:
            py_ver = m.group(0)

    cmd = [
        qmake,
        str(REPO / "trikRuntime.pro"),
        "-spec", spec,
        "CONFIG+=trik_not_brick",
        "CONFIG+=trik_nopython",
        "CONFIG+=tests",
        "CONFIG+=release",
    ]
    if py_ver:
        cmd.append(f"PYTHON_VERSION={py_ver}")
    print(f"--- qmake ---")
    print(f"  PATH={env['PATH'][:200]}...")
    print(f"  CMD: {' '.join(shlex.quote(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=build_dir, env=env)
    if result.returncode != 0:
        print("ERROR: qmake failed")
        sys.exit(result.returncode)
    print("qmake OK")


def run_make(env: dict, build_dir: Path, target: str = ""):
    make = shutil.which("mingw32-make", path=env["PATH"])
    if not make:
        make = shutil.which("make", path=env["PATH"])
    if not make:
        print("ERROR: mingw32-make not found on PATH")
        sys.exit(1)

    cmd = [make, "-j", str(os.cpu_count() or 2)]
    if target:
        cmd.append(target)

    print(f"\n--- mingw32-make [{target or 'all'}] ---")
    print(f"  CMD: {' '.join(shlex.quote(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=build_dir, env=env)
    if result.returncode != 0:
        print(f"ERROR: make [{target or 'all'}] failed")
        sys.exit(result.returncode)
    print("make OK")


def main():
    parser = argparse.ArgumentParser(description="Build trikRuntime")
    parser.add_argument("--qmake", action="store_true", help="Run qmake only")
    parser.add_argument("--clean", action="store_true", help="Clean build directory first")
    parser.add_argument("--qt", choices=["5.15", "6.7"], default="5.15", help="Qt version")
    parser.add_argument("--target", default="", help="Make target (e.g., sub-trikKernel)")
    args = parser.parse_args()

    env = build_env(args.qt)
    run_qmake(env, BUILD_DIR, clean=args.clean)
    if not args.qmake:
        run_make(env, BUILD_DIR, target=args.target)


if __name__ == "__main__":
    main()
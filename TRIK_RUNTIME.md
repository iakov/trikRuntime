# TRIK Runtime Developer Reference

**Scope:** Build system, architecture, conventions, CI, and translation workflow for
the TRIK controller firmware runtime. This is the canonical reference for anyone
developing, building, or debugging the runtime.

## What this doc covers

- Project structure and subproject dependency graph
- Build system (qmake, config flags, sanitizers, global.pri conventions)
- CI pipelines, linting, testing, formatting
- Translation system and how to add/modify languages
- Deployment and cross-compilation
- Key codebase conventions discovered from analysis

## What this doc does NOT cover

- User manual or end-user features (see README.md)
- API reference (see Doxygen docs and header files)
- Changelog (see resources/changelog.txt)
- ROS2 subsystem details (see trikRos2/README.md)
- Git workflow or contribution guide (see AGENTS.md)
- Detailed PythonQt binding generation

## Structure

Progressive disclosure — start with the overview, then drill into specific
subsystems. Each major section is self-contained.

---

## 1. Project Overview

TRIK Runtime is a Qt5/C++14 firmware for the TRIK educational robotics
controller. Apache 2.0 licensed. The robot hardware is referred to as the
"brick" in code. Two scripting engines are supported: QtScript (JavaScript,
default) and Python (via PythonQt, optional).

Key repos:
- [trikRuntime](https://github.com/trikset/trikRuntime) — this firmware
- [trikStudio](https://github.com/trikset/trikStudio) — visual IDE

---

## 2. Subproject Dependency Graph

Defined in `trikRuntime.pro`. Build order follows depended-upon-first:

| # | Project | Role | `.pro` location |
|---|---------|------|-----------------|
| 1 | `initvars` | Init qmake variables | `initvars.pre` |
| 2 | `qslog` | Logging library | `qslog/QsLogSharedLibrary.pro` |
| 3 | `trikKernel` | Common code (paths, config parsing, translations, exceptions) | `trikKernel/trikKernel.pro` |
| 4 | `trikWiFi` | WiFi management via wpa_supplicant | `trikWiFi/trikWiFi.pro` |
| 5 | `trikNetwork` | Network communication (mailbox protocol) | `trikNetwork/trikNetwork.pro` |
| 6 | `trikHal` | Hardware abstraction layer | `trikHal/trikHal.pro` |
| 7 | `trikDsp` | DSP/media processing | `trikDsp/trikDsp.pro` |
| 8 | `trikControl` | Robot hardware interface (brick) | `trikControl/trikControl.pro` |
| 9 | `trikTelemetry` | Telemetry service | `trikTelemetry/trikTelemetry.pro` |
| 10 | `trikCommunicator` | Network server for remote script execution | `trikCommunicator/trikCommunicator.pro` |
| 11 | `trikScriptRunner` | JS/Python/C++ script engine | `trikScriptRunner/trikScriptRunner.pro` |
| 12 | `trikGui` | User interface (QML-based) | `trikGui/trikGui.pro` |
| 13 | `trikRun` | CLI script runner | `trikRun/trikRun.pro` |
| 14 | `trikServer` | Network daemon | `trikServer/trikServer.pro` |
| 15 | `mlx90640-library` | Thermal camera driver | `mlx90640-library/mlx90640-library.pro` |
| 16 | `trikCppProgram` | C++ program runner | `trikCppProgram/trikCppProgram.pro` |
| 17 | `trikRos2` | ROS2 integration (optional, disabled with `CONFIG+=trik_not_brick`) | `trikRos2/trikRos2.pro` |
| 18 | `PythonQt` | Python bindings (optional, disabled with `CONFIG+=trik_nopython`) | `PythonQt/PythonQt.pro` |
| 19 | `translations` | Qt translations (.ts → .qm) | `translations/translations.pro` |

Build-time configuration flags:
- `CONFIG+=trik_not_brick` — disable hardware-dependent code (use stubs)
- `CONFIG+=trik_nopython` — disable Python scripting support
- `CONFIG+=tests` — include test subprojects
- `CONFIG+=ccache` — use ccache for faster rebuilds

---

## 3. Build System

### Prerequisites

```bash
git submodule update --init --recursive
```

Requires Qt 5.12+ with `qtscript`, `qtserialport`, `qtmultimedia`, `qtsvg`,
`qtdeclarative`, `qtquickcontrols2`. On Windows: MinGW 8.1.

### Build command

```bash
qmake -r
make -j$(nproc)
```

Or with options:

```bash
qmake CONFIG+=release CONFIG+=trik_not_brick CONFIG+=tests CONFIG+=sanitizer \
      CONFIG+=sanitize_undefined \
      PYTHON_VERSION=$(python3 --version | grep -o '3\.[^.]\+') \
      PYTHON_DIR=$(which python3 | xargs dirname | xargs dirname)
make -j$(nproc)
```

### Build config details

Set via `qmake` command line or `.qmake.cache`:

| Variable | Purpose |
|----------|---------|
| `PYTHON_PATH` | Path to Python installation (Windows) |
| `PYTHON_VERSION` | Python version string (e.g., "3.12") |
| `PYTHON_DIR` | Python prefix dir (Linux) |
| `INSTALL_ROOT` | Root for `make install` rules |

### Sanitizers

Controlled via `CONFIG` in `global.pri`:
- `sanitize-address` — address sanitizer
- `sanitize-undefined` — UB sanitizer (default when no other requested)
- `sanitize-thread` — thread sanitizer
- `sanitize_leak` — leak sanitizer (debug builds)
- `nosanitizers` — disable all sanitizers
- `debug_fps` — enable FPS counters in camera pipeline

### global.pri conventions

`global.pri` provides these functions to all subprojects (`global.pri:339-436`):

| Function | Purpose |
|----------|---------|
| `interfaceIncludes(projects)` | Add `include/` dir of given projects to INCLUDEPATH |
| `links(projects)` | Link against given projects' libraries |
| `copyToDestdir(files, [now])` | Copy files to DESTDIR; with `now` for config files |
| `installs()` | Set up `make install` rules for headers + target |
| `installAdditionalConfigs(files)` | Install configs to `/etc/trik/trikRuntime/` |
| `installAdditionalSharedFiles(files)` | Install files to `/usr/share/trikRuntime/` |
| `enableFlagIfCan(flag)` | Test-compile a flag before adding it to CXXFLAGS |

All projects output to a shared `bin/` directory. `rpath` is set to `$ORIGIN`
for portable binaries.

### C++ standard and warning flags

- C++14 (CONFIG += c++14)
- `-pedantic-errors -Wextra -Werror`
- Specific warnings-as-errors: `-Werror=cast-qual`, `-Werror=write-strings`,
  `-Werror=redundant-decls`, `-Werror=unreachable-code`,
  `-Werror=non-virtual-dtor`, `-Werror=uninitialized`
- Qt headers treated as system headers to suppress their warnings

---

## 4. CI & Quality

### GitHub Actions workflows (`/.github/workflows/`)

| Workflow | OS | Tools | Triggers |
|----------|----|-------|----------|
| `main.yml` | Windows MinGW 8.1 | Qt 5.15, Python, `mingw32-make check` | push, PR |
| `linter.yml` | Ubuntu latest | clang-tidy 15, clazy, Qt 5.15 | push, PR |
| `trik-toolchain.yml` | Ubuntu latest | ARM cross-compiler toolchain | push, PR |
| `rockylinux.yml` | Rocky Linux | RPM build | push, PR |
| `macos.yml` | macOS | Xcode | push, PR |

### Linting

- **clang-tidy 15** (`linter.yml:89-103`) — runs on changed files only
- **clazy** (level0/1/2) — Qt-specific static analysis
- Ignored paths: PythonQt/, mlx90640-library/, trikRos2/, generated_cpp/

### Testing

- Framework: Google Test (`tests/thirdparty/googletest.pri`)
- Entry point: `tests/mainTest.cpp` — calls `RUN_ALL_TESTS()`
- Run with: `make check` (or `mingw32-make check -k` on Windows MinGW)
- Test subprojects: `trikKernelTests`, `trikJsRunnerTests`, `trikPyRunnerTests`,
  `trikCommunicatorTests`, `trikNetworkTests`, `trikCameraPhotoTests`, `selftest`
- Common test config: `tests/common.pri` sets `CONFIG += testcase`
- Config files: `test-system-config.xml`, `test-model-config.xml`

### Formatting

- `.clang-format` at repository root
- `run-clang-format.sh` script available

---

## 5. Translations

### File format

Qt `.ts` XML files in `translations/`. Compiled to `.qm` binary format via
`lrelease` (triggered by `CONFIG += lrelease` in `translations/translations.pro`).

### Discovery

`trikKernel::TranslationsHelper` (`trikKernel/src/translationsHelper.cpp:33-53`)
loads all `.ts` files from `Paths::translationsPath()` whose filename suffix
matches the current locale code.

### How to add a new language

Full step-by-step (also at `translations/ADDING_TRANSLATIONS.en.md`):

1. Create `translations/trikRuntime_<lang>.ts` (copy `trikRuntime_sample.ts`,
   set `language="<lang>"`)
2. Register in `translations/translations.pro`: add
   `$$PWD/trikRuntime_<lang>.ts \` to `TRANSLATIONS +=`
3. Register in `trikRuntime.pro`: add
   `$$PWD/translations/trikRuntime_<lang>.ts \` to `TRANSLATIONS +=`
4. Run `lupdate` (Qt Creator: Tools → External → Linguist → Update Translations)
5. Translate strings using Qt Linguist
6. Add a flag icon `trikGui/resourcesQml/<lang>.png` (24×16 px)
7. Register the icon in `trikGui/trikGui.qrc`:
   `<file>resourcesQml/<lang>.png</file>`
8. Edit `trikGui/qml/Language.qml` — add `case "<lang>":` to both
   `getLanguageIcon()` (icon path) and `getLanguage()` (display name)
9. Rebuild to generate `.qm` files

### UI registration

In `trikGui/qml/Language.qml:69-93`, two hardcoded switch statements map
language codes to icons and display names:
- `getLanguageIcon(language)` — returns icon path
- `getLanguage(language)` — returns display name (e.g., "Español")

Add a `case "es":` entry to both for each new language.

### Display on robot

The `LanguageSelection` C++ class (`trikGui/languageSelection.cpp`) scans the
`translations/` directory for files matching `*_<lang>.ts` to populate the
language selection list. Any `.ts` file with a language code suffix is
automatically discovered — no C++ code change needed for discovery.

### Current languages

| Code | File | Status |
|------|------|--------|
| `en` | (built-in, no `.ts` file) | English (source) |
| `ru` | `trikRuntime_ru.ts` | Full translation (Russian) |
| `fr` | `trikRuntime_fr.ts` | Full translation (French) |
| `de` | `trikRuntime_de.ts` | Full translation (German) |
| `es` | `trikRuntime_es.ts` | Full translation (Spanish) |

All non-English translation files have been fully backfilled from the original
Russian translations.

---

## 6. Key Code Conventions

### Naming

- Namespaces: `trikControl`, `trikKernel`, `trikHal`, `trikCommunicator`, etc.
- Classes: `TrikXxx` or `XxxInterface` (interfaces)
- Include pattern: each subproject has `include/` directory with public headers
- Export macros: `TRIKKERNEL_EXPORT`, `TRIKCONTROL_EXPORT`, `TRIKHAL_EXPORT`

### Architecture

- `BrickInterface` (`trikControl/include/trikControl/brickInterface.h`) is the
  central facade for robot hardware — motors, sensors, encoders, display,
  camera, etc.
- Hardware access goes through `trikHal` interfaces
- Configuration is XML-based (`system-config.xml`, `model-config.xml`)

### DEFINES

| Define | Purpose |
|--------|---------|
| `QT_FORCE_ASSERTS` | Always-on Qt assertions (set in `global.pri`) |
| `TRIKKERNEL_LIBRARY` | trikKernel export macro |
| `TRIKCONTROL_LIBRARY` | trikControl export macro |
| `TRIKHAL_LIBRARY` | trikHal export macro |
| `TRIK_DEBUG_FPS` | Enable FPS counters in camera pipeline |
| `ENGINES_INIT_INTERNAL_TYPES` | Enable PythonQt internal type initialization |

### Error handling

- Custom exception hierarchy in `trikKernel/include/trikKernel/exceptions/`
- QsLog for structured logging (levels: Trace, Debug, Info, Warning, Error, Fatal)

---

## 7. Deployment

### To a robot

```bash
cd bin/
./deploy.sh <robot-ip>
```

Uses SSH + rsync to copy binaries to `/home/root/trik` on the robot, then
restarts `trikGui`.

### Docker-based CI builds

- `docker/Dockerfile.bionic` — Qt 5.12.10, GCC 9, ARM cross
- `docker/Dockerfile.xenial` — older base

---

## 8. Branching Policy

This project follows a **dev → upstream** workflow:

- **Dev branch** (`origin/me/*`) — all work-in-progress lives here. Kept as a
  **single squashed commit** ahead of `upstream/master`. Contains everything:
  developer docs, scripts, translation files, regenerated assets, AI agent
  configuration.

- **Upstream PRs** — created from `upstream/master` base, cherry-picking only
  the files that belong to the firmware product or CI pipeline:
  - Translation `.ts` files and `.pro`/`.qrc` build registrations
  - Product assets (flag PNGs, icons)
  - Legal files (`LICENSE`, `NOTICE`, `licenses/*`, `attribution.txt`)
  - CI workflow files (`.github/workflows/*`)

- **Dev-only files** (never upstream):
  - Developer documentation (`TRIK_RUNTIME.md`, `AGENTS.md`)
  - Development scripts and config (`.mdformat`, `scripts/generate_flag_icons.py`,
    `scripts/mdformat.sh`, `scripts/mdl_style.rb`)
  - Scratch/reference artifacts (`.tmp/`, `.local_development.db`)
  - AI agent configuration

  These files stay exclusively on the dev branch to keep upstream focused on
  the shipping product. They can be added to an upstream PR only when
  explicitly requested.

### PR body safety

PowerShell interprets backticks (`) as escape characters inside double-quoted
strings. When creating pull requests, always write description text to
`.tmp/pr_<number>_body.md` and pass via `gh pr create --body-file .tmp/...` to
avoid shell corruption of backticks, dollar signs, and other special characters.

---

## 9. Related Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| AGENTS.md | `/AGENTS.md` | Entry point for AI agents |
| README.md | `/README.md` | High-level project description |
| Changelog | `/resources/changelog.txt` | Release history (Russian) |
| VPP model | `/docs/trikRuntime.vpp` | Visual Paradigm UML model |
| Translation guide | `/translations/ADDING_TRANSLATIONS.en.md` | Step-by-step translation workflow |
| ROS2 details | `/trikRos2/README.md` | ROS2 subsystem documentation |
| C++ program guide | `/trikCppProgram/README.md` | Writing C++ programs for TRIK |
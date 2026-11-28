# Migration Plan: `trikset/trikRuntime` to Dual Qt 5.15 / Qt 6.x Support

## 1. Objective & Hard Constraints
* **Primary Target:** Maintain 100% compatibility and green CI on **Qt 5.15** (required for `trik-distro` / Yocto builds).
* **Secondary Target:** Add a parallel **Qt 6.x (6.8 LTS)** GitHub Actions CI job that incrementally expands build and test coverage until the entire repository builds cleanly on both Qt 5.15 and Qt 6.x.
* **Out of Scope:** Do **not** modify `trik-distro` or `meta-trik` Yocto recipes. Do **not** migrate from `qmake` to `CMake` during this phase.
* **Merge Policy:** Every pull request must be atomic, keep the Qt 5.15 CI pipeline green, and never regress already-ported Qt 6 subprojects.

---

## 2. Repository Architecture & Dependency Order
Port subprojects strictly bottom-up to avoid blocked builds:
1. `trikKernel` (logging, time, config, core utilities)
2. `trikHal` (hardware abstraction layer)
3. `trikControl` (motors, sensors, brick interfaces)
4. `trikNetwork` / `trikWiFi` / `trikTelemetry`
5. `trikScriptRunner` / `trikRun` (`QJSEngine` & `PythonQt`)
6. `trikCommunicator` / `trikServer`
7. `trikGui` / `trikRos2` (optional/conditional targets)

Key build files: `trikRuntime.pro`, `global.pri`, `initvars.pre`, `.github/workflows/*`, `.mergify.yml`.

---

## 3. Milestones & Acceptance Criteria

### Milestone 1: C++17 Baseline & Qt 5.15 Deprecation Cleanup
* **Tasks:**
  * Set `CONFIG += c++17` globally in `global.pri` (done in `qt6-pre1`).
  * Enable `DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x050F00` in `global.pri` (done — applied globally, not per-subproject). Exempt `trikScriptRunner` with `DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x000000` (postponed).
  * Replace deprecated Qt 5 APIs:
    * `QRegExp` → `QRegularExpression` (done: `trikGui/communicationSettings.cpp`).
    * `QSet<T>` → `std::set<T>` (done: 5 files in `trikControl/`, 1 in `trikKernel/`). Method mapping: `contains()` → `count()`, `remove()` → `erase()`.
    * `QString::KeepEmptyParts` / `QString::SkipEmptyParts` → `Qt::KeepEmptyParts` / `Qt::SkipEmptyParts` (done: `trikControl/gamepad.cpp`, `soundSensorWorker.cpp`, `trikHal/trikFifo.cpp`). Guard with `#if QT_VERSION >= 0x060000` when needed.
    * `endl` → `'\n'` on QTextStream (done: `qslog/QsLogDestFile.cpp`).
    * `QOverload<...>::of(&QTcpSocket::error)` → `SIGNAL("error(QAbstractSocket::SocketError)")` + `SLOT(...)` (done: `trikNetwork/connection.cpp`).
    * `QRegExp`/`QSet`/`QString::SkipEmptyParts` usages in `trikScriptRunner/` are **postponed**.
  * Add `QT += core5compat` under `greaterThan(QT_MAJOR_VERSION, 5)` where `QSettings` is used: `trikKernel/trikKernel.pro`, `trikGui/trikGui.pro`.
  * Guard removed Qt 6 modules:
    * `QT += quick` — guard with `!greaterThan(QT_MAJOR_VERSION, 5)` in `trikGui.pro`, `trikControl.pro`.
    * `QT += concurrent` — guard with `!greaterThan(QT_MAJOR_VERSION, 5)` in `trikGui.pro`.
* **Green CI Gate:**
  * Existing Qt 5.15 CI workflow builds all targets and passes all tests with zero deprecation errors.

### Milestone 2: Replace `QtScript` with `QJSEngine` (on Qt 5.15)
* **Context:** `QtScript` (`QScriptEngine`) was removed in Qt 6, whereas `QJSEngine` (`QT += qml`) exists in both Qt 5.15 and Qt 6.
* **Tasks:**
  * Update `.pro` files (`trikScriptRunner`, `trikRun`, `trikCommunicator`, etc.): replace `QT += script` with `QT += qml`.
  * Refactor `trikScriptRunner` (`scriptEngineWorker`, thread wrappers, value conversions) from `QScriptEngine` / `QScriptValue` to `QJSEngine` / `QJSValue`.
  * Replace `QScriptable` / custom `QScriptValue` prototypes with `Q_INVOKABLE`, `Q_PROPERTY`, `Q_ENUM`, and `QJSEngine::newQObject()`.
  * Ensure `QJSEngine` thread affinity rules are respected (create/use `QJSEngine` strictly on its worker `QThread`).
* **Green CI Gate:**
  * Qt 5.15 CI builds with zero references to `QtScript` and passes all JavaScript execution and hardware mock tests.

### Milestone 3: Non-Blocking Qt 6.x CI Setup
* **Tasks:**
  * (Postponed: PythonQt submodule update — focus on Qt 5.15 first)
  * Guard version-specific `qmake` rules in `global.pri` and `.pro` files using `greaterThan(QT_MAJOR_VERSION, 5)`.
  * Add a new GitHub Actions workflow (e.g., `.github/workflows/qt6.yml`) using `jurplel/install-qt-action` (Qt `6.8.*` LTS with `qtdeclarative` / `qt5compat` as needed) marked `continue-on-error: true`.
  * Configure the Qt 6 CI job to run `qmake` and compile `trikKernel` (`make sub-trikKernel`).
* **Green CI Gate:**
  * Qt 5.15 CI remains green (required).
  * Qt 6.x CI workflow configures `qmake` and builds `trikKernel` cleanly.

### Milestone 4: Port Core & Headless Libraries to Qt 6
* **Tasks:**
  * Enable subprojects sequentially in `.github/workflows/qt6.yml`:
    1. `sub-trikHal`
    2. `sub-trikControl`
    3. `sub-trikNetwork`, `sub-trikWiFi`, `sub-trikTelemetry`
    4. `sub-trikScriptRunner`, `sub-trikRun`
  * Resolve Qt 6 breaking changes while preserving Qt 5.15 compatibility:
    * `QTextCodec` removals -> use `QStringConverter` (`#if QT_VERSION >= QT_VERSION_CHECK(6, 0, 0)`) or UTF-8 `QTextStream` defaults.
    * `QNetworkConfigurationManager` removals in `trikNetwork` -> guard or replace with `QNetworkInformation` / platform checks.
    * Container index types (`qsizetype` vs `int`) -> fix narrowing conversions and `qHash` return types (`size_t` in Qt 6).
    * `QVariant::type()` -> use `typeId()` / `metaType()` with version guards where needed.
* **Green CI Gate:**
  * Qt 5.15 CI green (required).
  * Qt 6.x CI builds all headless libraries and passes unit tests.

### Milestone 5: Port GUI/Server Entry Points & Enforce Dual-Green CI
* **Tasks:**
  * Enable `trikCommunicator`, `trikServer`, `trikGui`, and conditional `trikRos2` builds in `.github/workflows/qt6.yml`.
  * Fix widget/GUI API differences in `trikGui`:
    * `QWidget::enterEvent(QEvent *)` (Qt 5) vs `enterEvent(QEnterEvent *)` (Qt 6).
    * `QFontMetrics::width()` -> `QFontMetrics::horizontalAdvance()` (available since Qt 5.11).
    * `QMouseEvent::pos()` / `globalPos()` -> `position().toPoint()` / `globalPosition().toPoint()` under version guards.
  * Remove `continue-on-error: true` from `.github/workflows/qt6.yml` and add the Qt 6 check to `.mergify.yml` required status checks.
* **Green CI Gate:**
  * Full `trikRuntime.pro` builds and passes tests on **both** Qt 5.15 and Qt 6.8 LTS on every PR.

---

## 4. Coding Agent Rules & Patterns

### Version Guards (Use Sparingly)
Prefer APIs available in both Qt 5.15 and Qt 6 (e.g., `QRegularExpression`, `horizontalAdvance()`, `QJSEngine`). Only use preprocessor guards when APIs genuinely diverge:
```cpp
#if QT_VERSION >= QT_VERSION_CHECK(6, 0, 0)
    // Qt 6 implementation
#else
    // Qt 5.15 implementation
#endif
```

### `qmake` Version Checks
```qmake
equals(QT_VERSION_MAJOR, 6) {
    # Qt 6 specific modules or flags
} else {
    # Qt 5.15 specific modules or flags
}
```

### Verification Checklist Before Every Commit
1. `qmake` succeeds under both Qt 5.15 and Qt 6.x without unknown module errors.
2. No unguarded Qt 6-only headers are included in paths compiled by Qt 5.15.
3. No `QtScript` headers or `QT += script` remain in modified subprojects.
4. All existing unit tests pass on Qt 5.15, and newly enabled subprojects pass on Qt 6.x.

### Build Environment Notes (Windows)

- **Submodules:** All submodules must be initialized (`git submodule update --init --recursive`) before building. Key submodules: `trikGui/Qt-QrCodeGenerator`, `trikDsp/trik-media-sensors`, `PythonQt/PythonQt`.
- **MinGW:** Use Qt-bundled MinGW 8.1 at `C:\Qt\Tools\mingw810_32\bin\g++.exe` (32-bit), or the MSYS2 MinGW installation.
- **PATH:** Must include MinGW bin (for g++, mingw32-make) and Qt bin (for qmake, moc, lrelease).
- **Python:** The build requires `PYTHON_VERSION` for PythonQt. Use `CONFIG+=trik_nopython` to skip (or pass `PYTHON_VERSION=3.x`).
- **Wrapper:** Use `.tmp/build_wrapper.py` for reproducible builds — it sets up PATH, detects Python version, and runs qmake + make. Run via `uv run python .tmp/build_wrapper.py`.

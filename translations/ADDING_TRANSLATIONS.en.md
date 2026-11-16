# Adding Translation to the TRIK firmware (trik-runtime) Project

## Fork and branch

1. Fork the repository on GitHub: open
   [trikset/trikRuntime](https://github.com/trikset/trikRuntime) and click
   "Fork".

2. Clone your fork:
   ```shell
   git clone https://github.com/your-username/trikRuntime.git
   cd trikRuntime
   ```

3. Create a branch:
   ```shell
   git checkout -b add-translation-<language_code>
   ```

## Add the language — step by step

### 1. Create the translation file

Create `translations/trikRuntime_<language_code>.ts` using
`translations/trikRuntime_sample.ts` as a template:

```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="<language_code>">
</TS>
```

Set the `language` attribute to your language code (use the 2-letter ISO 639-1
code, e.g. `es`, `de`, `fr`, `ru`).

### 2. Register in `translations/translations.pro`

Add your file to the `TRANSLATIONS +=` block:

```shell
        $$PWD/trikRuntime_<language_code>.ts \
```

Maintain the existing style: trailing backslash on every line.

### 3. Register in `trikRuntime.pro`

Add your file to the `TRANSLATIONS +=` block in the project root:

```shell
        $$PWD/translations/trikRuntime_<language_code>.ts \
```

Trailing backslash on every line.

### 4. Run lupdate

In Qt Creator: **Tools → External → Linguist → Update Translations (lupdate)**.
Or from command line:

```shell
lupdate trikRuntime.pro
```

This populates your `.ts` file with all translatable source strings extracted
from the codebase.

### 5. Translate strings

Open your `.ts` file in **Qt Linguist** and provide translations for every
source string. Save the file when done.

### 6. Generate a flag icon

```shell
uv run python scripts/generate_flag_icons.py --flags <language_code>
```

This renders the flag as an SVG vector graphic and converts it to a 60×60 RGBA
PNG in `trikGui/resourcesQml/<language_code>.png` using cairosvg. Each flag's
geometry is defined compactly in the script — no system font dependencies.

To regenerate all flags at once:

```shell
uv run python scripts/generate_flag_icons.py --all
```

Run with no arguments to see usage and supported codes.

Register the icon in `trikGui/trikGui.qrc`:

```xml
        <file>resourcesQml/<language_code>.png</file>
```

### 7. Wire up the QML language picker

Edit `trikGui/qml/Language.qml`. Two hardcoded switch statements need a new
`case` entry:

**`getLanguageIcon()` function (line ~69)** — maps language code to icon path:

```qml
                    case "<language_code>":
                        return iconsPath + "<language_code>.png";
```

**`getLanguage()` function (line ~84)** — maps language code to display name:

```qml
                    case "<language_code>":
                        return "<Display name in native language>";
```

Use the language's own name for display, e.g. `"Español"`, `"Deutsch"`,
`"Française"`, `"Русский"`.

### 8. Rebuild

Build the project:

```shell
qmake -r
make -j$(nproc)
```

The `lrelease` step runs automatically via `CONFIG += lrelease` in
`translations/translations.pro` and produces `.qm` files in the output
`translations/` directory.

### 9. Verify

Run `trikGui` or `trikRun` on the robot. Open the language selection menu —
your new language should appear automatically. Select it to verify the UI
displays your translations.

### 10. Commit and push

```shell
git add .
git commit -m "Add translation for <language>"
git push origin add-translation-<language_code>
```

Open a Pull Request on the main repository.

## How auto-discovery works

No C++ code changes are needed for the language to appear in the settings menu.
The robot discovers languages automatically:

1. `LanguageSelection::loadLocales()` scans the `translations/` directory for
   files matching `trikRuntime_<code>.ts` (see
   `trikGui/languageSelection.cpp:35-51`).

2. Each matching file produces a language entry in the list.

3. The QML `Language.qml` delegates to `getLanguageIcon()` and `getLanguage()`
   for the icon and display name — these are the only two places that require a
   code change (step 7 above).

4. When a language is selected, `TranslationsHelper::loadTranslators()` loads
   all `.ts` files whose two-letter code matches the chosen locale.

English (`en`) is hardcoded as default and does not have a `.ts` file — it uses
the source strings directly.

## Reusable reference artifacts

When adding a new language, the files in `.tmp/` may help:

| File | Purpose |
|------|---------|
| `.tmp/translation_map.csv` | Cross-reference of all 123 source strings with context, Russian, German, French, and Spanish translations |
| `.tmp/prompts/translate_spanish.prompt.md` | Complete subagent prompt template for translating all strings |
| Existing `.ts` files | Reference implementations in `translations/trikRuntime_*.ts` |

## Editing existing translation files

1. Open the `.ts` file in **Qt Linguist**.
2. Edit or add translations as needed.
3. Rebuild the project to regenerate `.qm` files.

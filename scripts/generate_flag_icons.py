#!/usr/bin/env python3
"""
Generate flag icons for the TRIK Runtime language selector.

Renders flags as 60x60 RGBA PNGs. Uses two backends:

1. uharfbuzz (default) — renders via HarfBuzz RasterPaint for color emoji
   glyphs. Falls back to cairosvg if the font lacks COLR/CPAL paint support.
2. cairosvg — SVG vector rendering, no font dependency.

Usage:
    uv run python scripts/generate_flag_icons.py --all
    uv run python scripts/generate_flag_icons.py --flags es pt
    uv run python scripts/generate_flag_icons.py --all --output trikGui/resourcesQml
    uv run python scripts/generate_flag_icons.py --all --svg    # force SVG mode
"""

import argparse
import os
import sys
from pathlib import Path

FLAG_SVGS = {
    'en': '''<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 60 60">
  <rect x="0" y="0" width="60" height="60" fill="#012169"/>
  <polygon points="0,0 60,60" fill="none" stroke="#FFFFFF" stroke-width="4"/>
  <polygon points="0,60 60,0" fill="none" stroke="#FFFFFF" stroke-width="4"/>
  <polygon points="0,4 60,56" fill="none" stroke="#C8102E" stroke-width="8"/>
  <polygon points="4,60 56,0" fill="none" stroke="#C8102E" stroke-width="8"/>
  <rect x="0" y="26" width="60" height="8" fill="#C8102E"/>
  <rect x="26" y="0" width="8" height="60" fill="#C8102E"/>
</svg>''',

    'ru': '''<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60">
  <rect x="0" y="0" width="60" height="20" fill="#FFFFFF"/>
  <rect x="0" y="20" width="60" height="20" fill="#0039A6"/>
  <rect x="0" y="40" width="60" height="20" fill="#D52B1E"/>
</svg>''',

    'fr': '''<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60">
  <rect x="0" y="0" width="20" height="60" fill="#002395"/>
  <rect x="20" y="0" width="20" height="60" fill="#FFFFFF"/>
  <rect x="40" y="0" width="20" height="60" fill="#ED2939"/>
</svg>''',

    'de': '''<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60">
  <rect x="0" y="0" width="60" height="20" fill="#000000"/>
  <rect x="0" y="20" width="60" height="20" fill="#DD0000"/>
  <rect x="0" y="40" width="60" height="20" fill="#FFCE00"/>
</svg>''',

    'es': '''<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60">
  <rect x="0" y="0" width="60" height="20" fill="#AA151B"/>
  <rect x="0" y="20" width="60" height="20" fill="#FBBF1C"/>
  <rect x="0" y="40" width="60" height="20" fill="#AA151B"/>
</svg>''',
}

FLAG_EMOJI = {
    'en': '\U0001F1EC\U0001F1E7',
    'ru': '\U0001F1F7\U0001F1FA',
    'fr': '\U0001F1EB\U0001F1F7',
    'de': '\U0001F1E9\U0001F1EA',
    'es': '\U0001F1EA\U0001F1F8',
}

DEFAULT_OUTPUT = 'trikGui/resourcesQml'


def find_emoji_font():
    candidates = []
    if sys.platform == 'win32':
        windir = os.environ.get('WINDIR', r'C:\Windows')
        candidates.append(os.path.join(windir, 'Fonts', 'seguiemj.ttf'))
    elif sys.platform == 'darwin':
        candidates.append('/System/Library/Fonts/Apple Color Emoji.ttc')
    else:
        candidates.extend([
            '/usr/share/fonts/noto/NotoColorEmoji.ttf',
            '/usr/share/fonts/opentype/noto/NotoColorEmoji.ttf',
        ])
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None


def render_via_uharfbuzz(code, font_path, output_size=(60, 60)):
    """Render flag using uharfbuzz RasterPaint. Returns PIL Image or None."""
    import uharfbuzz as hb
    from PIL import Image

    blob = hb.Blob.from_file_path(font_path)
    face = hb.Face(blob)
    font = hb.Font(face)

    if not face.has_color_paint:
        print(f"  Font has no color paint support, skipping uharfbuzz for {code}")
        return None

    buf = hb.Buffer()
    buf.add_str(FLAG_EMOJI[code])
    buf.guess_segment_properties()
    hb.shape(font, buf)
    gids = [info.codepoint for info in buf.glyph_infos]

    # Use RasterPaint for COLR color rendering
    rp = hb.RasterPaint()
    rp.foreground = hb.Color(255, 255, 255, 255)

    for gid in gids:
        glyph_has_paint = font.get_glyph_color_paint(gid) if hasattr(font, 'get_glyph_color_paint') else None
        if glyph_has_paint:
            rp.paint_glyph(font, gid)
        else:
            # Fallback: paint as solid silhouette
            rp.paint_glyph(font, gid)

    result = rp.render()
    if result is None:
        return None

    e = result.extents
    w, h, stride = e.width, e.height, e.stride
    buf_data = result.buffer

    # BGRA stride to RGBA
    row_size = w * 4
    stripped = bytearray()
    for y in range(h):
        stripped.extend(buf_data[y * stride : y * stride + row_size])

    img = Image.frombuffer('RGBA', (w, h), bytes(stripped), 'raw', 'BGRA', 0, 1)
    resized = img.resize(output_size, Image.LANCZOS)
    return resized


def render_via_cairosvg(code, output_size=(60, 60)):
    """Render flag using SVG via cairosvg. Returns PIL Image or None."""
    from PIL import Image
    import cairosvg
    import io

    svg = FLAG_SVGS.get(code)
    if svg is None:
        return None

    png_data = cairosvg.svg2png(svg)
    img = Image.open(io.BytesIO(png_data))
    if img.size != output_size:
        img = img.resize(output_size, Image.LANCZOS)
    return img


def render_flag(code, use_font=False, font_path=None, output_size=(60, 60)):
    """Render flag, trying font first then falling back to SVG."""
    if use_font and font_path:
        img = render_via_uharfbuzz(code, font_path, output_size)
        if img is not None:
            # Check if image has color content
            r, g, b, a = img.split()
            has_color = r.getextrema()[1] > 0 or g.getextrema()[1] > 0 or b.getextrema()[1] > 0
            if has_color:
                return img
            print(f"  Font render for {code} produced no color, falling back to SVG")

    return render_via_cairosvg(code, output_size)


def main():
    parser = argparse.ArgumentParser(
        description="Generate flag icons for TRIK Runtime language selector.",
        add_help=False,
    )
    parser.add_argument('--all', action='store_true',
                        help='Regenerate all known flags')
    parser.add_argument('--flags', nargs='+', default=None,
                        help='Space-separated list of language codes to generate')
    parser.add_argument('--output', default=DEFAULT_OUTPUT,
                        help=f'Output directory (default: {DEFAULT_OUTPUT})')
    parser.add_argument('--font', nargs='?', const='auto', default=None,
                        help='Use font rendering (optional: path to font)')
    parser.add_argument('--svg', action='store_true',
                        help='Force SVG rendering (default: try font first)')

    args = parser.parse_args()

    if not args.all and not args.flags:
        print("Generate flag icons for TRIK Runtime language selector.\n")
        print("Usage:")
        print("  uv run python scripts/generate_flag_icons.py --all")
        print("  uv run python scripts/generate_flag_icons.py --flags es pt")
        print("  uv run python scripts/generate_flag_icons.py --all --output trikGui/resourcesQml\n")
        print("  uv run python scripts/generate_flag_icons.py --flags es --font")
        print("    (render from emoji font instead of SVG)\n")
        print("Supported flag codes:")
        for code in sorted(FLAG_SVGS):
            print(f"  {code}")
        print()
        print("Requires cairosvg or uharfbuzz:")
        print("  uv pip install cairosvg")
        print("  uv pip install uharfbuzz")
        sys.exit(0)

    if args.all and args.flags:
        print("Note: --all and --flags both given; --all takes precedence.", file=sys.stderr)

    if args.all:
        codes = list(FLAG_SVGS.keys())
    else:
        codes = args.flags

    # Determine render mode
    use_font = bool(args.font) and not args.svg
    font_path = None
    if use_font:
        if args.font == 'auto':
            font_path = find_emoji_font()
            if font_path is None:
                print("No emoji font found, falling back to SVG rendering", file=sys.stderr)
                use_font = False
        else:
            font_path = args.font

    if font_path:
        print(f"Using font: {font_path}")

    # Check dependencies
    if not use_font:
        try:
            import cairosvg
        except ImportError:
            print("Error: cairosvg not installed.", file=sys.stderr)
            print("Install with: uv pip install cairosvg", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            import uharfbuzz
        except ImportError:
            print("Error: uharfbuzz not installed.", file=sys.stderr)
            print("Install with: uv pip install uharfbuzz", file=sys.stderr)
            sys.exit(1)

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    generated = 0
    skipped = 0

    for code in codes:
        if code not in FLAG_SVGS:
            print(f"  Skip '{code}': unknown flag code (supported: {', '.join(sorted(FLAG_SVGS))})")
            skipped += 1
            continue

        img = render_flag(code, use_font=use_font, font_path=font_path)
        if img is None:
            print(f"  Skip '{code}': render failed")
            skipped += 1
            continue

        out_path = out_dir / f'{code}.png'
        img.save(str(out_path))
        file_size = os.path.getsize(str(out_path))
        print(f"  {code}.png -> {file_size} bytes")
        generated += 1

    print(f"\nDone: {generated} generated, {skipped} skipped")


if __name__ == '__main__':
    main()
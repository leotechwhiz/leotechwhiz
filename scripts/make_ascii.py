"""Generate animated ASCII art portrait SVG from source-photo.jpg.

Light & dark mode adaptive via CSS variables and prefers-color-scheme.
Two accents only: Accent 1 (Blue) and Accent 2 (Green).
Animation strictly confined to portrait draw-in and smoke looping.
"""

import html
import sys
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.theme import THEME

WIDTH, HEIGHT = 460, 480
COLS          = 110
RAMP          = " .:-=+*#%@"
FONT          = THEME.get("font_family", "monospace")


def _process_image(path: Path):
    img = Image.open(path)
    w, h = img.size
    crop = img.crop((int(w * .08), int(h * .02), int(w * .92), int(h * .94)))
    gray = ImageOps.grayscale(crop)
    gray = ImageEnhance.Contrast(gray).enhance(1.85)
    gray = ImageEnhance.Sharpness(gray).enhance(1.6)
    rows = int(COLS * (gray.height / gray.width) * 0.51)
    return gray.resize((COLS, rows), Image.Resampling.LANCZOS), rows


def _opacity_bucket(b: int) -> float:
    if b < 16:
        return 0.0
    return round(max(0.2, min(1.0, round((0.25 + 0.75 * b / 255) * 10) / 10)), 1)


def generate_ascii_svg(photo: Path, output: Path) -> None:
    img, rows = _process_image(photo)

    pad_x, pad_y = 18, 22
    usable_h     = HEIGHT - pad_y * 2
    line_h       = usable_h / rows
    font_size    = round(line_h * 0.98, 2)

    ROW_DELAY    = 0.043
    DRAW_TIME    = round(rows * ROW_DELAY, 2)
    SMOKE_START  = DRAW_TIME + 0.3

    CIG_R0, CIG_R1 = int(rows * .50), int(rows * .68)
    CIG_C0, CIG_C1 = int(COLS * .44), int(COLS * .68)

    # ── build text rows ───────────────────────────────────────────────────────
    text_rows = []
    for y in range(rows):
        spans   = []
        cur_op  = None
        cur_buf = []

        def flush():
            if not cur_buf:
                return
            txt = html.escape("".join(cur_buf))
            if cur_op == 0.0:
                spans.append(txt)
            else:
                spans.append(f'<tspan fill-opacity="{cur_op:.1f}">{txt}</tspan>')

        for x in range(COLS):
            b = img.getpixel((x, y))
            if CIG_R0 <= y <= CIG_R1 and CIG_C0 <= x <= CIG_C1 and b >= 200:
                ch = "=" if b < 235 else "#"
                op = 1.0
            else:
                ch = RAMP[int(b / 255 * (len(RAMP) - 1))] if b >= 16 else " "
                op = _opacity_bucket(b)

            if op != cur_op:
                flush()
                cur_op, cur_buf = op, [ch]
            else:
                cur_buf.append(ch)

        flush()
        base_y = round(pad_y + y * line_h + line_h * 0.82, 2)
        delay  = round(y * ROW_DELAY, 3)
        text_rows.append(
            f'  <text x="{pad_x}" y="{base_y}" class="ar"'
            f' style="animation-delay:{delay}s">{"".join(spans)}</text>'
        )

    # ── smoke text groups (4 staggered loops) ────────────────────────────────
    tip_x = pad_x + int(COLS * 0.55 * (WIDTH - 2 * pad_x) / COLS)
    tip_y = pad_y + int(rows * 0.57 * line_h)

    smoke_groups = [
        (0,   ". : ~ `",  5.2, 0.0,  14),
        (-6,  "~ . ' o",  6.0, 1.4, -12),
        (4,   ": ~ ' `",  7.1, 2.7,  16),
        (-3,  ". : ' o",  5.6, 4.0, -10),
    ]

    smoke_keyframes = ""
    smoke_els       = []
    for i, (xoff, chars, dur, extra, drift) in enumerate(smoke_groups):
        kn = f"sf{i}"
        rise = 60 + i * 15
        smoke_keyframes += f"""
      @keyframes {kn} {{
        0%   {{ transform:translate(0,0) scale(.9);            opacity:0   }}
        15%  {{ opacity:.7 }}
        50%  {{ transform:translate({drift}px,-{rise//2}px) scale(1.15); opacity:.4 }}
        80%  {{ transform:translate({-drift//2}px,-{int(rise*.85)}px) scale(1.35); opacity:.15 }}
        100% {{ transform:translate({drift//3}px,-{rise}px) scale(1.5);  opacity:0   }}
      }}"""
        sd = round(SMOKE_START + extra, 2)
        smoke_els.append(
            f'    <text x="{tip_x + xoff}" y="{tip_y}" class="sc"'
            f' style="animation:{kn} {dur}s ease-in-out {sd}s infinite">'
            f'{html.escape(chars)}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="{HEIGHT}"
     role="img" aria-label="Roshan Gautam Animated ASCII Portrait">
  <defs>
    <filter id="sf">
      <feGaussianBlur stdDeviation=".45"/>
    </filter>
    <style>
      :root {{
        --bg: #0d1117;
        --border: #30363d;
        --accent1: #58a6ff;
        --accent2: #3fb950;
        --text-mut: #6e7681;
      }}
      @media (prefers-color-scheme: light) {{
        :root {{
          --bg: #ffffff;
          --border: #d0d7de;
          --accent1: #0969da;
          --accent2: #1a7f37;
          --text-mut: #8c959f;
        }}
      }}
      .ar {{
        font-family:{FONT}; font-size:{font_size}px;
        fill:var(--accent1); white-space:pre;
        opacity:0;
        animation:rev .12s ease-out forwards;
      }}
      @keyframes rev {{
        to {{ opacity:1 }}
      }}
      .sl {{
        animation:scan {DRAW_TIME}s linear forwards;
      }}
      @keyframes scan {{
        0%   {{ opacity:.8; transform:translateY(0) }}
        95%  {{ opacity:.6; transform:translateY({usable_h}px) }}
        100% {{ opacity:0;  transform:translateY({usable_h}px) }}
      }}
      .sc {{
        font-family:{FONT}; font-size:11px; fill:var(--accent2);
      }}{smoke_keyframes}
      @media(prefers-reduced-motion:reduce){{
        .ar{{ animation:none!important; opacity:1!important }}
        .sl{{ display:none }}
        .sc{{ animation:none!important; opacity:.3!important }}
      }}
    </style>
  </defs>

  <!-- border -->
  <rect x=".5" y=".5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="10"
        fill="var(--bg)" stroke="var(--border)" stroke-width="1"/>

  <!-- header dots -->
  <circle cx="20" cy="14" r="3.5" fill="#ff5f56" stroke="#e0443e" stroke-width=".5"/>
  <circle cx="30" cy="14" r="3.5" fill="#ffbd2e" stroke="#dea123" stroke-width=".5"/>
  <circle cx="40" cy="14" r="3.5" fill="#27c93f" stroke="#1aab29" stroke-width=".5"/>
  <text x="{WIDTH-18}" y="17" text-anchor="end"
        font-family="{FONT}" font-size="9" fill="var(--text-mut)">leo-portrait.sh</text>

  <!-- ascii art -->
  <g id="art">
{chr(10).join(text_rows)}
  </g>

  <!-- scanline drawing head -->
  <line class="sl" x1="{pad_x}" y1="{pad_y}"
        x2="{WIDTH-pad_x}" y2="{pad_y}"
        stroke="var(--accent1)" stroke-width="1.5"/>

  <!-- smoke layer -->
  <g id="smoke" filter="url(#sf)">
{chr(10).join(smoke_els)}
  </g>
</svg>
"""
    output.write_text(svg, encoding="utf-8")
    print(f"Generated: {output}")


if __name__ == "__main__":
    generate_ascii_svg(
        REPO_ROOT / "source-photo.jpg",
        REPO_ROOT / "leo-ascii.svg"
    )

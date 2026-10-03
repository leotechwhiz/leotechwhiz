"""Generate animated ASCII art portrait SVG for GitHub profile README.

Pillow-only processing from source-photo.jpg:
- Pure SVG + CSS animations (works inside <img> tags, no JS)
- Line-by-line drawing animation top to bottom (typewriter wipe / fade) over ~4.3s
- Faint glowing scanline / drawing head tracking the current row
- Multi-layer continuous looping smoke rising above cigarette tip
  (sparse characters . : ~ ' ` o, translateY 60-120px, sideways drift, light blur)
- Smoke starts only after the portrait finishes drawing
- Full prefers-reduced-motion support (shows static final frame)
- Single accent color with brightness mapped to opacity
"""

import html
import sys
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.theme import THEME, PROFILE

BG_COLOR = THEME.get("background", "#0d1117")
BORDER_COLOR = THEME.get("border", "#30363d")
ACCENT_COLOR = THEME.get("accent", "#7ee787")
FONT_FAMILY = THEME.get("font_family", "SFMono-Regular, Consolas, monospace")

WIDTH = 460
HEIGHT = 480
TARGET_COLS = 110

RAMP = " .:-=+*#%@"
SMOKE_RAMP = " .:~'`"


def generate_ascii_svg(
    photo_path: Path,
    output_path: Path,
    cols: int = TARGET_COLS,
    width: int = WIDTH,
    height: int = HEIGHT,
) -> None:
    if not photo_path.exists():
        raise FileNotFoundError(f"Source photo not found: {photo_path}")

    # 1. Load & Crop to head and shoulders
    img = Image.open(photo_path)
    img_w, img_h = img.size

    crop_x1 = int(img_w * 0.08)
    crop_y1 = int(img_h * 0.02)
    crop_x2 = int(img_w * 0.92)
    crop_y2 = int(img_h * 0.94)
    cropped = img.crop((crop_x1, crop_y1, crop_x2, crop_y2))

    # 2. Grayscale & Contrast Boost
    gray = ImageOps.grayscale(cropped)
    contrasted = ImageEnhance.Contrast(gray).enhance(1.85)
    sharpened = ImageEnhance.Sharpness(contrasted).enhance(1.6)

    # 3. Resize with monospace character aspect correction (~0.51)
    aspect_correction = 0.51
    rows = int(cols * (sharpened.height / sharpened.width) * aspect_correction)
    resized = sharpened.resize((cols, rows), Image.Resampling.LANCZOS)

    pad_x = 18
    pad_y = 22
    usable_w = width - (pad_x * 2)
    usable_h = height - (pad_y * 2)
    line_height = usable_h / rows
    font_size = round(line_height * 0.98, 2)

    # Cigarette coordinate zone (around hand/mouth)
    cig_min_row = int(rows * 0.50)
    cig_max_row = int(rows * 0.68)
    cig_min_col = int(cols * 0.44)
    cig_max_col = int(cols * 0.68)

    # Animation timing: total ~4.3s
    row_delay_step = 0.070  # ~4.27s total for ~61 rows
    total_draw_time = round(rows * row_delay_step, 2)

    svg_text_rows = []

    for y in range(rows):
        current_bucket = None
        current_text = []
        row_spans = []

        for x in range(cols):
            b = resized.getpixel((x, y))
            is_cig_area = (cig_min_row <= y <= cig_max_row) and (cig_min_col <= x <= cig_max_col)

            if is_cig_area and b >= 200:
                ch = "=" if (b < 235) else "#"
                opacity = 1.0
            else:
                if b < 16:
                    ch = " "
                    opacity = 0.0
                else:
                    ramp_idx = int((b / 255.0) * (len(RAMP) - 1))
                    ramp_idx = max(0, min(len(RAMP) - 1, ramp_idx))
                    ch = RAMP[ramp_idx]
                    opacity = 0.25 + 0.75 * (b / 255.0)

            if ch == " ":
                bucket = 0.0
            else:
                bucket = round(opacity * 10) / 10.0
                bucket = max(0.2, min(1.0, bucket))

            if bucket != current_bucket:
                if current_text:
                    escaped_txt = html.escape("".join(current_text))
                    if current_bucket == 0.0 or not escaped_txt.strip():
                        row_spans.append(escaped_txt)
                    else:
                        row_spans.append(f'<tspan fill-opacity="{current_bucket:.1f}">{escaped_txt}</tspan>')
                current_bucket = bucket
                current_text = [ch]
            else:
                current_text.append(ch)

        if current_text:
            escaped_txt = html.escape("".join(current_text))
            if current_bucket == 0.0 or not escaped_txt.strip():
                row_spans.append(escaped_txt)
            else:
                row_spans.append(f'<tspan fill-opacity="{current_bucket:.1f}">{escaped_txt}</tspan>')

        baseline_y = round(pad_y + (y * line_height) + (line_height * 0.82), 2)
        row_content = "".join(row_spans)
        row_delay = round(y * row_delay_step, 3)

        svg_text_rows.append(
            f'  <text x="{pad_x}" y="{baseline_y}" class="ascii-row r-{y}" style="animation-delay: {row_delay}s;">{row_content}</text>'
        )

    all_rows = "\n".join(svg_text_rows)

    # Smoke layer starts after portrait finishes drawing
    smoke_delay_1 = round(total_draw_time + 0.1, 2)
    smoke_delay_2 = round(total_draw_time + 1.4, 2)
    smoke_delay_3 = round(total_draw_time + 2.7, 2)
    smoke_delay_4 = round(total_draw_time + 4.0, 2)

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}" style="background-color: {BG_COLOR}; border-radius: 10px;" role="img" aria-label="Roshan Gautam Animated ASCII Portrait">
  <defs>
    <!-- Light blur filter for smoke plume -->
    <filter id="smoke-blur" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="0.45"/>
    </filter>

    <style>
      .ascii-row {{
        font-family: {FONT_FAMILY};
        font-size: {font_size}px;
        fill: {ACCENT_COLOR};
        white-space: pre;
        opacity: 0;
        animation: rowReveal 0.12s ease-out forwards;
      }}

      @keyframes rowReveal {{
        0% {{
          opacity: 0;
        }}
        100% {{
          opacity: 1;
        }}
      }}

      /* Faint drawing head / scanline tracking the current row */
      .scanline {{
        animation: scanlineMove {total_draw_time}s linear forwards;
        filter: drop-shadow(0 0 3px {ACCENT_COLOR});
      }}

      @keyframes scanlineMove {{
        0% {{
          opacity: 0.85;
          transform: translateY(0px);
        }}
        95% {{
          opacity: 0.75;
          transform: translateY({usable_h}px);
        }}
        100% {{
          opacity: 0;
          transform: translateY({usable_h}px);
        }}
      }}

      /* Smoke animation: looped upward translation with sine-like drift and fade */
      .smoke-char {{
        font-family: {FONT_FAMILY};
        font-size: 11px;
        fill: {ACCENT_COLOR};
      }}

      .smoke-puff-1 {{
        opacity: 0;
        animation: smokeFloat1 5.2s ease-in-out {smoke_delay_1}s infinite;
      }}
      .smoke-puff-2 {{
        opacity: 0;
        animation: smokeFloat2 6.0s ease-in-out {smoke_delay_2}s infinite;
      }}
      .smoke-puff-3 {{
        opacity: 0;
        animation: smokeFloat3 7.1s ease-in-out {smoke_delay_3}s infinite;
      }}
      .smoke-puff-4 {{
        opacity: 0;
        animation: smokeFloat4 5.6s ease-in-out {smoke_delay_4}s infinite;
      }}

      @keyframes smokeFloat1 {{
        0% {{
          transform: translate(0, 0) scale(0.9);
          opacity: 0;
        }}
        15% {{
          opacity: 0.7;
        }}
        50% {{
          transform: translate(14px, -55px) scale(1.15);
          opacity: 0.45;
        }}
        80% {{
          transform: translate(-6px, -100px) scale(1.35);
          opacity: 0.2;
        }}
        100% {{
          transform: translate(10px, -135px) scale(1.5);
          opacity: 0;
        }}
      }}

      @keyframes smokeFloat2 {{
        0% {{
          transform: translate(0, 0) scale(0.85);
          opacity: 0;
        }}
        20% {{
          opacity: 0.65;
        }}
        45% {{
          transform: translate(-12px, -48px) scale(1.1);
          opacity: 0.4;
        }}
        75% {{
          transform: translate(10px, -92px) scale(1.3);
          opacity: 0.18;
        }}
        100% {{
          transform: translate(-5px, -130px) scale(1.45);
          opacity: 0;
        }}
      }}

      @keyframes smokeFloat3 {{
        0% {{
          transform: translate(0, 0) scale(0.9);
          opacity: 0;
        }}
        18% {{
          opacity: 0.7;
        }}
        55% {{
          transform: translate(16px, -62px) scale(1.2);
          opacity: 0.35;
        }}
        85% {{
          transform: translate(-5px, -108px) scale(1.4);
          opacity: 0.15;
        }}
        100% {{
          transform: translate(8px, -145px) scale(1.55);
          opacity: 0;
        }}
      }}

      @keyframes smokeFloat4 {{
        0% {{
          transform: translate(0, 0) scale(0.8);
          opacity: 0;
        }}
        15% {{
          opacity: 0.6;
        }}
        40% {{
          transform: translate(-10px, -42px) scale(1.05);
          opacity: 0.38;
        }}
        70% {{
          transform: translate(12px, -88px) scale(1.25);
          opacity: 0.18;
        }}
        100% {{
          transform: translate(-4px, -125px) scale(1.4);
          opacity: 0;
        }}
      }}

      @media (prefers-reduced-motion: reduce) {{
        .ascii-row {{
          animation: none !important;
          opacity: 1 !important;
        }}
        .scanline {{
          display: none !important;
        }}
        .smoke-puff-1, .smoke-puff-2, .smoke-puff-3, .smoke-puff-4 {{
          animation: none !important;
          opacity: 0.35 !important;
          transform: none !important;
        }}
      }}
    </style>
  </defs>

  <!-- Card Background & Border -->
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="1"/>
  
  <!-- Subtle Header Accents -->
  <circle cx="20" cy="14" r="3.5" fill="#30363d" />
  <circle cx="30" cy="14" r="3.5" fill="#30363d" />
  <circle cx="40" cy="14" r="3.5" fill="#30363d" />
  <text x="{width - 18}" y="17" text-anchor="end" font-family="{FONT_FAMILY}" font-size="9" fill="#484f58">leo-portrait.sh</text>

  <!-- ASCII Lines Container -->
  <g id="ascii-art">
{all_rows}
  </g>

  <!-- Moving Scanline / Drawing Head -->
  <line class="scanline" x1="{pad_x}" y1="{pad_y}" x2="{width - pad_x}" y2="{pad_y}" stroke="{ACCENT_COLOR}" stroke-width="1.5" opacity="0"/>

  <!-- Dynamic Smoke Layer (above cigarette tip, starts after draw finishes) -->
  <g id="smoke-layer" filter="url(#smoke-blur)">
    <g class="smoke-puff-1">
      <text x="250" y="272" class="smoke-char">. : ~ `</text>
      <text x="256" y="260" class="smoke-char">: ~ ' o</text>
      <text x="262" y="246" class="smoke-char">~ ' .</text>
    </g>
    <g class="smoke-puff-2">
      <text x="246" y="268" class="smoke-char">~ . ' `</text>
      <text x="252" y="255" class="smoke-char">. : ~ o</text>
      <text x="258" y="242" class="smoke-char">: . ~</text>
    </g>
    <g class="smoke-puff-3">
      <text x="252" y="274" class="smoke-char">: ~ ' `</text>
      <text x="258" y="262" class="smoke-char">~ ' . o</text>
      <text x="264" y="248" class="smoke-char">. : ~</text>
    </g>
    <g class="smoke-puff-4">
      <text x="248" y="270" class="smoke-char">. : ' `</text>
      <text x="254" y="257" class="smoke-char">: ~ . o</text>
      <text x="260" y="244" class="smoke-char">~ ' `</text>
    </g>
  </g>
</svg>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated animated ASCII portrait SVG at: {output_path}")


if __name__ == "__main__":
    photo_file = REPO_ROOT / "source-photo.jpg"
    out_file = REPO_ROOT / "leo-ascii.svg"
    generate_ascii_svg(photo_file, out_file)

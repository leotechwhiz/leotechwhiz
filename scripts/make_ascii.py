"""Generate ASCII art portrait SVG for GitHub profile README.

Pillow-only processing from source-photo.jpg:
- Crop to head & shoulders
- Grayscale & contrast enhancement
- Monospace aspect ratio correction (~110 columns)
- Smoke trail thinning out toward the top with sparse characters (. : ~ ' `)
- Cigarette stick and glowing ember preserved with high contrast
- Single accent color with brightness mapped to opacity
"""

import html
import sys
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance

# Ensure scripts package / theme can be imported
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.theme import THEME, PROFILE

# Theme & dimensions
BG_COLOR = THEME.get("background", "#0d1117")
BORDER_COLOR = THEME.get("border", "#30363d")
ACCENT_COLOR = THEME.get("accent", "#7ee787")
FONT_FAMILY = THEME.get("font_family", "SFMono-Regular, Consolas, monospace")

WIDTH = 460
HEIGHT = 480
TARGET_COLS = 110

# Character ramps
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

    # Crop focusing on head, shoulders, cigarette, and rising smoke plume
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

    # Padding and layout calculations
    pad_x = 18
    pad_y = 22
    usable_w = width - (pad_x * 2)
    usable_h = height - (pad_y * 2)
    line_height = usable_h / rows
    font_size = round(line_height * 0.98, 2)

    # Identify smoke zone (upper right quadrant above cigarette)
    smoke_max_row = int(rows * 0.52)
    smoke_min_col = int(cols * 0.52)

    # Cigarette coordinate zone (around hand/mouth)
    cig_min_row = int(rows * 0.50)
    cig_max_row = int(rows * 0.68)
    cig_min_col = int(cols * 0.44)
    cig_max_col = int(cols * 0.68)

    svg_text_rows = []

    for y in range(rows):
        current_bucket = None
        current_text = []
        row_spans = []

        for x in range(cols):
            b = resized.getpixel((x, y))

            # Detect smoke region
            is_smoke_area = (y < smoke_max_row) and (x > smoke_min_col)
            # Detect cigarette area
            is_cig_area = (cig_min_row <= y <= cig_max_row) and (cig_min_col <= x <= cig_max_col)

            if is_smoke_area and (20 <= b <= 135):
                # Smoke plume: thin out and fade toward top
                # Progress from 0 (top) to 1.0 (near cigarette)
                y_ratio = max(0.05, y / max(1, smoke_max_row))
                fade = y_ratio ** 0.85
                faded_b = b * fade

                if faded_b < 18 or ((x + y * 3) % 4 == 0 and y_ratio < 0.45):
                    # Natural thinning of smoke wisp
                    ch = " "
                    opacity = 0.0
                else:
                    ramp_idx = int((faded_b / 135.0) * (len(SMOKE_RAMP) - 1))
                    ramp_idx = max(0, min(len(SMOKE_RAMP) - 1, ramp_idx))
                    ch = SMOKE_RAMP[ramp_idx]
                    opacity = max(0.18, min(0.65, (faded_b / 135.0) * 0.8))

            elif is_cig_area and b >= 200:
                # Crisp bright cigarette stick & ember
                ch = "=" if (b < 235) else "#"
                opacity = 1.0

            else:
                # Normal face and clothing rendering
                if b < 16:
                    ch = " "
                    opacity = 0.0
                else:
                    ramp_idx = int((b / 255.0) * (len(RAMP) - 1))
                    ramp_idx = max(0, min(len(RAMP) - 1, ramp_idx))
                    ch = RAMP[ramp_idx]
                    # Map brightness to opacity with dynamic range floor
                    opacity = 0.25 + 0.75 * (b / 255.0)

            # Quantize opacity into clean discrete buckets to optimize SVG size
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
        svg_text_rows.append(
            f'  <text x="{pad_x}" y="{baseline_y}" class="ascii-row">{row_content}</text>'
        )

    all_rows = "\n".join(svg_text_rows)

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}" style="background-color: {BG_COLOR}; border-radius: 10px;" role="img" aria-label="Leo ASCII Art Portrait">
  <defs>
    <style>
      .ascii-row {{
        font-family: {FONT_FAMILY};
        font-size: {font_size}px;
        fill: {ACCENT_COLOR};
        white-space: pre;
      }}
    </style>
  </defs>
  <!-- Card Background & Border -->
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="1"/>
  <!-- Subtle Header Accents -->
  <circle cx="20" cy="14" r="3.5" fill="#30363d" />
  <circle cx="30" cy="14" r="3.5" fill="#30363d" />
  <circle cx="40" cy="14" r="3.5" fill="#30363d" />
  <text x="{width - 18}" y="17" text-anchor="end" font-family="{FONT_FAMILY}" font-size="9" fill="#484f58">leo-portrait.raw</text>
  <!-- ASCII Lines -->
  <g id="ascii-art">
{all_rows}
  </g>
</svg>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated ASCII portrait SVG at: {output_path}")


if __name__ == "__main__":
    photo_file = REPO_ROOT / "source-photo.jpg"
    out_file = REPO_ROOT / "leo-ascii.svg"
    generate_ascii_svg(photo_file, out_file)

"""Render profile info card SVG for GitHub profile README.

Pulls all data directly from data/profile.json using shared theme.
Features:
- Exact same dimensions as leo-ascii.svg (460x480) for a seamless banner row
- Rounded-corner card with subtle border and dark background
- Faux terminal title bar with red/yellow/green buttons and whoami command
- EXPERIENCE section (role, company, years)
- STACK section (compact tag pills grouped by category)
- HIGHLIGHTS section (one-line bullets with > accent markers)
- Generous padding, no clutter, clean monospace typography
"""

import html
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.theme import THEME, PROFILE

WIDTH = 460
HEIGHT = 480

BG_COLOR = THEME.get("background", "#0d1117")
CARD_BG = THEME.get("card_bg", "#161b22")
BORDER_COLOR = THEME.get("border", "#30363d")
ACCENT_COLOR = THEME.get("accent", "#7ee787")
ACCENT_DIM = THEME.get("accent_dim", "#238636")
TEXT_PRIMARY = THEME.get("text_primary", "#f0f6fc")
TEXT_SECONDARY = THEME.get("text_secondary", "#8b949e")
TEXT_MUTED = THEME.get("text_muted", "#484f58")
FONT_FAMILY = THEME.get("font_family", "SFMono-Regular, Consolas, monospace")


def estimate_text_width(text: str, font_size: float = 9.5) -> float:
    """Approximate width of monospace text string."""
    return len(text) * (font_size * 0.60)


def generate_card_svg(output_path: Path) -> None:
    terminal_title = PROFILE.get("terminal_title", "leo@github:~$ whoami")
    experience_list = PROFILE.get("experience", [])
    stack_list = PROFILE.get("stack", [])
    highlights_list = PROFILE.get("highlights", [])

    svg_parts = []

    # SVG Header
    svg_parts.append(f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="{HEIGHT}" style="background-color: {BG_COLOR}; border-radius: 10px;" role="img" aria-label="Leo Profile Information Card">
  <defs>
    <style>
      .mono {{ font-family: {FONT_FAMILY}; }}
      .accent-head {{ font-family: {FONT_FAMILY}; font-size: 10px; font-weight: 700; fill: {ACCENT_COLOR}; letter-spacing: 1.2px; }}
      .role-title {{ font-family: {FONT_FAMILY}; font-size: 11px; font-weight: 600; fill: {TEXT_PRIMARY}; }}
      .company-text {{ font-family: {FONT_FAMILY}; font-size: 10.5px; fill: {TEXT_SECONDARY}; }}
      .years-text {{ font-family: {FONT_FAMILY}; font-size: 9.5px; fill: {ACCENT_COLOR}; font-weight: 500; text-anchor: end; }}
      .cat-label {{ font-family: {FONT_FAMILY}; font-size: 9px; font-weight: 700; fill: {TEXT_SECONDARY}; letter-spacing: 0.8px; }}
      .tag-text {{ font-family: {FONT_FAMILY}; font-size: 9.5px; fill: #c9d1d9; }}
      .bullet-marker {{ font-family: {FONT_FAMILY}; font-size: 11px; font-weight: 700; fill: {ACCENT_COLOR}; }}
      .bullet-text {{ font-family: {FONT_FAMILY}; font-size: 10px; fill: #c9d1d9; }}
      .term-cmd {{ font-family: {FONT_FAMILY}; font-size: 11px; fill: {TEXT_SECONDARY}; font-weight: 600; }}
      .term-user {{ fill: {ACCENT_COLOR}; }}
      .status-text {{ font-family: {FONT_FAMILY}; font-size: 9.5px; fill: {TEXT_MUTED}; }}
    </style>
  </defs>

  <!-- Card Background & 1px Border -->
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="10" fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="1"/>

  <!-- Faux Terminal Title Bar -->
  <path d="M 0.5 10.5 A 10 10 0 0 1 10.5 0.5 L {WIDTH - 10.5} 0.5 A 10 10 0 0 1 {WIDTH - 0.5} 10.5 L {WIDTH - 0.5} 32.5 L 0.5 32.5 Z" fill="{CARD_BG}" />
  <line x1="0.5" y1="32.5" x2="{WIDTH - 0.5}" y2="32.5" stroke="{BORDER_COLOR}" stroke-width="1"/>

  <!-- Terminal Window Dots -->
  <circle cx="20" cy="16.5" r="4.5" fill="#ff5f56" stroke="#e0443e" stroke-width="0.5"/>
  <circle cx="34" cy="16.5" r="4.5" fill="#ffbd2e" stroke="#dea123" stroke-width="0.5"/>
  <circle cx="48" cy="16.5" r="4.5" fill="#27c93f" stroke="#1aab29" stroke-width="0.5"/>

  <!-- Terminal Command -->
  <text x="66" y="20.5" class="term-cmd">
    <tspan class="term-user">leo</tspan><tspan fill="{TEXT_MUTED}">@</tspan><tspan fill="{TEXT_PRIMARY}">github</tspan><tspan fill="{TEXT_MUTED}">:~$</tspan> <tspan fill="{TEXT_PRIMARY}">whoami</tspan>
  </text>
""")

    # 1. EXPERIENCE SECTION
    exp_y_start = 55
    svg_parts.append(f"""
  <!-- SECTION: EXPERIENCE -->
  <g id="section-experience">
    <text x="22" y="{exp_y_start}" class="accent-head">// EXPERIENCE</text>
""")

    exp_item_y = exp_y_start + 20
    for exp in experience_list[:3]:
        role = html.escape(exp.get("role", ""))
        company = html.escape(exp.get("company", ""))
        years = html.escape(exp.get("years", ""))

        svg_parts.append(f"""    <g>
      <circle cx="26" cy="{exp_item_y - 3.5}" r="2" fill="{ACCENT_COLOR}"/>
      <text x="35" y="{exp_item_y}" class="role-title">{role} <tspan class="company-text">@ {company}</tspan></text>
      <text x="{WIDTH - 22}" y="{exp_item_y}" class="years-text">{years}</text>
    </g>""")
        exp_item_y += 20

    svg_parts.append("  </g>")

    # 2. STACK SECTION
    stack_y_start = exp_item_y + 12
    svg_parts.append(f"""
  <!-- SECTION: STACK -->
  <g id="section-stack">
    <text x="22" y="{stack_y_start}" class="accent-head">// TECH STACK</text>
""")

    row_y = stack_y_start + 18
    for group in stack_list[:4]:
        cat_name = html.escape(group.get("category", ""))
        tags = group.get("tags", [])

        # Category pill/label
        cat_box_w = 68
        svg_parts.append(f"""    <!-- {cat_name} -->
    <g>
      <rect x="22" y="{row_y - 12}" width="{cat_box_w}" height="17" rx="3.5" fill="{CARD_BG}" stroke="{BORDER_COLOR}" stroke-width="0.8"/>
      <text x="27" y="{row_y}" class="cat-label">{cat_name}</text>
    </g>""")

        tag_x = 22 + cat_box_w + 6
        for tag in tags:
            tag_escaped = html.escape(tag)
            text_w = estimate_text_width(tag, 9.5)
            pill_w = round(text_w + 12, 1)

            # Check if exceeds line width
            if tag_x + pill_w > WIDTH - 18:
                break

            svg_parts.append(f"""    <g>
      <rect x="{tag_x}" y="{row_y - 12}" width="{pill_w}" height="17" rx="3.5" fill="#21262d" stroke="#30363d" stroke-width="0.8"/>
      <text x="{tag_x + 6}" y="{row_y}" class="tag-text">{tag_escaped}</text>
    </g>""")
            tag_x += pill_w + 5

        row_y += 23

    svg_parts.append("  </g>")

    # 3. HIGHLIGHTS SECTION
    hl_y_start = row_y + 12
    svg_parts.append(f"""
  <!-- SECTION: HIGHLIGHTS -->
  <g id="section-highlights">
    <text x="22" y="{hl_y_start}" class="accent-head">// HIGHLIGHTS</text>
""")

    bullet_y = hl_y_start + 19
    for hl in highlights_list[:4]:
        raw_text = hl
        if raw_text.startswith(">"):
            raw_text = raw_text.lstrip(">").strip()
        escaped_hl = html.escape(raw_text)

        # Truncate if unusually long to avoid cutting off
        max_chars = 58
        if len(escaped_hl) > max_chars:
            escaped_hl = escaped_hl[:max_chars - 3] + "..."

        svg_parts.append(f"""    <g>
      <text x="24" y="{bullet_y}" class="bullet-marker">&gt;</text>
      <text x="36" y="{bullet_y}" class="bullet-text">{escaped_hl}</text>
    </g>""")
        bullet_y += 20

    svg_parts.append("  </g>")

    # Subtle Footer / Terminal Status
    svg_parts.append(f"""
  <!-- Footer Status Bar -->
  <line x1="22" y1="{HEIGHT - 28}" x2="{WIDTH - 22}" y2="{HEIGHT - 28}" stroke="#21262d" stroke-width="1"/>
  <circle cx="27" cy="{HEIGHT - 14}" r="3" fill="{ACCENT_COLOR}"/>
  <text x="36" y="{HEIGHT - 11}" class="status-text">status: active &amp; shipping</text>
  <text x="{WIDTH - 22}" y="{HEIGHT - 11}" class="status-text" text-anchor="end">sys: linux · term: zsh<tspan fill="{ACCENT_COLOR}">_</tspan></text>
</svg>
""")

    full_svg = "\n".join(svg_parts)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_svg)

    print(f"Successfully generated info card SVG at: {output_path}")


if __name__ == "__main__":
    out_file = REPO_ROOT / "info-card.svg"
    generate_card_svg(out_file)

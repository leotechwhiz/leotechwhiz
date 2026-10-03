"""Render animated profile info card SVG for GitHub profile README.

Pulls data from data/profile.json using shared theme.
Features:
- Pure CSS animations (works inside <img> tags)
- HIGHLIGHTS moved to top under terminal title bar with 3 exact specified lines
- STACK section in the middle
- PROJECTS section with live links and tech details
- Blinking terminal cursor on prompt line
- Staggered section fade/slide-in animations
- Exact dimensions (460x480) matching leo-ascii.svg
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


def estimate_text_width(text: str, font_size: float = 9.0) -> float:
    return len(text) * (font_size * 0.60)


def wrap_text(text: str, max_chars: int = 58):
    """Simple word-wrap for monospace text."""
    words = text.split(" ")
    lines = []
    curr = []
    curr_len = 0
    for w in words:
        if curr_len + len(w) + (1 if curr else 0) <= max_chars:
            curr.append(w)
            curr_len += len(w) + (1 if len(curr) > 1 else 0)
        else:
            if curr:
                lines.append(" ".join(curr))
            curr = [w]
            curr_len = len(w)
    if curr:
        lines.append(" ".join(curr))
    return lines


def generate_card_svg(output_path: Path) -> None:
    terminal_title = PROFILE.get("terminal_title", "roshan@github:~$ whoami")
    highlights_list = PROFILE.get("highlights", [])[:3]
    stack_list = PROFILE.get("stack", [])
    projects_list = PROFILE.get("projects", [])

    svg_parts = []

    # SVG Header with CSS Keyframe animations
    svg_parts.append(f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="{HEIGHT}" style="background-color: {BG_COLOR}; border-radius: 10px;" role="img" aria-label="Roshan Gautam Profile Card">
  <defs>
    <style>
      .mono {{ font-family: {FONT_FAMILY}; }}
      .accent-head {{ font-family: {FONT_FAMILY}; font-size: 10px; font-weight: 700; fill: {ACCENT_COLOR}; letter-spacing: 1.2px; }}
      .term-cmd {{ font-family: {FONT_FAMILY}; font-size: 11px; fill: {TEXT_SECONDARY}; font-weight: 600; }}
      .term-user {{ fill: {ACCENT_COLOR}; }}
      .cursor {{
        animation: cursorBlink 1s infinite steps(1);
        fill: {ACCENT_COLOR};
      }}
      @keyframes cursorBlink {{
        0%, 49% {{ opacity: 1; }}
        50%, 100% {{ opacity: 0; }}
      }}
      @keyframes sectionSlideIn {{
        0% {{
          opacity: 0;
          transform: translateY(8px);
        }}
        100% {{
          opacity: 1;
          transform: translateY(0);
        }}
      }}
      .anim-highlights {{
        animation: sectionSlideIn 0.5s ease-out 0.20s forwards;
        opacity: 0;
      }}
      .anim-stack {{
        animation: sectionSlideIn 0.5s ease-out 0.60s forwards;
        opacity: 0;
      }}
      .anim-projects {{
        animation: sectionSlideIn 0.5s ease-out 1.00s forwards;
        opacity: 0;
      }}
      .anim-footer {{
        animation: sectionSlideIn 0.5s ease-out 1.40s forwards;
        opacity: 0;
      }}
      @media (prefers-reduced-motion: reduce) {{
        .anim-highlights, .anim-stack, .anim-projects, .anim-footer {{
          animation: none !important;
          opacity: 1 !important;
          transform: none !important;
        }}
        .cursor {{
          animation: none !important;
          opacity: 1 !important;
        }}
      }}
      .bullet-marker {{ font-family: {FONT_FAMILY}; font-size: 10.5px; font-weight: 700; fill: {ACCENT_COLOR}; }}
      .bullet-strong {{ font-family: {FONT_FAMILY}; font-size: 9.5px; font-weight: 700; fill: {TEXT_PRIMARY}; }}
      .bullet-text {{ font-family: {FONT_FAMILY}; font-size: 9px; fill: #c9d1d9; }}
      .cat-label {{ font-family: {FONT_FAMILY}; font-size: 8.5px; font-weight: 700; fill: {TEXT_SECONDARY}; letter-spacing: 0.8px; }}
      .tag-text {{ font-family: {FONT_FAMILY}; font-size: 8.5px; fill: #c9d1d9; }}
      .proj-title {{ font-family: {FONT_FAMILY}; font-size: 11px; font-weight: 700; fill: {TEXT_PRIMARY}; }}
      .proj-link {{ font-family: {FONT_FAMILY}; font-size: 9px; fill: {ACCENT_COLOR}; font-weight: 500; }}
      .proj-desc {{ font-family: {FONT_FAMILY}; font-size: 9px; fill: #c9d1d9; }}
      .proj-tech {{ font-family: {FONT_FAMILY}; font-size: 8.5px; fill: {TEXT_SECONDARY}; }}
      .status-text {{ font-family: {FONT_FAMILY}; font-size: 9px; fill: {TEXT_MUTED}; }}
    </style>
  </defs>

  <!-- Card Background & 1px Border -->
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="10" fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="1"/>

  <!-- Faux Terminal Title Bar -->
  <path d="M 0.5 10.5 A 10 10 0 0 1 10.5 0.5 L {WIDTH - 10.5} 0.5 A 10 10 0 0 1 {WIDTH - 0.5} 10.5 L {WIDTH - 0.5} 32.5 L 0.5 32.5 Z" fill="{CARD_BG}" />
  <line x1="0.5" y1="32.5" x2="{WIDTH - 0.5}" y2="32.5" stroke="{BORDER_COLOR}" stroke-width="1"/>

  <!-- Window Dots -->
  <circle cx="20" cy="16.5" r="4.5" fill="#ff5f56" stroke="#e0443e" stroke-width="0.5"/>
  <circle cx="34" cy="16.5" r="4.5" fill="#ffbd2e" stroke="#dea123" stroke-width="0.5"/>
  <circle cx="48" cy="16.5" r="4.5" fill="#27c93f" stroke="#1aab29" stroke-width="0.5"/>

  <!-- Terminal Command with Blinking Cursor -->
  <text x="66" y="20.5" class="term-cmd">
    <tspan class="term-user">roshan</tspan><tspan fill="{TEXT_MUTED}">@</tspan><tspan fill="{TEXT_PRIMARY}">github</tspan><tspan fill="{TEXT_MUTED}">:~$</tspan> <tspan fill="{TEXT_PRIMARY}">whoami</tspan><tspan class="cursor">_</tspan>
  </text>
""")

    # 1. HIGHLIGHTS SECTION (TOP: Right under terminal title bar)
    hl_y_start = 50
    svg_parts.append(f"""
  <!-- SECTION: HIGHLIGHTS (Top) -->
  <g id="section-highlights" class="anim-highlights">
    <text x="22" y="{hl_y_start}" class="accent-head">// HIGHLIGHTS</text>
""")

    bullet_y = hl_y_start + 16
    for hl in highlights_list[:3]:
        raw_text = hl
        if raw_text.startswith(">"):
            raw_text = raw_text.lstrip(">").strip()

        # Split at colon if present for strong label styling
        if ":" in raw_text:
            title_part, rest_part = raw_text.split(":", 1)
            first_line_prefix = f"{title_part}: "
            full_line_text = f"{title_part}:{rest_part}"
        else:
            first_line_prefix = ""
            full_line_text = raw_text

        wrapped = wrap_text(full_line_text, max_chars=54)

        # Draw bullet marker and wrapped lines
        svg_parts.append(f"""    <g>
      <text x="24" y="{bullet_y}" class="bullet-marker">&gt;</text>""")

        for line_idx, line_str in enumerate(wrapped):
            line_y = bullet_y + (line_idx * 12)
            escaped_line = html.escape(line_str)
            svg_parts.append(f'      <text x="36" y="{line_y}" class="bullet-text">{escaped_line}</text>')

        svg_parts.append("    </g>")
        bullet_y += (len(wrapped) * 12) + 6

    svg_parts.append("  </g>")

    # 2. STACK SECTION (Middle)
    stack_y_start = bullet_y + 4
    svg_parts.append(f"""
  <!-- SECTION: STACK (Middle) -->
  <g id="section-stack" class="anim-stack">
    <text x="22" y="{stack_y_start}" class="accent-head">// TECH STACK</text>
""")

    row_y = stack_y_start + 16
    for group in stack_list[:4]:
        cat_name = html.escape(group.get("category", ""))
        tags = group.get("tags", [])
        cat_box_w = 62

        svg_parts.append(f"""    <!-- {cat_name} -->
    <g>
      <rect x="22" y="{row_y - 11}" width="{cat_box_w}" height="15" rx="3" fill="{CARD_BG}" stroke="{BORDER_COLOR}" stroke-width="0.8"/>
      <text x="26" y="{row_y}" class="cat-label">{cat_name}</text>
    </g>""")

        tag_x = 22 + cat_box_w + 5
        for tag in tags:
            tag_escaped = html.escape(tag)
            text_w = estimate_text_width(tag, 8.5)
            pill_w = round(text_w + 10, 1)

            if tag_x + pill_w > WIDTH - 18:
                break

            svg_parts.append(f"""    <g>
      <rect x="{tag_x}" y="{row_y - 11}" width="{pill_w}" height="15" rx="3" fill="#21262d" stroke="#30363d" stroke-width="0.8"/>
      <text x="{tag_x + 5}" y="{row_y}" class="tag-text">{tag_escaped}</text>
    </g>""")
            tag_x += pill_w + 4

        row_y += 19

    svg_parts.append("  </g>")

    # 3. PROJECTS SECTION (Bottom of content)
    proj_y_start = row_y + 8
    svg_parts.append(f"""
  <!-- SECTION: PROJECTS (Bottom) -->
  <g id="section-projects" class="anim-projects">
    <text x="22" y="{proj_y_start}" class="accent-head">// FEATURED PROJECTS</text>
""")

    p_item_y = proj_y_start + 16
    for proj in projects_list[:2]:
        p_name = html.escape(proj.get("name", ""))
        p_desc = html.escape(proj.get("description", ""))
        p_tech = html.escape(proj.get("tech", ""))
        p_links = proj.get("links", [])

        # Title line
        svg_parts.append(f"""    <!-- Project: {p_name} -->
    <g>
      <circle cx="26" cy="{p_item_y - 3.5}" r="2" fill="{ACCENT_COLOR}"/>
      <text x="35" y="{p_item_y}" class="proj-title">{p_name}</text>
""")

        # Links on right
        link_str_parts = []
        for lk in p_links:
            lbl = html.escape(lk.get("label", "link"))
            link_str_parts.append(f"[{lbl} ↗]")
        if link_str_parts:
            combined_links = "  ".join(link_str_parts)
            svg_parts.append(f'      <text x="{WIDTH - 22}" y="{p_item_y}" class="proj-link" text-anchor="end">{combined_links}</text>')

        # Description line
        svg_parts.append(f'      <text x="35" y="{p_item_y + 13}" class="proj-desc">{p_desc}</text>')
        # Tech stack line
        svg_parts.append(f'      <text x="35" y="{p_item_y + 25}" class="proj-tech">⚡ {p_tech}</text>')
        svg_parts.append("    </g>")

        p_item_y += 40

    svg_parts.append("  </g>")

    # Footer status
    svg_parts.append(f"""
  <!-- Footer Status Bar -->
  <g id="section-footer" class="anim-footer">
    <line x1="22" y1="{HEIGHT - 24}" x2="{WIDTH - 22}" y2="{HEIGHT - 24}" stroke="#21262d" stroke-width="1"/>
    <circle cx="27" cy="{HEIGHT - 12}" r="3" fill="{ACCENT_COLOR}"/>
    <text x="36" y="{HEIGHT - 9}" class="status-text">status: active &amp; shipping</text>
    <text x="{WIDTH - 22}" y="{HEIGHT - 9}" class="status-text" text-anchor="end">sys: linux · term: zsh</text>
  </g>
</svg>
""")

    full_svg = "\n".join(svg_parts)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_svg)

    print(f"Successfully generated animated info card SVG at: {output_path}")


if __name__ == "__main__":
    out_file = REPO_ROOT / "info-card.svg"
    generate_card_svg(out_file)

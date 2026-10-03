"""Render animated profile info card SVG for GitHub profile README.

Pulls data from data/profile.json using shared theme.
Features:
- Pure CSS animations (works inside <img> tags)
- Staggered section fade/slide-in animations
- Blinking terminal cursor on prompt line
- STACK section (compact category pills)
- PROJECTS section (Markly AI & Gunaso with descriptions, tech, and live links)
- HIGHLIGHTS section (concise 3-line max with > markers)
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


def estimate_text_width(text: str, font_size: float = 9.5) -> float:
    return len(text) * (font_size * 0.60)


def generate_card_svg(output_path: Path) -> None:
    terminal_title = PROFILE.get("terminal_title", "roshan@github:~$ whoami")
    stack_list = PROFILE.get("stack", [])
    projects_list = PROFILE.get("projects", [])
    highlights_list = PROFILE.get("highlights", [])[:3]

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
          transform: translateY(10px);
        }}
        100% {{
          opacity: 1;
          transform: translateY(0);
        }}
      }}
      .anim-stack {{
        animation: sectionSlideIn 0.6s ease-out 0.25s forwards;
        opacity: 0;
      }}
      .anim-projects {{
        animation: sectionSlideIn 0.6s ease-out 0.65s forwards;
        opacity: 0;
      }}
      .anim-highlights {{
        animation: sectionSlideIn 0.6s ease-out 1.05s forwards;
        opacity: 0;
      }}
      .anim-footer {{
        animation: sectionSlideIn 0.6s ease-out 1.45s forwards;
        opacity: 0;
      }}
      @media (prefers-reduced-motion: reduce) {{
        .anim-stack, .anim-projects, .anim-highlights, .anim-footer {{
          animation: none !important;
          opacity: 1 !important;
          transform: none !important;
        }}
        .cursor {{
          animation: none !important;
          opacity: 1 !important;
        }}
      }}
      .cat-label {{ font-family: {FONT_FAMILY}; font-size: 9px; font-weight: 700; fill: {TEXT_SECONDARY}; letter-spacing: 0.8px; }}
      .tag-text {{ font-family: {FONT_FAMILY}; font-size: 9px; fill: #c9d1d9; }}
      .proj-title {{ font-family: {FONT_FAMILY}; font-size: 11.5px; font-weight: 700; fill: {TEXT_PRIMARY}; }}
      .proj-link {{ font-family: {FONT_FAMILY}; font-size: 9.5px; fill: {ACCENT_COLOR}; font-weight: 500; }}
      .proj-desc {{ font-family: {FONT_FAMILY}; font-size: 9.5px; fill: #c9d1d9; }}
      .proj-tech {{ font-family: {FONT_FAMILY}; font-size: 8.5px; fill: {TEXT_SECONDARY}; }}
      .bullet-marker {{ font-family: {FONT_FAMILY}; font-size: 11px; font-weight: 700; fill: {ACCENT_COLOR}; }}
      .bullet-text {{ font-family: {FONT_FAMILY}; font-size: 9.5px; fill: #c9d1d9; }}
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

    # 1. STACK SECTION
    stack_y_start = 50
    svg_parts.append(f"""
  <!-- SECTION: STACK (Animated) -->
  <g id="section-stack" class="anim-stack">
    <text x="22" y="{stack_y_start}" class="accent-head">// TECH STACK</text>
""")

    row_y = stack_y_start + 18
    for group in stack_list[:4]:
        cat_name = html.escape(group.get("category", ""))
        tags = group.get("tags", [])
        cat_box_w = 64

        svg_parts.append(f"""    <!-- {cat_name} -->
    <g>
      <rect x="22" y="{row_y - 12}" width="{cat_box_w}" height="16" rx="3" fill="{CARD_BG}" stroke="{BORDER_COLOR}" stroke-width="0.8"/>
      <text x="26" y="{row_y}" class="cat-label">{cat_name}</text>
    </g>""")

        tag_x = 22 + cat_box_w + 5
        for tag in tags:
            tag_escaped = html.escape(tag)
            text_w = estimate_text_width(tag, 9.0)
            pill_w = round(text_w + 10, 1)

            if tag_x + pill_w > WIDTH - 18:
                break

            svg_parts.append(f"""    <g>
      <rect x="{tag_x}" y="{row_y - 12}" width="{pill_w}" height="16" rx="3" fill="#21262d" stroke="#30363d" stroke-width="0.8"/>
      <text x="{tag_x + 5}" y="{row_y}" class="tag-text">{tag_escaped}</text>
    </g>""")
            tag_x += pill_w + 4

        row_y += 21

    svg_parts.append("  </g>")

    # 2. PROJECTS SECTION
    proj_y_start = row_y + 10
    svg_parts.append(f"""
  <!-- SECTION: PROJECTS (Animated) -->
  <g id="section-projects" class="anim-projects">
    <text x="22" y="{proj_y_start}" class="accent-head">// FEATURED PROJECTS</text>
""")

    p_item_y = proj_y_start + 18
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

        # Links on the right
        link_str_parts = []
        for lk in p_links:
            lbl = html.escape(lk.get("label", "link"))
            link_str_parts.append(f"[{lbl} ↗]")
        if link_str_parts:
            combined_links = "  ".join(link_str_parts)
            svg_parts.append(f'      <text x="{WIDTH - 22}" y="{p_item_y}" class="proj-link" text-anchor="end">{combined_links}</text>')

        # Description line
        svg_parts.append(f'      <text x="35" y="{p_item_y + 14}" class="proj-desc">{p_desc}</text>')
        # Tech stack line
        svg_parts.append(f'      <text x="35" y="{p_item_y + 27}" class="proj-tech">⚡ {p_tech}</text>')
        svg_parts.append("    </g>")

        p_item_y += 44

    svg_parts.append("  </g>")

    # 3. HIGHLIGHTS SECTION (3 lines max)
    hl_y_start = p_item_y + 4
    svg_parts.append(f"""
  <!-- SECTION: HIGHLIGHTS (Animated) -->
  <g id="section-highlights" class="anim-highlights">
    <text x="22" y="{hl_y_start}" class="accent-head">// HIGHLIGHTS</text>
""")

    bullet_y = hl_y_start + 18
    for hl in highlights_list[:3]:
        raw_text = hl
        if raw_text.startswith(">"):
            raw_text = raw_text.lstrip(">").strip()
        escaped_hl = html.escape(raw_text)

        max_chars = 62
        if len(escaped_hl) > max_chars:
            escaped_hl = escaped_hl[:max_chars - 3] + "..."

        svg_parts.append(f"""    <g>
      <text x="24" y="{bullet_y}" class="bullet-marker">&gt;</text>
      <text x="36" y="{bullet_y}" class="bullet-text">{escaped_hl}</text>
    </g>""")
        bullet_y += 18

    svg_parts.append("  </g>")

    # Footer status
    svg_parts.append(f"""
  <!-- Footer Status Bar (Animated) -->
  <g id="section-footer" class="anim-footer">
    <line x1="22" y1="{HEIGHT - 26}" x2="{WIDTH - 22}" y2="{HEIGHT - 26}" stroke="#21262d" stroke-width="1"/>
    <circle cx="27" cy="{HEIGHT - 13}" r="3" fill="{ACCENT_COLOR}"/>
    <text x="36" y="{HEIGHT - 10}" class="status-text">status: active &amp; shipping</text>
    <text x="{WIDTH - 22}" y="{HEIGHT - 10}" class="status-text" text-anchor="end">sys: linux · term: zsh</text>
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

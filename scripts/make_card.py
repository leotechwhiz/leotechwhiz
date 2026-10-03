"""Render animated profile info card SVG for GitHub profile README.

Sections (top to bottom):
  - Terminal title bar with blinking cursor
  - HIGHLIGHTS (3 lines, > markers, staggered CSS slide-in)
  - TECH STACK (compact category pills)
  - FEATURED PROJECTS (name, description, tech, links)
  - Footer status bar

All content sourced from data/profile.json via scripts/theme.py.
Pure CSS animations — no JavaScript. Works inside <img> on GitHub.
Respects prefers-reduced-motion.
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

BG_COLOR   = THEME["background"]
CARD_BG    = THEME["card_bg"]
BORDER     = THEME["border"]
ACCENT     = THEME["accent"]
TEXT_PRI   = THEME["text_primary"]
TEXT_SEC   = THEME["text_secondary"]
TEXT_MUT   = THEME["text_muted"]
FONT       = THEME["font_family"]


def _pill_w(text: str, fs: float = 8.5) -> float:
    return round(len(text) * fs * 0.60 + 10, 1)


def _wrap(text: str, max_chars: int = 52) -> list[str]:
    words = text.split()
    lines, cur, cur_len = [], [], 0
    for w in words:
        need = len(w) + (1 if cur else 0)
        if cur_len + need <= max_chars:
            cur.append(w)
            cur_len += need
        else:
            if cur:
                lines.append(" ".join(cur))
            cur, cur_len = [w], len(w)
    if cur:
        lines.append(" ".join(cur))
    return lines


def generate_card_svg(output_path: Path) -> None:
    highlights = PROFILE.get("highlights", [])[:3]
    stack      = PROFILE.get("stack", [])
    projects   = PROFILE.get("projects", [])

    parts = []

    # ── SVG open + defs + styles ──────────────────────────────────────────────
    parts.append(f"""<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="{HEIGHT}"
     style="background:{BG_COLOR};border-radius:10px;"
     role="img" aria-label="Roshan Gautam Profile Card">
  <defs>
    <style>
      @keyframes blink {{
        0%,49% {{ opacity:1 }} 50%,100% {{ opacity:0 }}
      }}
      @keyframes slideIn {{
        from {{ opacity:0; transform:translateY(9px) }}
        to   {{ opacity:1; transform:translateY(0)   }}
      }}
      .cursor  {{ fill:{ACCENT}; animation:blink 1s steps(1) infinite }}
      .s0 {{ opacity:0; animation:slideIn .5s ease-out .15s forwards }}
      .s1 {{ opacity:0; animation:slideIn .5s ease-out .55s forwards }}
      .s2 {{ opacity:0; animation:slideIn .5s ease-out .95s forwards }}
      .s3 {{ opacity:0; animation:slideIn .5s ease-out 1.35s forwards }}
      @media(prefers-reduced-motion:reduce){{
        .s0,.s1,.s2,.s3{{ animation:none!important; opacity:1!important }}
        .cursor{{ animation:none!important; opacity:1!important }}
      }}
      .ah  {{ font:{FONT}; font-size:10px; font-weight:700; fill:{ACCENT}; letter-spacing:1.2px }}
      .bm  {{ font:{FONT}; font-size:10.5px; font-weight:700; fill:{ACCENT} }}
      .bt  {{ font:{FONT}; font-size:9px; fill:#c9d1d9 }}
      .cl  {{ font:{FONT}; font-size:8.5px; font-weight:700; fill:{TEXT_SEC}; letter-spacing:.8px }}
      .tt  {{ font:{FONT}; font-size:8.5px; fill:#c9d1d9 }}
      .pt  {{ font:{FONT}; font-size:11px; font-weight:700; fill:{TEXT_PRI} }}
      .pl  {{ font:{FONT}; font-size:9px; fill:{ACCENT}; font-weight:500 }}
      .pd  {{ font:{FONT}; font-size:9px; fill:#c9d1d9 }}
      .pk  {{ font:{FONT}; font-size:8.5px; fill:{TEXT_SEC} }}
      .st  {{ font:{FONT}; font-size:9px; fill:{TEXT_MUT} }}
      .tc  {{ font:{FONT}; font-size:11px; fill:{TEXT_SEC}; font-weight:600 }}
    </style>
  </defs>

  <!-- card background -->
  <rect x=".5" y=".5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="10"
        fill="{BG_COLOR}" stroke="{BORDER}" stroke-width="1"/>

  <!-- terminal title bar -->
  <path d="M.5 10.5A10 10 0 0 1 10.5.5L{WIDTH-10.5}.5A10 10 0 0 1 {WIDTH-.5} 10.5V32.5H.5Z"
        fill="{CARD_BG}"/>
  <line x1=".5" y1="32.5" x2="{WIDTH-.5}" y2="32.5" stroke="{BORDER}" stroke-width="1"/>

  <!-- window dots -->
  <circle cx="20" cy="16.5" r="4.5" fill="#ff5f56" stroke="#e0443e" stroke-width=".5"/>
  <circle cx="34" cy="16.5" r="4.5" fill="#ffbd2e" stroke="#dea123" stroke-width=".5"/>
  <circle cx="48" cy="16.5" r="4.5" fill="#27c93f" stroke="#1aab29" stroke-width=".5"/>

  <!-- prompt + blinking cursor -->
  <text x="66" y="20.5" class="tc">
    <tspan fill="{ACCENT}">leo</tspan><tspan fill="{TEXT_MUT}">@</tspan><tspan fill="{TEXT_PRI}">github</tspan><tspan fill="{TEXT_MUT}">:~$</tspan>
    <tspan fill="{TEXT_PRI}"> whoami</tspan><tspan class="cursor">_</tspan>
  </text>
""")

    y = 50  # cursor below title bar

    # ── HIGHLIGHTS ────────────────────────────────────────────────────────────
    parts.append(f'  <g class="s0">')
    parts.append(f'    <text x="22" y="{y}" class="ah">// HIGHLIGHTS</text>')
    y += 15

    for hl in highlights:
        raw = hl.lstrip(">").strip()
        wrapped = _wrap(raw, max_chars=52)
        parts.append(f'    <text x="24" y="{y}" class="bm">&gt;</text>')
        for i, line in enumerate(wrapped):
            parts.append(f'    <text x="36" y="{y + i*12}" class="bt">{html.escape(line)}</text>')
        y += len(wrapped) * 12 + 5

    parts.append('  </g>')
    y += 4

    # ── TECH STACK ────────────────────────────────────────────────────────────
    parts.append(f'  <g class="s1">')
    parts.append(f'    <text x="22" y="{y}" class="ah">// TECH STACK</text>')
    y += 15

    for group in stack[:4]:
        cat  = html.escape(group.get("category", ""))
        tags = group.get("tags", [])
        cw   = 62
        parts.append(f'    <rect x="22" y="{y-11}" width="{cw}" height="15" rx="3" fill="{CARD_BG}" stroke="{BORDER}" stroke-width=".8"/>')
        parts.append(f'    <text x="26" y="{y}" class="cl">{cat}</text>')
        tx = 22 + cw + 5
        for tag in tags:
            pw = _pill_w(tag)
            if tx + pw > WIDTH - 16:
                break
            parts.append(f'    <rect x="{tx}" y="{y-11}" width="{pw}" height="15" rx="3" fill="#21262d" stroke="{BORDER}" stroke-width=".8"/>')
            parts.append(f'    <text x="{tx+5}" y="{y}" class="tt">{html.escape(tag)}</text>')
            tx += pw + 4
        y += 19

    parts.append('  </g>')
    y += 6

    # ── PROJECTS ──────────────────────────────────────────────────────────────
    parts.append(f'  <g class="s2">')
    parts.append(f'    <text x="22" y="{y}" class="ah">// FEATURED PROJECTS</text>')
    y += 15

    for proj in projects[:2]:
        name  = html.escape(proj.get("name", ""))
        desc  = html.escape(proj.get("description", ""))
        tech  = html.escape(proj.get("tech", ""))
        links = proj.get("links", [])

        link_str = "  ".join(f"[{html.escape(lk.get('label','link'))} ↗]" for lk in links)

        parts.append(f'    <circle cx="26" cy="{y-3.5}" r="2" fill="{ACCENT}"/>')
        parts.append(f'    <text x="35" y="{y}" class="pt">{name}</text>')
        if link_str:
            parts.append(f'    <text x="{WIDTH-22}" y="{y}" class="pl" text-anchor="end">{link_str}</text>')
        parts.append(f'    <text x="35" y="{y+13}" class="pd">{desc}</text>')
        parts.append(f'    <text x="35" y="{y+25}" class="pk">⚡ {tech}</text>')
        y += 40

    parts.append('  </g>')

    # ── FOOTER ────────────────────────────────────────────────────────────────
    parts.append(f'  <g class="s3">')
    parts.append(f'    <line x1="22" y1="{HEIGHT-24}" x2="{WIDTH-22}" y2="{HEIGHT-24}" stroke="#21262d" stroke-width="1"/>')
    parts.append(f'    <circle cx="27" cy="{HEIGHT-12}" r="3" fill="{ACCENT}"/>')
    parts.append(f'    <text x="36" y="{HEIGHT-9}" class="st">status: active &amp; shipping</text>')
    parts.append(f'    <text x="{WIDTH-22}" y="{HEIGHT-9}" class="st" text-anchor="end">sys: linux · term: zsh</text>')
    parts.append('  </g>')

    parts.append('</svg>')

    output_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    generate_card_svg(REPO_ROOT / "info-card.svg")

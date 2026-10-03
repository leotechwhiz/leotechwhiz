"""Render static profile info card SVG for GitHub profile README.

Light & dark mode adaptive via CSS variables and prefers-color-scheme.
Two accents only: Accent 1 (Blue) and Accent 2 (Green).
Zero animation — completely static per spec.
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
FONT = THEME.get("font_family", "monospace")


def _pill_w(text: str, fs: float = 8.5) -> float:
    return round(len(text) * fs * 0.60 + 10, 1)


def _wrap(text: str, max_chars: int = 54) -> list[str]:
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
    projects   = PROFILE.get("projects", [])[:3]

    parts = []

    parts.append(f"""<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="{HEIGHT}"
     role="img" aria-label="Roshan Gautam Profile Card">
  <defs>
    <style>
      :root {{
        --bg: #0d1117;
        --card-bg: #161b22;
        --border: #30363d;
        --pill-bg: #21262d;
        --text-pri: #f0f6fc;
        --text-sec: #8b949e;
        --text-mut: #6e7681;
        --accent1: #58a6ff;
        --accent2: #3fb950;
      }}
      @media (prefers-color-scheme: light) {{
        :root {{
          --bg: #ffffff;
          --card-bg: #f6f8fa;
          --border: #d0d7de;
          --pill-bg: #eaeef2;
          --text-pri: #1f2328;
          --text-sec: #57606a;
          --text-mut: #8c959f;
          --accent1: #0969da;
          --accent2: #1a7f37;
        }}
      }}
      .ah {{ font-family:{FONT}; font-size:10px; font-weight:700; fill:var(--accent1); letter-spacing:1.2px }}
      .bm {{ font-family:{FONT}; font-size:10.5px; font-weight:700; fill:var(--accent2) }}
      .bt {{ font-family:{FONT}; font-size:9px; fill:var(--text-pri) }}
      .cl {{ font-family:{FONT}; font-size:8.5px; font-weight:700; fill:var(--text-sec); letter-spacing:.8px }}
      .tt {{ font-family:{FONT}; font-size:8.5px; fill:var(--text-pri) }}
      .pt {{ font-family:{FONT}; font-size:10.5px; font-weight:700; fill:var(--text-pri) }}
      .pl {{ font-family:{FONT}; font-size:8.5px; fill:var(--accent1); font-weight:500 }}
      .pd {{ font-family:{FONT}; font-size:8.5px; fill:var(--text-sec) }}
      .pk {{ font-family:{FONT}; font-size:8px; fill:var(--accent2) }}
      .st {{ font-family:{FONT}; font-size:8.5px; fill:var(--text-mut) }}
      .tc {{ font-family:{FONT}; font-size:11px; fill:var(--text-sec); font-weight:600 }}
    </style>
  </defs>

  <!-- card background -->
  <rect x=".5" y=".5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="10"
        fill="var(--bg)" stroke="var(--border)" stroke-width="1"/>

  <!-- terminal title bar -->
  <path d="M.5 10.5A10 10 0 0 1 10.5.5L{WIDTH-10.5}.5A10 10 0 0 1 {WIDTH-.5} 10.5V32.5H.5Z"
        fill="var(--card-bg)"/>
  <line x1=".5" y1="32.5" x2="{WIDTH-.5}" y2="32.5" stroke="var(--border)" stroke-width="1"/>

  <!-- window dots -->
  <circle cx="20" cy="16.5" r="4.5" fill="#ff5f56" stroke="#e0443e" stroke-width=".5"/>
  <circle cx="34" cy="16.5" r="4.5" fill="#ffbd2e" stroke="#dea123" stroke-width=".5"/>
  <circle cx="48" cy="16.5" r="4.5" fill="#27c93f" stroke="#1aab29" stroke-width=".5"/>

  <!-- prompt static (no animation) -->
  <text x="66" y="20.5" class="tc">
    <tspan fill="var(--accent1)">roshan</tspan><tspan fill="var(--text-mut)">@</tspan><tspan fill="var(--text-pri)">github</tspan><tspan fill="var(--text-mut)">:~$</tspan>
    <tspan fill="var(--text-pri)"> whoami</tspan><tspan fill="var(--accent1)">_</tspan>
  </text>
""")

    y = 50

    # ── HIGHLIGHTS ────────────────────────────────────────────────────────────
    parts.append('  <g id="highlights">')
    parts.append(f'    <text x="22" y="{y}" class="ah">// FOCUS AREAS</text>')
    y += 14

    for hl in highlights:
        raw = hl.lstrip(">").strip()
        wrapped = _wrap(raw, max_chars=54)
        parts.append(f'    <text x="24" y="{y}" class="bm">&gt;</text>')
        for i, line in enumerate(wrapped):
            parts.append(f'    <text x="36" y="{y + i*11.5}" class="bt">{html.escape(line)}</text>')
        y += len(wrapped) * 11.5 + 4

    parts.append('  </g>')
    y += 4

    # ── TECH STACK ────────────────────────────────────────────────────────────
    parts.append('  <g id="stack">')
    parts.append(f'    <text x="22" y="{y}" class="ah">// TECH &amp; TOOLS</text>')
    y += 14

    for group in stack[:2]:
        cat  = html.escape(group.get("category", ""))
        tags = group.get("tags", [])
        cw   = 72
        parts.append(f'    <rect x="22" y="{y-10}" width="{cw}" height="14" rx="3" fill="var(--card-bg)" stroke="var(--border)" stroke-width=".8"/>')
        parts.append(f'    <text x="26" y="{y}" class="cl">{cat}</text>')
        tx = 22 + cw + 5
        for tag in tags:
            pw = _pill_w(tag, fs=8)
            if tx + pw > WIDTH - 16:
                break
            parts.append(f'    <rect x="{tx}" y="{y-10}" width="{pw}" height="14" rx="3" fill="var(--pill-bg)" stroke="var(--border)" stroke-width=".8"/>')
            parts.append(f'    <text x="{tx+5}" y="{y}" class="tt">{html.escape(tag)}</text>')
            tx += pw + 4
        y += 18

    parts.append('  </g>')
    y += 6

    # ── PROJECTS ──────────────────────────────────────────────────────────────
    parts.append('  <g id="projects">')
    parts.append(f'    <text x="22" y="{y}" class="ah">// FEATURED WORK</text>')
    y += 14

    for proj in projects:
        name  = html.escape(proj.get("name", ""))
        desc  = html.escape(proj.get("description", ""))
        tech  = html.escape(proj.get("tech", ""))
        links = proj.get("links", [])

        link_str = "  ".join(f"[{html.escape(lk.get('label','link'))} ↗]" for lk in links)

        parts.append(f'    <circle cx="26" cy="{y-3.5}" r="2" fill="var(--accent1)"/>')
        parts.append(f'    <text x="35" y="{y}" class="pt">{name}</text>')
        if link_str:
            parts.append(f'    <text x="{WIDTH-22}" y="{y}" class="pl" text-anchor="end">{link_str}</text>')
        parts.append(f'    <text x="35" y="{y+11}" class="pd">{desc}</text>')
        parts.append(f'    <text x="35" y="{y+21}" class="pk">⚡ {tech}</text>')
        y += 33

    parts.append('  </g>')

    # ── FOOTER ────────────────────────────────────────────────────────────────
    parts.append(f'  <g id="footer">')
    parts.append(f'    <line x1="22" y1="{HEIGHT-22}" x2="{WIDTH-22}" y2="{HEIGHT-22}" stroke="var(--border)" stroke-width="1"/>')
    parts.append(f'    <circle cx="27" cy="{HEIGHT-11}" r="3" fill="var(--accent2)"/>')
    parts.append(f'    <text x="36" y="{HEIGHT-8}" class="st">status: open for full stack &amp; SEO roles</text>')
    parts.append(f'    <text x="{WIDTH-22}" y="{HEIGHT-8}" class="st" text-anchor="end">Kathmandu, Nepal</text>')
    parts.append('  </g>')

    parts.append('</svg>')

    output_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    generate_card_svg(REPO_ROOT / "info-card.svg")

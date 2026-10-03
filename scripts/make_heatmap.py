"""Fetch real 12-month GitHub contributions for @leotechwhiz and render contrib-heatmap.svg.

Strict requirements:
- Queries GitHub GraphQL API for user 'leotechwhiz'
- Last 12 months with from/to parameters
- Maps real contributionCount to 5-level scale:
    Level 0 = empty (0 contributions)
    Level 1 = 1 to Q1
    Level 2 = Q1+1 to Q2
    Level 3 = Q2+1 to Q3
    Level 4 = Q3+1 to max (quartiles of user's own max)
- No mock data or random fallback: exits with a clear error if GH_TOKEN is missing or API fails
- Reads token strictly from GH_TOKEN env var
- Displays real total contribution count in SVG header
"""

import datetime
import html
import os
import sys
from pathlib import Path
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.theme import THEME, PROFILE

# Theme & Dimensions
WIDTH = 880
HEIGHT = 180

BG_COLOR = THEME.get("background", "#0d1117")
BORDER_COLOR = THEME.get("border", "#30363d")
ACCENT_COLOR = THEME.get("accent", "#7ee787")
TEXT_PRIMARY = THEME.get("text_primary", "#f0f6fc")
TEXT_SECONDARY = THEME.get("text_secondary", "#8b949e")
TEXT_MUTED = THEME.get("text_muted", "#484f58")
FONT_FAMILY = THEME.get("font_family", "SFMono-Regular, Consolas, monospace")

COLOR_LEVELS = [
    "#161b22",  # Level 0 (0 contributions)
    "#0e4429",  # Level 1 (1st quartile)
    "#006d32",  # Level 2 (2nd quartile)
    "#26a641",  # Level 3 (3rd quartile)
    ACCENT_COLOR,  # Level 4 (4th quartile / max)
]

GRAPHQL_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            weekday
          }
        }
      }
    }
  }
}
"""

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fetch_real_contributions(username: str, token: str):
    """Query GitHub GraphQL API for the exact last 12 months of contributions."""
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    to_date = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    from_date = (now_utc - datetime.timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")

    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "leotechwhiz-profile-heatmap-fetcher",
    }
    payload = {
        "query": GRAPHQL_QUERY,
        "variables": {
            "login": username,
            "from": from_date,
            "to": to_date,
        },
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as exc:
        sys.stderr.write(f"GitHub API HTTP error: {exc}\n")
        sys.exit(1)

    data = response.json()
    if "errors" in data:
        sys.stderr.write(f"GitHub GraphQL query error: {data['errors']}\n")
        sys.exit(1)

    user_data = data.get("data", {}).get("user")
    if not user_data:
        sys.stderr.write(f"User '{username}' not found on GitHub or inaccessible with token.\n")
        sys.exit(1)

    collection = user_data.get("contributionsCollection")
    if not collection:
        sys.stderr.write(f"No contributionsCollection found for '{username}'.\n")
        sys.exit(1)

    calendar = collection.get("contributionCalendar")
    if not calendar:
        sys.stderr.write(f"No contributionCalendar returned for '{username}'.\n")
        sys.exit(1)

    return calendar


def map_count_to_level(count: int, q1: int, q2: int, q3: int) -> int:
    """Map count to 0-4 based on quartiles of user's own maximum."""
    if count <= 0:
        return 0
    if count <= q1:
        return 1
    if count <= q2:
        return 2
    if count <= q3:
        return 3
    return 4


def generate_heatmap_svg(output_path: Path):
    username = PROFILE.get("username", "leotechwhiz")

    # Read token strictly from GH_TOKEN
    token = os.environ.get("GH_TOKEN")
    if not token:
        sys.stderr.write(
            "ERROR: 'GH_TOKEN' environment variable is not set.\n"
            "This script requires a valid GitHub token (GH_TOKEN) to fetch real contribution data.\n"
            "Never generating mock or placeholder data.\n"
        )
        sys.exit(1)

    print(f"Fetching real GitHub contribution data for @{username}...")
    calendar = fetch_real_contributions(username, token)

    total_count = calendar.get("totalContributions", 0)
    weeks = calendar.get("weeks", [])

    if len(weeks) > 53:
        weeks = weeks[-53:]

    # Calculate max count and quartiles of user's own max
    max_count = 0
    for week in weeks:
        for day in week.get("contributionDays", []):
            cnt = day.get("contributionCount", 0)
            if cnt > max_count:
                max_count = cnt

    if max_count <= 0:
        q1, q2, q3 = 1, 2, 3
    else:
        q1 = max(1, int(round(max_count * 0.25)))
        q2 = max(q1 + 1, int(round(max_count * 0.50)))
        q3 = max(q2 + 1, int(round(max_count * 0.75)))

    print(f"Total contributions: {total_count}, Max in a day: {max_count} (Quartiles: Q1={q1}, Q2={q2}, Q3={q3})")

    # Layout parameters
    square_size = 10.5
    cell_gap = 3.5
    stride = square_size + cell_gap
    grid_start_x = 44
    grid_start_y = 52

    svg_parts = []
    svg_parts.append(f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="{HEIGHT}" style="background-color: {BG_COLOR}; border-radius: 10px;" role="img" aria-label="GitHub Contribution Heatmap">
  <defs>
    <style>
      .heat-title {{ font-family: {FONT_FAMILY}; font-size: 11.5px; font-weight: 700; fill: {TEXT_PRIMARY}; }}
      .heat-count {{ font-family: {FONT_FAMILY}; font-size: 11px; fill: {ACCENT_COLOR}; font-weight: 600; }}
      .heat-user {{ font-family: {FONT_FAMILY}; font-size: 10.5px; fill: {TEXT_MUTED}; text-anchor: end; }}
      .label-text {{ font-family: {FONT_FAMILY}; font-size: 9px; fill: {TEXT_SECONDARY}; }}
      .day-text {{ font-family: {FONT_FAMILY}; font-size: 8.5px; fill: {TEXT_MUTED}; }}
      .legend-text {{ font-family: {FONT_FAMILY}; font-size: 9px; fill: {TEXT_MUTED}; }}
      .cell {{ shape-rendering: geometricPrecision; }}
    </style>
  </defs>

  <!-- Background and Border -->
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="10" fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="1"/>

  <!-- Header with Real Total Contributions -->
  <g id="heatmap-header">
    <circle cx="24" cy="24" r="4" fill="{ACCENT_COLOR}"/>
    <text x="36" y="27.5" class="heat-title">CONTRIBUTIONS <tspan class="heat-count">({total_count:,} in the last year)</tspan></text>
    <text x="{WIDTH - 24}" y="27.5" class="heat-user">@{html.escape(username)}</text>
  </g>
""")

    # Day labels (Mon, Wed, Fri)
    day_labels = [("Mon", 1), ("Wed", 3), ("Fri", 5)]
    for label, day_idx in day_labels:
        label_y = grid_start_y + (day_idx * stride) + 8.5
        svg_parts.append(f'  <text x="20" y="{label_y:.1f}" class="day-text">{label}</text>')

    last_month = None
    month_svg_tags = []
    grid_cells_svg = []

    for w_idx, week in enumerate(weeks):
        col_x = grid_start_x + (w_idx * stride)
        days = week.get("contributionDays", [])

        # Month labels
        for day in days:
            date_str = day.get("date", "")
            if date_str:
                month_idx = int(date_str.split("-")[1]) - 1
                if month_idx != last_month and w_idx < 50:
                    last_month = month_idx
                    month_name = MONTH_NAMES[month_idx]
                    month_svg_tags.append(
                        f'  <text x="{col_x:.1f}" y="{grid_start_y - 10}" class="label-text">{month_name}</text>'
                    )
                break

        # Week cells
        for day in days:
            weekday = day.get("weekday", 0)
            row_y = grid_start_y + (weekday * stride)
            cnt = day.get("contributionCount", 0)
            lvl = map_count_to_level(cnt, q1, q2, q3)
            cell_color = COLOR_LEVELS[lvl]
            date_val = day.get("date", "")

            stroke_attr = f'stroke="{BORDER_COLOR}" stroke-width="0.5"' if lvl == 0 else ""
            grid_cells_svg.append(
                f'    <rect class="cell" x="{col_x:.1f}" y="{row_y:.1f}" width="{square_size}" height="{square_size}" rx="2.5" fill="{cell_color}" {stroke_attr}><title>{cnt} contributions on {date_val}</title></rect>'
            )

    svg_parts.append("  <!-- Month Labels -->")
    svg_parts.extend(month_svg_tags)

    svg_parts.append("  <!-- Grid Cells -->\n  <g id=\"grid-cells\">")
    svg_parts.extend(grid_cells_svg)
    svg_parts.append("  </g>")

    # Legend at bottom right: "Less" [0][1][2][3][4] "More"
    legend_start_x = WIDTH - 165
    legend_y = HEIGHT - 20
    svg_parts.append(f"""
  <!-- Legend -->
  <g id="heatmap-legend">
    <text x="{legend_start_x - 30}" y="{legend_y + 8}" class="legend-text">Less</text>
""")

    for i, col in enumerate(COLOR_LEVELS):
        lx = legend_start_x + (i * (square_size + 3))
        stroke_attr = f'stroke="{BORDER_COLOR}" stroke-width="0.5"' if i == 0 else ""
        svg_parts.append(
            f'    <rect class="cell" x="{lx:.1f}" y="{legend_y}" width="{square_size}" height="{square_size}" rx="2" fill="{col}" {stroke_attr}/>'
        )

    svg_parts.append(f"""    <text x="{legend_start_x + 5 * (square_size + 3) + 6}" y="{legend_y + 8}" class="legend-text">More</text>
  </g>
</svg>
""")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))

    print(f"Successfully generated contrib-heatmap.svg at: {output_path} with REAL GitHub data.")


if __name__ == "__main__":
    out_file = REPO_ROOT / "contrib-heatmap.svg"
    generate_heatmap_svg(out_file)

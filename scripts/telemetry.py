#!/usr/bin/env python3
"""Regenerate assets/telemetry.svg — Grand Line sea chart light theme."""
import json
import os
import urllib.request

LOGIN = "devsoniclk"
ROOT = os.path.join(os.path.dirname(__file__), "..", "assets")

TOKEN = os.environ.get("GH_TOKEN", os.environ.get("GITHUB_TOKEN", ""))

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC) { totalCount }
    followers { totalCount }
    following { totalCount }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def api(url, payload=None):
    headers = {
        "Authorization": f"bearer {TOKEN.strip()}",
        "Accept": "application/vnd.github+json",
    }
    data = json.dumps(payload).encode() if payload else None
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def fetch():
    user = api("https://api.github.com/graphql", {"query": QUERY, "variables": {"login": LOGIN}})["data"]["user"]
    coll = user["contributionsCollection"]
    days = [d for w in coll["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    days.sort(key=lambda d: d["date"])
    counts = [d["contributionCount"] for d in days]
    last14 = counts[-14:]
    max14 = max(last14) if last14 else 1

    repos = api(f"https://api.github.com/users/{LOGIN}/repos?per_page=100")
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)

    return {
        "repos": user["repositories"]["totalCount"],
        "stars": total_stars,
        "followers": user["followers"]["totalCount"],
        "following": user["following"]["totalCount"],
        "last14": last14,
        "max14": max14,
    }


def bar(x, height, max_h, delay):
    bar_h = max(3, int(32 * height / max_h)) if max_h > 0 else 3
    bar_y = 278 - bar_h
    opacity = max(0.45, height / max_h) if max_h > 0 else 0.45
    if opacity > 0.8:
        fill = "#92400e"
    elif opacity > 0.6:
        fill = "#b45309"
    elif opacity > 0.4:
        fill = "#d97706"
    else:
        fill = "#fcd34d"
    return (
        f'<rect x="{x}" y="{bar_y}" width="18" height="{bar_h}" rx="3" '
        f'fill="{fill}" opacity="{opacity:.2f}"/>'
    )


def island(cx, cy, size, color, label, delay):
    return f'''<circle class="isle" cx="{cx}" cy="{cy}" r="{size}" fill="{color}" style="animation-delay:{delay:.1f}s"/>
  <text x="{cx}" y="{cy + 22}" text-anchor="middle" font-size="9" fill="#92400e" font-family="monospace">{label}</text>'''


def generate_telemetry(data):
    bars = "\n  ".join(
        bar(190 + i * 22, v, data["max14"], i * 0.05)
        for i, v in enumerate(data["last14"])
    )

    # Generate island markers along the route
    islands = []
    labels = ["WK1", "WK2", "WK3", "WK4", "WK5", "WK6", "NOW"]
    positions = [(180, 160), (300, 130), (420, 150), (540, 110), (640, 140), (760, 120), (860, 140)]
    colors = ["#f59e0b", "#d97706", "#ef4444", "#b45309", "#22c55e", "#d97706", "#22c55e"]
    for i, (pos, label, color) in enumerate(zip(positions, labels, colors)):
        islands.append(island(pos[0], pos[1], 5 if i < len(labels)-1 else 6, color, label, i * 0.3))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 300" font-family="'Georgia','Times New Roman',serif" role="img" aria-label="Grand Line — contribution sea chart">
  <defs>
    <linearGradient id="sea" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#e0f2fe"/>
      <stop offset="1" stop-color="#bae6fd"/>
    </linearGradient>
    <filter id="watercolor">
      <feTurbulence type="fractalNoise" baseFrequency="0.015" numOctaves="3" result="noise"/>
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="3"/>
    </filter>
  </defs>
  <style>
    @keyframes pulse{{0%,100%{{r:4}}50%{{r:7}}}}
    .isle{{animation:pulse 2.5s ease-in-out infinite}}
    @keyframes fadein{{from{{opacity:0}}to{{opacity:1}}}}
    .fi{{animation:fadein 1s ease-out both}}
  </style>

  <rect x="1" y="1" width="938" height="298" rx="12" fill="#fefce8" stroke="#ca8a04" stroke-opacity="0.3" stroke-width="1.5"/>
  <rect x="20" y="50" width="900" height="200" rx="8" fill="url(#sea)" opacity="0.4" filter="url(#watercolor)"/>

  <!-- Compass rose -->
  <g transform="translate(870, 75)" opacity="0.4">
    <circle cx="0" cy="0" r="28" fill="none" stroke="#ca8a04" stroke-width="1.5"/>
    <text x="0" y="-32" text-anchor="middle" font-size="10" fill="#ca8a04" font-weight="bold">N</text>
    <text x="0" y="42" text-anchor="middle" font-size="10" fill="#ca8a04">S</text>
    <text x="38" y="4" text-anchor="middle" font-size="10" fill="#ca8a04">E</text>
    <text x="-38" y="4" text-anchor="middle" font-size="10" fill="#ca8a04">W</text>
    <polygon points="0,-22 4,-6 -4,-6" fill="#ca8a04"/>
    <polygon points="0,22 4,6 -4,6" fill="#ca8a04" opacity="0.5"/>
  </g>

  <text x="36" y="36" font-size="15" letter-spacing="3" fill="#92400e" font-weight="bold">⚓ GRAND LINE — CONTRIBUTION SEA CHART</text>

  <!-- Route -->
  <path d="M80,200 C140,170 200,130 280,145 C360,160 380,110 460,130 C540,150 520,100 620,120 C720,140 700,160 800,135 C840,125 860,130 880,140"
        fill="none" stroke="#ca8a04" stroke-width="2" stroke-dasharray="8 4" opacity="0.5"/>

  <!-- Islands -->
  {chr(10).join(islands)}

  <!-- Activity bars -->
  <text x="36" y="275" font-size="11" letter-spacing="2" fill="#a16207">▸ 14-DAY VOYAGE</text>
  {bars}
  <line x1="188" y1="280" x2="496" y2="280" stroke="#e5e7eb" stroke-width="1"/>

  <!-- Legend -->
  <text x="530" y="275" font-size="11" fill="#92400e" font-family="monospace">LEGEND:</text>
  <circle cx="590" cy="271" r="4" fill="#ef4444"/>
  <text x="600" y="276" font-size="10" fill="#78350f">PEAK</text>
  <circle cx="645" cy="271" r="4" fill="#22c55e"/>
  <text x="655" y="276" font-size="10" fill="#78350f">PORT</text>
  <circle cx="695" cy="271" r="4" fill="#f59e0b"/>
  <text x="705" y="276" font-size="10" fill="#78350f">VOYAGE</text>
</svg>'''

    with open(os.path.join(ROOT, "telemetry.svg"), "w") as f:
        f.write(svg)
    print(f"telemetry.svg updated: {data['repos']} repos, {data['stars']} stars")


if __name__ == "__main__":
    data = fetch()
    generate_telemetry(data)
    print("Done.")

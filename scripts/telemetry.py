#!/usr/bin/env python3
"""Regenerate assets/telemetry.svg from live GitHub data."""
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
    bar_h = max(3, int(98 * height / max_h)) if max_h > 0 else 3
    bar_y = 208 - bar_h
    opacity = max(0.20, height / max_h) if max_h > 0 else 0.20
    return (
        f'<rect class="bar" x="{x}" y="{bar_y}" width="16" height="{bar_h}" rx="3" '
        f'fill="#0ea5e9" opacity="{opacity:.2f}" style="animation-delay:{delay:.2f}s"/>'
    )


def generate_telemetry(data):
    bars = "\n  ".join(
        bar(580 + i * 22, v, data["max14"], i * 0.08)
        for i, v in enumerate(data["last14"])
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 280" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" role="img" aria-label="fleet telemetry">
  <style>
    @keyframes blink{{0%,45%{{opacity:1}}50%,100%{{opacity:0}}}}
    .cur{{animation:blink 1.1s steps(1) infinite}}
    @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
    .dot{{animation:pulse 2.2s ease-in-out infinite}}
    @keyframes grow{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
    .bar{{transform-box:fill-box;transform-origin:bottom;animation:grow .9s ease-out both}}
  </style>

  <rect x="1" y="1" width="938" height="278" rx="12" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>

  <text x="36" y="42" font-size="14" letter-spacing="2" fill="#0ea5e9" font-weight="bold">OSIRIS // FLEET TELEMETRY</text>
  <text x="904" y="42" font-size="12" letter-spacing="1.5" fill="#94a3b8" text-anchor="end">DEVSONICLK · LIVE <tspan class="dot" fill="#22c55e">●</tspan></text>
  <line x1="24" y1="56" x2="916" y2="56" stroke="#e2e8f0" stroke-width="1"/>

  <text x="36" y="90" font-size="13" fill="#94a3b8">▸ REPOSITORIES<tspan dx="8" fill="#0f172a" font-weight="600">{data["repos"]}</tspan></text>
  <text x="36" y="118" font-size="13" fill="#94a3b8">▸ TOTAL STARS<tspan dx="8" fill="#0f172a" font-weight="600">{data["stars"]}</tspan></text>
  <text x="36" y="146" font-size="13" fill="#94a3b8">▸ PRIMARY<tspan dx="8" fill="#0f172a" font-weight="600">PYTHON</tspan></text>
  <text x="36" y="174" font-size="13" fill="#94a3b8">▸ LANGUAGES<tspan dx="8" fill="#0f172a" font-weight="600">5 ACTIVE</tspan></text>
  <text x="36" y="202" font-size="13" fill="#94a3b8">▸ LOCATION<tspan dx="8" fill="#0f172a" font-weight="600">SRI LANKA</tspan></text>
  <text x="36" y="230" font-size="13" fill="#94a3b8">▸ FOLLOWERS / FOLLOWING<tspan dx="8" fill="#0f172a" font-weight="600">{data["followers"]} / {data["following"]}</tspan></text>

  <text x="580" y="90" font-size="11" letter-spacing="2" fill="#94a3b8">ACTIVITY // 14D</text>
  {bars}
  <line x1="578" y1="208" x2="884" y2="208" stroke="#e2e8f0" stroke-width="1"/>

  <text x="36" y="260" font-size="12" letter-spacing="1" fill="#94a3b8">TARGETS: FLY.IO · SUPABASE · BINANCE · TELEGRAM <tspan class="cur" fill="#0ea5e9">█</tspan></text>
</svg>'''

    with open(os.path.join(ROOT, "telemetry.svg"), "w") as f:
        f.write(svg)
    print(f"telemetry.svg updated: {data['repos']} repos, {data['stars']} stars")


if __name__ == "__main__":
    data = fetch()
    generate_telemetry(data)
    print("Done.")

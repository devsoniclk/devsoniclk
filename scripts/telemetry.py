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

    # Get total stars
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


def bar(x, y, height, max_h, delay):
    bar_h = max(3, int(118 * height / max_h)) if max_h > 0 else 3
    bar_y = 234 - bar_h
    opacity = max(0.25, height / max_h) if max_h > 0 else 0.25
    return (
        f'<rect class="bar" x="{x}" y="{bar_y}" width="13" height="{bar_h}" rx="2" '
        f'fill="#0ea5e9" opacity="{opacity:.2f}" style="animation-delay:{delay:.2f}s"/>'
    )


def generate_telemetry(data):
    bars = "\n  ".join(
        bar(646 + i * 19, 0, v, data["max14"], i * 0.09)
        for i, v in enumerate(data["last14"])
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 310" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" role="img" aria-label="fleet telemetry">
  <style>
    @keyframes blink{{0%,45%{{opacity:1}}50%,100%{{opacity:0}}}}
    .cur{{animation:blink 1.1s steps(1) infinite}}
    @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
    .dot{{animation:pulse 2.2s ease-in-out infinite}}
    @keyframes sweep{{from{{transform:translateY(-10px)}}to{{transform:translateY(320px)}}}}
    .sweep{{animation:sweep 8s linear infinite}}
    @keyframes grow{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
    .bar{{transform-box:fill-box;transform-origin:bottom;animation:grow .9s ease-out both}}
  </style>

  <rect x="1" y="1" width="938" height="308" rx="12" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>
  <clipPath id="panel"><rect x="1" y="1" width="938" height="308" rx="12"/></clipPath>
  <g clip-path="url(#panel)"><rect class="sweep" width="940" height="3" fill="#0ea5e9" opacity="0.06"/></g>

  <text x="36" y="42" font-size="15" letter-spacing="2" fill="#0ea5e9" font-weight="bold">OSIRIS // FLEET TELEMETRY</text>
  <text x="904" y="42" font-size="12.5" letter-spacing="1.5" fill="#94a3b8" text-anchor="end">DEVSONICLK · LIVE <tspan class="dot" fill="#22c55e">●</tspan></text>
  <line x1="24" y1="58" x2="916" y2="58" stroke="#e2e8f0" stroke-width="1"/>

  <text x="36" y="96" font-size="14.5" fill="#94a3b8">▸ REPOSITORIES ·····················<tspan fill="#0f172a" font-weight="600"> {data["repos"]}</tspan></text>
  <text x="36" y="126" font-size="14.5" fill="#94a3b8">▸ TOTAL STARS ······················<tspan fill="#0f172a" font-weight="600"> {data["stars"]}</tspan></text>
  <text x="36" y="156" font-size="14.5" fill="#94a3b8">▸ PRIMARY LANGUAGE ·················<tspan fill="#0f172a" font-weight="600"> PYTHON</tspan></text>
  <text x="36" y="186" font-size="14.5" fill="#94a3b8">▸ ACTIVE LANGUAGES ·················<tspan fill="#0f172a" font-weight="600"> 5</tspan></text>
  <text x="36" y="216" font-size="14.5" fill="#94a3b8">▸ LOCATION ·························<tspan fill="#0f172a" font-weight="600"> SRI LANKA</tspan></text>
  <text x="36" y="246" font-size="14.5" fill="#94a3b8">▸ FOLLOWERS / FOLLOWING ············<tspan fill="#0f172a" font-weight="600"> {data["followers"]} / {data["following"]}</tspan></text>

  <text x="646" y="96" font-size="11.5" letter-spacing="2" fill="#94a3b8">ACTIVITY // 14D</text>
  {bars}
  <line x1="644" y1="235" x2="912" y2="235" stroke="#e2e8f0" stroke-width="1"/>

  <text x="36" y="284" font-size="13" letter-spacing="1" fill="#94a3b8">DEPLOYMENT TARGETS: FLY.IO · SUPABASE · BINANCE · TELEGRAM <tspan class="cur" fill="#0ea5e9">█</tspan></text>
</svg>'''

    with open(os.path.join(ROOT, "telemetry.svg"), "w") as f:
        f.write(svg)
    print(f"telemetry.svg updated: {data['repos']} repos, {data['stars']} stars")


if __name__ == "__main__":
    data = fetch()
    generate_telemetry(data)
    print("Done.")

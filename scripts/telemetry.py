#!/usr/bin/env python3
"""Regenerate assets/telemetry.svg from live GitHub data — One Piece dark theme."""
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
    bar_h = max(3, int(88 * height / max_h)) if max_h > 0 else 3
    bar_y = 228 - bar_h
    opacity = max(0.30, height / max_h) if max_h > 0 else 0.30
    # Color gradient from red to orange based on intensity
    if opacity > 0.8:
        fill = "#ffa500"
    elif opacity > 0.6:
        fill = "#ff8833"
    elif opacity > 0.4:
        fill = "#ff6b35"
    else:
        fill = "#ff4444"
    return (
        f'<rect class="bar" x="{x}" y="{bar_y}" width="20" height="{bar_h}" rx="3" '
        f'fill="{fill}" opacity="{opacity:.2f}" style="animation-delay:{delay:.2f}s"/>'
    )


def generate_telemetry(data):
    bars = "\n  ".join(
        bar(36 + i * 26, v, data["max14"], i * 0.05)
        for i, v in enumerate(data["last14"])
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 260" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" role="img" aria-label="gear power stats">
  <defs>
    <linearGradient id="fire2" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#ff4444"/>
      <stop offset="1" stop-color="#ffa500"/>
    </linearGradient>
    <filter id="glow2">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <style>
    @keyframes countup{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
    .cu{{animation:countup .6s ease-out both}}
    @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
    .dot{{animation:pulse 2s ease-in-out infinite}}
    @keyframes grow{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
    .bar{{transform-box:fill-box;transform-origin:bottom;animation:grow .8s ease-out both}}
  </style>

  <rect x="1" y="1" width="938" height="258" rx="14" fill="#111" stroke="#ff4444" stroke-opacity="0.2" stroke-width="1"/>

  <text x="36" y="40" font-size="14" letter-spacing="3" fill="#ff6b35" font-weight="bold">⚙ GEAR POWER LEVEL</text>
  <circle class="dot" cx="900" cy="36" r="4" fill="#22c55e"/>
  <text x="888" y="41" font-size="11" fill="#666" text-anchor="end">ACTIVE</text>
  <line x1="24" y1="54" x2="916" y2="54" stroke="#ff4444" stroke-opacity="0.15"/>

  <g class="cu" style="animation-delay:0.2s">
    <text x="36" y="90" font-size="11" letter-spacing="2" fill="#666">PUBLIC REPOS</text>
    <text x="36" y="118" font-size="28" fill="#ffa500" font-weight="bold" filter="url(#glow2)">{data["repos"]}</text>
  </g>

  <g class="cu" style="animation-delay:0.4s">
    <text x="200" y="90" font-size="11" letter-spacing="2" fill="#666">TOTAL STARS</text>
    <text x="200" y="118" font-size="28" fill="#ffa500" font-weight="bold" filter="url(#glow2)">{data["stars"]}</text>
  </g>

  <g class="cu" style="animation-delay:0.6s">
    <text x="364" y="90" font-size="11" letter-spacing="2" fill="#666">LANGUAGES</text>
    <text x="364" y="118" font-size="28" fill="#ffa500" font-weight="bold" filter="url(#glow2)">5</text>
    <text x="400" y="118" font-size="13" fill="#555" dx="-2">active</text>
  </g>

  <g class="cu" style="animation-delay:0.8s">
    <text x="520" y="90" font-size="11" letter-spacing="2" fill="#666">PRIMARY</text>
    <text x="520" y="118" font-size="22" fill="#ff6b35" font-weight="bold">PYTHON</text>
  </g>

  <g class="cu" style="animation-delay:1s">
    <text x="700" y="90" font-size="11" letter-spacing="2" fill="#666">LOCATION</text>
    <text x="700" y="118" font-size="22" fill="#ff6b35" font-weight="bold">SRI LANKA</text>
  </g>

  <text x="36" y="160" font-size="11" letter-spacing="2" fill="#666">CONTRIBUTION ACTIVITY // LAST 14 DAYS</text>
  {bars}
  <line x1="34" y1="228" x2="396" y2="228" stroke="#333" stroke-width="1"/>

  <text x="450" y="160" font-size="11" letter-spacing="2" fill="#666">DEPLOYMENT FLEET</text>
  <g class="cu" style="animation-delay:1.2s">
    <rect x="450" y="175" width="80" height="24" rx="12" fill="none" stroke="#ff4444" stroke-opacity="0.4"/>
    <text x="490" y="191" font-size="11" fill="#ff6b35" text-anchor="middle" font-weight="600">Fly.io</text>
    <rect x="538" y="175" width="100" height="24" rx="12" fill="none" stroke="#ff4444" stroke-opacity="0.4"/>
    <text x="588" y="191" font-size="11" fill="#ff6b35" text-anchor="middle" font-weight="600">Supabase</text>
    <rect x="646" y="175" width="80" height="24" rx="12" fill="none" stroke="#ff4444" stroke-opacity="0.4"/>
    <text x="686" y="191" font-size="11" fill="#ff6b35" text-anchor="middle" font-weight="600">Binance</text>
    <rect x="734" y="175" width="90" height="24" rx="12" fill="none" stroke="#ff4444" stroke-opacity="0.4"/>
    <text x="779" y="191" font-size="11" fill="#ff6b35" text-anchor="middle" font-weight="600">Telegram</text>
  </g>

  <text x="36" y="246" font-size="12" letter-spacing="1" fill="#555">ALL SYSTEMS OPERATIONAL · HORIZON STABLE <tspan fill="#ff6b35" class="dot">●</tspan></text>
</svg>'''

    with open(os.path.join(ROOT, "telemetry.svg"), "w") as f:
        f.write(svg)
    print(f"telemetry.svg updated: {data['repos']} repos, {data['stars']} stars")


if __name__ == "__main__":
    data = fetch()
    generate_telemetry(data)
    print("Done.")

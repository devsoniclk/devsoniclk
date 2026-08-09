#!/usr/bin/env python3
"""Regenerate assets/telemetry.svg — minimal contribution chart."""
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
    headers = {"Authorization": f"bearer {TOKEN.strip()}", "Accept": "application/vnd.github+json"}
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
    return {"repos": user["repositories"]["totalCount"], "stars": total_stars,
            "followers": user["followers"]["totalCount"], "following": user["following"]["totalCount"],
            "last14": last14, "max14": max14}

def bar(x, height, max_h, delay):
    bar_h = max(3, int(90 * height / max_h)) if max_h > 0 else 3
    bar_y = 170 - bar_h
    opacity = max(0.20, height / max_h) if max_h > 0 else 0.20
    return (f'<rect class="dot" style="animation-delay:{delay:.2f}s" x="{x}" y="{bar_y}" '
            f'width="24" height="{bar_h}" rx="4" fill="#d97706" opacity="{opacity:.2f}"/>')

def generate(data):
    bars = "\n  ".join(bar(50 + i * 62, v, data["max14"], 0.1 + i * 0.05) for i, v in enumerate(data["last14"]))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 200" role="img" aria-label="contributions">
  <defs><style>@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&amp;display=swap');</style></defs>
  <style>
    text{{font-family:'Lato',sans-serif}}
    @keyframes fadeIn{{from{{opacity:0}}to{{opacity:1}}}}
    .dot{{animation:fadeIn .4s ease-out both}}
    @keyframes gentlePulse{{0%,100%{{r:3;opacity:.6}}50%{{r:5;opacity:1}}}}
    .isle{{animation:gentlePulse 3s ease-in-out infinite}}
  </style>
  <rect width="940" height="200" fill="#fffef9" rx="12"/>
  <text x="36" y="30" font-size="10" font-weight="700" fill="#94a3b8" letter-spacing="3">CONTRIBUTIONS — LAST 14 DAYS</text>
  <line x1="36" y1="170" x2="900" y2="170" stroke="#f1f5f9" stroke-width="1"/>
  <line x1="36" y1="130" x2="900" y2="130" stroke="#f1f5f9" stroke-width="0.5" stroke-dasharray="4 4"/>
  <line x1="36" y1="90" x2="900" y2="90" stroke="#f1f5f9" stroke-width="0.5" stroke-dasharray="4 4"/>
  {bars}
  <circle class="isle" cx="{50 + 13 * 62 + 12}" cy="{170 - max(3, int(90 * data['last14'][-1] / data['max14'])) if data['max14'] > 0 else 3}" r="4" fill="#22c55e" style="animation-delay:2s"/>
  <text x="36" y="190" font-size="10" fill="#cbd5e1">each bar = 1 day · taller = more contributions</text>
</svg>'''
    with open(os.path.join(ROOT, "telemetry.svg"), "w") as f:
        f.write(svg)
    print(f"telemetry.svg updated: {data['repos']} repos, {data['stars']} stars")

if __name__ == "__main__":
    generate(fetch())
    print("Done.")

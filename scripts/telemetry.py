#!/usr/bin/env python3
"""Regenerate assets/telemetry.svg — Grand Line journey, clean layout, no ship."""
import json
import os
import urllib.request

LOGIN = "devsoniclk"
ROOT = os.path.join(os.path.dirname(__file__), "..", "assets")
TOKEN = os.environ.get("GH_TOKEN", os.environ.get("GITHUB_TOKEN", ""))

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER) { totalCount }
    followers { totalCount }
    contributionsCollection {
      contributionYears
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    createdAt
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
    monthly = {}
    for d in days:
        ym = d["date"][:7]
        if ym not in monthly:
            monthly[ym] = 0
        monthly[ym] += d["contributionCount"]
    total_year = sum(d["contributionCount"] for d in days)
    repos = api(f"https://api.github.com/users/{LOGIN}/repos?per_page=100&type=all")
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    return {"repos": user["repositories"]["totalCount"], "stars": total_stars,
            "years": len(coll["contributionYears"]), "total_year": total_year,
            "monthly": monthly, "created": user["createdAt"][:4]}

def generate(data):
    months_2026 = {k: v for k, v in data["monthly"].items() if k.startswith("2026")}
    max_m = max(months_2026.values()) if months_2026 else 1
    labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    bars = []
    for i, lbl in enumerate(labels):
        key = f"2026-{i+1:02d}"
        val = months_2026.get(key, 0)
        if val == 0 and i > 7:
            continue
        h = max(3, int(94 * val / max_m)) if max_m > 0 and val > 0 else 3
        y = 242 - h
        op = max(0.20, val / max_m) if max_m > 0 and val > 0 else 0.15
        x = 500 + i * 36
        bars.append(f'<rect class="bar" x="{x}" y="{y}" width="28" height="{h}" rx="3" fill="#d97706" opacity="{op:.2f}" style="animation-delay:{2.2+i*0.1:.1f}s"/>')
        bars.append(f'<text x="{x+14}" y="258" text-anchor="middle" font-size="8" fill="#94a3b8">{lbl}</text>')

    bars_svg = "\n  ".join(bars)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 300" role="img" aria-label="Grand Line — contribution journey since {data["created"]}">
  <defs>
    <style>@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&amp;display=swap');</style>
    <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f59e0b"/>
      <stop offset="1" stop-color="#d97706"/>
    </linearGradient>
  </defs>
  <style>
    text{{font-family:'Lato',sans-serif}}
    @keyframes islandPop{{from{{opacity:0;transform:scale(0)}}to{{opacity:1;transform:scale(1)}}}}
    .isle{{animation:islandPop .4s ease-out both}}
    @keyframes barGrow{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
    .bar{{transform-box:fill-box;transform-origin:bottom;animation:barGrow .6s ease-out both}}
    @keyframes drawRoute{{from{{stroke-dashoffset:900}}to{{stroke-dashoffset:0}}}}
    .route{{stroke-dasharray:900;animation:drawRoute 3s ease-out both}}
  </style>

  <rect width="940" height="300" fill="#fffef9" rx="12"/>

  <text x="36" y="30" font-size="10" font-weight="700" fill="#94a3b8" letter-spacing="3">GRAND LINE — CONTRIBUTION JOURNEY</text>
  <text x="904" y="30" font-size="10" fill="#cbd5e1" text-anchor="end">{data["repos"]} repos · {data["total_year"]} contributions last year · sailing since {data["created"]}</text>

  <rect x="24" y="48" width="892" height="180" rx="8" fill="#f0f9ff" opacity="0.25"/>

  <path class="route" d="M80,180 C140,170 180,150 240,155 C300,160 320,140 380,142 C440,144 460,125 520,128 C580,131 600,110 660,115 C720,120 740,95 800,100 C840,103 860,90 880,95"
        fill="none" stroke="#d97706" stroke-width="1.5" stroke-dasharray="6 4" opacity="0.35"/>

  <g class="isle" style="animation-delay:0.1s"><circle cx="80" cy="180" r="5" fill="#94a3b8" stroke="#64748b" stroke-width="1.5"/><text x="80" y="168" text-anchor="middle" font-size="8" fill="#94a3b8">account born</text><text x="80" y="200" text-anchor="middle" font-size="10" font-weight="700" fill="#64748b">2018</text><text x="80" y="213" text-anchor="middle" font-size="8" fill="#94a3b8">East Blue</text></g>
  <g class="isle" style="animation-delay:0.3s"><circle cx="170" cy="160" r="4" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/><text x="170" y="180" text-anchor="middle" font-size="9" font-weight="700" fill="#94a3b8">2019</text></g>
  <g class="isle" style="animation-delay:0.5s"><circle cx="250" cy="152" r="4" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/><text x="250" y="172" text-anchor="middle" font-size="9" font-weight="700" fill="#94a3b8">2020</text></g>
  <g class="isle" style="animation-delay:0.7s"><circle cx="330" cy="142" r="4" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/><text x="330" y="162" text-anchor="middle" font-size="9" font-weight="700" fill="#94a3b8">2021</text></g>
  <g class="isle" style="animation-delay:0.9s"><circle cx="410" cy="135" r="4" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/><text x="410" y="155" text-anchor="middle" font-size="9" font-weight="700" fill="#94a3b8">2022</text></g>
  <g class="isle" style="animation-delay:1.1s"><circle cx="490" cy="128" r="4" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/><text x="490" y="148" text-anchor="middle" font-size="9" font-weight="700" fill="#94a3b8">2023</text></g>
  <g class="isle" style="animation-delay:1.3s"><circle cx="570" cy="118" r="5" fill="#fcd34d" stroke="#f59e0b" stroke-width="1.5"/><text x="570" y="138" text-anchor="middle" font-size="9" font-weight="700" fill="#92400e">2024</text><text x="570" y="151" text-anchor="middle" font-size="8" fill="#d97706">new world</text></g>
  <g class="isle" style="animation-delay:1.6s"><circle cx="680" cy="110" r="6" fill="#f59e0b" stroke="#d97706" stroke-width="2"/><text x="680" y="96" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">40</text><text x="680" y="130" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">2025</text><text x="680" y="143" text-anchor="middle" font-size="8" fill="#d97706">awakening</text></g>
  <g class="isle" style="animation-delay:2s"><circle cx="840" cy="92" r="8" fill="#d97706" stroke="#92400e" stroke-width="2.5"/><text x="840" y="76" text-anchor="middle" font-size="16" font-weight="900" fill="#92400e">{data["total_year"]}</text><text x="840" y="114" text-anchor="middle" font-size="11" font-weight="900" fill="#92400e">2026</text><text x="840" y="128" text-anchor="middle" font-size="9" fill="#d97706" font-weight="700">GEAR 5</text></g>

  <text x="500" y="200" font-size="8" font-weight="700" fill="#94a3b8" letter-spacing="2">2026 MONTHLY BREAKDOWN</text>
  {bars_svg}

  <g transform="translate(36, 268)">
    <circle cx="0" cy="0" r="3.5" fill="#cbd5e1"/><text x="10" y="4" font-size="9" fill="#94a3b8">dormant</text>
    <circle cx="70" cy="0" r="3.5" fill="#fcd34d"/><text x="80" y="4" font-size="9" fill="#94a3b8">waking</text>
    <circle cx="130" cy="0" r="3.5" fill="#d97706"/><text x="140" y="4" font-size="9" fill="#94a3b8">active</text>
    <circle cx="185" cy="0" r="3.5" fill="#22c55e"/><text x="195" y="4" font-size="9" fill="#94a3b8">today</text>
  </g>
  <text x="904" y="280" font-size="9" fill="#cbd5e1" text-anchor="end">{data["repos"]} repos · {data["stars"]} stars · 5 languages · {data["years"]} years on the Grand Line</text>
</svg>'''

    with open(os.path.join(ROOT, "telemetry.svg"), "w") as f:
        f.write(svg)
    print(f"telemetry.svg updated: {data['repos']} repos, {data['total_year']} contributions, {data['years']} years")

if __name__ == "__main__":
    data = fetch()
    generate(data)
    print("Done.")

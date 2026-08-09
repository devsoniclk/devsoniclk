#!/usr/bin/env python3
"""Regenerate assets/telemetry.svg — Grand Line journey with verified stats."""
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
    following { totalCount }
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

    # Monthly breakdown for current year
    monthly = {}
    for d in days:
        ym = d["date"][:7]
        if ym not in monthly:
            monthly[ym] = 0
        monthly[ym] += d["contributionCount"]

    total_year = sum(d["contributionCount"] for d in days)

    repos = api(f"https://api.github.com/users/{LOGIN}/repos?per_page=100&type=all")
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)

    return {
        "repos": user["repositories"]["totalCount"],
        "stars": total_stars,
        "followers": user["followers"]["totalCount"],
        "following": user["following"]["totalCount"],
        "years": len(coll["contributionYears"]),
        "year_list": coll["contributionYears"],
        "total_year": total_year,
        "monthly": monthly,
        "created": user["createdAt"][:4],
    }

def generate(data):
    # Build monthly bars for 2026
    months_2026 = {k: v for k, v in data["monthly"].items() if k.startswith("2026")}
    max_monthly = max(months_2026.values()) if months_2026 else 1
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_bars = []
    for i, label in enumerate(month_labels):
        key = f"2026-{i+1:02d}"
        val = months_2026.get(key, 0)
        bar_h = max(3, int(104 * val / max_monthly)) if max_monthly > 0 and val > 0 else 3
        bar_y = 220 - bar_h
        opacity = max(0.25, val / max_monthly) if max_monthly > 0 and val > 0 else 0.15
        x = 680 + i * 22
        monthly_bars.append(
            f'<rect class="bar" x="{x}" y="{bar_y}" width="18" height="{bar_h}" rx="2" '
            f'fill="#d97706" opacity="{opacity:.2f}" style="animation-delay:{3.2 + i*0.1:.1f}s"/>'
        )
        monthly_bars.append(f'<text x="{x+9}" y="235" text-anchor="middle" font-size="6" fill="#94a3b8">{label[0]}</text>')

    monthly_svg = "\n  ".join(monthly_bars)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 320" role="img" aria-label="Grand Line — contribution journey since {data["created"]}">
  <defs>
    <style>@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&amp;display=swap');</style>
    <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f0f9ff" stop-opacity="0.3"/>
      <stop offset="1" stop-color="#e0f2fe" stop-opacity="0.5"/>
    </linearGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f59e0b"/>
      <stop offset="1" stop-color="#d97706"/>
    </linearGradient>
  </defs>
  <style>
    text{{font-family:'Lato',sans-serif}}
    @keyframes drawRoute{{from{{stroke-dashoffset:1200}}to{{stroke-dashoffset:0}}}}
    .route{{stroke-dasharray:1200;animation:drawRoute 4s ease-out both}}
    @keyframes islandPop{{from{{opacity:0;transform:scale(0)}}to{{opacity:1;transform:scale(1)}}}}
    .isle{{animation:islandPop .4s ease-out both}}
    @keyframes barGrow{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
    .bar{{transform-box:fill-box;transform-origin:bottom;animation:barGrow .6s ease-out both}}
    @keyframes shipSail{{from{{offset-distance:0%}}to{{offset-distance:100%}}}}
    .ship{{offset-path:path('M80,240 C150,220 200,180 280,190 C360,200 380,140 460,150 C540,160 560,100 640,120 C720,140 740,80 820,100 C860,110 880,90 900,100');animation:shipSail 15s linear infinite}}
  </style>

  <rect width="940" height="320" fill="#fffef9" rx="12"/>
  <rect x="20" y="60" width="900" height="220" rx="8" fill="url(#sea)" opacity="0.4"/>

  <text x="36" y="32" font-size="10" font-weight="700" fill="#94a3b8" letter-spacing="3">GRAND LINE — CONTRIBUTION JOURNEY</text>
  <text x="904" y="32" font-size="10" fill="#cbd5e1" text-anchor="end">{data["repos"]} repos · {data["total_year"]} contributions last year · sailing since {data["created"]}</text>

  <path class="route" d="M80,240 C150,220 200,180 280,190 C360,200 380,140 460,150 C540,160 560,100 640,120 C720,140 740,80 820,100 C860,110 880,90 900,100"
        fill="none" stroke="#d97706" stroke-width="1.5" stroke-dasharray="6 4" opacity="0.4"/>

  <g class="ship">
    <polygon points="0,-6 4,6 -4,6" fill="#92400e" stroke="#78350f" stroke-width="0.8"/>
    <line x1="0" y1="-6" x2="0" y2="-11" stroke="#78350f" stroke-width="1"/>
    <rect x="-1" y="-15" width="6" height="5" rx="1" fill="#dc2626" opacity="0.8"/>
  </g>

  <!-- Year islands -->
  <g class="isle" style="animation-delay:0.2s"><circle cx="80" cy="240" r="6" fill="#94a3b8" stroke="#64748b" stroke-width="1.5"/><text x="80" y="265" text-anchor="middle" font-size="10" font-weight="700" fill="#64748b">2018</text><text x="80" y="278" text-anchor="middle" font-size="8" fill="#94a3b8">East Blue</text></g>
  <g class="isle" style="animation-delay:0.5s"><circle cx="180" cy="210" r="5" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/><text x="180" y="232" text-anchor="middle" font-size="9" font-weight="700" fill="#94a3b8">2019</text></g>
  <g class="isle" style="animation-delay:0.8s"><circle cx="260" cy="190" r="5" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/><text x="260" y="212" text-anchor="middle" font-size="9" font-weight="700" fill="#94a3b8">2020</text></g>
  <g class="isle" style="animation-delay:1.1s"><circle cx="340" cy="175" r="5" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/><text x="340" y="197" text-anchor="middle" font-size="9" font-weight="700" fill="#94a3b8">2021</text></g>
  <g class="isle" style="animation-delay:1.4s"><circle cx="420" cy="155" r="5" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/><text x="420" y="177" text-anchor="middle" font-size="9" font-weight="700" fill="#94a3b8">2022</text></g>
  <g class="isle" style="animation-delay:1.7s"><circle cx="490" cy="145" r="5" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/><text x="490" y="167" text-anchor="middle" font-size="9" font-weight="700" fill="#94a3b8">2023</text></g>
  <g class="isle" style="animation-delay:2s"><circle cx="560" cy="130" r="6" fill="#fcd34d" stroke="#f59e0b" stroke-width="1.5"/><text x="560" y="152" text-anchor="middle" font-size="9" font-weight="700" fill="#92400e">2024</text><text x="560" y="164" text-anchor="middle" font-size="8" fill="#d97706">new world</text></g>

  <!-- 2025: First contributions -->
  <g class="isle" style="animation-delay:2.3s">
    <circle cx="660" cy="115" r="7" fill="#f59e0b" stroke="#d97706" stroke-width="2"/>
    <text x="660" y="140" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">2025</text>
    <text x="660" y="152" text-anchor="middle" font-size="8" fill="#d97706">awakening</text>
  </g>

  <!-- 2026: Gear 5 -->
  <g class="isle" style="animation-delay:2.8s">
    <circle cx="830" cy="95" r="9" fill="#d97706" stroke="#92400e" stroke-width="2.5"/>
    <text x="830" y="122" text-anchor="middle" font-size="11" font-weight="900" fill="#92400e">2026</text>
    <text x="830" y="136" text-anchor="middle" font-size="9" fill="#d97706" font-weight="700">GEAR 5</text>
    <rect class="bar" x="806" y="48" width="48" height="47" rx="6" fill="url(#gold)" opacity="0.8" style="animation-delay:3s"/>
    <text x="830" y="44" text-anchor="middle" font-size="14" font-weight="900" fill="#92400e">{data["total_year"]}</text>
  </g>

  <!-- Monthly breakdown 2026 -->
  <g opacity="0.35">
    <text x="680" y="195" font-size="8" fill="#94a3b8" letter-spacing="1">2026 MONTHLY</text>
    {monthly_svg}
  </g>

  <!-- Legend -->
  <circle cx="36" cy="305" r="4" fill="#cbd5e1"/><text x="46" y="309" font-size="9" fill="#94a3b8">dormant</text>
  <circle cx="100" cy="305" r="4" fill="#fcd34d"/><text x="110" y="309" font-size="9" fill="#94a3b8">waking</text>
  <circle cx="155" cy="305" r="4" fill="#d97706"/><text x="165" y="309" font-size="9" fill="#94a3b8">active</text>
  <circle cx="210" cy="305" r="4" fill="#22c55e"/><text x="220" y="309" font-size="9" fill="#94a3b8">today</text>
  <text x="904" y="309" font-size="9" fill="#cbd5e1" text-anchor="end">{data["repos"]} repos · {data["stars"]} stars · 5 languages · {data["years"]} years on the Grand Line</text>
</svg>'''

    with open(os.path.join(ROOT, "telemetry.svg"), "w") as f:
        f.write(svg)
    print(f"telemetry.svg updated: {data['repos']} repos, {data['total_year']} contributions, {data['years']} years")

if __name__ == "__main__":
    data = fetch()
    generate(data)
    print("Done.")

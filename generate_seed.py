#!/usr/bin/env python3
"""
CupIQ - Seed dataset generator.
Produces worldcup_data.json with the FULL advanced-metric set for all 48
2026 World Cup teams. Values are MODELED SEED DATA (deterministic, based on
approximate strength ratings) so the dashboard works instantly. Replace by
running fetch_stats.py once you have free data sources wired (see README).
"""
import json, math, random
from datetime import datetime, timezone

random.seed(2026)  # deterministic output

# (name, confederation, group, approx_elo)  -- group "-" where draw unconfirmed
TEAMS = [
    # CONMEBOL
    ("Argentina","CONMEBOL","-",2105),("Brazil","CONMEBOL","-",2030),
    ("Colombia","CONMEBOL","-",1900),("Uruguay","CONMEBOL","-",1915),
    ("Ecuador","CONMEBOL","-",1840),("Paraguay","CONMEBOL","D",1760),
    # UEFA
    ("France","UEFA","-",2070),("Spain","UEFA","-",2050),("England","UEFA","-",2010),
    ("Portugal","UEFA","-",2000),("Netherlands","UEFA","-",1985),("Germany","UEFA","-",1965),
    ("Belgium","UEFA","-",1940),("Croatia","UEFA","-",1900),("Switzerland","UEFA","-",1860),
    ("Austria","UEFA","-",1850),("Türkiye","UEFA","D",1840),("Norway","UEFA","-",1830),
    ("Sweden","UEFA","-",1800),("Scotland","UEFA","-",1790),("Czechia","UEFA","A",1785),
    ("Bosnia and Herzegovina","UEFA","B",1760),
    # CONCACAF
    ("United States","CONCACAF","D",1810),("Mexico","CONCACAF","A",1800),
    ("Canada","CONCACAF","B",1770),("Panama","CONCACAF","-",1700),
    ("Curaçao","CONCACAF","-",1620),("Haiti","CONCACAF","-",1600),
    # CAF
    ("Morocco","CAF","-",1870),("Senegal","CAF","-",1850),("Egypt","CAF","-",1790),
    ("Algeria","CAF","-",1785),("Côte d'Ivoire","CAF","-",1775),("Ghana","CAF","-",1740),
    ("Tunisia","CAF","-",1730),("South Africa","CAF","A",1700),
    ("Cabo Verde","CAF","-",1640),("DR Congo","CAF","-",1680),
    # AFC
    ("Japan","AFC","-",1820),("Iran","AFC","-",1800),("South Korea","AFC","A",1790),
    ("Australia","AFC","D",1760),("Saudi Arabia","AFC","-",1690),("Qatar","AFC","-",1680),
    ("Uzbekistan","AFC","-",1660),("Jordan","AFC","-",1640),("Iraq","AFC","-",1635),
    # OFC
    ("New Zealand","OFC","-",1620),
]
# Note: CAF list in some sources includes DR Congo; rosters of 48 vary slightly
# pre-tournament. Confederation labels are accurate; adjust names in TEAMS if a
# late playoff changes a qualifier.

def around(base, spread, lo, hi, nd=2):
    v = base + random.uniform(-spread, spread)
    return round(max(lo, min(hi, v)), nd)

def build(name, conf, group, elo):
    # normalize strength 0..1 across realistic Elo band
    s = (elo - 1590) / (2110 - 1590)
    s = max(0.0, min(1.0, s))
    xg_for      = around(0.9 + s*1.5, 0.18, 0.6, 2.6)
    xg_against  = around(1.7 - s*1.0, 0.18, 0.5, 2.2)
    npxg        = round(max(0.4, xg_for - around(0.18,0.05,0.05,0.35)), 2)
    shots       = around(8 + s*9, 1.6, 6, 20, 1)
    sot         = round(shots * around(0.36,0.04,0.28,0.46), 1)
    big_ch      = around(1.0 + s*2.4, 0.5, 0.3, 4.2, 1)
    goals_vs_xg = around(s*0.25 - 0.05, 0.35, -0.7, 0.7)   # over/underperformance
    ppda        = around(13 - s*6, 1.3, 6.0, 15.0)          # lower = presses harder
    possession  = around(44 + s*16, 3.5, 36, 64, 1)
    prog_passes = around(28 + s*26, 5, 18, 62, 1)
    aerial      = around(46 + s*10, 4, 38, 62, 1)
    gk_psxg     = around(s*1.6 - 0.6, 0.5, -1.6, 1.8)       # +ve = keeper overperforms
    setpiece_xg = around(0.15 + s*0.35, 0.08, 0.05, 0.6)
    form        = around(1.4 + s*3.2, 0.5, 0.4, 5.0, 1)
    momentum    = int(around(40 + s*48, 8, 20, 99, 0))
    return {
        "team": name, "confederation": conf, "group": group,
        "elo": elo,
        "metrics": {
            "xg_for": xg_for, "xg_against": xg_against, "npxg": npxg,
            "shots_per90": shots, "shots_on_target": sot, "big_chances_per90": big_ch,
            "goals_vs_xg": goals_vs_xg, "ppda": ppda, "possession_pct": possession,
            "progressive_passes": prog_passes, "aerial_win_pct": aerial,
            "gk_psxg_minus_ga": gk_psxg, "setpiece_xg": setpiece_xg,
            "form_last5": form, "momentum_index": momentum,
        },
        "_strength": round(s, 4),
    }

teams = [build(*t) for t in TEAMS]

# ---- tournament model outputs (softmax on strength) ----
exp = [math.exp(t["_strength"] * 3.2) for t in teams]
tot = sum(exp)
for t, e in zip(teams, exp):
    trophy = e / tot
    s = t["_strength"]
    t["projection"] = {
        "advance_r32_pct": round(min(0.985, 0.55 + s * 0.42) * 100, 1),
        "reach_quarters_pct": round(min(0.90, 0.12 + s * 0.62) * 100, 1),
        "reach_final_pct": round(min(0.55, s ** 2 * 0.6) * 100, 1),
        "win_trophy_pct": round(trophy * 100, 1),
    }
    del t["_strength"]

teams.sort(key=lambda x: x["projection"]["win_trophy_pct"], reverse=True)

out = {
    "source": "SEED (modeled) - replace via fetch_stats.py for live FBref/Elo data",
    "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "season": "FIFA World Cup 2026",
    "team_count": len(teams),
    "metric_glossary": {
        "xg_for": "Expected goals created per match",
        "xg_against": "Expected goals conceded per match",
        "npxg": "Non-penalty expected goals per match",
        "shots_per90": "Shots per 90 minutes",
        "shots_on_target": "Shots on target per 90",
        "big_chances_per90": "High-quality chances created per 90",
        "goals_vs_xg": "Goals scored minus xG (finishing over/underperformance)",
        "ppda": "Passes allowed per defensive action (lower = more aggressive press)",
        "possession_pct": "Projected possession share",
        "progressive_passes": "Progressive passes per match",
        "aerial_win_pct": "Aerial duels won %",
        "gk_psxg_minus_ga": "Post-shot xG minus goals allowed (keeper over/underperformance)",
        "setpiece_xg": "Expected goals from set pieces per match",
        "form_last5": "Form rating over last 5 matches (0-5)",
        "momentum_index": "Composite momentum index (0-100)",
    },
    "teams": teams,
}

with open("worldcup_data.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(f"Wrote worldcup_data.json - {len(teams)} teams")
print("Top 5 by trophy %:")
for t in teams[:5]:
    print(f"  {t['team']:<16} {t['projection']['win_trophy_pct']}%  xGfor {t['metrics']['xg_for']}")

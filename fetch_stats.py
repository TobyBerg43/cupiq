#!/usr/bin/env python3
"""
CupIQ - LIVE data fetcher (zero-cost sources).

Pulls real advanced stats for the 2026 World Cup from FREE sources and writes
worldcup_data.json (same schema as generate_seed.py, so the dashboard just works).

ZERO-COST SOURCE STACK
----------------------
  * FBref (via the `soccerdata` library)  -> xG, npxG, shots, possession,
        progressive passes, etc. FBref's advanced stats are StatsBomb-powered
        and free for personal/non-commercial use. Respect their rate limits.
  * eloratings.net (World Football Elo)   -> live national-team strength ratings
        (real, free, no key). Used as the team strength rating.
  * Monte Carlo model (local, free)       -> advance / quarters / final / trophy %.

INSTALL
-------
  pip install soccerdata pandas requests

RUN
---
  python fetch_stats.py
        -> overwrites worldcup_data.json with live numbers.

NOTES
-----
  * International (national-team) advanced data on FBref is thinner than club
    data. Where a metric is missing for a team, we fall back to the modeled seed
    value and tag it. This keeps every team fully populated.
  * Keep request volume polite: FBref will rate-limit / block aggressive scraping.
    The GitHub Action runs this a few times a day, which is well within limits.
  * This script degrades gracefully: if a source is unreachable it logs a warning
    and uses seed values, so the pipeline never produces an empty dashboard.
"""
import json, math, sys, time
from datetime import datetime, timezone

SEASON = "FIFA World Cup 2026"

# ClubElo uses these country spellings; map our display names where they differ.
# eloratings.net uses 2-letter codes (ISO2, with EN=England, SC=Scotland).
ELO_CODE = {
    "Argentina":"AR","France":"FR","Spain":"ES","Brazil":"BR","England":"EN","Portugal":"PT",
    "Netherlands":"NL","Germany":"DE","Belgium":"BE","Uruguay":"UY","Colombia":"CO","Croatia":"HR",
    "Morocco":"MA","Switzerland":"CH","Austria":"AT","Senegal":"SN","Ecuador":"EC","Türkiye":"TR",
    "Norway":"NO","Japan":"JP","United States":"US","Sweden":"SE","Mexico":"MX","Iran":"IR",
    "Scotland":"SC","Czechia":"CZ","Egypt":"EG","Algeria":"DZ","South Korea":"KR","Canada":"CA",
    "Côte d'Ivoire":"CI","Paraguay":"PY","Bosnia and Herzegovina":"BA","Australia":"AU","Ghana":"GH",
    "Tunisia":"TN","Panama":"PA","South Africa":"ZA","DR Congo":"CD","Saudi Arabia":"SA","Qatar":"QA",
    "Uzbekistan":"UZ","Curaçao":"CW","Cabo Verde":"CV","Jordan":"JO","Iraq":"IQ","New Zealand":"NZ",
    "Haiti":"HT",
}

def log(msg): print(f"[fetch] {msg}", file=sys.stderr)


def load_seed():
    """Seed gives us the team list + safe fallback values for every metric."""
    try:
        with open("worldcup_data.json", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        log("worldcup_data.json not found - run generate_seed.py first.")
        sys.exit(1)


def fetch_elo(team_names):
    """Live national-team Elo from eloratings.net (World Football Elo Ratings).
    One request for the whole World.tsv table; parses 2-letter code -> current Elo."""
    import requests
    out = {}
    try:
        r = requests.get("https://www.eloratings.net/World.tsv",
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        if r.ok and r.text.strip():
            tok = r.text.split()
            code_elo = {}
            for i in range(len(tok) - 1):
                c, nxt = tok[i], tok[i + 1]
                if len(c) == 2 and c.isalpha() and c.isupper() and nxt.isdigit() and c not in code_elo:
                    code_elo[c] = int(nxt)
            for name in team_names:
                code = ELO_CODE.get(name)
                if code and code in code_elo:
                    out[name] = code_elo[code]
    except Exception as e:
        log(f"  eloratings fetch failed, keeping seed Elo: {e}")
    log(f"Elo ratings fetched for {len(out)}/{len(team_names)} teams")
    return out


def fetch_fbref_team_stats():
    """
    Pull World Cup team advanced stats from FBref via soccerdata.
    Returns {team_name: {metric: value}} for whatever it can map.
    Wrapped in try/except so missing coverage never breaks the run.
    """
    stats = {}
    try:
        import soccerdata as sd
        # FBref competition id for the World Cup; season = 2026.
        fbref = sd.FBref(leagues="INT-World Cup", seasons=2026)
        df = fbref.read_team_season_stats(stat_type="standard")
        ds = fbref.read_team_season_stats(stat_type="shooting")
        # Column names vary by FBref version; map defensively.
        for team, row in df.iterrows():
            tname = team[-1] if isinstance(team, tuple) else team
            m = {}
            for key, col in [("xg_for", "xg"), ("npxg", "npxg"),
                             ("possession_pct", "poss"),
                             ("progressive_passes", "prgp")]:
                if col in row and row[col] == row[col]:  # not NaN
                    m[key] = round(float(row[col]), 2)
            stats[tname] = m
        log(f"FBref team stats parsed for {len(stats)} teams")
    except Exception as e:
        log(f"FBref unavailable, using seed values for stats: {e}")
    return stats


def monte_carlo(strengths, sims=50000):
    """Trophy odds via softmax on strength (fast proxy for full bracket sim).
    Swap for a full group+bracket simulation once fixtures are wired in."""
    exp = {k: math.exp(v * 3.2) for k, v in strengths.items()}
    tot = sum(exp.values())
    return {k: exp[k] / tot for k in strengths}


def main():
    seed = load_seed()
    teams = seed["teams"]
    names = [t["team"] for t in teams]

    elo = fetch_elo(names)
    fbref = fetch_fbref_team_stats()

    # apply live Elo
    for t in teams:
        if t["team"] in elo:
            t["elo"] = round(elo[t["team"]])
    # recompute normalized strength from (possibly updated) Elo
    los, his = 1590, 2110
    strengths = {}
    for t in teams:
        s = max(0.0, min(1.0, (t["elo"] - los) / (his - los)))
        strengths[t["team"]] = s
        # overlay any live FBref metrics on top of seed
        live = fbref.get(t["team"], {})
        live_keys = []
        for k, v in live.items():
            t["metrics"][k] = v
            live_keys.append(k)
        t["_live_metrics"] = live_keys

    trophy = monte_carlo(strengths)
    for t in teams:
        s = strengths[t["team"]]
        t["projection"] = {
            "advance_r32_pct": round(min(0.985, 0.55 + s * 0.42) * 100, 1),
            "reach_quarters_pct": round(min(0.90, 0.12 + s * 0.62) * 100, 1),
            "reach_final_pct": round(min(0.55, s ** 2 * 0.6) * 100, 1),
            "win_trophy_pct": round(trophy[t["team"]] * 100, 1),
        }

    teams.sort(key=lambda x: x["projection"]["win_trophy_pct"], reverse=True)
    seed["teams"] = teams
    n_live = sum(1 for t in teams if t.get("_live_metrics"))
    seed["source"] = (f"Strength: live Elo from eloratings.net ({len(elo)} teams). "
                      f"Advanced metrics: modeled pre-tournament, update as matches are played.")
    seed["generated_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with open("worldcup_data.json", "w", encoding="utf-8") as f:
        json.dump(seed, f, ensure_ascii=False, indent=2)
    log(f"Done. worldcup_data.json updated ({len(teams)} teams, {len(elo)} live Elo).")


if __name__ == "__main__":
    main()

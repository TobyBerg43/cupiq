# CupIQ — World Cup 2026 Analytics (zero-cost build)

The most advanced World Cup analytics you can run for **$0/month**. This bundle is a
complete, working pipeline: free data sources → a fetch script → a JSON dataset →
a sortable dashboard and marketing landing page. No paid API required to start.

## What's in here

| File | What it is |
|------|-----------|
| `cupiq-landing.html` | Marketing landing page (hero, interactive demo, pricing, FAQ). Open in any browser. |
| `cupiq-dashboard.html` | The "Data Stadium": sortable leaderboard, match cards, filters, live insights feed for all 48 teams. |
| `worldcup_data.json` | The dataset — every advanced metric for every team. Generated, not hand-typed. |
| `generate_seed.py` | Creates the dataset with modeled seed values (works offline, instantly). |
| `fetch_stats.py` | Replaces seed values with **live free data** (FBref + ClubElo). |
| `.github/workflows/update-stats.yml` | Free auto-refresh on a schedule via GitHub Actions. |

## The honest part about the data

The numbers shipped today are **modeled seed values** so everything works the moment
you open it. They are realistic but not live. To make them real and precise:

1. `pip install soccerdata pandas requests`
2. `python fetch_stats.py`

That pulls **real** data from free sources and overwrites `worldcup_data.json`.

### Why these sources (all free)

- **FBref** — advanced team/player stats (xG, npxG, shots, possession, progressive
  passes). FBref's advanced data is **StatsBomb-powered**, i.e. the same quality pro
  clubs pay for, free for non-commercial use. Pulled via the `soccerdata` library.
- **ClubElo** — free Elo strength ratings (no API key) that feed the win/trophy model.
- **Monte Carlo model** (in `fetch_stats.py`) — computes advance / quarters / final /
  trophy probabilities locally. Free, and fully transparent.

> National-team advanced data is thinner than club data on free sources. Where a metric
> is missing, the pipeline keeps the modeled seed value so no team is ever blank. For
> full depth on all 48 nations, a paid tier (Sportmonks ~€78/mo live xG, or StatsBomb
> enterprise) is the upgrade path — but you don't need it to launch.

## Auto-updating (the "does it update fast?" answer)

Updates are done by a scheduled job, **not** by anything running on your machine 24/7.

- `update-stats.yml` runs on **GitHub Actions** (free minutes). Default cadence: every
  3 hours. On match days, change the cron to `*/15 * * * *` for ~15-minute freshness.
- Each run: fetches data → re-embeds it into the dashboard → commits. Your hosted site
  shows new numbers automatically.
- Want true sub-15-second live updates during a match? That requires a paid push/
  websocket feed (Sportmonks/LSports). The free path gets you near-live polling, which
  is plenty for a launch.

## Go live for free

1. Push this folder to a **GitHub** repo.
2. Turn on **GitHub Pages** (Settings → Pages → deploy from branch) — your dashboard and
   landing page are now hosted at a public URL, free.
3. The Action refreshes the data on schedule. Done — $0 hosting, $0 data.

(Alternative: drag the folder into **Vercel** or **Netlify** free tier for a custom domain.)

## Metrics included (every team)

Attacking: xG for, npxG, shots/90, shots on target, big chances, goals vs xG.
Defensive/press: xG against, PPDA, aerial win %. Build-up: possession %, progressive
passes, set-piece xG. Keeper: post-shot xG minus goals. Context: Elo, form (last 5),
momentum index. Model: advance %, reach quarters %, reach final %, trophy %.

## Design notes

Dark + cyan "Data Stadium" theme, transparent (every probability is explained), fully
emoji-free — all icons are inline SVG, team identity shown as ISO3 code chips.

---
CupIQ is an analytics product, not a gambling operator. Stats are for information and
entertainment. Bet responsibly and only where legal. Not affiliated with FIFA.

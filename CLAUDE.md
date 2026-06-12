# CLAUDE.md — CupIQ project context

This file orients any Claude Code session working in this folder. Read it first.

## What CupIQ is
A **World Cup 2026 analytics product** — advanced football stats, win/trophy probabilities,
and a simulation model for all 48 teams. Positioned deliberately as a **data/analytics product,
NOT a betting/gambling operator** (this keeps it ad-platform friendly and reduces chargebacks).
Probabilities are always framed as model estimates, never guarantees. Tournament runs
**June 11 – July 19, 2026** (48 teams; hosts USA/Canada/Mexico).

Live at **https://cupiq.app**. Owner: Toby (GitHub: TobyBerg43).

## Tech stack (deliberately simple — keep it that way unless asked)
- **Pure static site**: hand-written HTML + CSS + vanilla JS. **No build step, no framework.**
- **Host**: Cloudflare Pages, connected to the GitHub repo `TobyBerg43/cupiq` (branch `main`).
  Every push to `main` auto-deploys. Build command empty, output dir `/` (root).
- **Domain**: cupiq.app (registered + DNS on Cloudflare; custom domain attached to the Pages project).
- **Data refresh**: GitHub Actions (free). No server/backend.
- **Payments**: Stripe Payment Links (no backend, no API keys in the site).

## Files
| File | Role |
|------|------|
| `index.html` | Landing page. Hero (soccer "data-ball" SVG), ticker, features, interactive demo, pricing, FAQ. **`STRIPE_LINKS` config object near the top of `<script>`** holds the checkout URLs; a small loop sets button hrefs from it. "Free" buttons point to `dashboard.html`. |
| `dashboard.html` | **FREE teaser**. Shows only win/trophy % + advance %, standings, match cards, feed. Advanced metrics are intentionally removed; an upsell banner links to `index.html#pricing`. |
| `pro-k9x3f7q2a8.html` | **PRO full dashboard** (all 15 advanced metrics, sortable, etc.). `noindex`. **Secret URL** — Stripe redirects buyers here after payment. Do NOT link to it publicly or add it to the sitemap. |
| `worldcup_data.json` | The dataset: 48 teams, 15 metrics each + projections. Auto-refreshed by the workflow. Dashboards `fetch()` it at runtime and fall back to an embedded `SEED` const if offline. |
| `generate_seed.py` | Builds the dataset from modeled seed values (deterministic, offline). |
| `fetch_stats.py` | Overwrites the dataset with **live free data**: FBref (via `soccerdata`) + ClubElo + a local Monte Carlo model. Degrades to seed values if a source is down, so it never produces an empty file. |
| `.github/workflows/update-stats.yml` | Runs `generate_seed.py` then `fetch_stats.py` and commits `worldcup_data.json`. Cron `0 */3 * * *` (every 3h) + manual `workflow_dispatch`. Repo Actions permission is set to **read & write** (required). |
| `favicon.svg`, `robots.txt`, `sitemap.xml`, `README.md`, `DEPLOY.md` | Branding, SEO, docs. |

## Design system
- Dark + cyan "Data Stadium" theme. CSS variables defined in `:root` (`--accent` #22e0a1,
  `--accent-2` #3b82f6, `--accent-3` #f7b500, dark `--bg` #070b14, etc.).
- **Emoji-free**: all icons are inline SVG. Teams shown as ISO3 code chips (e.g. ARG, FRA),
  not flag emoji.
- Probability color coding: green = strong, amber = mid, red = low. Trophy % uses a separate
  (lower) threshold scale than advance % because trophy odds are small in absolute terms.

## Pricing & payments (current, live)
- **Free (Fan)**: opens `dashboard.html`.
- **Analyst — $19/mo** recurring. **No free trial** (decided: the free tier is the trial; a 7-day
  trial would give away ~18% of a 39-day event).
- **Tournament Pass — $29 one-time** (primary offer; lowest chargeback risk; covers full event).
- Both Stripe links set an **"After payment → redirect"** to the secret Pro URL above.
- Stripe statement descriptor: `CUPIQ`.

## Important constraints / decisions
- Gating is **"soft"**: paid customers get the secret Pro URL via Stripe redirect. The URL is
  shareable (not true auth). Acceptable for a one-month event; the real-accounts upgrade is the
  future option if it scales.
- Keep the analytics framing — avoid "guaranteed picks / beat the bookies / value bet" language.
- Stripe dashboard and `buy.stripe.com` checkout are not automatable here; payment setup is manual.

## Open / next ideas (not yet built)
- Real authentication + paywall to replace the soft secret-URL gating.
- A bracket / knockout simulator page.
- Per-team and per-match SEO content pages (this is how you rank for "world cup stats").
- "Beat the model" prediction game (engagement hook).
- Subscriber emails (daily Pro briefing) — Twilio/SendGrid.
- On match days, change the workflow cron to `*/15 * * * *` for ~15-min freshness.

## How to work here
- To change the live site, edit the HTML directly and commit/push to `main` (Cloudflare redeploys).
- `dashboard.html` and `pro-k9x3f7q2a8.html` share most code; if you change shared UI, update both.
- Test JS with `node --check` after edits (these files have been truncated by naive large edits
  before — verify the file still ends with `</html>` after any scripted edit).
- Don't reintroduce emoji or betting-tip language.

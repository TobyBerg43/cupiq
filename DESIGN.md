# Design

CupIQ visual system — **"Data Desk"**: a precise, dark, information-dense analytics surface. Restraint and hairline structure carry the premium feel; color carries data meaning only. Replaces the earlier gradient/glass build.

## Theme

Dark, single theme. Physical scene: a professional football-analytics desk at night — a calm dark room, one screen of precise numbers, accent light only where it means something. Not a tipster's neon board, not a glassy SaaS hero.

## Color (OKLCH-reasoned, shipped as hex)

| Token | Value | Use |
|---|---|---|
| `--canvas` | `#06090f` | page background |
| `--surface` | `#0b1018` | panels, cards, table |
| `--surface-2` | `#0f1724` | elevated, row hover, inputs |
| `--hair` | `rgba(255,255,255,.09)` | hairline borders (primary structure device) |
| `--hair-2` | `rgba(255,255,255,.15)` | stronger dividers, focus |
| `--ink` | `#f3f6fb` | primary text |
| `--ink-2` | `#aeb9cc` | secondary text (≥4.5:1 on canvas) |
| `--ink-3` | `#7b8799` | labels, large/secondary only |
| `--accent` | `#18d68f` | THE brand/primary: actions, selection, "good" tier |
| `--good` `--mid` `--low` `--info` | `#18d68f` `#f5b32b` `#fb5a68` `#5b9dff` | data tiers / semantic only |

Strategy: **Committed-restrained.** One accent (emerald) does the brand + primary work; amber/red/blue are *data* colors, never decoration. No violet, no gradient text, no decorative glass.

## Typography

- **Inter** — UI, body, data (variable weights 400–800). **JetBrains Mono** — values, metric labels, codes, methodology numbers. Two families, contrast on a geometric-sans vs mono axis. Both already loaded.
- Brand headlines (landing): `clamp()` max **≤ 64px**, weight 800, `letter-spacing: -0.025em`, `text-wrap: balance`.
- Product headings (dashboards): fixed rem (20 / 16 / 14px), weight 700. Tighter 1.2 scale.
- Everywhere: `font-variant-numeric: tabular-nums`. Body line-length 65–75ch.
- Section context uses a small mono label as a deliberate "data desk" system — used sparingly, not above every heading.

## Radii / elevation / motion

- Radii: card **12px**, control 9px, chip 6px, pill 999px. Never ≥18px on cards.
- Structure via **hairline borders**, not shadow. Shadow only on floating layers (drawer, dropdown), ≤10px blur, never paired with a decorative border on the same element.
- Motion: 150–220ms `cubic-bezier(.2,.7,.2,1)` (ease-out). Conveys state. One tasteful landing entrance. Full `prefers-reduced-motion` fallbacks.

## Components

Precise data table (sticky header, hairline rows, hover), probability pill (value + tier color + always a number), metric bar, stat cell (solid, no gradient), SVG charts (xG scatter, trophy tiers, Elo distribution), team-detail drawer, methodology cards, tournament group/venue grid, country flag chips (local `flags/`).

## Content depth (this redesign adds)

Tournament structure (48 teams · 12 groups · 16 host cities · 104 matches · Jun 11–Jul 19 2026), model methodology (inputs → 50k Monte Carlo → calibration → sources → refresh), per-team detail (full 15-metric breakdown + strengths/weaknesses + projection path), data visualizations from the live dataset.

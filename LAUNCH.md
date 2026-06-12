# CupIQ — launch runbook

Everything you need to take CupIQ from "looks done" to "safely taking money."
Work top to bottom. Items marked **[you]** need your accounts/decisions; the rest is already in the code.

---

## 0. What's already built

- **Pro access gate** — `functions/_middleware.js` blocks `pro-k9x3f7q2a8.html` unless a valid, signed access cookie is present, set by `functions/api/unlock.js`. Buyers land on `unlock.html`, which auto-verifies their Stripe payment (or accepts a license key).
- **License keys** — `tools/gen-keys.mjs` mints keys that the gate validates with one shared secret (no database).
- **Email capture** — the landing's "Daily briefing" form posts to `functions/api/subscribe.js`, which stores emails in a `EMAILS` KV namespace.
- **Analytics** — a Cloudflare Web Analytics beacon is on every page (token placeholder).
- **Legal** — `terms.html`, `privacy.html`, `responsible-use.html`, footer links + contact.
- **Honest framing** — "live" wording was changed to "modeled" because, pre-tournament, the numbers are modeled (see §6).

---

## 1. Deploy on Cloudflare Pages **[you]**

Use **Git + Cloudflare Pages** (not drag-and-drop) — Pages Functions only run on a Git/Wrangler deploy, and they are what protect Pro.

1. Push this whole folder to your GitHub repo (it must include `functions/`, `flags/`, `tools/`, and the new `.html` files).
2. Cloudflare → Workers & Pages → Create → Pages → connect the repo.
   - Framework preset: **None**. Build command: empty. Output dir: `/`.
3. Add the custom domain `cupiq.app`.

> Drag-and-drop deploys do **not** run Functions, so Pro would be ungated. Don't ship that way.

---

## 2. Set secrets & bindings **[you]**

Cloudflare Pages → your project → **Settings → Environment variables / Bindings** (set for **Production**, and Preview if you use it):

| Name | Type | Value |
|------|------|-------|
| `LICENSE_SECRET` | Secret (env var) | a long random string (e.g. `openssl rand -hex 32`). Signs cookies **and** license keys. |
| `STRIPE_SECRET_KEY` | Secret (env var) | your Stripe **live** secret key (`sk_live_...`). Lets `unlock.html` confirm a purchase automatically. |
| `EMAILS` | KV namespace binding | create a KV namespace, bind it as `EMAILS`. Holds captured emails. |
| `REVOKED` | KV namespace binding (optional) | bind a KV namespace as `REVOKED` if you want to revoke individual license keys. |
| `STRIPE_WEBHOOK_SECRET` | Secret (env var) | `whsec_...` from the Stripe webhook (step 3); lets `/api/stripe-webhook` verify events. |
| `ORDERS` | KV namespace binding (optional) | records each completed purchase from the webhook. |
| `RESEND_API_KEY` + `EMAIL_FROM` | Secret + var (optional) | a [Resend](https://resend.com) key + a verified `From` (e.g. `CupIQ <hello@cupiq.app>`) to send the welcome + receipt emails. |

After changing variables, redeploy so Functions pick them up.

---

## 3. Wire Stripe **[you]**

1. Confirm you're in **live mode** with a verified business (Stripe KYC done).
2. For **both** Payment Links (Analyst $19/mo and Tournament Pass $29), set the post-payment **redirect** to:
   `https://cupiq.app/unlock.html?session_id={CHECKOUT_SESSION_ID}`
   Stripe substitutes the real session id; `unlock.html` posts it to `/api/unlock`, which checks `payment_status` against Stripe and sets the access cookie. No key copying needed.
3. Add a **webhook**: Stripe → Developers → Webhooks → endpoint `https://cupiq.app/api/stripe-webhook`, event `checkout.session.completed`. Copy the signing secret into `STRIPE_WEBHOOK_SECRET`. This records orders (in `ORDERS` KV) and emails a receipt.
4. Enable the **Customer Portal** (Settings → Billing) so subscribers can cancel/update cards themselves.
4. Turn on **Stripe Tax** if you owe VAT/sales tax. Confirm statement descriptor is `CUPIQ`.
5. The `STRIPE_LINKS` object near the top of `index.html`'s script already holds your two `buy.stripe.com` URLs — no change needed unless they rotate.

### License keys (fallback / comps)
The Stripe redirect is the main path. Keys are for manual grants, support, or affiliates:
```
LICENSE_SECRET="<same secret as Cloudflare>" node tools/gen-keys.mjs 50 > keys.txt
```
Hand a key to a buyer; they paste it on `unlock.html`. Revoke one by putting its **middle segment** (the `XXXXXXXXXX` id) into the `REVOKED` KV namespace. Rotating `LICENSE_SECRET` invalidates **all** keys and cookies at once.

---

## 4. Analytics — GA4 + Meta Pixel **[you]**

A cookie-consent banner is on every page; **GA4 and the Meta Pixel only load after a visitor clicks Accept** (GDPR-friendly, matches the privacy policy). To turn them on, set your IDs in the consent `<script>` block near the bottom of **every** HTML page (search for `var GA_ID`):
- `GA_ID` → your GA4 Measurement ID (`G-XXXXXXXXXX`)
- `META_PIXEL_ID` → your Meta Pixel ID (numeric)

Buy-button clicks already fire `InitiateCheckout` (Meta) and `begin_checkout` (GA4) so you can optimise ads to purchases. Leaving an ID as its placeholder keeps that tool off. A quick way to set both across all pages at once is a find-and-replace in your editor.

---

## 5. Email list **[you]**

Emails land in the `EMAILS` KV namespace as `sub:<email>`. To actually send the daily briefing you still need a sender (Cloudflare doesn't send email). Options when you're ready: a scheduled Worker + an email API (Resend, SendGrid, MailChannels), or export the KV list into a tool like Buttondown. For launch, capturing the list is the priority; sending can follow.

---

## 6. Data: make "live" actually true (or keep it honest) **[you + me]**

Right now `worldcup_data.json` is **modeled seed data**, and the site says "modeled" accordingly. Be careful before switching that wording back to "live":

- **The tournament hasn't started.** Until matches are played there is no real WC-2026 xG/possession data on FBref, so advanced metrics are modeled by definition.
- **Strength (Elo) is live and real.** `fetch_stats.py` now pulls national-team ratings from eloratings.net (World Football Elo); the shipped dataset already has real Elo for all 48 teams. Advanced metrics (xG etc.) stay modeled until matches are played — there is no free pre-tournament source for them.
- **The model is a proxy.** `monte_carlo()` is a softmax over strength, not a full group+bracket simulation. For credible projections, that should be upgraded (the code notes it).

**Real-time reality:** free sources (eloratings, FBref) refresh *after* matches, on a delay — not live/in-game. True in-match real-time data needs a paid feed (Sportmonks, Opta, or StatsBomb). If you want live in-match stats, get one of those keys and wire it into `fetch_stats.py`; otherwise the honest framing is "refreshed every few hours," which the site now says.

To refresh data:
```
pip install soccerdata pandas requests
python generate_seed.py    # rebuilds the team list + safe fallbacks
python fetch_stats.py      # overlays live ClubElo/FBref where available
```
The included GitHub Action (`.github/workflows/update-stats.yml`) runs this every ~3h and commits the result; Cloudflare redeploys. Only restore "live/calibrated" wording once the numbers are genuinely observed and the model is upgraded.

---

## 7. Legal **[you]**

- Fill every highlighted `[bracket]` in `terms.html` and `privacy.html` (legal entity, jurisdiction, currency, analytics provider).
- Have a lawyer in your jurisdiction review all three legal pages before launch.
- Create the `support@cupiq.app` inbox (or forward it somewhere you read).

---

## Pre-launch checklist

- [ ] Git-deployed to Cloudflare Pages with `functions/` present
- [ ] `LICENSE_SECRET` + `STRIPE_SECRET_KEY` set; `EMAILS` KV bound
- [ ] Bought, paid, redirected to `unlock.html`, landed in Pro — end-to-end test
- [ ] Tried opening `pro-k9x3f7q2a8.html` directly in a fresh browser → redirected to `unlock.html`
- [ ] Stripe live mode, Customer Portal on, tax handled, descriptor `CUPIQ`
- [ ] Analytics token set (or dashboard analytics enabled)
- [ ] Email form returns success on the live site
- [ ] Legal `[brackets]` filled, reviewed; `support@` inbox live
- [ ] Decided "modeled" vs "live" wording matches reality

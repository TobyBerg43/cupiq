# Going live with CupIQ on cupiq.app (free)

Your domain `cupiq.app` is on Cloudflare, so the fastest free host is **Cloudflare Pages**.
This guide gets you a live site at https://cupiq.app today.

## Files that get deployed

These are the production files (everything else in the folder is source/tooling):

- `index.html` — home / landing page
- `dashboard.html` — the live stats "Data Stadium"
- `worldcup_data.json` — the data the dashboard reads
- `favicon.svg`, `robots.txt`, `sitemap.xml` — SEO + branding

## Option A — Cloudflare Pages via drag-and-drop (fastest, 5 min)

1. Go to **dash.cloudflare.com → Workers & Pages → Create → Pages → Upload assets**.
2. Drag in these files: `index.html`, `dashboard.html`, `worldcup_data.json`, `favicon.svg`, `robots.txt`, `sitemap.xml`.
3. Name the project `cupiq` and deploy. You'll get a `*.pages.dev` URL immediately.
4. **Custom domain:** in the project → **Custom domains → Set up a domain → `cupiq.app`**. Because the domain is already in your Cloudflare account, it wires up automatically (SSL included).

Downside: drag-and-drop is manual. The auto-updating data won't refresh on its own with this method — re-upload `worldcup_data.json` when you want fresh numbers, or use Option B.

## Option B — GitHub + Cloudflare Pages (auto-updating, recommended)

This gives you free hosting **and** the free auto-refresh of stats.

1. Push this whole folder to a new **GitHub** repo.
2. In Cloudflare Pages → **Create → Connect to Git →** pick the repo. Build settings: **framework = None**, build command = empty, output directory = `/` (root). Deploy.
3. Add the custom domain `cupiq.app` (same as step 4 above).
4. The included `.github/workflows/update-stats.yml` runs on schedule, refreshes `worldcup_data.json`, and commits it — Cloudflare Pages then auto-redeploys. Live data, $0.

## Finish Stripe (so the buttons charge)

1. Create the two Payment Links in Stripe (see chat for exact steps): **CupIQ Analyst $19/mo** and **CupIQ Tournament Pass $49 one-time**.
2. Open `index.html`, find the `STRIPE_LINKS` block near the top of the `<script>`, and paste the two `https://buy.stripe.com/...` URLs into `analyst` and `pass`.
3. Re-deploy (re-upload the file, or commit if using Option B).
4. In Stripe → **Settings → Public details**, set the statement descriptor to `CUPIQ` (reduces chargebacks).

## After launch — SEO checklist

- **Google Search Console** (free): add `cupiq.app`, verify, and submit `sitemap.xml`.
- This is where you win "world cup stats" searches — through page titles and content, not the domain.
  Good title tags are already set; add per-team or per-match content pages over time.
- **Bing Webmaster Tools** (free) — same idea, submit the sitemap.
- Share the link on social (Reddit r/soccer, Twitter/X) for initial backlinks and traffic.

## Quick local check

Open `index.html` in any browser to preview the home page; click **Live Stats** to confirm
it loads `dashboard.html`. Both work offline; the dashboard shows seed data until the live
fetch runs (Option B) or you replace `worldcup_data.json`.

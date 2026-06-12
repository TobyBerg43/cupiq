# CupIQ — Go-live for advertising & subscriptions

Status after this pass: legal pages finalized (no more placeholders/draft notes),
recurring-billing disclosure added at checkout. Three things still need YOU, below.

---

## 1. Analytics + ad tracking (Meta Pixel + GA4) — paste-ready

You need two IDs first:
- **Meta Pixel ID**: business.facebook.com → Events Manager → create a Pixel/dataset → copy the ID (a long number).
- **GA4 Measurement ID**: analytics.google.com → Admin → Data Streams → Web → copy `G-XXXXXXXXXX`.

Then paste this block **right before `</body>`** on every page (`index.html`, `dashboard.html`,
`pro-k9x3f7q2a8.html`, `unlock.html`). It includes a cookie-consent banner that only loads the
trackers after the visitor accepts (required for EU/UK). Replace the two IDs at the top.

```html
<!-- CupIQ analytics + consent -->
<div id="cc" style="display:none;position:fixed;left:16px;right:16px;bottom:16px;max-width:560px;margin:0 auto;z-index:9999;background:#0f1724;border:1px solid rgba(255,255,255,.15);border-radius:12px;padding:16px 18px;font:14px/1.5 Inter,system-ui,sans-serif;color:#aeb9cc;box-shadow:0 10px 40px rgba(0,0,0,.5)">
  We use cookies for analytics and to measure ad performance. See our <a href="privacy.html" style="color:#18d68f">Privacy Policy</a>.
  <div style="margin-top:12px;display:flex;gap:10px">
    <button id="ccA" style="flex:1;background:#18d68f;color:#04130d;border:none;border-radius:8px;padding:9px;font-weight:600;cursor:pointer">Accept</button>
    <button id="ccD" style="flex:1;background:transparent;color:#aeb9cc;border:1px solid rgba(255,255,255,.15);border-radius:8px;padding:9px;cursor:pointer">Decline</button>
  </div>
</div>
<script>
(function(){
  var META_PIXEL_ID = "YOUR_PIXEL_ID";    // <-- replace
  var GA4_ID        = "G-XXXXXXXXXX";      // <-- replace
  function loadTrackers(){
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};
      if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
      t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq('init',META_PIXEL_ID);fbq('track','PageView');
    var g=document.createElement('script');g.async=true;g.src='https://www.googletagmanager.com/gtag/js?id='+GA4_ID;document.head.appendChild(g);
    window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};gtag('js',new Date());gtag('config',GA4_ID);
  }
  var c=localStorage.getItem('cupiq_consent');
  if(c==='yes'){loadTrackers();}
  else if(c!=='no'){var el=document.getElementById('cc');if(el)el.style.display='block';}
  var a=document.getElementById('ccA'),d=document.getElementById('ccD');
  if(a)a.onclick=function(){localStorage.setItem('cupiq_consent','yes');document.getElementById('cc').style.display='none';loadTrackers();};
  if(d)d.onclick=function(){localStorage.setItem('cupiq_consent','no');document.getElementById('cc').style.display='none';};
})();
</script>
```

**Track purchases (important for ad optimization):** on the page buyers land on *after* paying
(`pro-k9x3f7q2a8.html`, or `unlock.html` on success), add this once consent is granted:
```html
<script>if(window.fbq)fbq('track','Purchase',{value:29.00,currency:'USD'});
if(window.gtag)gtag('event','purchase',{value:29.00,currency:'USD'});</script>
```
That tells Meta/Google which clicks became sales, so the ad algorithms optimize toward buyers.

> Tip: I (Claude) can paste these in for you once you give me the Pixel ID and GA4 ID.

---

## 2. Make support@cupiq.app actually receive mail (free, Cloudflare Email Routing)

1. dash.cloudflare.com → select **cupiq.app** → left menu **Email → Email Routing**.
2. Click **Get started / Enable**. Cloudflare auto-adds the needed MX/TXT records.
3. Under **Routing rules → Custom addresses**, add **support@cupiq.app** → forward to your real
   inbox (e.g. your Gmail).
4. Cloudflare emails that inbox a **verification link** — click it. Done; mail to support@cupiq.app
   now lands in your inbox.

Without this, the contact link on every page and in your legal pages goes nowhere — which fails
ad review and loses customers.

---

## 3. Easy cancellation (FTC "click to cancel" + fewer chargebacks)

Turn on Stripe's self-serve cancellation so subscribers can cancel without emailing you:
- Stripe Dashboard → **Settings → Billing → Customer portal** → enable, allow "cancel subscription",
  save. Then put the portal link in your purchase receipt / confirmation email.
This satisfies the US rule that cancelling must be as easy as subscribing.

---

## 4. One legal field only you can set

In `terms.html` section 9 (Governing law) I put **"the United States"**. For a US sole proprietor
you should change this to your **home state** (e.g. "the State of Texas"). Quick find-and-replace.

> Reminder: these legal pages are solid plain-English drafts, but they are not lawyer-reviewed.
> For a paid product it's worth a quick review by a lawyer in your state.

---

## 5. Deploy

All the above are edits to the files in this folder. To make them live, **push/upload the changed
files to the `TobyBerg43/cupiq` GitHub repo** — Cloudflare Pages redeploys automatically.
Changed in this pass: `terms.html`, `privacy.html`, `index.html`.

## Optional polish
- Add an `og:image` (a 1200×630 share image) so links show a preview card on social/ads.
- Submit `sitemap.xml` in Google Search Console.

// POST /api/subscribe  — captures an email into the EMAILS KV namespace and
// (if configured) sends a welcome email via Resend.
// Body: { email, ref? }.  Returns { ok: true } on success.
//
// Optional KV binding:  EMAILS  (if absent, the endpoint still returns ok)
// Optional env:         RESEND_API_KEY, EMAIL_FROM  (to send the welcome email)

function json(obj, status) {
  return new Response(JSON.stringify(obj), {
    status: status || 200,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
  });
}

async function sendEmail(env, to, subject, html) {
  if (!env.RESEND_API_KEY || !to) return;
  try {
    await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: "Bearer " + env.RESEND_API_KEY, "Content-Type": "application/json" },
      body: JSON.stringify({ from: env.EMAIL_FROM || "CupIQ <hello@cupiq.app>", to: to, subject: subject, html: html }),
    });
  } catch (e) {}
}

export async function onRequestPost(context) {
  const { request, env } = context;
  let body = {};
  try { body = await request.json(); } catch (e) {}

  const email = String(body.email || "").trim().toLowerCase();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || email.length > 254) {
    return json({ ok: false, error: "invalid_email" }, 400);
  }

  let isNew = true;
  if (env.EMAILS) {
    try {
      const existing = await env.EMAILS.get("sub:" + email);
      isNew = !existing;
      await env.EMAILS.put(
        "sub:" + email,
        JSON.stringify({ email: email, ref: String(body.ref || "").slice(0, 80), t: Date.now() })
      );
    } catch (e) {
      return json({ ok: false, error: "store_failed" }, 500);
    }
  }

  if (isNew) {
    await sendEmail(env, email,
      "You're on the CupIQ briefing list",
      "<p>Thanks for signing up. Once the World Cup kicks off you'll get a short daily stat briefing: " +
      "the biggest movers, who's beating their xG, and the matchups worth a look.</p>" +
      "<p>Explore the live data anytime: <a href=\"https://cupiq.app/dashboard.html\">cupiq.app/dashboard.html</a></p>" +
      "<p>— CupIQ. Reply to unsubscribe.</p>");
  }

  return json({ ok: true });
}

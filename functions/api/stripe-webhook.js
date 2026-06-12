// POST /api/stripe-webhook  — Stripe sends purchase events here.
// Verifies the signature, records the order in the ORDERS KV namespace, and
// (if configured) emails the buyer a receipt. This is belt-and-suspenders on top
// of the redirect-based unlock; it gives you a durable record of who paid.
//
// Stripe dashboard: Developers → Webhooks → add endpoint
//   https://cupiq.app/api/stripe-webhook   event: checkout.session.completed
//
// Required env:  STRIPE_WEBHOOK_SECRET  (whsec_...)
// Optional env:  RESEND_API_KEY, EMAIL_FROM   (to send the receipt)
// Optional KV:   ORDERS                        (to record orders)

const enc = new TextEncoder();

function hex(buf) {
  const b = new Uint8Array(buf);
  let s = "";
  for (let i = 0; i < b.length; i++) s += b[i].toString(16).padStart(2, "0");
  return s;
}
async function hmacHex(secret, msg) {
  const k = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return hex(await crypto.subtle.sign("HMAC", k, enc.encode(msg)));
}
function eq(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
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
  const secret = env.STRIPE_WEBHOOK_SECRET;
  const body = await request.text();
  const sigHeader = request.headers.get("Stripe-Signature") || "";

  // Verify the Stripe signature (t=timestamp,v1=signature over `${t}.${body}`)
  if (secret) {
    const parts = {};
    sigHeader.split(",").forEach(function (p) { const i = p.indexOf("="); if (i > -1) parts[p.slice(0, i)] = p.slice(i + 1); });
    if (!parts.t || !parts.v1) return new Response("bad signature", { status: 400 });
    const expected = await hmacHex(secret, parts.t + "." + body);
    if (!eq(expected, parts.v1)) return new Response("invalid signature", { status: 400 });
    // basic replay guard: reject events older than 5 minutes
    if (Math.abs(Date.now() / 1000 - Number(parts.t)) > 300) return new Response("stale", { status: 400 });
  }

  let event = {};
  try { event = JSON.parse(body); } catch (e) { return new Response("bad json", { status: 400 }); }

  if (event.type === "checkout.session.completed") {
    const s = event.data && event.data.object ? event.data.object : {};
    const email = (s.customer_details && s.customer_details.email) || s.customer_email || "";
    const record = {
      session: s.id, email: email, amount_total: s.amount_total, currency: s.currency,
      mode: s.mode, payment_status: s.payment_status, t: Date.now(),
    };
    if (env.ORDERS && s.id) {
      try { await env.ORDERS.put("order:" + s.id, JSON.stringify(record)); } catch (e) {}
    }
    if (email) {
      await sendEmail(env, email,
        "Your CupIQ access is live",
        "<p>Thanks for your purchase. Your CupIQ Pro access is active.</p>" +
        "<p>Open the full dashboard here: <a href=\"https://cupiq.app/unlock.html\">cupiq.app/unlock.html</a> " +
        "(if you weren't redirected automatically after checkout).</p>" +
        "<p>Questions? Just reply to this email or contact support@cupiq.app.</p><p>— CupIQ</p>");
    }
  }

  return new Response(JSON.stringify({ received: true }), { status: 200, headers: { "Content-Type": "application/json" } });
}

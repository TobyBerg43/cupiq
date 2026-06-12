// POST /api/unlock  — grants Pro access.
// Body: { sessionId } (from Stripe success redirect) OR { key } (a CUPIQ-... license key).
// On success sets an HttpOnly, signed access cookie and returns { ok: true }.
//
// Required Pages env vars:
//   LICENSE_SECRET     – long random string; signs cookies and license keys
//   STRIPE_SECRET_KEY  – (optional) enables verifying a Stripe checkout session
// Optional KV binding:
//   REVOKED            – KV namespace; put a key id to revoke that license

const COOKIE = "cupiq_access";
// Access is valid through the end of the 2026 tournament (Jul 20 UTC, day after the final).
const ACCESS_EXP = Math.floor(Date.UTC(2026, 6, 20) / 1000);

const enc = new TextEncoder();

function b64url(bytes) {
  let s = btoa(String.fromCharCode.apply(null, Array.from(bytes)));
  return s.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
async function hmac(secret, msg) {
  const k = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", k, enc.encode(msg));
  return b64url(new Uint8Array(sig));
}
function eq(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}
async function makeToken(secret, exp) {
  return exp + "." + (await hmac(secret, "access:" + exp));
}
async function verifyLicense(secret, key, env) {
  const m = /^CUPIQ-([0-9A-Z]{6,})-([0-9A-Za-z_-]{8,})$/.exec((key || "").trim());
  if (!m) return false;
  const id = m[1], sig = m[2];
  const expect = (await hmac(secret, "key:" + id)).slice(0, sig.length);
  if (!eq(sig, expect)) return false;
  if (env.REVOKED) {
    try { if (await env.REVOKED.get(id)) return false; } catch (e) {}
  }
  return true;
}
function json(obj, status, extra) {
  return new Response(JSON.stringify(obj), {
    status: status || 200,
    headers: Object.assign({ "Content-Type": "application/json", "Cache-Control": "no-store" }, extra || {}),
  });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const secret = env.LICENSE_SECRET;
  if (!secret) return json({ ok: false, error: "server_not_configured" }, 500);

  let body = {};
  try { body = await request.json(); } catch (e) {}

  let granted = false;

  if (body.sessionId && env.STRIPE_SECRET_KEY) {
    try {
      const r = await fetch(
        "https://api.stripe.com/v1/checkout/sessions/" + encodeURIComponent(body.sessionId),
        { headers: { Authorization: "Bearer " + env.STRIPE_SECRET_KEY } }
      );
      if (r.ok) {
        const s = await r.json();
        if (s && (s.payment_status === "paid" || s.status === "complete")) granted = true;
      }
    } catch (e) {}
  } else if (body.key) {
    granted = await verifyLicense(secret, body.key, env);
  }

  if (!granted) return json({ ok: false, error: "not_verified" }, 403);

  const token = await makeToken(secret, ACCESS_EXP);
  const maxAge = Math.max(0, ACCESS_EXP - Math.floor(Date.now() / 1000));
  const cookie = COOKIE + "=" + token + "; Path=/; Max-Age=" + maxAge + "; HttpOnly; Secure; SameSite=Lax";
  return json({ ok: true }, 200, { "Set-Cookie": cookie });
}

// Optional: clear access (logout)
export async function onRequestDelete() {
  return json({ ok: true }, 200, { "Set-Cookie": COOKIE + "=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax" });
}

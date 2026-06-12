// Gates the Pro dashboard behind a valid access cookie set by /api/unlock.
// Only intercepts the Pro path; everything else passes through untouched.
// On Cloudflare Pages this runs at the edge. (Locally, with a plain static
// server, Functions don't run, so the page stays open for development.)

const COOKIE = "cupiq_access";
const PRO_PATH = "/pro-k9x3f7q2a8.html";
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
async function verifyToken(secret, token) {
  if (!secret || !token) return false;
  const dot = token.lastIndexOf(".");
  if (dot < 1) return false;
  const exp = token.slice(0, dot), sig = token.slice(dot + 1);
  if (!/^\d+$/.test(exp)) return false;
  if (Number(exp) < Math.floor(Date.now() / 1000)) return false;
  const expect = await hmac(secret, "access:" + exp);
  return eq(sig, expect);
}
function parseCookie(header) {
  const out = {};
  (header || "").split(";").forEach(function (p) {
    const i = p.indexOf("=");
    if (i > -1) out[p.slice(0, i).trim()] = p.slice(i + 1).trim();
  });
  return out;
}

export async function onRequest(context) {
  const { request, next, env } = context;
  const url = new URL(request.url);

  if (url.pathname === PRO_PATH) {
    const token = parseCookie(request.headers.get("Cookie"))[COOKIE];
    const ok = await verifyToken(env.LICENSE_SECRET, token);
    if (!ok) {
      const to = new URL("/unlock.html", url.origin);
      return Response.redirect(to.toString(), 302);
    }
  }
  return next();
}

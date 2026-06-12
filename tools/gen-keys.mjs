// Generate CupIQ Pro license keys.
//
//   LICENSE_SECRET="your-long-random-secret" node tools/gen-keys.mjs 50 > keys.txt
//   (or)  node tools/gen-keys.mjs <secret> <count>
//
// Each key validates against functions/api/unlock.js with the SAME secret.
// Keep keys.txt private. Hand one key to each buyer (e.g. via your Stripe
// post-purchase email/receipt). Revoke a key by putting its middle id into
// the REVOKED KV namespace.

import crypto from "node:crypto";

const secret = process.env.LICENSE_SECRET || process.argv[2];
const count = Number(process.env.LICENSE_SECRET ? process.argv[2] : process.argv[3]) || 20;

if (!secret || secret.length < 16) {
  console.error("Set LICENSE_SECRET (>=16 chars). Usage: LICENSE_SECRET=... node tools/gen-keys.mjs [count]");
  process.exit(1);
}

function keyFor(id) {
  const sig = crypto.createHmac("sha256", secret).update("key:" + id).digest("base64url").slice(0, 12);
  return `CUPIQ-${id}-${sig}`;
}

for (let i = 0; i < count; i++) {
  const id = crypto.randomBytes(5).toString("hex").toUpperCase(); // 10 hex chars, matches [0-9A-Z]{6,}
  console.log(keyFor(id));
}

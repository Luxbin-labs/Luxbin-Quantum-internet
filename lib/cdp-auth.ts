import { SignJWT, importPKCS8 } from "jose";
import crypto from "crypto";

export const ONRAMP_API_BASE_URL = "https://api.developer.coinbase.com/onramp";

export function getCDPCredentials() {
  const keyId = process.env.CDP_API_KEY_ID;
  const keySecret = process.env.CDP_API_KEY_SECRET;

  if (!keyId || !keySecret) {
    throw new Error("CDP API credentials not configured");
  }

  return { keyId, keySecret };
}

function buildPem(secret: string): string {
  const lines = ["-----BEGIN EC PRIVATE KEY-----"];
  for (let i = 0; i < secret.length; i += 64) {
    lines.push(secret.slice(i, i + 64));
  }
  lines.push("-----END EC PRIVATE KEY-----");
  return lines.join("\n");
}

export async function generateCDPJWT({
  requestMethod,
  requestHost,
  requestPath,
}: {
  requestMethod: string;
  requestHost: string;
  requestPath: string;
}): Promise<string> {
  const { keyId, keySecret } = getCDPCredentials();

  const uri = `${requestMethod} ${requestHost}${requestPath}`;
  const now = Math.floor(Date.now() / 1000);
  const nonce = crypto.randomUUID();

  const pem = buildPem(keySecret);
  const privateKey = await importPKCS8(pem, "ES256");

  const jwt = await new SignJWT({
    sub: keyId,
    iss: "cdp",
    aud: ["cdp_service"],
    nbf: now,
    exp: now + 120,
    uris: [uri],
  })
    .setProtectedHeader({ alg: "ES256", kid: keyId, nonce, typ: "JWT" })
    .sign(privateKey);

  return jwt;
}

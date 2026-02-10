import { SignJWT, importPKCS8, importJWK } from "jose";
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

function isEd25519Key(secret: string): boolean {
  try {
    const decoded = Buffer.from(secret, "base64");
    return decoded.length === 64;
  } catch {
    return false;
  }
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

  const claims = {
    sub: keyId,
    iss: "cdp",
    aud: ["cdp_service"],
    uris: [uri],
  };

  if (isEd25519Key(keySecret)) {
    // Ed25519 key: 64 bytes base64 (32 seed + 32 public key)
    const decoded = Buffer.from(keySecret, "base64");
    const seed = decoded.subarray(0, 32);
    const publicKey = decoded.subarray(32);

    const jwk = {
      kty: "OKP" as const,
      crv: "Ed25519" as const,
      d: seed.toString("base64url"),
      x: publicKey.toString("base64url"),
    };

    const key = await importJWK(jwk, "EdDSA");

    return await new SignJWT(claims)
      .setProtectedHeader({ alg: "EdDSA", kid: keyId, typ: "JWT", nonce })
      .setIssuedAt(now)
      .setNotBefore(now)
      .setExpirationTime(now + 120)
      .sign(key);
  } else {
    // EC key in PEM format
    const privateKey = await importPKCS8(keySecret, "ES256");

    return await new SignJWT(claims)
      .setProtectedHeader({ alg: "ES256", kid: keyId, typ: "JWT", nonce })
      .setIssuedAt(now)
      .setNotBefore(now)
      .setExpirationTime(now + 120)
      .sign(privateKey);
  }
}

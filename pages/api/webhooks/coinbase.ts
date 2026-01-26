import type { NextApiRequest, NextApiResponse } from "next";
import crypto from "crypto";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    // Verify webhook signature if secret is configured
    const webhookSecret = process.env.CDP_WEBHOOK_SECRET;
    if (webhookSecret) {
      const signature = req.headers["x-coinbase-signature"] as string;
      if (signature) {
        const payload = JSON.stringify(req.body);
        const expectedSig = crypto
          .createHmac("sha256", webhookSecret)
          .update(payload)
          .digest("hex");
        if (signature !== expectedSig) {
          console.error("Webhook signature verification failed");
          return res.status(401).json({ error: "Invalid signature" });
        }
      }
    }

    const event = req.body;
    console.log("Luxbin webhook received:", JSON.stringify(event, null, 2));

    // Handle different event types
    const eventType = event?.eventType || event?.event_type;

    switch (eventType) {
      case "onchain.activity.detected":
        console.log("Onchain activity detected:", {
          network: event?.data?.network,
          contractAddress: event?.data?.contract_address,
          eventName: event?.data?.event_name,
        });
        break;
      case "wallet.activity.detected":
        console.log("Wallet activity detected:", {
          walletId: event?.data?.wallet_id,
          address: event?.data?.address,
        });
        break;
      default:
        console.log("Unknown event type:", eventType);
    }

    return res.status(200).json({ received: true });
  } catch (error) {
    console.error("Webhook processing error:", error);
    return res.status(500).json({ error: "Internal server error" });
  }
}

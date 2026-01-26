import { useEffect } from "react";

export default function MiniKitReady() {
  useEffect(() => {
    // Signal to Farcaster/Base that the mini app is ready
    import("@farcaster/miniapp-sdk").then(({ sdk }) => {
      sdk.actions.ready();
    }).catch(() => {
      // Not running inside a mini app context, ignore
    });
  }, []);

  return null;
}

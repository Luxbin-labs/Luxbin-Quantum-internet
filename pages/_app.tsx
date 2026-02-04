import type { AppProps } from "next/app";
import dynamic from "next/dynamic";
import { Analytics } from "@vercel/analytics/next";

const CDPWrapper = dynamic(
  () => import("../components/CDPWrapper"),
  { ssr: false }
);

const MiniKitReady = dynamic(
  () => import("../components/MiniKitReady"),
  { ssr: false }
);

export default function App({ Component, pageProps }: AppProps) {
  return (
    <CDPWrapper>
      <MiniKitReady />
      <Component {...pageProps} />
      <Analytics />
    </CDPWrapper>
  );
}

import type { AppProps } from "next/app";
import dynamic from "next/dynamic";
import "../styles/globals.css";

const MiniKitReady = dynamic(
  () => import("../components/MiniKitReady"),
  { ssr: false }
);

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <MiniKitReady />
      <Component {...pageProps} />
    </>
  );
}

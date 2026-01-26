import { Html, Head, Main, NextScript } from "next/document";

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta
          name="fc:miniapp"
          content={JSON.stringify({
            version: "next",
            imageUrl: "https://quantum-internet.vercel.app/favicon.svg",
            button: {
              title: "Launch Luxbin",
              action: {
                type: "launch_miniapp",
                name: "Luxbin",
                url: "https://quantum-internet.vercel.app",
              },
            },
          })}
        />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}

import { CDPReactProvider, type Config as CDPConfig } from "@coinbase/cdp-react";

export default function CDPWrapper({ children }: { children: React.ReactNode }) {
  const projectId = "c93e3649-cf68-4953-a933-2c46bce6fdeb";

  const cdpConfig: CDPConfig = {
    projectId,
    appName: "Luxbin",
    ethereum: {
      createOnLogin: "eoa",
    },
  };

  return (
    <CDPReactProvider config={cdpConfig}>
      {children}
    </CDPReactProvider>
  );
}

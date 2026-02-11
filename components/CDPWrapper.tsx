import { CDPReactProvider, type Config as CDPConfig } from "@coinbase/cdp-react";

const projectId = process.env.NEXT_PUBLIC_COINBASE_PROJECT_ID;

const cdpConfig: CDPConfig = {
  projectId: projectId || "",
  basePath: "https://api.cdp.coinbase.com",
  appName: "Luxbin",
  appLogoUrl: "https://luxbinquantuminternet.xyz/icon.jpg",
  ethereum: {
    createOnLogin: "eoa",
  },
};

export default function CDPWrapper({ children }: { children: React.ReactNode }) {
  // If no project ID configured, skip the CDP provider to avoid crashes
  if (!projectId) {
    return <>{children}</>;
  }

  return (
    <CDPReactProvider config={cdpConfig}>
      {children}
    </CDPReactProvider>
  );
}

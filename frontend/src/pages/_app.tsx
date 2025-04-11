import React from 'react';
import type { AppProps } from 'next/app';
import { MsalProvider } from "@azure/msal-react";
import { PublicClientApplication } from "@azure/msal-browser";
import { msalConfig } from '../lib/auth/msalConfig';
import '../styles/globals.css';

// Initialize MSAL outside components for singleton usage
const msalInstance = new PublicClientApplication(msalConfig);

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <MsalProvider instance={msalInstance}>
      <Component {...pageProps} />
    </MsalProvider>
  );
}

export default MyApp;

import React, { useState, useEffect } from 'react';
import { MsalProvider as DefaultMsalProvider } from '@azure/msal-react';
import { PublicClientApplication } from '@azure/msal-browser';
import { msalConfig } from '../authConfig';

let msalInstance: PublicClientApplication | null = null;

interface MsalProviderProps {
  children: React.ReactNode;
}

export const MsalProvider: React.FC<MsalProviderProps> = ({ children }) => {
  const [instance, setInstance] = useState<PublicClientApplication | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // Initialize MSAL in client-side only
    if (typeof window === 'undefined') return;
    
    try {
      if (!msalInstance) {
        console.log('Creating new MSAL instance');
        msalInstance = new PublicClientApplication(msalConfig);
        msalInstance.initialize().catch(e => {
          console.error('MSAL initialization failed:', e);
        });
      }
      
      setInstance(msalInstance);
    } catch (e) {
      setError(e instanceof Error ? e : new Error('Unknown error initializing MSAL'));
      console.error('Error creating MSAL instance:', e);
    }
  }, []);

  if (error) {
    return (
      <div style={{ padding: '20px', color: 'red' }}>
        <h2>Authentication Error</h2>
        <p>{error.message}</p>
        <button onClick={() => window.location.reload()}>Reload Page</button>
      </div>
    );
  }

  if (!instance) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <p>Initializing authentication...</p>
      </div>
    );
  }

  return <DefaultMsalProvider instance={instance}>{children}</DefaultMsalProvider>;
};

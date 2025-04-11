import React, { ReactNode, useEffect, useState } from 'react';
import { MsalProvider } from '@azure/msal-react';
import { msalInstance } from './auth-service';

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * AuthProvider component that wraps the application with MSAL provider
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Handle potential redirect on initial load
    if (msalInstance) {
      msalInstance.handleRedirectPromise().catch(error => {
        console.error("Error handling redirect:", error);
      }).finally(() => {
        setIsInitialized(true);
      });
    } else {
      setIsInitialized(true);
    }
  }, []);

  if (!isInitialized) {
    return <div>Initializing authentication...</div>;
  }

  // Render children directly if MSAL is not available (server-side)
  if (!msalInstance) {
    return <>{children}</>;
  }

  return <MsalProvider instance={msalInstance}>{children}</MsalProvider>;
};

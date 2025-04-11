import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { loginRequest } from '../../lib/auth/msalConfig';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const router = useRouter();
  const { instance } = useMsal();
  const isAuthenticated = useIsAuthenticated();

  useEffect(() => {
    if (!isAuthenticated) {
      console.log('ProtectedRoute: User not authenticated, redirecting to login');
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  // Return children when authenticated, show loading state otherwise
  if (!isAuthenticated) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <p>Authentication required...</p>
      </div>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;

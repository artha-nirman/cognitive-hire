import { useEffect, ReactNode } from 'react';
import { useRouter } from 'next/router';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';

interface ProtectedRouteProps {
  children: ReactNode;
}

/**
 * Protected route component that ensures user is authenticated
 * Redirects to login page if not authenticated
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const router = useRouter();
  const { instance } = useMsal();
  const isAuthenticated = useIsAuthenticated();

  useEffect(() => {
    if (!isAuthenticated) {
      console.log('Access denied: User not authenticated');
      router.replace('/login');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Checking authentication...</p>
      </div>
    );
  }

  return <>{children}</>;
};

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/lib/auth/AuthProvider';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  const [accessGranted, setAccessGranted] = useState(false);

  useEffect(() => {
    // Check if user is authenticated
    if (!isLoading) {
      // Check for authentication state
      if (isAuthenticated || localStorage.getItem('isAuthenticated') === 'true') {
        setAccessGranted(true);
      } else {
        console.log('User not authenticated, redirecting to login');
        router.replace('/login');
      }
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading state while checking authentication
  if (isLoading && !accessGranted) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  // Allow access if explicitly granted or authentication passed
  if (accessGranted || isAuthenticated) {
    return <>{children}</>;
  }

  // Default loading screen
  return (
    <div className="flex justify-center items-center min-h-screen">
      <p>Checking authentication...</p>
    </div>
  );
};

export default ProtectedRoute;

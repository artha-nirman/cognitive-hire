import { useEffect } from 'react';
import { authService } from '../auth/auth-service';

export default function Home() {
  useEffect(() => {
    // Process any auth redirects then check auth status
    const checkAuth = async () => {
      try {
        await authService.handleRedirect();
        
        if (authService.isAuthenticated()) {
          window.location.href = '/dashboard';
        } else {
          window.location.href = '/login';
        }
      } catch (error) {
        console.error('Auth error:', error);
        window.location.href = '/login';
      }
    };

    checkAuth();
  }, []);

  return (
    <div style={{ 
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh'
    }}>
      <p>Loading...</p>
    </div>
  );
}
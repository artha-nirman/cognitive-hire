import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useMsal } from '@azure/msal-react';

export default function AuthCallback() {
  const router = useRouter();
  const { instance } = useMsal();

  useEffect(() => {
    const handleRedirect = async () => {
      try {
        // Process the authentication response
        await instance.handleRedirectPromise();
        
        // Check if authenticated and redirect accordingly
        const accounts = instance.getAllAccounts();
        if (accounts.length > 0) {
          router.replace('/dashboard');
        } else {
          router.replace('/login');
        }
      } catch (error) {
        console.error('Error processing authentication:', error);
        router.replace('/login');
      }
    };

    handleRedirect();
  }, [instance, router]);

  // Simple loading UI
  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh' 
    }}>
      <p>Processing authentication...</p>
    </div>
  );
}

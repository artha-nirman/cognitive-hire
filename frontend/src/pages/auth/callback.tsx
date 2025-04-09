import React, { useEffect, useState } from 'react';
import { authService } from '../../services/authService';

const AuthCallback: React.FC = () => {
  const [status, setStatus] = useState<'processing'|'success'|'error'>('processing');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const processAuthResponse = async () => {
      try {
        // Process the auth response
        await authService.initialize();
        await authService.handleRedirectPromise();
        
        // Check if we're authenticated after processing
        if (authService.isAuthenticated()) {
          setStatus('success');
          // Redirect to dashboard
          window.location.href = '/dashboard';
        } else {
          setStatus('error');
          setError('Authentication completed but no user was found.');
        }
      } catch (err) {
        setStatus('error');
        setError((err as Error).message);
        console.error('Auth callback error:', err);
      }
    };

    // Only run on client side
    if (typeof window !== 'undefined') {
      processAuthResponse();
    }
  }, []);

  // Simple static UI that works with SSR
  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      alignItems: 'center', 
      justifyContent: 'center',
      minHeight: '100vh',
      padding: '20px'
    }}>
      <div style={{
        maxWidth: '500px',
        width: '100%',
        padding: '30px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        borderRadius: '8px',
        backgroundColor: 'white',
        textAlign: 'center'
      }}>
        <h1>Authentication {status === 'success' ? 'Successful' : status === 'error' ? 'Failed' : 'in Progress'}</h1>
        
        {status === 'processing' && (
          <p>Please wait while we complete the authentication process...</p>
        )}
        
        {status === 'success' && (
          <p>Authentication successful. Redirecting to dashboard...</p>
        )}
        
        {status === 'error' && error && (
          <>
            <p style={{ color: 'red' }}>Authentication failed: {error}</p>
            <button
              onClick={() => window.location.href = '/login'}
              style={{
                padding: '10px 20px',
                backgroundColor: '#0078d4',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                marginTop: '20px',
                cursor: 'pointer'
              }}
            >
              Return to Login
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default AuthCallback;

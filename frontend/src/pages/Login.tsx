import React, { useEffect, useState } from 'react';
import { authService } from '../services/authService';

const Login: React.FC = () => {
  const [isInitializing, setIsInitializing] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [debugInfo, setDebugInfo] = useState<{[key: string]: string}>({});
  const [showDebug, setShowDebug] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  // Safe debug logger that won't cause hydration mismatches
  const addDebugInfo = (key: string, value: string) => {
    if (!isMounted) return; // Skip during SSR or before mount
    
    console.log(`LOGIN DEBUG - ${key}: ${value}`);
    setDebugInfo(prev => ({...prev, [key]: value}));
  };

  // First effect just for mounting
  useEffect(() => {
    setIsMounted(true);
    console.log('Login component mounted');
  }, []);

  // Second effect for auth logic after mounting
  useEffect(() => {
    if (!isMounted) return;
    
    addDebugInfo('Component', 'Login component ready');
    
    const initializeAuth = async () => {
      try {
        addDebugInfo('Auth Init', 'Starting initialization');
        
        // Check if already authenticated
        if (localStorage.getItem('authSuccess') === 'true') {
          addDebugInfo('Auth Status', 'Auth success flag found in localStorage');
        }
        
        // Get env vars
        addDebugInfo('Client ID', process.env.REACT_APP_AZURE_CLIENT_ID || 'Not found in env');
        addDebugInfo('Authority', process.env.REACT_APP_AZURE_AUTHORITY || 'Not found in env');
        
        // Make sure auth is initialized
        await authService.initialize();
        addDebugInfo('Auth Init', 'Initialization complete');
        
        // Check if user is already logged in
        const isAuthenticated = authService.isAuthenticated();
        addDebugInfo('Auth Status', isAuthenticated ? 'Already authenticated' : 'Not authenticated');
        
        if (isAuthenticated) {
          addDebugInfo('Action', 'Already authenticated, redirecting to dashboard');
          window.location.href = '/dashboard';
          return;
        }
        
        setIsInitializing(false);
      } catch (err) {
        const errorMessage = (err as Error).message;
        console.error('Failed to initialize auth:', err);
        addDebugInfo('Auth Error', errorMessage);
        setError(`Authentication initialization failed: ${errorMessage}`);
        setIsInitializing(false);
      }
    };
    
    initializeAuth();
  }, [isMounted]);

  const handleSignIn = async () => {
    try {
      if (isInitializing) {
        addDebugInfo('Sign In', 'Still initializing, please wait');
        return;
      }
      
      setIsLoading(true);
      setError(null);
      addDebugInfo('Sign In', 'Starting login process');
      
      // Store intended action for debugging
      localStorage.setItem('loginAttempt', new Date().toISOString());
      
      // Call login method which should redirect to Azure AD B2C
      await authService.login();
      addDebugInfo('Sign In', 'Login method completed (this should not be seen)');
    } catch (err) {
      const errorMessage = (err as Error).message;
      setError(`Authentication failed: ${errorMessage}`);
      addDebugInfo('Sign In Error', errorMessage);
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Initial static render for SSR
  if (!isMounted) {
    return (
      <div style={{padding: '20px', textAlign: 'center'}}>
        <h2>Initializing Authentication...</h2>
        <p>Please wait while we set up the authentication service.</p>
      </div>
    );
  }

  // Conditional rendering for client only after mount
  if (isInitializing) {
    return (
      <div style={{padding: '20px', textAlign: 'center'}}>
        <h2>Initializing Authentication...</h2>
        <p>Please wait while we set up the authentication service.</p>
        <div style={{margin: '20px 0'}}>
          <button onClick={() => setShowDebug(!showDebug)}>
            {showDebug ? 'Hide Debug Info' : 'Show Debug Info'}
          </button>
        </div>
        
        {showDebug && (
          <div style={{
            textAlign: 'left',
            border: '1px solid #ccc',
            padding: '10px',
            borderRadius: '5px',
            backgroundColor: '#f9f9f9'
          }}>
            <h3>Debug Information:</h3>
            {Object.entries(debugInfo).map(([key, value]) => (
              <div key={key} style={{margin: '5px 0'}}>
                <strong>{key}:</strong> {value}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

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
        maxWidth: '400px',
        width: '100%',
        padding: '30px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        borderRadius: '8px',
        backgroundColor: 'white',
        textAlign: 'center'
      }}>
        <h1>Welcome to Hire Cognition</h1>
        <p style={{ marginBottom: '30px' }}>Please sign in to continue</p>
        
        {error && (
          <div className="error-message" style={{
            color: 'red',
            border: '1px solid red',
            padding: '10px',
            marginBottom: '15px',
            borderRadius: '5px',
            backgroundColor: '#fff0f0'
          }}>
            <strong>Error:</strong> {error}
          </div>
        )}
        
        <button 
          onClick={handleSignIn}
          disabled={isLoading}
          className="signin-button"
          data-testid="azure-login-button"
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: '#0078d4',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '16px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            opacity: isLoading ? 0.7 : 1
          }}
        >
          {isLoading ? 'Signing In...' : 'Sign in with Azure AD B2C'}
        </button>
      </div>
    </div>
  );
};

export default Login;

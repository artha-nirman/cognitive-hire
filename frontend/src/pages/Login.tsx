import React, { useState } from 'react';
import { useMsal } from '@azure/msal-react';
import { loginRequest } from '../authConfig';
import { useRouter } from 'next/router'; // Use Next.js router instead

const Login: React.FC = () => {
  const { instance } = useMsal();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter(); // Next.js router
  
  const handleLogin = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Login using redirect
      await instance.loginRedirect(loginRequest);
      // This won't execute immediately due to redirect
    } catch (err) {
      console.error("Login error:", err);
      setError(`Login failed: ${(err as Error).message}`);
      setIsLoading(false);
    }
  };

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh',
      padding: '20px',
      backgroundColor: '#f5f5f5' 
    }}>
      <div style={{ 
        maxWidth: '400px',
        width: '100%',
        padding: '2rem',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        textAlign: 'center'
      }}>
        <h1 style={{ marginBottom: '1rem' }}>Welcome to Hire Cognition</h1>
        <p style={{ marginBottom: '2rem' }}>Please sign in to continue</p>
        
        {error && (
          <div style={{ 
            color: 'red', 
            padding: '10px',
            backgroundColor: '#ffeeee',
            borderRadius: '4px',
            marginBottom: '1rem'
          }}>
            {error}
          </div>
        )}
        
        <button
          onClick={handleLogin}
          disabled={isLoading}
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

import React, { useEffect, useState } from 'react';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';

const Dashboard: React.FC = () => {
  const { instance } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [account, setAccount] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Manually get account information instead of relying on useAccount hook
  useEffect(() => {
    if (instance && isAuthenticated) {
      // Get all accounts from MSAL
      const accounts = instance.getAllAccounts();
      
      if (accounts.length > 0) {
        // Use the first account (most common scenario)
        setAccount(accounts[0]);
        console.log("Retrieved account:", accounts[0]);
      } else {
        console.warn("No accounts found despite being authenticated");
      }
    }
    setIsLoading(false);
  }, [instance, isAuthenticated]);

  const handleLogout = () => {
    instance.logoutRedirect({
      postLogoutRedirectUri: window.location.origin + '/login'
    });
  };

  return (
    <div style={{ padding: '2rem' }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '2rem'
      }}>
        <h1>Dashboard</h1>
        
        <button
          onClick={handleLogout}
          style={{
            padding: '8px 16px',
            backgroundColor: '#f44336',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Sign Out
        </button>
      </div>
      
      {isAuthenticated ? (
        isLoading ? (
          <p>Loading account information...</p>
        ) : (
          <div>
            <p>Welcome, {account?.name || account?.username || 'User'}!</p>
            <p>You are now signed in.</p>
            
            <div style={{ marginTop: '2rem' }}>
              <h2>Account Information</h2>
              <pre style={{ 
                backgroundColor: '#f5f5f5', 
                padding: '1rem',
                borderRadius: '4px',
                overflow: 'auto'
              }}>
                {account ? JSON.stringify(account, null, 2) : 'No account data available'}
              </pre>
            </div>
            
            {!account && (
              <div style={{ marginTop: '1rem', color: '#d32f2f' }}>
                <p>Note: Your account details couldn't be retrieved. This might be due to authentication issues.</p>
                <button 
                  onClick={() => window.location.reload()} 
                  style={{ marginTop: '0.5rem', padding: '5px 10px' }}
                >
                  Reload Page
                </button>
              </div>
            )}
          </div>
        )
      ) : (
        <p>You are not authenticated. Please sign in.</p>
      )}
    </div>
  );
};

export default Dashboard;
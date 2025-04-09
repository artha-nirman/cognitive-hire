import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { authService } from './services/authService';
import Login from './pages/Login';
// Import the component from the auth subdirectory instead of the root pages directory
import AuthCallback from './pages/auth/callback';
import Dashboard from './pages/Dashboard';
import ProtectedRoute from './components/ProtectedRoute';

// Log when App component loads
console.log('App component loading');

const App: React.FC = () => {
  console.log('App component rendering');

  useEffect(() => {
    console.log('App useEffect running - initializing auth');
    const initializeAuth = async () => {
      try {
        await authService.initialize();
        console.log('Auth initialized in App');
      } catch (error) {
        console.error('Auth initialization error in App:', error);
      }
    };

    initializeAuth();
  }, []);

  // Define routes - explicitly log the routes we're setting up
  console.log('Setting up routes including /auth/callback');
  
  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        
        {/* Use the component from auth/callback.tsx */}
        <Route path="/auth/callback" element={<AuthCallback />} />
        
        {/* Protected routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<Dashboard />} />
        </Route>
        
        {/* Default routes */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
};

export default App;

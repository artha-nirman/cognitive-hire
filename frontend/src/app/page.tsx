'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { CircularProgress, Box, Typography } from '@mui/material';
import { useAuth } from '@/contexts/auth-context';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  
  useEffect(() => {
    // If authentication check is complete and user is authenticated, redirect to dashboard
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard');
    }
    
    // If authentication check is complete and user is not authenticated, redirect to login
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);
  
  // While checking authentication, show loading indicator
  return (
    <Box 
      sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        alignItems: 'center', 
        justifyContent: 'center',
        height: '100vh'
      }}
    >
      <CircularProgress size={60} />
      <Typography variant="h6" sx={{ mt: 2 }}>
        Initializing Cognitive Hire...
      </Typography>
    </Box>
  );
}

'use client';

import { useState } from 'react';
import { Button, Container, Paper, Typography, Box, CircularProgress } from '@mui/material';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { Microsoft, Google } from '@mui/icons-material';

export default function LoginPage() {
  const { login, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // If user is already authenticated, redirect to dashboard
  if (isAuthenticated && !isLoading) {
    router.push('/dashboard');
    return null;
  }
  
  const handleLogin = async () => {
    setIsSubmitting(true);
    try {
      await login();
      router.push('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  if (isLoading) {
    return (
      <Container maxWidth="sm" sx={{ mt: 8, textAlign: 'center' }}>
        <CircularProgress />
        <Typography variant="body1" sx={{ mt: 2 }}>
          Initializing authentication...
        </Typography>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Welcome to Cognitive Hire
        </Typography>
        <Typography variant="body1" paragraph align="center" sx={{ mb: 4 }}>
          Sign in with your account to continue
        </Typography>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Button
            variant="contained"
            color="primary"
            size="large"
            fullWidth
            startIcon={<Microsoft />}
            onClick={handleLogin}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Signing in...' : 'Sign in with Microsoft'}
          </Button>
          
          <Button
            variant="outlined"
            color="primary"
            size="large"
            fullWidth
            startIcon={<Google />}
            onClick={handleLogin}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Signing in...' : 'Sign in with Google'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}

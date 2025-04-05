'use client';

import { useEffect } from 'react';
import { Container, Typography, Box, Grid, Paper, CircularProgress } from '@mui/material';
import { useAuth } from '@/contexts/auth-context';
import { useApiClient } from '@/lib/api-client';

export default function DashboardPage() {
  const { user, isLoading } = useAuth();
  const apiClient = useApiClient();
  
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Example API call - replace with actual endpoint
        // const data = await apiClient.get('/api/dashboard/summary');
        // Process data here
      } catch (error) {
        console.error('Failed to fetch dashboard data', error);
      }
    };
    
    if (user) {
      fetchDashboardData();
    }
  }, [user, apiClient]);
  
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Welcome back, {user?.name || 'User'}
      </Typography>
      
      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Typography variant="h6" color="primary" gutterBottom>
              Active Jobs
            </Typography>
            <Typography variant="h4">
              5
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Typography variant="h6" color="primary" gutterBottom>
              Candidates
            </Typography>
            <Typography variant="h4">
              24
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Typography variant="h6" color="primary" gutterBottom>
              Pending Tasks
            </Typography>
            <Typography variant="h4">
              3
            </Typography>
          </Paper>
        </Grid>
        
        {/* Recent Activity */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" color="primary" gutterBottom>
              Recent Activity
            </Typography>
            <Typography variant="body2" color="text.secondary">
              No recent activity to display
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

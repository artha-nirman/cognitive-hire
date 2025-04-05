'use client';

import React from 'react';
import { AuthProvider } from '@/providers/auth-provider';
import { MuiProvider } from '@/providers/mui-provider';

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <MuiProvider>
      <AuthProvider>
        {children}
      </AuthProvider>
    </MuiProvider>
  );
}

'use client';

import React from 'react';
import { AuthProvider as MsalAuthProvider } from '@/contexts/auth-context';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return <MsalAuthProvider>{children}</MsalAuthProvider>;
}

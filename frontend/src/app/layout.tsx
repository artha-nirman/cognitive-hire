'use client';

import React from 'react';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/providers/auth-provider';
import { metadata } from './metadata';
import ClientLayout from './client-layout';

const inter = Inter({ subsets: ['latin'] });

// Export the metadata for Next.js
export { metadata };

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <ClientLayout>{children}</ClientLayout>
        </AuthProvider>
      </body>
    </html>
  );
}

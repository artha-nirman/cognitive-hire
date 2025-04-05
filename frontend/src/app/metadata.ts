import { Metadata } from 'next';

// This must be a separate file (not inline in layout.tsx)
// because layout.tsx is a client component marked with 'use client'
export const metadata: Metadata = {
  title: 'Cognitive Hire',
  description: 'AI-powered recruitment platform',
};

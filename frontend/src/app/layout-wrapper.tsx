import { Inter } from 'next/font/google';
import './globals.css';
import type { Metadata } from 'next';
import { metadata } from './metadata';

// Cannot use client components at the root level for metadata - this is the server component
const inter = Inter({ subsets: ['latin'] });

export { metadata };

export default function LayoutWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}

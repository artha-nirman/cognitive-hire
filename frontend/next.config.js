/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Make Next.js handle the auth callback path properly
  async rewrites() {
    return [
      {
        source: '/auth/callback',
        destination: '/auth/callback',
      },
    ];
  },
}

module.exports = nextConfig;

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Allow images from external domains if needed
  images: {
    domains: [],
  },
  // Note: API requests are now handled by Next.js API routes in pages/api/
  // These routes proxy to Django backend and preserve the Host header via X-Forwarded-Host
}

module.exports = nextConfig

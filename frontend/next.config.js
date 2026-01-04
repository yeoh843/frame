/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost', 'frame-69044886986.asia-southeast1.run.app'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '*.asia-southeast1.run.app',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      },
    ],
  },
}

module.exports = nextConfig















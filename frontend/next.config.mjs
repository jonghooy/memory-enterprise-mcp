/** @type {import('next').NextConfig} */
const nextConfig = {
  // Base path for deployment at /kms
  basePath: process.env.BASE_PATH || '',

  // Asset prefix for static files
  assetPrefix: process.env.ASSET_PREFIX || '',

  // Trailing slash for better nginx compatibility
  trailingSlash: true,

  // Other optimizations
  reactStrictMode: true,
  swcMinify: true,

  // API proxy to backend MCP server
  async rewrites() {
    return [
      {
        source: '/api/knowledge/:path*',
        destination: 'http://localhost:8005/api/knowledge/:path*',
      },
    ]
  },
};

export default nextConfig;

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
};

export default nextConfig;

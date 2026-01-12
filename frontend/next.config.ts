import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/proxy/:path*',
        destination: 'https://fluxo-231046660634.europe-west1.run.app/:path*',
      },
    ];
  },
};

export default nextConfig;

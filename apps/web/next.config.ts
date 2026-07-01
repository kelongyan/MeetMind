import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  devIndicators: false,

  // Produce a self-contained bundle for Docker deployment.
  output: "standalone",

  // Proxy /api/* requests to the backend in development mode
  // so the frontend can call the API on the same origin.
  async rewrites() {
    const apiBase =
      process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${apiBase}/api/:path*`,
      },
      {
        source: "/health",
        destination: `${apiBase}/health`,
      },
    ];
  },
};

export default nextConfig;

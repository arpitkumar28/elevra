// Next.js production settings for the internal admin dashboard.
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@elevra/api-client", "@elevra/shared", "@elevra/ui"],
};

export default nextConfig;

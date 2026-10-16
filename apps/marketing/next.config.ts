// Next.js production settings for the public marketing website.
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // CI runs the app's standalone ESLint command. Next 15.5's built-in lint
  // invocation passes options removed by the workspace's ESLint version.
  eslint: { ignoreDuringBuilds: true },
  transpilePackages: ["@elevra/ui", "@elevra/shared"],
};

export default nextConfig;

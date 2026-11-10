// Next.js production settings for the public marketing website.
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@elevra/ui", "@elevra/shared"],
};

export default nextConfig;

// Next.js production settings for the student web application.
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@elevra/api-client", "@elevra/shared", "@elevra/ui"],
};

export default nextConfig;

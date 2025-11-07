import type { NextConfig } from "next";

const isGithubPages = process.env.GITHUB_PAGES === "true";
const repo = "face-recognition-system"; // repository name

const nextConfig: NextConfig = {
  output: "export",
  images: { unoptimized: true },
  basePath: isGithubPages ? `/${repo}` : undefined,
  assetPrefix: isGithubPages ? `/${repo}/` : undefined,
  trailingSlash: true,
};

export default nextConfig;

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  output: "standalone",

  async redirects() {
    return [{ source: "/", destination: "/case", permanent: false }];
  },
};

export default nextConfig;

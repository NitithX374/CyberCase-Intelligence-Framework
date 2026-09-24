import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  output: "standalone",

  async redirects() {
    return [
      { source: "/", destination: "/case", permanent: false },
      { source: "/case/:caseId/intake", destination: "/case/:caseId/sources", permanent: false },
      { source: "/case/:caseId/materials", destination: "/case/:caseId/sources", permanent: false },
    ];
  },
};

export default nextConfig;

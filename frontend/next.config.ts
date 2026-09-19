import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  output: "standalone",

  // There is no public front page: the workspace is the product. Sending the
  // root to the case library puts AccountGate in charge, and it already knows
  // to bounce a signed-out reader to /login and back afterwards. Temporary
  // (307) rather than permanent, so a browser never caches it past a rethink.
  async redirects() {
    return [{ source: "/", destination: "/case", permanent: false }];
  },
};

export default nextConfig;

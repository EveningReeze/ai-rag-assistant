import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
   output: "standalone",   // ⭐ Docker 多阶段构建需要
};

export default nextConfig;

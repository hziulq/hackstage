/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  async rewrites() {
    const apiInternalUrl = process.env.API_INTERNAL_URL;
    if (!apiInternalUrl) {
      // apps/api は未着手（フロントエンド単体プロトタイプ）。
      // API_INTERNAL_URL が無い間は rewrites を追加しない。
      return [];
    }
    return [
      {
        source: "/api/:path*",
        destination: `${apiInternalUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;

# dev / prod はローカルと Render で同じ Dockerfile を使う(docs/design.md §12)
FROM node:22-slim AS base
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# ── ローカル開発(compose) ──────────────────────────
FROM base AS dev
ENV NODE_ENV=development
COPY . .
CMD ["npm", "run", "dev"]

# ── ビルド(本番用の.next/standaloneを生成) ───────────
FROM base AS builder
ENV NODE_ENV=production
# next.config.js の rewrites() はビルド時に評価され .next/routes-manifest.json に
# 焼き込まれる(standalone サーバーは実行時に再評価しない)。値はローカル/本番で
# 同一固定(docs/design.md §5, §9)なのでここに直書きする。
ENV API_INTERNAL_URL=http://api:8000
COPY . .
RUN npm run build

# ── 本番(Render, dockerTarget: prod) ────────────────
FROM node:22-slim AS prod
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
CMD ["node", "server.js"]

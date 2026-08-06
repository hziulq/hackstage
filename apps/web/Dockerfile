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

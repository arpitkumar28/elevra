# Production image for the Elevra admin dashboard.
FROM node:22-alpine AS deps
WORKDIR /repo
RUN corepack enable
COPY package.json pnpm-lock.yaml* pnpm-workspace.yaml turbo.json tsconfig.base.json ./
COPY apps/admin ./apps/admin
COPY packages ./packages
RUN pnpm install --frozen-lockfile

FROM deps AS builder
RUN pnpm --filter @elevra/admin build

FROM node:22-alpine AS runner
WORKDIR /repo
ENV NODE_ENV=production
RUN corepack enable
COPY --from=builder /repo ./
EXPOSE 3002
CMD ["pnpm", "--filter", "@elevra/admin", "start"]

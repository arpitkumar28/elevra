# Production image for the Elevra student web app.
FROM node:22-alpine AS deps
WORKDIR /repo
RUN corepack enable
COPY package.json pnpm-lock.yaml* pnpm-workspace.yaml turbo.json tsconfig.base.json ./
COPY apps/web ./apps/web
COPY packages ./packages
RUN pnpm install --frozen-lockfile

FROM deps AS builder
RUN pnpm --filter @elevra/web build

FROM node:22-alpine AS runner
WORKDIR /repo
ENV NODE_ENV=production
RUN corepack enable
COPY --from=builder /repo ./
EXPOSE 3001
CMD ["pnpm", "--filter", "@elevra/web", "start"]

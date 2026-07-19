# Production image for the Elevra marketing website.
FROM node:22-alpine AS deps
WORKDIR /repo
RUN corepack enable
COPY package.json pnpm-lock.yaml* pnpm-workspace.yaml turbo.json tsconfig.base.json ./
COPY apps/marketing ./apps/marketing
COPY packages ./packages
RUN pnpm install --frozen-lockfile

FROM deps AS builder
RUN pnpm --filter @elevra/marketing build

FROM node:22-alpine AS runner
WORKDIR /repo
ENV NODE_ENV=production
RUN corepack enable
COPY --from=builder /repo ./
EXPOSE 3000
CMD ["pnpm", "--filter", "@elevra/marketing", "start"]

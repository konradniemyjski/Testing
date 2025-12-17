FROM public.ecr.aws/docker/library/node:25-slim AS build
WORKDIR /app

COPY package*.json ./
RUN npm config set fetch-retry-maxtimeout 600000 \
    && npm config set fetch-retry-mintimeout 10000 \
    && npm install --no-audit --no-fund
COPY . .
RUN npm run build

FROM public.ecr.aws/docker/library/node:25-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/.output ./.output
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]

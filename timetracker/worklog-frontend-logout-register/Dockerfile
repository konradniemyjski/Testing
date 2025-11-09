
# ===== Build Angular =====
FROM node:20 AS build
WORKDIR /app

# Optional: quieter npm & skip audit during CI
ENV npm_config_fund=false
ENV npm_config_update_notifier=false
ENV npm_config_audit=false

COPY package*.json ./
# Use ci for deterministic installs; skip audit to reduce noise
RUN npm ci --no-audit --no-fund

COPY . .
# DEBUG: pokaż zawartość styles.css w kontenerze buildu
RUN echo "==== styles.css inside build container ====" && \
    ls -l src/styles.css && \
    sed -n '1,80p' src/styles.css
# Build production (Angular 15+ outputs to dist/<name>/browser)
RUN npm run build -- --configuration production

# ===== Nginx serve (SPA) =====
FROM nginx:alpine

# SPA fallback to index.html on client-side routes
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Angular build now lives in dist/<app-name>/browser
COPY --from=build /app/dist/worker-hours-frontend/browser /usr/share/nginx/html

EXPOSE 80

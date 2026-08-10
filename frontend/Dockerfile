# ── Stage 1: Node build ───────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /build

# Install dependencies first (layer cache friendly).
# If package-lock.json exists (CI / committed lockfile) use `npm ci` for
# deterministic, reproducible installs. Otherwise fall back to `npm install`
# which also generates the lockfile so the build succeeds locally before the
# lockfile has been committed.
COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then \
      echo "package-lock.json found — running npm ci" && \
      npm ci --prefer-offline; \
    else \
      echo "No package-lock.json — running npm install" && \
      npm install; \
    fi

# Copy source and build
COPY . .

# VITE_API_BASE_URL is intentionally empty — the nginx proxy handles /api routing.
RUN npm run build


# ── Stage 2: Production nginx image ───────────────────────────────────────────
FROM nginx:1.27-alpine AS runtime

# Remove default nginx static content
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets
COPY --from=builder /build/dist /usr/share/nginx/html

# nginx configuration: SPA routing + gzip + security headers
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Security: nginx worker runs as nginx user (uid 101) by default in alpine image.
# Ensure the html directory is readable.
RUN chown -R nginx:nginx /usr/share/nginx/html \
 && chmod -R 755 /usr/share/nginx/html

EXPOSE 80

# Graceful shutdown
STOPSIGNAL SIGQUIT

CMD ["nginx", "-g", "daemon off;"]

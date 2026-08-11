# ── Stage 1: Node build ───────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /build

COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then \
      npm ci --prefer-offline; \
    else \
      npm install; \
    fi

COPY . .
RUN npm run build


# ── Stage 2: Production nginx image ───────────────────────────────────────────
FROM nginx:1.27-alpine AS runtime

# Remove default nginx config and content
RUN rm -rf /usr/share/nginx/html/* /etc/nginx/conf.d/default.conf

# Copy built assets
COPY --from=builder /build/dist /usr/share/nginx/html

# Copy our nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# nginx non-root setup:
# - /var/cache/nginx ve /var/run nginx kullanıcısına ver
# - port 80 yerine 8080 kullan (non-root port)
# - pid dosyası için /tmp kullan
RUN sed -i 's/listen\s*80;/listen 8082;/g' /etc/nginx/conf.d/default.conf \
 && sed -i 's|/var/run/nginx.pid|/tmp/nginx.pid|g' /etc/nginx/nginx.conf \
 && chown -R nginx:nginx /usr/share/nginx/html \
 && chown -R nginx:nginx /var/cache/nginx \
 && chmod -R 755 /usr/share/nginx/html

USER nginx

EXPOSE 8082

STOPSIGNAL SIGQUIT

CMD ["nginx", "-g", "daemon off;"]

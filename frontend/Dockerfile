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

ENV BACKEND_HOST=investment-platform-backend

# Remove default nginx config and content
RUN rm -rf /usr/share/nginx/html/* /etc/nginx/conf.d/default.conf \
    && mkdir -p /tmp/nginx /var/cache/nginx /var/run

# Copy built assets
COPY --from=builder /build/dist /usr/share/nginx/html

# Copy our nginx template config. nginx entrypoint will substitute env vars
# from /etc/nginx/templates/*.template into /etc/nginx/conf.d/default.conf.
COPY nginx.conf /etc/nginx/templates/default.conf.template

# nginx non-root setup: make conf.d writable for envsubst template processing
RUN sed -i 's|/var/run/nginx.pid|/tmp/nginx.pid|g' /etc/nginx/nginx.conf \
 && chown -R nginx:nginx /usr/share/nginx/html \
 && chown -R nginx:nginx /var/cache/nginx \
 && chown -R nginx:nginx /var/run \
 && chown -R nginx:nginx /etc/nginx/conf.d \
 && chown -R nginx:nginx /etc/nginx/templates \
 && chmod -R 755 /usr/share/nginx/html

USER nginx

EXPOSE 8082

STOPSIGNAL SIGQUIT

CMD ["nginx", "-g", "daemon off;"]

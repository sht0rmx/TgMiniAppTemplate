# --- Base Stage ---
FROM node:22-alpine AS base
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --legacy-peer-deps

# --- Development Stage ---
FROM base AS dev
COPY . .
RUN npm run type-check
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# --- Builder Stage ---
FROM base AS build
COPY . .
RUN npm run type-check
RUN npm run build

# --- Production Stage ---
FROM nginx:stable-alpine AS prod
RUN sed -i 's/application\/json json;/application\/json json webmanifest;/' /etc/nginx/mime.types

COPY <<EOF /etc/nginx/conf.d/default.conf
server {
    listen 80;
    server_tokens off;

    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files \$uri \$uri/ /index.html;

        location ~* \.(?:html|js|webmanifest)$ {
            if (\$request_filename ~* (sw\.js|index\.html|manifest\.webmanifest)$ ) {
                add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0";
            }
        }

        location ~* ^/assets/ {
            add_header Cache-Control "public, max-age=31536000, immutable";
            access_log off;
        }
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
EOF

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
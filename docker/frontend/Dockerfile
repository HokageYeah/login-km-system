FROM node:20-alpine AS builder

WORKDIR /build

COPY web/admin-frontend/package*.json ./
RUN npm ci

COPY web/admin-frontend/ ./
RUN npm run build

FROM nginx:1.27-alpine

COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /build/dist /usr/share/nginx/html

EXPOSE 5174

CMD ["nginx", "-g", "daemon off;"]

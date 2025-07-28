# Simple root Dockerfile for React frontend only
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy React app files
COPY react/package*.json ./
RUN npm ci --only=production

# Copy all React source files
COPY react/public ./public
COPY react/src ./src
COPY react/tailwind.config.js ./
COPY react/postcss.config.js ./
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY react/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

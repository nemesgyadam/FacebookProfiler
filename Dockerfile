# Simple root Dockerfile for React frontend only
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy React app files
COPY react/package*.json ./
RUN npm ci --only=production

# Copy all React files maintaining directory structure
COPY react/ ./

# Debug: List files to verify structure
RUN ls -la && ls -la src/ && ls -la src/data/

RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY react/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# Simple root Dockerfile for React frontend only
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy React app files
COPY react/package*.json ./
RUN npm ci --only=production

# Copy all React files maintaining directory structure
COPY react/ ./

# Create missing data directory and requiredFiles.js if not present
RUN mkdir -p src/data && \
    if [ ! -f src/data/requiredFiles.js ]; then \
        echo 'export const requiredFilePaths = [];' > src/data/requiredFiles.js && \
        echo 'export const requiredFilePathsSet = new Set();' >> src/data/requiredFiles.js && \
        echo 'export default requiredFilePaths;' >> src/data/requiredFiles.js; \
    fi

RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY react/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

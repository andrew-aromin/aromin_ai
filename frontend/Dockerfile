# Stage 1: Build the frontend
FROM node:20-slim AS build
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code and build
COPY . .
# Set VITE_API_BASE_URL to empty to use relative paths (prevents CORS)
ENV VITE_API_BASE_URL=""
RUN npm run build

# Stage 2: Serve the frontend
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

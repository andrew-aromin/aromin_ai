# Use a Node base image
FROM node:20-slim AS build

# Set the working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

RUN npm run build

# Use a lightweight web server to serve the production build
FROM nginx:alpine

# Copy the production build
COPY --from=build /app/dist /usr/share/nginx/html

# Support running as non-root user
# 1. Change port to 8080 (non-root users can't bind to < 1024)
# 2. Change ownership of necessary directories
RUN sed -i 's/listen\(.*\)80;/listen 8080;/' /etc/nginx/conf.d/default.conf && \
    chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/log/nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown nginx:nginx /var/run/nginx.pid

USER nginx

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
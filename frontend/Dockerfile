# Use a Node base image
FROM node:20-slim AS build

# Set the working directory
WORKDIR /app

# Copy package files and install dependencies
# Note: Installing as dev dependencies ensures tools like ESLint 
# are available for the build step
COPY package*.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

RUN npm run build

# Use a lightweight web server to serve the production build
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80 (or 3000 if mapped in docker-compose)
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
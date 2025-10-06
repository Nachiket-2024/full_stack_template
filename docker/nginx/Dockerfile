# ---------------------------- External Imports ----------------------------
# Base image providing Nginx 1.27 on Alpine Linux for lightweight web serving
FROM nginx:1.27-alpine

# ---------------------------- Copy Custom Config ----------------------------
# Copy custom Nginx configuration file into container
COPY ./docker/nginx/nginx.conf /etc/nginx/nginx.conf

# ---------------------------- Copy Frontend Build ----------------------------
# Copy the built frontend app from local 'frontend/dist' into Nginx html directory
# This assumes you have already run `npm run build` inside the frontend container
COPY ./frontend/dist /usr/share/nginx/html

# ---------------------------- Expose Ports ----------------------------
# Expose port 80 for Nginx
EXPOSE 80

# ---------------------------- CMD ----------------------------
# Start Nginx in foreground so Docker keeps container running
CMD ["nginx", "-g", "daemon off;"]

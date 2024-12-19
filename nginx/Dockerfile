FROM nginx:alpine

# Copy Nginx config and SSL certificates directly into the image
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf
COPY ./nginx/ssl/server.crt /etc/ssl/server.crt
COPY ./nginx/ssl/server.key /etc/ssl/server.key

# Copy frontend files into the image
COPY ./frontend/ /usr/share/nginx/html

# Expose Nginx logs directory
RUN mkdir -p /var/log/nginx
VOLUME ["/var/log/nginx"]

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]

FROM nginx:alpine

#copy nginx config
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

# Copy custom site configuration
COPY ./nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf

#copy SSL certificates
COPY ./nginx/ssl/server.crt /etc/ssl/server.crt
COPY ./nginx/ssl/server.key /etc/ssl/server.key


COPY ./frontend/ /usr/share/nginx/html

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
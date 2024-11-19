# Instructions

## To Run The app follow the steps

- Make sure docker is installed and running
- remove any previously active prosses `docker rm -f $(docker ps -a -q)`
- shut down all previous containers `docker-compose down -v`
- to build on production (no live updates) `docker-compose --f docker-compose.prod.yml up --build`
- to build on development (enable live udpates) `docker-compose docker-compose.dev.yml up --build`

## Explanations

### Dockerization

#### backend/Dockerfile

- Pulls a python version and prepares the python environment and runs all tasks then starts

#### nginx/Dockerfile

- Pulls nginx and prepares all need folders by copying them

#### docker-compose

Docker Compose file defines a multi-container setup for a Django application

1. **Backend:** A Django app container that applies database migrations, creates an admin user, collects static files, and serves the app via uvicorn.
2. **Nginx:** A reverse proxy server to handle client requests and serve static files.
3. **Database (PostgreSQL):** A containerized database for storing app data.
4. **Redis:** A caching layer for asynchronous tasks.
5. **Celery Worker and Beat:** Containers for task processing and periodic task scheduling.

#### nginx.conf files

This Nginx configuration sets up a reverse proxy for a Django backend and serves static files, media files, WebSocket traffic, and a static frontend. It redirects HTTP traffic to HTTPS for security and handles both standard API requests and WebSocket connections.

- **Static and Media Files:** Served directly from the /app/staticfiles/ and /app/media/ directories.
- **WebSocket Traffic:** Proxied to the Django backend at /ws/ with support for WebSocket headers.
- **API Requests:** Proxied to the backend at /api/.
- **Frontend Files:** Served from /usr/share/nginx/html/ with caching disabled.
- **HTTPS Configuration:** Includes SSL certificate and key for secure communication.

## Testing and debugging tips:

- for sending an email to test, after running container in a seperate terminal, `docker exec -it ft_transcendance_app_dev bash`, `from django.core.mail import send_mail`, `send_mail ('test mail', 'helloooooo', 'transcendence.42beirut@gmail.com', ['hussienkenaan93@gmail.com'])`
- for creating an admin user to test, after running container in a seperate terminal, `docker exec -it ft_transcendance_app_dev bash`, `python manage.py createsuperuser`
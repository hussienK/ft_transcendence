# Instructions

## To Run The app follow the steps

- Make sure docker is installed and running
- remove any previously active prosses `docker rm -f $(docker ps -a -q)`
- shut down all previous containers `docker-compose down -v`
- to build on production (no live updates) `docker-compose --f docker-compose.prod.yml up --build`
- to build on development (enable live udpates) `docker-compose docker-compose.dev.yml up --build`
- to access a container for debugging/testing `docker exec -it <container_name_or_id> /bin/bash`

## Chosen Modules

 ◦ Major module: Use a Framework as backend.
 ◦ Minor module: Use a front-end framework or toolkit.
 ◦ Minor module: Use a database for the backend.
  Major module: Standard user management, authentication, users across
 tournaments.
 • Major module: Remote players
• Minor module: User and Game Stats Dashboards.
 • Major module: Implement Two-Factor Authentication (2FA) and JWT.
• Major module: Replacing Basic Pong with Server-Side Pong and Implementing
 an API.
 • Minor module: Expanding Browser Compatibility.
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

#### DRF

DRF connects your Django models to a RESTful API, handling serialization, routing, views, and security seamless

1. **Serializers:** Convert complex data types (e.g., Django models) to JSON for API responses and validate incoming JSON data for requests.
2. **Views:** Handle HTTP methods (GET, POST, PUT, DELETE) and process requests. These can be function-based or class-based (e.g., APIView, GenericAPIView, or viewsets).
3. **Routers:** Automatically generate URL patterns for your views, especially for viewsets.
4. **Authentication & Permissions:** Provide built-in tools for securing APIs (e.g., token-based auth, session auth, or custom permissions).
5. **Browsable API:** Offers a web-based interface to test and explore your API.

#### Backend Apps

##### ft_transendance

- Contains our app's settings that tell the app how everything should behave
- Contains the routes that redirect into all other apps
- Contains ASGI the routes into websocket requests

##### Users

- Manages the users and everything related to them
- We have a few custom permissions, isEmail Verified, is2FA Enabled
- We have 2 mains db models, Friends and Friend requests
- User being Online/Offline is detected through signals on his logout/login. To make it more accurate we also use Celery to schedule auto tasks every duration to make user offline if not using the app
- Every user action passes through a Middleware to detect the Authentication Token and update the last activity accordingly
- Includes a verifyToken view for the frontend to call to make sure the token is valid and not expired before rendering any pages

##### Core

Currently Only for testing

##### Game

Under Development


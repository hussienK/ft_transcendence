# ft_transcendence Project Documentation

## Project Overview
This project involves the creation of a website for the mighty Pong contest. The site will allow users to participate in real-time multiplayer Pong games with a focus on delivering a seamless user experience and robust security.

### Key Features:
1. Real-time multiplayer Pong games.
2. User registration, authentication, and profile management.
3. Tournament management and matchmaking system.
4. Dashboards for user and game statistics.
5. Two-Factor Authentication (2FA) and JWT-based security.
6. Browser compatibility enhancements.
7. Server-side Pong game with API integration.

---

## Development Guidelines
- Use of libraries or tools providing a complete solution for a feature/module is prohibited.
- Small libraries solving unique subcomponent tasks are allowed.
- Justify the use of any library or tool not explicitly approved.

---

## Minimal Technical Requirements
1. The site must function as a single-page application.
2. Must be compatible with the latest stable version of Google Chrome.
3. The backend (if used) must be written in Django.
4. The frontend must be built using vanilla JavaScript or Bootstrap.
5. Ensure secure handling of passwords (hashed), protect against SQL injections/XSS, and use HTTPS.
6. Validate all user inputs.
7. Launch the entire application with a single command line using Docker.
8. No unhandled errors or warnings.

---

## Modules Implemented

### Major Modules:
1. **Framework as Backend**:
   - Backend developed using Django.
   - Supports database integration.

2. **Standard User Management**:
   - Secure user registration and login.
   - Unique display names, avatars, and friend lists.
   - User profiles display stats (wins/losses, match history).

3. **Remote Players**:
   - Real-time gameplay for players on separate computers.
   - Handles network issues for the best user experience.

4. **Two-Factor Authentication and JWT**:
   - Adds an extra security layer with 2FA.
   - Implements secure user authentication and authorization.

5. **Server-Side Pong and API**:
   - Server-side game logic and API for interaction.
   - Integrates with CLI and web interface.

### Minor Modules:
1. **Frontend Toolkit**:
   - Frontend developed using Bootstrap.

2. **User and Game Stats Dashboards**:
   - Dashboards for user and game statistics using data visualization techniques.

3. **Expanding Browser Compatibility**:
   - Added support for an additional browser with thorough testing.

---

## Security Considerations
1. Store passwords using a strong hashing algorithm.
2. Protect against SQL injections and XSS attacks.
3. Secure all routes and data transmissions using HTTPS.
4. Validate user inputs rigorously.
5. Store credentials and sensitive information in a `.env` file (ignored by Git).

---

## Deployment Instructions

### Prerequisites:
- Ensure Docker is installed and running on your system.

### Clean Up Active Processes:
```bash
docker rm -f $(docker ps -a -q)
```

### Shut Down Previous Containers:
```bash
docker-compose down -v
```

### Build and Run:
- **Production (no live updates):**
  ```bash
  docker-compose -f docker-compose.prod.yml up --build
  ```
- **Development (with live updates):**
  ```bash
  docker-compose -f docker-compose.dev.yml up --build
  ```

### Debugging/Testing:
To access a running container:
```bash
docker exec -it <container_name_or_id> /bin/bash
```

---

## Additional Notes
- Ensure your Docker runtime files are located in `/goinfre` or `/sgoinfre` for Linux clusters.
- Avoid bind-mount volumes if non-root UIDs are used in containers.

---

## Credits
This documentation is part of the ft_transcendence project guidelines and reflects the mandatory and additional modules implemented to deliver a functional and secure Pong contest website.


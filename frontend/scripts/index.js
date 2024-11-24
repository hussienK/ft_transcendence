let socket = null;  // Global variable to store the WebSocket connection

// Function to create a new WebSocket connection
function establishWebSocketConnection() {
  const ws_scheme = window.location.protocol === "https:" ? "ws" : "ws";
  const ws_path = `${ws_scheme}://localhost:8080/ws/updates/?token=${localStorage.getItem('accessToken')}`;

  if (socket) {
    socket.close();  // Close any existing connection
  }

  socket = new WebSocket(ws_path);

  // Add event listeners for WebSocket connection
  socket.onopen = () => {
    console.log("WebSocket connection established.");
  };

  socket.onclose = (event) => {
    console.log("WebSocket connection closed", event);
  };

  socket.onerror = (error) => {
    console.error("WebSocket error:", error);
  };

  socket.onmessage = (message) => {
    // {'type': 'Activity', 'username': user.username, 'display_name': user.display_name, 'message': 'offline'}
    
    // if (message.data["type"] === "Activity"){
    console.log(message)
      const feedContainer = document.getElementById('live-feeds');
      feedContainer.innerHTML += `<p>hello</p>`
    // }
    console.log("Received message:", message.data);
  };
}


        
async function loadPage(page) {
  try {
    const response = await axios.get(`./views/${page}.html`, {
      headers: {
        "Content-Type": "text/html",
      },
    });

    document.getElementById("main-content").innerHTML = response.data;

    if (page === "signup") {
      attachSignUpFormEventListeners();
    } else if (page === "login") {
      attachSigninFormEventListeners();
    } 

    else {
      if (!verifyUser()) {
        window.location.hash = "login";
        return;
      }

      if (page === "home") {
        attachHomeEventListeners();
      }    else if (page === 'game'){
        attachGameEventListeners();
      }else if (page === 'game2'){
        attachGameEventListeners2();
      }
      if (page === 'lobby'){
        attachLobbyEventListeners();
      }
      establishWebSocketConnection();
    }
  } catch (error) {
    console.error("Error loading page:", error);
    document.getElementById("main-content").innerHTML =
      "<p>Page not found.</p>";
  }
}

window.addEventListener("load", () => {
  const initialPage = window.location.hash.substring(1) || "home";
  loadPage(initialPage);
});
window.addEventListener("hashchange", () => {
  const page = window.location.hash.substring(1);
  loadPage(page);
});

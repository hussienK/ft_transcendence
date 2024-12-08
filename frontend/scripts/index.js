let socket = null;  // Global variable to store the WebSocket connection

function renderFeedMessage(message_formatted){
  const feedContainer = document.getElementById('live-feeds');
  let text = '';
  text += `<p style="padding: 0 8px;">`;
  text += '- '
  if (message_formatted.sender_username !== "NULL"){
    text += `<b>${message_formatted.sender_username} </b>`;
  }
  if (message_formatted.sender_displayname !== "NULL"){
    text += `<b>(${message_formatted.sender_displayname}):</b> `;
  }
  text += message_formatted.info;
  text += `<\p>`;
  feedContainer.innerHTML += text;
}

async function fetchFeed() {
  try {
      const response = await axios.get('https://localhost:8443/api/users/feed-updates/',
          {
              headers: {
                  Authorization: `Bearer ${localStorage.getItem('accessToken')}`
              }
          });
      return response.data;
  } catch (error) {
      console.log(error.response?.data?.error || "An error occurred", "danger");
  }
}

async function renderFeed(){
  const data = await fetchFeed();
  if (data)
  {
    data.forEach(element => {
      // console.log(element);
      // const message_formatted = JSON.parse(element);
      renderFeedMessage(element);
    });
  }
}

function joinMatch(messageFormatted) {
  const roomName = messageFormatted.session_id; // Extract data from the WebSocket message
  const player = messageFormatted.player;
  loadPage('game').then(() => {
      attachGameEventListeners(roomName, player); // Pass parameters to game event listeners
  });
}

function joinMatchLocal(messageFormatted) {
  const roomName = messageFormatted.session_id; // Extract data from the WebSocket message
  loadPage('game_local').then(() => {
      attachLocalGameEventListeners(roomName); // Pass parameters to game event listeners
  });
}

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
    const message_formatted = JSON.parse(message.data);
    if (message_formatted.type === 'feed')
    {
      renderFeedMessage(message_formatted);
    } else if (message_formatted.type === 'match_found')
    {
      joinMatch(message_formatted);
    }
    else if (message_formatted.type === 'match_found_local')
    {
      joinMatchLocal(message_formatted);
    }
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
      }
      if (page === "home")
      {
        await renderFeed();
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

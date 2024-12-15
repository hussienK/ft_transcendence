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


        
// Parse the hash to extract the page name and query parameters
function parseHash() {
  const hash = window.location.hash.slice(1); // Remove the '#' from the hash
  const [page, queryString] = hash.split("?"); // Split page and query parameters
  const queryParams = new URLSearchParams(queryString); // Parse query string

  const params = {};
  for (const [key, value] of queryParams.entries()) {
    params[key] = value;
  }

  return { page: page || "lobby", params }; // Default to "lobby" if no page is specified
}

// Function to load a page based on the current hash
async function loadPageFromHash() {
  const { page, params } = parseHash();
  await loadPage(page, params); // Pass the page and query parameters
}
async function loadPage(page, queryParams = {}) {
  try {
    if (!page) {
      throw new Error("Page parameter is required but not provided.");
    }

    //main pages
    if (page === "signup" || page === "login" || page === "game" || page === "game_local")
    {
      //load without feed/links
      const mainContent = document.getElementById("main-content");
      if (!mainContent) {
        throw new Error("Element with id 'main-content' not found in the DOM.");
      }
      let pageUrl = `./views/${page}.html`;
  
      if (queryParams && Object.keys(queryParams).length > 0) {
        const queryString = new URLSearchParams(queryParams).toString();
        pageUrl += `?${queryString}`;
      }
  
      const response = await axios.get(pageUrl, {
        headers: { "Content-Type": "text/html" },
      });
      mainContent.innerHTML = response.data;

      if (page === "signup") {
        attachSignUpFormEventListeners();
      } else if (page === "login") {
        attachSigninFormEventListeners();
      }
    }
    else
    {
      console.log("Verifying user...");
      const validUser = await verifyUser();
      if (!validUser) {
        console.warn("User verification failed. Redirecting to login.");
        window.location.hash = "login";
        return;
      }

      //load full content
      const homeResponse = await axios.get(`./views/home.html`, {
        headers: { "Content-Type": "text/html" },
      });
      const mainContent = document.getElementById("main-content");
      if (!mainContent) {
        throw new Error("Element with id 'main-content' not found in the DOM.");
      }
  
      mainContent.innerHTML = homeResponse.data;
  
      let pageUrl = `./views/${page}.html`;
  
      if (queryParams && Object.keys(queryParams).length > 0) {
        const queryString = new URLSearchParams(queryParams).toString();
        pageUrl += `?${queryString}`;
      }
  
      const response = await axios.get(pageUrl, {
        headers: { "Content-Type": "text/html" },
      });
      const homeDisplay = document.getElementById("home-display");
      if (!homeDisplay) {
        throw new Error("Element with id 'home-display' not found in the DOM.");
      }
      homeDisplay.innerHTML = response.data;


      // Handle specific pages
      if (page === "home") {
        loadPage("lobby");
      } else if (page === "lobby") {
        attachLobbyEventListeners();
        loadLinks("lobby");
        establishWebSocketConnection();
      } else if (page === "friends") {
        attachFriendsEventListeners();
        loadLinks("friends");
        establishWebSocketConnection();
      } else if (page === "profile") {
        if (queryParams.username) {
          attachProfileEventListeners(queryParams.username);
        } else {
          attachProfileEventListeners();
        }
        loadLinks("profile");
        establishWebSocketConnection();
      } else {
        console.warn(`No specific logic implemented for page: ${page}`);
      }
    }
  } catch (error) {
    console.error("Error loading page:", error.message || error);
    const mainContent = document.getElementById("main-content");
    if (mainContent) {
      mainContent.innerHTML = "<p>Page not found.</p>";
    } else {
      console.error("Unable to update 'main-content' because it was not found in the DOM.");
    }
  }
}


// Add event listeners for initial load and hash changes
window.addEventListener("load", loadPageFromHash);
window.addEventListener("hashchange", loadPageFromHash);
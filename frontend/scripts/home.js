function attachHomeEventListeners() {
  const lobbyLink = document.getElementById("lobby-link");
  const profileLink = document.getElementById("profile-link");
  const friendsLink = document.getElementById("friends-link");

  loadSection('lobby');

  const navItems = [profileLink, friendsLink, lobbyLink];

  async function loadSection(page = 'lobby') {
    try {
      const response = await axios.get(`./views/${page}.html`, {
        headers: {
          "Content-Type": "text/html",
        },
      });

      document.getElementById("home-display").innerHTML = response.data;

      if (page === 'lobby'){
        attachLobbyEventListeners();
      }

      if(page === "friends"){
        attachFriendsEventListeners()
        
      }

      if(page === "profile"){
        attachProfileEventListeners()
      }

    } catch (error) {
      console.error("Error loading page:", error);
      document.getElementById("main-content").innerHTML =
        "<p>Page not found.</p>";
    }
  }

  function setActiveLink(activeLink) {
    
    navItems.forEach((link) => {
      const parent = link.parentElement; // Get the parent `li` of the link
      if (link === activeLink) {
        parent.classList.remove("bg-dark"); // Remove black background
        parent.classList.add("bg-active-tab"); // Add white background
      } else {
        parent.classList.remove("bg-active-tab"); // Remove white background
        parent.classList.add("bg-dark"); // Add black background
      }
    });
  }

  lobbyLink.addEventListener("click", (e) => {
    e.preventDefault();
    setActiveLink(lobbyLink);
    loadSection("lobby");
  });

  profileLink.addEventListener("click", (e) => {
    e.preventDefault();
    setActiveLink(profileLink);
    loadSection("profile");
  });

  friendsLink.addEventListener("click", (e) => {
    e.preventDefault();
    setActiveLink(friendsLink);
    loadSection("friends");
  });
  
}

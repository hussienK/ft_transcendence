function loadLinks(current = "lobby") {
  const lobbyLink = document.getElementById("lobby-link");
  const profileLink = document.getElementById("profile-link");
  const friendsLink = document.getElementById("friends-link");

  const navItems = [profileLink, friendsLink, lobbyLink];

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

  if (current == "lobby")
  {
    setActiveLink(lobbyLink);
  }else if (current == "profile")
  {
    setActiveLink(profileLink);
  }
  else if (current == "friends")
  {
    setActiveLink(friendsLink);
  }

  lobbyLink.addEventListener("click", (e) => {
    e.preventDefault();
    setActiveLink(lobbyLink);
    window.location.hash = "lobby";
    });

  profileLink.addEventListener("click", (e) => {
    e.preventDefault();
    setActiveLink(profileLink);
    window.location.hash = "profile";
    });

  friendsLink.addEventListener("click", (e) => {
    e.preventDefault();
    setActiveLink(friendsLink);
    window.location.hash = "friends";
  });
  
}

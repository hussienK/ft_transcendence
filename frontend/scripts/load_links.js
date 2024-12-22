function loadLinks(current = "lobby") {
  const lobbyLink = document.getElementById("lobby-link");
  const profileLink = document.getElementById("profile-link");
  const friendsLink = document.getElementById("friends-link");

  lobbyLink.addEventListener("click", (e) => {
    e.preventDefault();
    window.location.hash = "lobby";
    });

  profileLink.addEventListener("click", (e) => {
    e.preventDefault();
    window.location.hash = "profile";
    });

  friendsLink.addEventListener("click", (e) => {
    e.preventDefault();
    window.location.hash = "friends";
  });
  
}

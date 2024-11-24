
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

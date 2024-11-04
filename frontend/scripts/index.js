function loadPage(page) {
  fetch(`./views/${page}.html`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Page not found");
      }
      return response.text();
    })
    .then((html) => {
      document.getElementById("main-content").innerHTML = html;
    })
    .catch((error) => {
      console.log("Error loading page:", error);
      document.getElementById("main-content").innerHTML =
        "<p>Page not found.</p>";
    });
}
window.addEventListener("load", () => {
  const initialPage = window.location.hash.substring(1) || "home";
  console.log(initialPage);
  loadPage(initialPage);
});
window.addEventListener("hashchange", () => {
  const page = window.location.hash.substring(1);
  loadPage(page);
});

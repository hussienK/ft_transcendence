function showAlert(message, type, timeout = 2000) {
    const mainContainer = document.getElementById("main-content");
  
    const alert = document.createElement("div");
  
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = "alert";
    alert.style.position = "absolute";
    alert.style.top = "10px";
    alert.style.left = "50%";
    alert.style.transform = "translateX(-50%)";
    alert.style.zIndex = "9999";
    alert.style.maxWidth = "400px";
    alert.style.textAlign = "center";
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      `;
  
    mainContainer.appendChild(alert);
  
    setTimeout(() => {
      alert.classList.remove("show");
      setTimeout(() => alert.remove(), 150);
    }, timeout);
  }
function attachSigninFormEventListeners() {
  const signinForm = document.getElementById("signinForm");

  signinForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    const username = document.getElementById("signinusername").value.trim();
    const password = document.getElementById("signinPassword").value;

    if (!username || !password) {
      showAlert("Please fill out all fields", "danger");
      return;
    }

    if (!validatePassword(password)) {
      showAlert("Please enter a valid password", "danger");
      return;
    }

    const userData = {
      username,
      password,
    };

    // signin action
    try {
      const response = await axios.post(
        "http://localhost:8000/api/users/signin/",
        userData
      );

      const accessToken = response.data.access;
      const refreshToken = response.data.refresh;
      const userInfo  = response.data.userInfo;
      localStorage.setItem("accessToken", accessToken);
      localStorage.setItem("refreshToken", refreshToken);
      localStorage.setItem("userInfo", JSON.stringify(userInfo));

      window.location.hash = "home";
    } catch (error) {
      showAlert(error.response?.data.error, "danger");
    }
  });
}

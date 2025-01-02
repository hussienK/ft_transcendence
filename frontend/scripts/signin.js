function attachSigninFormEventListeners() {
  const signinForm = document.getElementById("signinForm");
  const form2fa = document.getElementById("submit-2fa-btn");
  localStorage.clear();

  form2fa.addEventListener("click", async function (event) {
    event.preventDefault();
    const codeInput = document.getElementById("2fa-code").value; // Get 2FA code value
  
    try {
      const response = await axios.post(
        "https://localhost:8443/api/users/2fa/verify/",
        {
          code: codeInput, // Pass the 2FA code to the backend
          email: localStorage.getItem("email")
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
  
      // Destructure the tokens and user info
      const { access, refresh, userInfo } = response.data;
  
      // Store tokens and user info in localStorage
      localStorage.setItem("accessToken", access);
      localStorage.setItem("refreshToken", refresh);
      localStorage.setItem("userInfo", JSON.stringify(userInfo));
  
      // Redirect to home
      window.location.hash = "home";

      localStorage.removeItem("email");
    } catch (error) {
      const errorMessage = error.response?.data?.error || "An error occurred";
      showAlert(errorMessage, "danger");
    }
  });
  

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
        "https://localhost:8443/api/users/signin/",
        userData
      );

      if (response.data.detail == '2FA required')
      {
        console.log(response.data.email);
        localStorage.setItem("email", response.data.email);
        document.getElementById('fa-popup').classList.remove('hidden');
      }
      else
      {
        const accessToken = response.data.access;
        const refreshToken = response.data.refresh;
        const userInfo  = response.data.userInfo;
        localStorage.setItem("accessToken", accessToken);
        localStorage.setItem("refreshToken", refreshToken);
        localStorage.setItem("userInfo", JSON.stringify(userInfo));
  
        window.location.hash = "home";
      }
    } catch (error) {
      showAlert(error.response?.data.error, "danger");
    }
  });


}

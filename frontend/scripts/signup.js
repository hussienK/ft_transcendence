function attachSignUpFormEventListeners() {
  const signUpForm = document.getElementById("signupForm");

  signUpForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    const username = document.getElementById("registerUserName").value.trim();
    const displayName = document
      .getElementById("registerDisplayName")
      .value.trim();
    const email = document.getElementById("registerEmail").value.trim();
    const password = document.getElementById("registerPassword").value;
    const password2 = document.getElementById("registerPassword2").value;

    if (!username || !displayName || !email || !password || !password2) {
      showAlert("Please fill out all fields", "danger");
      return;
    }

    if (!validateEmail(email)) {
      showAlert("Please enter a valid email address", "danger");
      return;
    }

    if (!validatePassword(password)) {
      showAlert("Please enter a valid password", "danger");
      return;
    }

    if (password !== password2) {
      showAlert("Passwords do not match", "danger");
      return;
    }

    const userData = {
      username,
      display_name: displayName,
      email,
      password,
      password2,
    };

    // signup action
    try {
      const response = await axios.post(
        "http://localhost:8000/api/users/register/",
        userData
      );

      console.log(response);
      showAlert("SignUp Successfull!", "success");
    } catch (error) {
      console.error(
        "Error during signup:",
        error.response?.data || error.message
      );
      showAlert(error.response?.data.error, "danger");
    }
  });
}

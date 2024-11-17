async function verifyUser() {
  const accessToken = localStorage.getItem("accessToken");
  console.log(accessToken);
  if (!accessToken) {
    window.location.hash = "login";
    localStorage.clear();
    console.log("Invalid User token");
    return;
  }

  try {
    const response = await axios.post(
      "http://127.0.0.1:8000/api/users/token/verify/",
      {},
      {
        headers: {
          Authorization: `Bearer ${accessToken}`, // Authorization header with Bearer token
        },
      }
    );
    console.log("valid user");
  } catch (error) {
    console.log("Invalid User token");
    window.location.hash = "login";
    localStorage.clear();
  }
}

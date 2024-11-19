async function verifyUser() {
  const accessToken = localStorage.getItem("accessToken");
  const refreshToken = localStorage.getItem("refreshToken");

  if (!accessToken || !refreshToken) {
    window.location.hash = "login";
    localStorage.clear();
    console.log("Invalid User tokens");
    return;
  }

  try {
    const response = await axios.post(
      "https://localhost/api/users/token/verify/",
      {},
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );
    console.log("Valid user");
  } catch (error) {
    console.log("Access token expired or invalid. Attempting refresh...");

    try {
      const refreshResponse = await axios.post(
        "http://localhost/api/users/token/refresh/",
        {
          refresh: refreshToken,
        }
      );

      const newAccessToken = refreshResponse.data.access;
      localStorage.setItem("accessToken", newAccessToken);

      console.log("Access token refreshed successfully");

    } catch (refreshError) {
      console.log("Invalid refresh token. Redirecting to login...");
      window.location.hash = "login";
      localStorage.clear();
    }
  }
}

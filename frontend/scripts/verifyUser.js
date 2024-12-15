async function verifyUser() {
  const accessToken = localStorage.getItem("accessToken");
  const refreshToken = localStorage.getItem("refreshToken");

  if (!accessToken || !refreshToken) {
    window.location.hash = "login";
    localStorage.clear();
    console.log("Invalid User tokens");
    return false;
  }

  try {
    const response = await axios.post(
      "https://localhost:8443/api/users/token/verify/",
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
        "https://localhost:8443/api/users/token/refresh/",
        {
          refresh: refreshToken,
        }
      );

      const newAccessToken = refreshResponse.data.access;
      const newRefreshToken = refreshResponse.data.refresh;
      localStorage.setItem("accessToken", newAccessToken);
      localStorage.setItem("refreshToken", newRefreshToken);

      console.log("Access token refreshed successfully");

    } catch (refreshError) {
      console.log("Invalid refresh token. Redirecting to login...");
      window.location.hash = "login";
      localStorage.clear();
      return false;
    }
  }

  return true
}

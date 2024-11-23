 function attachAddFriendsEventListeners(){
	document.getElementById("sendFriendRequestButton").addEventListener("click", async () => {

		const username = document.getElementById("sendFriendRequestInput").value;
		try {
			// Await the axios.post call
			const response = await axios.post('https://localhost:8443/api/users/friend-request/send/', {
				receiver: username
			},
			{
				headers: {
					Authorization: `Bearer ${localStorage.getItem('accessToken')}`
				}
			});
			showAlert("Friend Request sent Successfully", "success");
		} catch (error) {
			// Handle errors properly
			console.error(error);
			showAlert(error.response?.data?.error || "An error occurred", "danger");
		}
	});
}
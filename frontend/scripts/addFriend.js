 function attachAddFriendsEventListeners(){
	document.getElementById("sendFriendRequestButton").addEventListener("click", async () => {
		const username = document.getElementById("sendFriendRequestInput").value;
		await addFriend(username);
	});
}
function populateSuggestedFriendsUI(friends) {
    const container = document.querySelector('#suggested-friends-container');
    container.innerHTML = ''; // Clear existing content

    friends.forEach(friend => {
        const friendElement = document.createElement('div');
        friendElement.classList.add('friend-suggestion');
        friendElement.innerHTML = `
            <p>${friend.friend}</p>
            <button class="btn btn-primary add-friend-btn" data-id="${friend.id}">Add Friend</button>
        `;
        container.appendChild(friendElement);
    });

    // Attach event listeners to the "Add Friend" buttons
    // attachAddFriendEventListeners();
}

async function attachSuggestedFriendsEven1tListeners(){
	
	 async function fetchFriendSuggestions() {
		const token = localStorage.getItem('accessToken');
	
		try {
			// Await the axios.post call
			const response = await axios.get('https://localhost:8443/api/users/friend-request/received/',
			{
				headers: {
					Authorization: `Bearer ${token}` 
				}
			});
			return response.data;
		} catch (error) {
		
			showAlert(error.response?.data?.error || "An error occurred", "danger");
		}
	}
	const friends = await fetchFriendSuggestions();
	populateSuggestedFriendsUI(friends);
}
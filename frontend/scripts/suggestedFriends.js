function populateSuggestedFriendsUI(friends) {
    const container = document.querySelector('#suggested-friends-container');
    container.innerHTML = ''; // Clear existing content

    friends.forEach(friend => {
        const friendElement = document.createElement('div');
        friendElement.classList.add('friend-suggestion');
        friendElement.innerHTML = `
            <div class="friend-avatar">
                <img src="./avatar2.png" alt="${"a"}'s avatar">
            </div>
            <div class="friend-info">
                <p class="friend-displayname">${friend.display_name}</p>
                <p class="friend-username">${friend.username}</p>
            </div>
			<div style="margin-left: auto;">
			 <button class="btn btn-danger decline-friend-btn" data-id="${friend.id}">Decline</button>
             <button class="btn btn-success add-friend-btn" data-id="${friend.id}">Accept</button>
			<div>
        `;
        container.appendChild(friendElement);
    });

	const acceptButtons = document.querySelectorAll('.add-friend-btn');
    const declineButtons = document.querySelectorAll('.decline-friend-btn');

    acceptButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            const friendRequestId = e.target.getAttribute('data-id');
            try {
                const response = await axios.post('https://localhost:8443/api/users/friend-request/accept/', {
                    friend_request_id: friendRequestId
                }, {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('accessToken')}`
                    }
                });
                showAlert('Friend request accepted!', 'success');
                e.target.closest('.friend-suggestion').remove();
            } catch (error) {
                showAlert(error.response?.data?.error || "An error occurred", 'danger');
            }
        });
    });

    declineButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            const friendRequestId = e.target.getAttribute('data-id');
            try {
                const response = await axios.post('https://localhost:8443/api/users/friend-request/decline/', {
                    friend_request_id: friendRequestId
                }, {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('accessToken')}`
                    }
                });
                showAlert('Friend request declined!', 'warning');
                e.target.closest('.friend-suggestion').remove();
            } catch (error) {
                showAlert(error.response?.data?.error || "An error occurred", 'danger');
            }
        });
    });
}

// const dummyFriendSuggestions = [
// 	{username: "John Doe1", displayname: "John Doe1", friend_request_id: 1, avatar: ""},
// 	{username: "John Doe2", displayname: "John Doe2", friend_request_id: 2, avatar: ""},
// 	{username: "John Doe3", displayname: "John Doe3", friend_request_id: 3, avatar: ""},
// 	{username: "John Doe4", displayname: "John Doe4", friend_request_id: 4, avatar: ""},
// 	{username: "John Doe5", displayname: "John Doe5", friend_request_id: 5, avatar: ""}
// ]
async function attachSuggestedFriendsEven1tListeners(){
	
	 async function fetchFriendSuggestions() {
		const token = localStorage.getItem('accessToken');
	
		try {
			const response = await axios.get('https://localhost:8443/api/users/friend-request/received/',
			{
				headers: {
					Authorization: `Bearer ${token}` 
				}
			});
			return response.data;
			// return dummyFriendSuggestions;
		} catch (error) {
		
			showAlert(error.response?.data?.error || "An error occurred", "danger");
		}
	}
	const friends = await fetchFriendSuggestions();
	populateSuggestedFriendsUI(friends);
}
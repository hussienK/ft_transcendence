function populatePendingFriendsUI(friends) {
    const container = document.querySelector('#pending-friends-container');
    container.innerHTML = ''; // Clear existing content

    friends.forEach(friend => {
        const friendElement = document.createElement('div');
        friendElement.classList.add('pending-friend');
        friendElement.innerHTML = `
            <div class="friend-avatar">
                <img src="./avatar2.png" alt="${"a"}'s avatar">
            </div>
            <div class="friend-info">
                <p class="friend-displayname">${friend.displayname}</p>
                <p class="friend-username">${friend.username}</p>
            </div>
			<div style="margin-left: auto;">
			 <button class="btn btn-danger cancel-friend-btn" data-id="${friend.friend_request_id}">Cancel</button>
            
			<div>
        `;
        container.appendChild(friendElement);
    });

	const declineButtons = document.querySelectorAll('.cancel-friend-btn');

	declineButtons.forEach((declineButton) => {
		declineButton.addEventListener('click', async (e) => {
			const friendRequestId = e.target.getAttribute('data-id');
			try {
				const response = await axios.post('https://localhost:8443/api/users/friend-request/accept/', {
					friend_request_id: friendRequestId,
				},{
					headers: {
                        Authorization: `Bearer ${localStorage.getItem('accessToken')}`
                    }
				});
				showAlert('Friend request accepted!', 'success');
                e.target.closest('.pending-friend').remove();
			} catch (error) {
				
			}
		})
	})
}

const dummyPendingFriends = [
	{username: "John Doe1", displayname: "John Doe1", friend_request_id: 1, avatar: ""},
	{username: "John Doe2", displayname: "John Doe2", friend_request_id: 2, avatar: ""},
	{username: "John Doe3", displayname: "John Doe3", friend_request_id: 3, avatar: ""},
	{username: "John Doe4", displayname: "John Doe4", friend_request_id: 4, avatar: ""},
]
async function attachPendingFriendsEventListeners(){
	
	 async function fetchPendingFriends() {
	
		try {
	
			// const response = await axios.get('https://localhost:8443/api/users/friend-request/sent/',
			// {
			// 	headers: {
            //             Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            //         }
			// });
			// return response.data;
			return dummyPendingFriends;
		} catch (error) {
			showAlert(error.response?.data?.error || "An error occurred", "danger");
		}
	}
	const friends = await fetchPendingFriends();
	populatePendingFriendsUI(friends);
}
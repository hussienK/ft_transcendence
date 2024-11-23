function populateOnlineFriendsUI(friends) {
    const container = document.querySelector('#online-friends-container');
    container.innerHTML = ''; // Clear existing content

    friends.forEach(friend => {
        const friendElement = document.createElement('div');
        friendElement.classList.add('online-friend');
        friendElement.innerHTML = `
            <div class="friend-avatar">
                <img src="./avatar2.png" alt="${"a"}'s avatar">
            </div>
            <div class="friend-info">
                <p class="friend-displayname">${friend.displayname}</p>
                <p class="friend-username">${friend.username}</p>
            </div>
			<div style="margin-left: auto;">
			 <button class="btn btn-primary viewProfile-btn" data-id="${friend.username}">Profile</button>
			 <button class="btn btn-danger unFriend-btn" data-id="${friend.username}">UnFriend</button>
			<div>
        `;
        container.appendChild(friendElement);
    });

	const profileButtons = document.querySelectorAll('.viewProfile-btn');
    const unFriendButtons = document.querySelectorAll('.unFriend-btn');

    profileButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            const friendUsername = e.target.getAttribute('data-id');
            try {
                const response = await axios.get(`https://localhost:8443/api/users/profile/${friendUsername}/`, {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('accessToken')}`
                    }
                });
                showAlert('Profile fetched!', 'success');
            } catch (error) {
                showAlert(error.response?.data?.error || "An error occurred", 'danger');
            }
        });
    });

    unFriendButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            const friendRequestId = e.target.getAttribute('data-id');
            try {
                const response = await axios.post('https://localhost:8443/api/users/friends/unfriend/', {
                    friend_request_id: friendRequestId
                }, {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('accessToken')}`
                    }
                });
                showAlert('unfriended successfully!', 'warning');
                e.target.closest('.friend-suggestion').remove();
            } catch (error) {
                showAlert(error.response?.data?.error || "An error occurred", 'danger');
            }
        });
    });
}

const dummyOnlineFriends = [
	{username: "John Doe1", displayname: "John Doe1",  avatar: ""},
	{username: "John Doe2", displayname: "John Doe2",  avatar: ""},
	{username: "John Doe3", displayname: "John Doe3",  avatar: ""},
	{username: "John Doe4", displayname: "John Doe4",  avatar: ""},
   
]
async function attachOnlineFriendsEventListeners(){
	
	 async function fetchOnlineFriends() {
	
	
		try {
	
			// const response = await axios.get('https://localhost:8443/api/users/friend-request/received/',
			// {
			// 	headers: {
            //             Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            //         }
			// });
			// return response.data;
			return dummyOnlineFriends;
		} catch (error) {
		
			showAlert(error.response?.data?.error || "An error occurred", "danger");
		}
	}
	const friends = await fetchOnlineFriends();
	populateOnlineFriendsUI(friends);
}
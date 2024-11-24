function populatePendingFriendsUI(friends) {
    const container = document.querySelector('#pending-friends-container');
    container.innerHTML = ''; 

    friends.forEach(friend => {
        const friendElement = document.createElement('div');
        friendElement.classList.add('pending-friend');
        friendElement.innerHTML = `
            <div class="friend-avatar">
                <img src="./avatar2.png" alt="${"a"}'s avatar">
            </div>
            <div class="friend-info">
                <p class="friend-displayname">${friend.display_name}</p>
                <p class="friend-username">${friend.username}</p>
            </div>
			<div style="margin-left: auto;">
			 <button class="btn btn-danger cancel-friend-btn" data-id="${friend.id}">Cancel</button>
            
			<div>
        `;
        container.appendChild(friendElement);
    });

	const declineButtons = document.querySelectorAll('.cancel-friend-btn');

	declineButtons.forEach((declineButton) => {
		declineButton.addEventListener('click', async (e) => {
			const friendRequestId = e.target.getAttribute('data-id');
			await cancelFriendRequest(friendRequestId);
            e.target.closest('.pending-friend').remove();
		})
	})
}

async function attachPendingFriendsEventListeners(){
	const friends = await fetchPendingFriends();
	populatePendingFriendsUI(friends);
}
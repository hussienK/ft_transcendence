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
            await acceptFriendRequest(friendRequestId);
        });
    });

    declineButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            const friendRequestId = e.target.getAttribute('data-id');
            await delineFriendRequest(friendRequestId);
            e.target.closest('.friend-suggestion').remove();
        });
    });
}

async function attachSuggestedFriendsEven1tListeners(){
	
	const friends = await fetchFriendSuggestions();
	populateSuggestedFriendsUI(friends);
}
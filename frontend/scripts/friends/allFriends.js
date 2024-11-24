function populateAllFriendsUI(friends) {
    const container = document.querySelector('#all-friends-container');
    container.innerHTML = ''; // Clear existing content

    friends.forEach(friend => {
        const friendElement = document.createElement('div');
        friendElement.classList.add('all-friend');
        friendElement.innerHTML = `
            <div class="friend-avatar">
                <img src="./avatar2.png" alt="${"a"}'s avatar">
            </div>
            <div class="friend-info">
                <p class="friend-displayname">${friend.display_name}</p>
                <p class="friend-username">${friend.username}</p>
            </div>
			<div style="margin-left: auto;">
            <button class="btn btn-primary viewProfile-btn" data-id="${friend.id}">Profile</button>
			 <button class="btn btn-danger unFriend-btn" data-id="${friend.id}">UnFriend</button>
			<div>
        `;
        container.appendChild(friendElement);
    });

	const profileButtons = document.querySelectorAll('.viewProfile-btn');
    const unFriendButtons = document.querySelectorAll('.unFriend-btn');

    profileButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            const friendRequestId = e.target.getAttribute('data-id');
            const profileInfo = await fetchProfile(friendRequestId);
        });
    });

    unFriendButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            const friendRequestId = e.target.getAttribute('data-id');
            await unFriend(friendRequestId);
            e.target.closest('.online-friend').remove();
        });
    });
}

async function attachAllFriendsEventListeners(){
	const friends = await fetchAllFriends();
	populateAllFriendsUI(friends);
}
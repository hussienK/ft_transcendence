function populateOnlineFriendsUI(friends) {
    const container = document.querySelector('#online-friends-container');
    container.innerHTML = ''; // Clear existing content

    friends.forEach(friend => {
        const friendElement = document.createElement('div');
        friendElement.classList.add('online-friend');
        friendElement.innerHTML = `
            <div class="friend-avatar">
                <img src="./assets/default_avatar.png" alt="${"a"}'s avatar">
            </div>
            <div class="friend-info">
                <p class="friend-displayname">${friend.display_name}</p>
                <p class="friend-username">${friend.username}</p>
            </div>
			<div style="margin-left: auto;">
			 <button class="btn btn-primary viewProfile-btn" data-id="${friend.username}">Profile</button>
			 <button class="btn btn-danger unFriend-btn" data-id="${friend.id}">UnFriend</button>
			<div>
        `;
        container.appendChild(friendElement);
    });

	const profileButtons = document.querySelectorAll('.viewProfile-btn');
    const unFriendButtons = document.querySelectorAll('.unFriend-btn');

    profileButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            const friendId = e.target.getAttribute('data-id');
            try {
                const response = await axios.get(`../views/profile.html`, {
                  headers: {
                    "Content-Type": "text/html",
                  },
                });
                document.getElementById("home-display").innerHTML = response.data;
                attachProfileEventListeners(friendId);
              } catch (error) {
                console.error("Error loading page:", error);
                document.getElementById("main-content").innerHTML =
                  "<p>Page not found.</p>";
              }
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


async function attachOnlineFriendsEventListeners(){
	const friends = await fetchOnlineFriends();
	populateOnlineFriendsUI(friends);
}
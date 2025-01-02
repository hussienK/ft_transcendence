function populateAllFriendsUI(friends) {
    const container = document.querySelector('#all-friends-container');
    container.innerHTML = ''; // Clear existing content

    friends.forEach(friend => {
        const friendElement = document.createElement('div');
        friendElement.classList.add('all-friend', 'neon-box', 'd-flex', 'align-items-center', 'p-3');
        friendElement.style.marginBottom = '10px';
        friendElement.innerHTML = `
            <div class="friend-avatar">
                <img src="${friend.avatar}" alt="${friend.display_name}'s avatar" 
                     class="rounded-circle neon-avatar">
            </div>
            <div class="friend-info ms-3">
                <p class="friend-displayname text-neon-blue mb-0">${friend.display_name}</p>
                <p class="friend-username text-light">${friend.username}</p>
            </div>
            <div class="ms-auto d-flex gap-2">
                <button class="btn neon-btn-green viewProfile-btn" data-id="${friend.username}">Profile</button>
                <button class="btn neon-btn-pink unFriend-btn" data-id="${friend.id}">Unfriend</button>
            </div>
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
                window.location.hash = "profile?username=" + friendId;
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
            e.target.closest('.all-friend').remove();
        });
    });
}

async function attachAllFriendsEventListeners() {
    const friends = await fetchAllFriends();
    populateAllFriendsUI(friends);
}

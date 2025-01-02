function populatePendingFriendsUI(friends) {
    const container = document.querySelector('#pending-friends-container');
    container.innerHTML = ''; // Clear existing content

    friends.forEach(friend => {
        const friendElement = document.createElement('div');
        friendElement.classList.add('pending-friend', 'neon-box', 'd-flex', 'align-items-center', 'p-3');
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
                <button class="btn neon-btn-pink cancel-friend-btn" data-id="${friend.id}">Cancel</button>
            </div>
        `;
        container.appendChild(friendElement);
    });

    const cancelButtons = document.querySelectorAll('.cancel-friend-btn');

    cancelButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            const friendRequestId = e.target.getAttribute('data-id');
            await cancelFriendRequest(friendRequestId);
            e.target.closest('.pending-friend').remove();
        });
    });
}

async function attachPendingFriendsEventListeners() {
    const friends = await fetchPendingFriends();
    populatePendingFriendsUI(friends);
}

function populateSuggestedFriendsUI(friends) {
    const container = document.querySelector('#suggested-friends-container');
    container.innerHTML = ''; // Clear existing content

    friends.forEach(friend => {
        const friendElement = document.createElement('div');
        friendElement.classList.add('friend-suggestion', 'neon-box', 'd-flex', 'align-items-center', 'p-3');
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
                <button class="btn neon-btn-pink decline-friend-btn" data-id="${friend.id}">Decline</button>
                <button class="btn neon-btn-green add-friend-btn" data-id="${friend.id}">Accept</button>
            </div>
        `;
        container.appendChild(friendElement);
    });

    const acceptButtons = document.querySelectorAll('.add-friend-btn');
    const declineButtons = document.querySelectorAll('.decline-friend-btn');

    acceptButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            const friendRequestId = e.target.getAttribute('data-id');
            await acceptFriendRequest(friendRequestId);
            e.target.closest('.friend-suggestion').remove();
        });
    });

    declineButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            const friendRequestId = e.target.getAttribute('data-id');
            await declineFriendRequest(friendRequestId);
            e.target.closest('.friend-suggestion').remove();
        });
    });
}

async function attachSuggestedFriendsEventListeners() {
    const friends = await fetchFriendSuggestions();
    populateSuggestedFriendsUI(friends);
}

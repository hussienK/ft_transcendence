async function fetchOnlineFriends() {
    try {
        const response = await axios.get('https://localhost:8443/api/users/friends/online/',
            {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('accessToken')}`
                }
            });
        return response.data;
    } catch (error) {
        console.log(error.response?.data?.error || "An error occurred", "danger");
    }
}

async function fetchAllFriends() {
    try {
        const response = await axios.get('https://localhost:8443/api/users/friends/',
            {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('accessToken')}`
                }
            });
        return response.data;
    } catch (error) {
        console.log(error.response?.data?.error || "An error occurred", 'danger');
    }
}

async function fetchPendingFriends() {
    try {
        const response = await axios.get('https://localhost:8443/api/users/friend-request/sent/',
        {
            headers: {
                    Authorization: `Bearer ${localStorage.getItem('accessToken')}`
                }
        });
        return response.data;
    } catch (error) {
        console.log(error.response?.data?.error || "An error occurred", 'danger');
    }
}

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
    } catch (error) {
        console.log(error.response?.data?.error || "An error occurred", 'danger');
    }
}

async function unFriend(friendRequestId) {
    try {
        const response = await axios.post('https://localhost:8443/api/users/friends/unfriend/', {
            friend_request_id: friendRequestId
        }, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        });
    } catch (error) {
        console.log(error.response?.data?.error || "An error occurred", 'danger');
    }
}

async function addFriend(username) {
    try {
        const response = await axios.post('https://localhost:8443/api/users/friend-request/send/', {
            receiver: username
        },
        {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        });
        showAlert("Friend Request sent Successfully", "success");
    } catch (error) {
        console.error(error.response?.data?.error || "An error occurred", "danger");
    }    
}

async function cancelFriendRequest(friendRequestId) {
    try {
        const response = await axios.post('https://localhost:8443/api/users/friend-request/cancel/', {
            friend_request_id: friendRequestId,
        },{
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        });
    } catch (error) {
        console.log(error.response?.data?.error || "An error occurred", 'danger');
    }
}

async function acceptFriendRequest(friendRequestId) {
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
}

async function delineFriendRequest(friendRequestId) {
    try {
        const response = await axios.post('https://localhost:8443/api/users/friend-request/decline/', {
            friend_request_id: friendRequestId
        }, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        });
    } catch (error) {
        console.log(error.response?.data?.error || "An error occurred", 'danger');
    }
}

async function fetchProfile(friendName){
    try {
        if (friendName === -42)
        {
            const response = await axios.get(`https://localhost:8443/api/users/profile/`, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('accessToken')}`
                }
            });
            return response.data;
        }
        const response = await axios.get(`https://localhost:8443/api/users/profile/${friendName}/`, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        });
        return response.data;

    } catch (error) {
        console.log(error.response?.data?.error || "An error occurred", 'danger');
    }
}

async function fetchStats(friendName){
    try {
        if (friendName === -42)
        {
            const response = await axios.get(`https://localhost:8443/api/users/match-history/`, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('accessToken')}`
                }
            });
            return response.data;
        }
        const response = await axios.get(`https://localhost:8443/api/users/match-history/${friendName}/`, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        });
        return response.data;

    } catch (error) {
        console.log(error.response?.data?.error || "An error occurred", 'danger');
    }
}

async function fetchMatchHistory(friendName){
    try {
        if (friendName === -42)
        {
            const response = await axios.get(`https://localhost:8443/api/users/match-history/`, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('accessToken')}`
                }
            });
            return response.data;
        }
        const response = await axios.get(`https://localhost:8443/api/users/match-history/${friendName}/`, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        });
        return response.data;

    } catch (error) {
        console.log(error.response?.data?.error || "An error occurred", 'danger');
    }
}
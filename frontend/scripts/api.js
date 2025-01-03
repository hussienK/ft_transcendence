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
        showAlert('Friend removed!', 'success');
    } catch (error) {
        showAlert(error.response?.data?.error || "An error occurred", 'danger');
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
        showAlert("Friend request sent successfully", "success");
    } catch (error) {
        showAlert(error.response?.data?.error || "An error occurred", "danger");
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
        showAlert('Friend request cancelled!', 'success');
    } catch (error) {
        showAlert(error.response?.data?.error || "An error occurred", 'danger');
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
        showAlert('Friend request declined!', 'success');
    } catch (error) {
        showAlert(error.response?.data?.error || "An error occurred", 'danger');
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
            const response = await axios.get(`https://localhost:8443/api/users/stats/`, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('accessToken')}`
                }
            });
            return response.data;
        }
        const response = await axios.get(`https://localhost:8443/api/users/stats/${friendName}/`, {
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

async function fetchRank(){
    try{
        const response = await axios.get(`https://localhost:8443/api/users/player-rank/`, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        });
        return response.data;
    } catch (error) {
        console.log(error.response?.data?.error || "An error occurred", 'danger');
    }
}

async function startLocalGame(){
    try{
        const response = await axios.post('https://localhost:8443/api/game/join-local/', {
        }, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        });
        return response.data;
    } catch (error) {
        console.log(error.response?.data?.error || "An error occurred", 'danger');
    }
}

async function logout(){
    try{
        const response = await axios.post('https://localhost:8443/api/users/logout/', {
            refresh: localStorage.getItem('refreshToken')
        }, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        });
        return true;
    } catch (error) {
        showAlert(error.response?.data?.error || "An error occurred", 'danger');
        return false;
    }
    return false;
}

async function updateProfile(data){
    try{
        const response = await axios.put('https://localhost:8443/api/users/profile/',   data,
            {
              headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
              },
            }
          );
          return response
    } catch (error) {
        showAlert(error.response?.data?.error || "An error occurred", 'danger');
    }
}

async function setup2fa(){
    try{
        const response = await axios.post('https://localhost:8443/api/users/2fa/setup/', {
            refresh: localStorage.getItem('refreshToken')
        }, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        });
        return true;
    } catch (error) {
        showAlert(error.response?.data?.error || "An error occurred", 'danger');
        return false;
    }
}

async function deleteAccount() {
    try {
        const response = await axios.delete('https://localhost:8443/api/users/delete/', {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
            },
            data: { // Axios allows sending data in DELETE requests via the `data` key
                refresh: localStorage.getItem('refreshToken'),
            }
        });

        return true; // Account deletion was successful
    } catch (error) {
        showAlert(error.response?.data?.error || "An error occurred", 'danger');
        return false; // Account deletion failed
    }
}

async function fetchMatch(matchId){
    try {
        const response = await axios.get(`https://localhost:8443/api/users/match/${matchId}/stats/`, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        });
        return response.data;

    } catch (error) {
        console.log(error.response?.data?.error || "An error occurred", 'danger');
    }
}
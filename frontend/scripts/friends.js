function attachFriendsEventListeners() {
	console.log("hi")
	const onlineLink = document.getElementById("onlineFriends-link");
	const allLink = document.getElementById("allFriends-link");
	const pendingLink = document.getElementById("pendingFriends-link");
	const suggestionsLink = document.getElementById("suggestionFriends-link");
	const addFriendLink = document.getElementById("addFriendLink");

	const friendsTabs = [onlineLink, allLink, pendingLink, suggestionsLink, addFriendLink];
  
	async function loadSection(page) {
	  try {
		const response = await axios.get(`./views/${page}.html`, {
		  headers: {
			"Content-Type": "text/html",
		  },
		});
		
		document.getElementById("friends-page-main").innerHTML = response.data;
		if (page === "addFriend"){
			attachAddFriendsEventListeners()
		}

	  } catch (error) {
		console.error("Error loading page:", error);
		document.getElementById("friends-page-main").innerHTML =
		  "<p>Page not found.</p>";
	  }
	}
  
	function setActiveLink(activeLink) {
		friendsTabs.forEach((link) => {
		  const parent = link.closest('li'); // Get the parent `li` of the link
		  if (link === activeLink && link !== addFriendLink) {
			parent.classList.add("bg-active-tab"); // Add white background to active tab
		  } else {
			parent.classList.remove("bg-active-tab"); // Remove active background from inactive tabs
			
		  }
		});
	  }
  
	onlineLink.addEventListener("click", (e) => {
	  e.preventDefault();
	  setActiveLink(onlineLink);
	  loadSection("onlineFriends");
	});
  
	allLink.addEventListener("click", (e) => {
	  e.preventDefault();
	  setActiveLink(allLink);
	  loadSection("allFriends");
	});
  
	pendingLink.addEventListener("click", (e) => {
		e.preventDefault();
		setActiveLink(pendingLink);
		loadSection("pendingFriends");
	  });
	
	  suggestionsLink.addEventListener("click", (e) => {
		e.preventDefault();
		setActiveLink(suggestionsLink);
		loadSection("suggestedFriends");
	  });

	  addFriendLink.addEventListener("click", (e) => {
		e.preventDefault();
		setActiveLink(addFriendLink);
		loadSection("addFriend");
	  });
  }

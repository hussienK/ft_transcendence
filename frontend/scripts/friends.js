function attachFriendsEventListeners() {
	// Select all navigation links
	const onlineLink = document.getElementById("onlineFriends-link");
	const allLink = document.getElementById("allFriends-link");
	const pendingLink = document.getElementById("pendingFriends-link");
	const suggestionsLink = document.getElementById("suggestedFriends-link");
	const addFriendLink = document.getElementById("addFriend-link");
  
	const friendsTabs = [onlineLink, allLink, pendingLink, suggestionsLink, addFriendLink];
  
	// Function to load the correct subsection based on the query parameter
	async function loadSection(subsection) {
	  try {
		const response = await axios.get(`./views/friends/${subsection}.html`, {
		  headers: {
			"Content-Type": "text/html",
		  },
		});
		// Update the content of the friends page main section
		document.getElementById("friends-page-main").innerHTML = response.data;
  
		// Attach specific event listeners based on the subsection
		if (subsection === "addFriend") {
		  attachAddFriendsEventListeners();
		} else if (subsection === "suggestedFriends") {
		  attachSuggestedFriendsEventListeners();
		} else if (subsection === "pendingFriends") {
		  attachPendingFriendsEventListeners();
		} else if (subsection === "allFriends") {
		  attachAllFriendsEventListeners();
		} else {
		  attachOnlineFriendsEventListeners();
		}
	  } catch (error) {
		console.error("Error loading subsection:", error);
		document.getElementById("friends-page-main").innerHTML =
		  "<p>Subsection not found.</p>";
	  }
	}
  
	// Function to highlight the active link
	function setActiveLink(activeLink) {
	  friendsTabs.forEach((link) => {
		const parent = link.closest("li"); // Get the parent `li` of the link
		if (link === activeLink && link !== addFriend-link) {
		  parent.classList.add("bg-active-tab"); // Add active class to the current tab
		} else {
		  parent.classList.remove("bg-active-tab"); // Remove active class from other tabs
		}
	  });
	}
  
	// Add event listeners for the navigation links
	onlineLink.addEventListener("click", (e) => {
	  e.preventDefault();
	  window.location.hash = "friends?subsection=onlineFriends";
	});
  
	allLink.addEventListener("click", (e) => {
	  e.preventDefault();
	  window.location.hash = "friends?subsection=allFriends";
	});
  
	pendingLink.addEventListener("click", (e) => {
	  e.preventDefault();
	  window.location.hash = "friends?subsection=pendingFriends";
	});
  
	suggestionsLink.addEventListener("click", (e) => {
	  e.preventDefault();
	  window.location.hash = "friends?subsection=suggestedFriends";
	});
  
	addFriendLink.addEventListener("click", (e) => {
	  e.preventDefault();
	  window.location.hash = "friends?subsection=addFriend";
	});
  
	// Function to handle hash change and load the correct subsection
	function handleHashChange() {
	  const { page, params } = parseHash();
	  if (page === "friends") {
		const subsection = params.subsection || "onlineFriends"; // Default to "onlineFriends"
		setActiveLink(
		  friendsTabs.find((link) => link.id === `${subsection}-link`) || onlineLink
		);
		loadSection(subsection);
	  }
	}
  
	// Load the default subsection on initial page load
	handleHashChange(); // Call on initial load
  }
  
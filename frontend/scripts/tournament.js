function attachTournamentEventListeners() {
	let tournamentId = null;
	let currentPlayerIndex = 1;
	let aliases = [];
	let matches = [];
	let currentMatchIndex = 0;

	document.getElementById("bracket-tournament").style.display = "none";

	const headers = {
		Authorization: `Bearer ${localStorage.getItem('accessToken')}`
	};

	// 1. Create Tournament
	document.getElementById("startTournamentButton").addEventListener("click", async () => {
		try {
			const response = await axios.post("/api/game/tournament/create/", {}, { headers });
			const data = response.data;
			if (data.status === "tournament_created") {
				tournamentId = data.tournament_id;
				document.getElementById("startTournamentButton").classList.add("hidden");
				document.getElementById("aliasInputContainer").classList.remove("hidden");
				document.getElementById("playerNumber").innerText = currentPlayerIndex;
			}
		} catch (error) {
			console.error("Error creating tournament:", error);
		}
	});

	// 2. Register Aliases
	document.getElementById("submitAliasButton").addEventListener("click", async () => {
		const aliasInput = document.getElementById("aliasInput").value.trim();
		if (!aliasInput) {
			document.getElementById("aliasPromptMessage").innerText = "Alias cannot be empty.";
			return;
		}

		try {
			const response = await axios.post(`/api/game/tournament/${tournamentId}/register/`,
				{ alias: aliasInput },
				{ headers }
			);

			const data = response.data;
			if (data.status === "registered") {
				aliases.push(aliasInput);
				currentPlayerIndex++;

				// Prompt next player or start the tournament
				if (currentPlayerIndex <= 4) {
					document.getElementById("playerNumber").innerText = currentPlayerIndex;
					document.getElementById("aliasInput").value = "";
					document.getElementById("aliasPromptMessage").innerText = "";
				} else {
					document.getElementById("aliasInputContainer").classList.add("hidden");
					await startTournament();
				}
			} else {
				document.getElementById("aliasPromptMessage").innerText = data.error || "An error occurred.";
			}
		} catch (error) {
			console.error("Error registering alias:", error);
		}
	});

	// 3. Start Tournament
	async function startTournament() {
		try {
			const response = await axios.post(`/api/game/tournament/${tournamentId}/start/`, {}, { headers });
			const data = response.data;
			if (data.status === "tournament_started") {
				matches = data.matches;
				document.getElementById("bracket-tournament").style.display = "flex";
				document.getElementById("create-tournament-button").style.display = "none";
				document.getElementById("top-container-game").style.gridTemplateColumns = "repeat(2, 1fr)";
				displayBracket(matches);
				playNextMatch();
			}
		} catch (error) {
			console.error("Error starting tournament:", error);
		}
	}

	function displayBracket(matches) {
		// Group matches by round
		const rounds = {
			"semi": matches.slice(0, 2),
			"final": matches.slice(2)
		};

		// Update Semi Finals
		const semiRound = document.querySelector('[data-round-title="Semi Finals"]');
		rounds.semi.forEach((match, idx) => {
			const matchElement = semiRound.children[idx];
			updateMatchDisplay(matchElement, match);
		});

		// Update Finals
		const finalRound = document.querySelector('[data-round-title="Finals"]');
		if (rounds.final.length > 0) {
			updateMatchDisplay(finalRound.children[0], rounds.final[0]);
		}
	}

	function updateMatchDisplay(matchElement, match) {
		const players = matchElement.querySelectorAll('.bracket-player');
		
		// Update first player
		players[0].querySelector('.player-name').textContent = match.player1 || 'TBD';
		players[0].querySelector('.player-score').textContent = match.score1 || '0';

		// Update second player
		if (match.player2) {
			players[1].querySelector('.player-name').textContent = match.player2;
			players[1].querySelector('.player-score').textContent = match.score2 || '0';
		} else {
			players[1].querySelector('.player-name').textContent = 'BYE';
			players[1].querySelector('.player-score').textContent = '-';
		}

		// Update match status classes
		matchElement.classList.remove('winner', 'upcoming', 'bye');
		if (match.winner) {
			matchElement.classList.add('winner');
			// Highlight winning player
			players.forEach(player => {
				if (player.querySelector('.player-name').textContent === match.winner) {
					player.classList.add('winner');
				} else {
					player.classList.remove('winner');
				}
			});
		} else if (!match.player2) {
			matchElement.classList.add('bye');
		} else if (!match.player1 || match.player1 === 'TBD') {
			matchElement.classList.add('upcoming');
		}
	}

	// 4. Play the Next Match
	function playNextMatch() {
		if (currentMatchIndex >= matches.length) {
			document.getElementById("matchContainer").innerHTML = "<h2 class='neon-text'>The Tournament is Over!</h2>";
			return;
		}

		const match = matches[currentMatchIndex];
		const matchText = match.player2 
			? `${match.player1} vs. ${match.player2}`
			: `${match.player1} gets a bye.`;

		document.getElementById("matchDetails").innerText = matchText;
		document.getElementById("matchContainer").classList.remove("hidden");
		document.getElementById("startMatchButton").onclick = () => simulateMatch(match);
	}

	async function playActualMatch(match) {
		const roomName = `match_${tournamentId}_${currentMatchIndex}`;
		const canvas = document.getElementById("canvas");
		const matchDetails = document.getElementById("matchDetails");
		const matchResult = document.getElementById("matchResult");
		const matchContainer = document.getElementById("matchContainer");
	
		attachLocalGameEventListeners(roomName);
	
		matchDetails.innerText = `${match.player1} vs. ${match.player2}`;
		matchContainer.classList.remove("hidden");
	
		return new Promise((resolve) => {
			const socket = new WebSocket(
				`wss://${window.location.host}/ws/game/${roomName}/?is_local=true&token=${localStorage.getItem('accessToken')}`
			);
	
			socket.onmessage = function (event) {
				const data = JSON.parse(event.data);
	
				if (data.winner) {
					const winnerAlias = data.winner === "player1" ? match.player1 : match.player2;
					matchResult.innerText = `Winner: ${winnerAlias}`;
					socket.close(); // Close the WebSocket connection
					setTimeout(() => {
						resolve(winnerAlias);
						const ctx = canvas.getContext("2d");
						document.getElementById("next-match-container").classList.remove("hidden");
						ctx.clearRect(0, 0, canvas.width, canvas.height);
					}, 1500);
				}
			};
	
			socket.onerror = function (error) {
				console.error("WebSocket error:", error);
				resolve(null); // Resolve with null if there's an error
			};
		});
	}
	
	
	
	async function playNextMatch() {
		if (currentMatchIndex >= matches.length) {
			document.getElementById("matchContainer").innerHTML = "<h2 class='neon-text'>The Tournament is Over!</h2>";
			return;
		}
	
		const match = matches[currentMatchIndex];
		document.getElementById("next-match-container").classList.add("hidden");
		const winner = await playActualMatch(match);
	
		if (winner) {
			await saveMatchResult(winner);
		} else {
			console.error("Error determining winner for match:", match);
		}
	}
	
	// Attach event listener to "Next Match" button
	document.getElementById("nextMatchButton").addEventListener("click", () => {
		playNextMatch();
	});
	
	
	document.addEventListener('keydown', function (event) {
		if (['ArrowUp', 'ArrowDown'].includes(event.key)) {
				event.preventDefault();
		}
	});

	document.addEventListener('keyup', function (event) {
		if (['ArrowUp', 'ArrowDown'].includes(event.key)) {
				event.preventDefault();
		}
	});

	async function saveMatchResult(winner) {
		document.getElementById("matchResult").innerText = `Winner: ${winner}`;
		const index = currentMatchIndex;
		currentMatchIndex++;
	
		try {
			const response = await axios.post(
				`/api/game/tournament/${tournamentId}/match/${index}/save_result/`,
				{ winner_alias: winner },
				{ headers }
			);
	
			matches = response.data.matches;
			displayBracket(matches);
	
		} catch (error) {
			console.error("Error saving match result:", error);
		}
	}	
}

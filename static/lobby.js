const socket = io();
let lobbyId = null;
let lobbyCreatorDiv = null;
let lobbyChooserDiv = null;
let lobbyDiv = null;
let gameDiv = null;
const nickname = sessionStorage.getItem("nickname");
let playerSymbol = null;

document.addEventListener("DOMContentLoaded", () => {
    showLobbyChooser();
    
});

socket.on("connect", () => {
    console.log("Połączono z serwerem SocketIO");

    socket.emit("join", { name: nickname }, (response) => {
        lobbyId = response.room;
        console.log("Dołączono do lobby:", lobbyId);

    });
});

socket.on("start_game", () => {
    startGame();
});

socket.on("show_lobby", () => {
    showLobby();
});

socket.onAny((event, data) => {
    console.log("Received event:", event, data);
});

function setReady() {
    if (!lobbyId) {
        return;
    }
    socket.emit("change_status", {
    });
}


socket.on("disconnect", () => {
    sessionStorage.removeItem("nickname");
});

window.addEventListener("beforeunload", () => {
    sessionStorage.removeItem("nickname");
});


function showLobbyChooser(lobbies = []) {

    if (!nickname) {
        window.location.href = "/";
        return;
    }

    hideAllViews();

    lobbyChooserDiv.style.display = "block";


    const wrapperDiv = document.createElement("div");
    wrapperDiv.className = "lobby-wrapper";
    lobbyChooserDiv.appendChild(wrapperDiv);

    const headerContainer = document.createElement("div");
    headerContainer.id = "headerContainer";
    headerContainer.style.display = "flex";
    headerContainer.style.justifyContent = "space-between";
    headerContainer.style.alignItems = "center";
    wrapperDiv.appendChild(headerContainer);

    const headerDiv = document.createElement("h1");
    headerDiv.className = "title";
    headerDiv.textContent = "Choose Lobby";
    headerContainer.appendChild(headerDiv);

    const topButton = document.createElement("button");
    topButton.id = "topButton";
    topButton.textContent = "Create Lobby";
    topButton.onclick = () => lobbyCreator();
    topButton.style.width = "auto";
    topButton.style.fontSize = "0.9em";
    headerContainer.appendChild(topButton);

    const tableWrapper = document.createElement("div");
    tableWrapper.style.maxHeight = "300px";
    tableWrapper.style.overflowY = "auto";
    tableWrapper.style.marginTop = "20px";
    wrapperDiv.appendChild(tableWrapper);

    const table = document.createElement("table");
    table.id = "lobbyTable";
    table.style.width = "100%";
    table.style.borderCollapse = "collapse";
    tableWrapper.appendChild(table);


    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    [".", "Lobby Name", "Players", "Action"].forEach(text => {
        const th = document.createElement("th");
        th.textContent = text;
        th.style.padding = "10px";
        th.style.borderBottom = "2px solid #4d2f1f";
        th.style.color = "#ffb84d";
        th.style.background = "#2a2a2a";
        th.style.textAlign = "left";
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    lobbies.forEach(lobby => {
        const row = document.createElement("tr");

        const idCell = document.createElement("td");
        idCell.textContent = lobby.id;
        row.appendChild(idCell);

        const nameCell = document.createElement("td");
        nameCell.textContent = lobby.name;
        row.appendChild(nameCell);

        const playersCell = document.createElement("td");
        playersCell.textContent = `${lobby.players}/2`;
        row.appendChild(playersCell);

        const statusCell = document.createElement("td");
        statusCell.textContent = lobby.players < 2 ? "Waiting" : "Full";
        row.appendChild(statusCell);

        const actionCell = document.createElement("td");
        const joinBtn = document.createElement("button");
        joinBtn.textContent = "Join";
        joinBtn.onclick = () => socket.emit("join_lobby", { lobby_id: lobby.id });
        actionCell.appendChild(joinBtn);
        row.appendChild(actionCell);

        tbody.appendChild(row);
    });
    table.appendChild(tbody);
    fetchLobbies();
}

function lobbyCreator() {
    hideAllViews();
    lobbyCreatorDiv.style.display = "block";
    lobbyCreatorDiv.innerHTML = "";

    const wrapper = document.createElement("div");
    wrapper.className = "lobby-wrapper";
    lobbyCreatorDiv.appendChild(wrapper);

    const header = document.createElement("h1");
    header.className = "title";
    header.textContent = "Create Lobby";
    wrapper.appendChild(header);

    const nameInput = document.createElement("input");
    nameInput.type = "text";
    nameInput.placeholder = "Lobby Name";
    nameInput.id = "lobbyNameInput";
    nameInput.style.marginBottom = "15px";
    wrapper.appendChild(nameInput);

    const passwordInput = document.createElement("input");
    passwordInput.type = "password";
    passwordInput.placeholder = "Password (optional)";
    passwordInput.id = "lobbyPasswordInput";
    passwordInput.style.marginBottom = "20px";
    wrapper.appendChild(passwordInput);

    const createBtn = document.createElement("button");
    createBtn.textContent = "Create Lobby";
    createBtn.onclick = () => {
        const lobbyName = nameInput.value.trim();
        const password = passwordInput.value.trim();

        if (!lobbyName) {
            alert("Please enter a lobby name.");
            return;
        }

        fetch("/create_lobby", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                lobby_name: lobbyName,
                password: password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log("Lobby created:", data.lobby_id);
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch(err => {
            console.error(err);
            alert("Server error, try again.");
        });
    };
    wrapper.appendChild(createBtn);

    const backBtn = document.createElement("button");
    backBtn.textContent = "Back";
    backBtn.style.marginTop = "10px";
    backBtn.onclick = () => showLobbyChooser();
    wrapper.appendChild(backBtn);
}

function showLobby(){

    hideAllViews();
    lobbyDiv.style.display = "block";


    const containerDiv = document.createElement("div");
    containerDiv.className = "container";

    const lobbyWrapper = document.createElement("div");
    lobbyWrapper.className = "lobby-wrapper";
    containerDiv.appendChild(lobbyWrapper);
    lobbyDiv.appendChild(containerDiv);

    const header = document.createElement("h1");
    header.textContent = "Game Lobby";
    header.className = "title";
    lobbyWrapper.appendChild(header);

    const playerSection = document.createElement("div");
    playerSection.className = "players-section";
    const playerHeader = document.createElement("h2");
    playerHeader.className = "section-title";
    playerHeader.textContent = "Players";
    playerSection.appendChild(playerHeader);
    lobbyWrapper.appendChild(playerSection);

    const playersList = document.createElement("div");
    playersList.id = "playersList";
    playersList.className = "players-list";

    const table = document.createElement("table");

    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    const headers = ["Nickname", "Symbol", "Status"];



    headers.forEach(text => {
        const th = document.createElement("th");
        th.textContent = text;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);
    playerSection.appendChild(playersList);
    playersList.appendChild(table);

    const btn = document.createElement("button");
    btn.textContent = "Change status";

    btn.onclick = () => setReady();

    playersList.appendChild(btn);

}

socket.on("lobby_update", (data) => {
    const table = document.querySelector("#playersList table");
    if (!table) return; // jeśli UI jeszcze nie zbudowane

    // Czyścimy tabelę
    table.innerHTML = "";

    // Tworzymy nagłówek
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    ["Nickname", "Symbol", "Status"].forEach(text => {
        const th = document.createElement("th");
        th.textContent = text;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    data.players.forEach(player => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${player.name}</td>
            <td>${player.symbol}</td>
            <td id="player-${player.id}-status">${player.status}</td>
        `;
        tbody.appendChild(row);
    });
    table.appendChild(tbody);
});


function startGame() {
    hideAllViews();
    lobbyDiv.style.display = "block";

    for (let i = 1; i <= 9; i++) {
        const cell = document.createElement("div");
        cell.id = `cell${i}`;
        cell.classList.add("cell", "empty");
        cell.style.backgroundImage = `url('/static/images/${playerSymbol.toLowerCase()}.png')`;
        gameDiv.appendChild(cell);
    }

    const cells = document.querySelectorAll(".cell");

    cells.forEach(cell => {
        cell.addEventListener("click", () => {
            console.log("Kliknięto komórkę:", cell.id);
            socket.emit("click_cell", { cell_id: cell.id });
        });
    });
}

socket.on("assign_symbol", (data) => {
    playerSymbol = data.player_symbol;
    console.log("Otrzymano symbol gracza:", playerSymbol);
});

socket.on("game_over", (data) => {
    const winner = data.winner;
    console.log("Otrzymano sygnał game_over, zwycięzca:", winner);
    alert(`Game Over! Winner: ${winner}`);
    showLobby();
});

socket.on("game_update", (board) => {


    Object.entries(board).forEach(([cellId, symbol]) => {
        const cell = document.getElementById(cellId);
        if (!cell) return;

        cell.classList.remove("cross", "circle", "empty");

        if (!symbol) {
            cell.classList.add("empty");
                } else {
            cell.classList.remove("empty");
            cell.classList.add(symbol);
            cell.style.backgroundImage = `url('/static/images/${symbol.toLowerCase()}.png')`;
            cell.style.opacity = 1;
            cell.style.border = "none";
        }
    });
});

function hideAllViews() {
    lobbyChooserDiv = document.getElementById("lobbyChooserDiv");
    lobbyCreatorDiv = document.getElementById("lobbyCreatorDiv");
    lobbyDiv = document.getElementById("lobbyDiv");
    gameDiv = document.getElementById("gameDiv");

    lobbyChooserDiv.innerHTML = "";
    lobbyCreatorDiv.innerHTML = "";
    lobbyDiv.innerHTML = "";
    gameDiv.innerHTML = "";

    if (lobbyChooserDiv) lobbyChooserDiv.style.display = "none";
    if (lobbyCreatorDiv) lobbyCreatorDiv.style.display = "none";
    if (lobbyDiv) lobbyDiv.style.display = "none";
    if (gameDiv) gameDiv.style.display = "none";
}

function fetchLobbies() {
    fetch("/get_lobbies")
        .then(res => res.json())
        .then(data => {
            const tbody = document.querySelector("#lobbyTable tbody");
            tbody.innerHTML = ""; // czyścimy poprzednie lobby


            data.lobbies.forEach(lobby => {
                const row = document.createElement("tr");


                
                const idCell = document.createElement("td");
                idCell.textContent = data.lobbies.indexOf(lobby) + 1;
                row.appendChild(idCell);


                const nameCell = document.createElement("td");
                nameCell.textContent = lobby.name;
                row.appendChild(nameCell);


                const playersCell = document.createElement("td");
                playersCell.textContent = `${lobby.players}/${lobby.max_players || 2}`;
                row.appendChild(playersCell);

                // Join button
                const joinCell = document.createElement("td");
                const joinBtn = document.createElement("button");
                joinBtn.textContent = "Join";
                joinBtn.onclick = () => {
                    if (lobby.has_password) {
                        const pw = prompt("Enter lobby password:");
                        // tutaj możesz zrobić POST z password
                        joinLobby(lobby.id, pw);
                    } else {
                        joinLobby(lobby.id);
                    }
                };
                joinCell.appendChild(joinBtn);
                row.appendChild(joinCell);

                tbody.appendChild(row);
            });
        })
        .catch(err => console.error("Error fetching lobbies:", err));
}

function joinLobby(lobbyId, password = null) {
    fetch("/join_lobby", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lobby_id: lobbyId, password: password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("Joined lobby!");
        } else {
            alert("Error: " + data.error);
        }
    });
}


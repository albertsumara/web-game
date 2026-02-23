const socket = io();
let lobbyId = null;
let lobbyDiv = null;
let gameDiv = null;
const nickname = sessionStorage.getItem("nickname");

document.addEventListener("DOMContentLoaded", () => {
    showLobby();
});

socket.on("connect", () => {
    console.log("Połączono z serwerem SocketIO");

    socket.emit("join", { name: nickname }, (response) => {
        lobbyId = response.room;
        console.log("Dołączono do lobby:", lobbyId);
        // statusDiv.textContent = "Połączono z serwerem, czekamy na innych graczy...";
    });
});

socket.on("start_game", () => {
    console.log("Otrzymano sygnał start_game, rozpoczynamy grę...");
    startGame();
});

socket.on("show_lobby", () => {
    console.log("Otrzymano sygnał show_lobby, pokazujemy lobby...");
    showLobby();
});

socket.onAny((event, data) => {
    console.log("Received event:", event, data);
});

function setReady() {
    if (!lobbyId) {
        console.error("Nieznane lobby_id!");
        return;
    }

    socket.emit("change_status", {
    });
}


socket.on("disconnect", () => {
    console.log("Rozłączono z serwerem, czyszczenie nicku...");
    sessionStorage.removeItem("nickname");
});

window.addEventListener("beforeunload", () => {
    sessionStorage.removeItem("nickname");
});

function showLobby(){


    if (!nickname) {
        // alert("Brak nicku!");
        window.location.href = "/";
    }

    lobbyDiv = document.getElementById("lobbyDiv");
    gameDiv = document.getElementById("gameDiv");
    gameDiv.innerHTML = "";
    lobbyDiv.innerHTML = "";
    gameDiv.style.display = "none";
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

    // const ul = document.createElement("ul");
    // ul.className = "players-list";
    // ul.id = "playerList";
    // playerSection.appendChild(ul);

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

    // Tworzymy tbody z graczami
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
    lobbyDiv.style.display = "none";
    gameDiv.style.display = "block";
    gameDiv.innerHTML = "";

    for (let i = 1; i <= 9; i++) {
        const cell = document.createElement("div");
        cell.id = `cell${i}`;      // cell1, cell2 ... cell9
        // cell.className = "cell.empty";   // wspólna klasa dla stylów
        cell.classList.add("cell", "empty");
        gameDiv.appendChild(cell);
    }

    const cells = document.querySelectorAll(".cell");

    cells.forEach(cell => {
        cell.addEventListener("click", () => {
            console.log("Kliknięto komórkę:", cell.id); // pokazuje ID klikniętej komórki
            socket.emit("click_cell", { cell_id: cell.id });
        });
    });
}


socket.on("game_update", (board) => {
    Object.entries(board).forEach(([cellId, symbol]) => {
        const cell = document.getElementById(cellId);
        if (!cell) return;

        cell.classList.remove("cross", "circle", "empty");

        if (!symbol) {
            cell.classList.add("empty");
            cell.style.backgroundImage = ""; 
        } else {
            cell.classList.remove("empty");
            cell.classList.add(symbol);
            cell.style.backgroundImage = `url('/static/images/${symbol.toLowerCase()}.png')`;
            cell.style.opacity = 1;
            cell.style.border = "none";
        }
    });
});
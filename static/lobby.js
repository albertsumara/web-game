const nickname = sessionStorage.getItem("nickname");

if (!nickname) {
    alert("Brak nicku!");
    window.location.href = "/";
}

const socket = io();

const lobbyDiv = document.getElementById("lobbyDiv");

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

let lobbyId = null;

socket.on("connect", () => {
    console.log("Połączono z serwerem SocketIO");

    socket.emit("join", { name: nickname }, (response) => {
        lobbyId = response.room;
        console.log("Dołączono do lobby:", lobbyId);
        // statusDiv.textContent = "Połączono z serwerem, czekamy na innych graczy...";
    });
});


socket.on("lobby_update", (data) => {
    table.innerHTML = "";
    table.appendChild(thead);



    const tbody = document.createElement("tbody");

    data.players.forEach(player => {
        const row = document.createElement("tr");

        const tdName = document.createElement("td");
        tdName.textContent = player.name;
        row.appendChild(tdName);

        const tdSymbol = document.createElement("td");
        tdSymbol.textContent = player.symbol;
        row.appendChild(tdSymbol);

        const tdStatus = document.createElement("td");
        tdStatus.textContent = player.status;
        tdStatus.id = `player-${player.id}-status`;
        row.appendChild(tdStatus);

        // const tdChange = document.createElement("td");
        // const btn = document.createElement("button");
        // btn.textContent = "Change";

        // btn.onclick = () => setReady(player.id);

        // tdChange.appendChild(btn);
        // row.appendChild(tdChange);

        tbody.appendChild(row);
    });

    table.appendChild(tbody);
});

const btn = document.createElement("button");
btn.textContent = "Change status";

btn.onclick = () => setReady();

playersList.appendChild(btn);

// lobbyDiv.appendChild(playersList);


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

function startGame() {
    lobbyDiv.innerHTML = "";
    const board = document.createElement("div");
    board.id = "gameBoard";

    const boardImg = document.createElement("img");
    boardImg.src = "/static/images/board.png";
    boardImg.alt = "Plansza gry";
    boardImg.className = "boardImage";


    board.appendChild(boardImg);

    lobbyDiv.appendChild(board);
}

socket.on("start_game", () => {
    console.log("Otrzymano sygnał start_game, rozpoczynamy grę...");
    startGame();
});
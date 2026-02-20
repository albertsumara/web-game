const nickname = sessionStorage.getItem("nickname");

if (!nickname) {
    alert("Brak nicku!");
    window.location.href = "/";
}

const socket = io();

const playersList = document.getElementById("playersList");
const statusDiv = document.getElementById("status");
const table = document.createElement("table");

// Tworzenie nagłówka tabeli
const thead = document.createElement("thead");
const headerRow = document.createElement("tr");
const headers = ["Nickname", "Symbol", "Status"];
// const headers = ["Nickname", "Symbol", "Status", "Change Status"];


headers.forEach(text => {
    const th = document.createElement("th");
    th.textContent = text;
    headerRow.appendChild(th);
});

thead.appendChild(headerRow);
table.appendChild(thead);
playersList.appendChild(table);

let lobbyId = null;

socket.on("connect", () => {
    console.log("Połączono z serwerem SocketIO");

    socket.emit("join", { name: nickname }, (response) => {
        lobbyId = response.room;
        console.log("Dołączono do lobby:", lobbyId);
        statusDiv.textContent = "Połączono z serwerem, czekamy na innych graczy...";
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

        const tdChange = document.createElement("td");
        const btn = document.createElement("button");
        btn.textContent = "Change";

        btn.onclick = () => setReady(player.id);

        tdChange.appendChild(btn);
        row.appendChild(tdChange);

        tbody.appendChild(row);
    });

    table.appendChild(tbody);
});

socket.onAny((event, data) => {
    console.log("Received event:", event, data);
});

function setReady(playerId) {
    if (!lobbyId) {
        console.error("Nieznane lobby_id!");
        return;
    }

    socket.emit("change_status", {
        player_id: playerId,
        // lobby_id: lobbyId
    });
}


socket.on("disconnect", () => {
    console.log("Rozłączono z serwerem, czyszczenie nicku...");
    sessionStorage.removeItem("nickname");
});

window.addEventListener("beforeunload", () => {
    sessionStorage.removeItem("nickname");
});
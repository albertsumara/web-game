const nickname = sessionStorage.getItem("nickname");

if (!nickname) {
    alert("Brak nicku!");
    window.location.href = "/";
}


const socket = io();


const playersList = document.getElementById("playersList");
const statusDiv = document.getElementById("status");
const table = document.createElement("table");

const thead = document.createElement("thead");
const headerRow = document.createElement("tr");

const headers = ["Nickname", "Symbol", "Status", "Change Status"];

headers.forEach(text => {
    const th = document.createElement("th");
    th.textContent = text;
    headerRow.appendChild(th);
});

thead.appendChild(headerRow);
table.appendChild(thead);

socket.on("connect", () => {
    console.log("Połączono z serwerem SocketIO");
    socket.emit("join", { name: nickname });
    statusDiv.textContent = "Połączono z serwerem, czekamy na innych graczy...";
});

socket.on("lobby_update", (data) => {
    // console.log("Otrzymano lobby_update:", data);


    playersList.innerHTML = "";

    const tbody = document.createElement("tbody");

    data.players.forEach(player => {

        console.log("player:", player);

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

    playersList.appendChild(table);

    // if (data.players.length < 2) {
    //     statusDiv.textContent = "Czekamy na kolejnego gracza...";
    // } else {
    //     statusDiv.textContent = "Lobby pełne! Gotowi do startu gry.";
    // }
});


socket.onAny((event, data) => {
    console.log("Received event:", event, data);
});


function setReady(playerId, lobbyId) {
    fetch(`/player/${playerId}`, { method: 'POST' })
      .then(res => res.json())
      .then(data => {
          console.log("Updated player:", data);
          document.getElementById(`player-${data.id}-status`).innerText = data.status;
      });
}
const nickname = sessionStorage.getItem("nickname");


if (!nickname) {
    alert("Brak nicku!");
    window.location.href = "/";
}


const socket = io();


const playersList = document.getElementById("playersList");
const statusDiv = document.getElementById("status");


socket.on("connect", () => {
    console.log("Połączono z serwerem SocketIO");
    socket.emit("join", { name: nickname });
    statusDiv.textContent = "Połączono z serwerem, czekamy na innych graczy...";
});

// odbieramy aktualizację lobby
socket.on("lobby_update", (data) => {
    console.log("Otrzymano lobby_update:", data);

    // czyścimy listę graczy
    playersList.innerHTML = "";

    // wyświetlamy wszystkich graczy
    data.players.forEach(player => {
        const li = document.createElement("li");
        li.textContent = `${player.name} (${player.symbol})`;
        playersList.appendChild(li);
    });

    // aktualizujemy status
    if (data.players.length < 2) {
        statusDiv.textContent = "Czekamy na kolejnego gracza...";
    } else {
        statusDiv.textContent = "Lobby pełne! Gotowi do startu gry.";
    }
});

// opcjonalnie debug — logujemy każdy event
socket.onAny((event, data) => {
    console.log("Received event:", event, data);
});

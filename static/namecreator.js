const lobbyDiv = document.getElementById("namecreator");

const input = document.createElement("input");
input.type = "text";
input.placeholder = "Wpisz nick";
input.id = "nicknameInput";

const joinButton = document.createElement("button");
joinButton.textContent = "dołącz";

lobbyDiv.appendChild(input);
lobbyDiv.appendChild(joinButton);

const socket = io("http://localhost:5000");

joinButton.addEventListener("click", () => {
    const nickname = input.value.trim();
    if (!nickname) return alert("Wpisz nick!");

    socket.emit("join", {
        lobby_id: "0",
        name: nickname
    });

    // input.disabled = true;
    // joinButton.disabled = true;
});
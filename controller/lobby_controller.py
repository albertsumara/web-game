from flask_socketio import emit, join_room
from service.game_service import GameService

def register_lobby_socket(socketio, game_service):
    
    @socketio.on("join")
    def handle_join(data):
        print("Otrzymano event JOIN:", data, flush=True)

        name = data["name"]
        player, lobby = game_service.join_lobby(name)

        print(f"Gracz utworzony: {player.name} | id: {player.player_id}", flush=True)
        print(f"Przypisano do lobby: {lobby.lobby_id}", flush=True)

        join_room(str(lobby.lobby_id))
        print(f"Dołączono do pokoju SocketIO: {lobby.lobby_id}", flush=True)

        emit(
            "lobby_update",
            {"players": [{"id": p.player_id,"name": p.name, "symbol": p.symbol, "status": p.status} for p in lobby.players.values()]},
            room=str(lobby.lobby_id)
        )

        print("Wysłano lobby_update do pokoju:", lobby.lobby_id, flush=True)

        return {"room": str(lobby.lobby_id)}


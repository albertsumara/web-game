from flask_socketio import emit, join_room
from service.game_service import GameService

def register_lobby_socket(socketio, game_service):
    
    @socketio.on("join")
    def handle_join(data):
        name = data["name"]
        player, lobby = game_service.join_lobby(name)

        join_room(str(lobby.lobby_id))

        emit(
            "lobby_update",
            {"players": [{"name": p.name, "symbol": p.symbol} for p in lobby.players.values()]},
            room=str(lobby.lobby_id)
        )
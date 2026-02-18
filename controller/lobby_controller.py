from flask_socketio import emit, join_room
from service.game_service import GameService

def register_lobby_socket(socketio, game_service):
    
    @socketio.on("join")
    def handle_join(data):
        name = data["name"]

        player = game_service.create_player(name)

        game_service.append_to_exists_lobby(player)

        lobby = game_service.get_last_lobby()

        print(f"Gracz {player.name} ({player.player_id}) dołączył do lobby {lobby.lobby_id}")
        print("Aktualny stan lobby:")
        for p in lobby.players.values():
            print(f"- {p.name} ({p.symbol}) [{p.status}]")

        emit(
            "lobby_update",
            {"players": [{ "name": p.name, "symbol": p.symbol } for p in lobby.players.values()]},
            room=str(lobby.lobby_id)
        )
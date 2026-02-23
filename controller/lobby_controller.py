from flask import request
from flask_socketio import emit, join_room

def register_lobby_socket(socketio, game_service):

    socket_to_player = {}

    @socketio.on("join")
    def handle_join(data):
        print("Otrzymano event JOIN:", data, flush=True)

        name = data["name"]
        player, lobby = game_service.join_lobby(name)

        socket_to_player[request.sid] = player.player_id

        print(f"Gracz utworzony: {player.name} | id: {player.player_id}", flush=True)
        print(f"Przypisano do lobby: {lobby.lobby_id}", flush=True)

        join_room(str(lobby.lobby_id))
        print(f"Dołączono do pokoju SocketIO: {lobby.lobby_id}", flush=True)

        emit(
            "lobby_update",
            {"players": [{"name": p.name, "symbol": p.symbol, "status": p.status} 
                         for p in lobby.players]},
            room=str(lobby.lobby_id)
        )

        print("Wysłano lobby_update do pokoju:", lobby.lobby_id, flush=True)

        return {"room": str(lobby.lobby_id)}

    @socketio.on("change_status")
    def handle_toggle_ready(data):
        print(f"testtt: {data}", flush=True)
        result = game_service.toggle_player_status(socket_to_player.get(request.sid))

        if not result["success"]:
            emit("error", {"message": result["error"]})
            return


        socketio.emit(
            "lobby_update",
            result["lobby"],
            room=result["lobby_id"]
        )

        player_status = [p["status"] for p in result["lobby"]["players"]]

        if len(player_status) > 1 and all(status == "ready" for status in player_status):
            socketio.emit("start_game", room=result["lobby_id"])
            # print(f"Wszystkie gotowe w lobby {result['lobby_id']} - można rozpocząć grę!", flush=True)

    @socketio.on("disconnect")
    def handle_disconnect(sid):
        print(f"[DISCONNECT] Socket {request.sid} odłączony", flush=True)

        # sprawdzamy, czy mamy przypisanego gracza do tego socketu
        player_id = socket_to_player.pop(request.sid, None)
        if not player_id:
            print(f"[DISCONNECT] Brak przypisanego gracza do socketu {request.sid}", flush=True)
            return

        print(f"[DISCONNECT] Usuwamy gracza {player_id} z lobby...", flush=True)

        # usuwamy gracza z lobby
        lobby_id = game_service.remove_player(player_id)
        if lobby_id:
            print(f"[DISCONNECT] Gracz {player_id} usunięty z lobby {lobby_id}", flush=True)
            # wysyłamy aktualizację do pozostałych graczy w lobby
            socketio.emit("show_lobby", room=lobby_id)
            socketio.emit(
                "lobby_update",
                {"players": [p.to_dict() for p in game_service.game.lobbies[lobby_id].players]},
                room=lobby_id
            )
            print(f"[DISCONNECT] Wysłano lobby_update do lobby {lobby_id}", flush=True)

            

        else:
            print(f"[DISCONNECT] Lobby dla gracza {player_id} nie znaleziono", flush=True)
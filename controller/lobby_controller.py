from flask import request
from flask_socketio import emit, join_room

def register_lobby_socket(app, socketio, game_service):

    socket_to_player = {}

    @socketio.on("join")
    def handle_join(data):
        name = data["name"]
        player = game_service.create_player(name)
        socket_to_player[request.sid] = player
        return {"success": True, "player_id": player.player_id}

    @app.route("/create_lobby", methods=["POST"])
    def create_lobby_endpoint():
        data = request.get_json()
        lobby_name = data.get("lobby_name")
        password = data.get("password")
        lobby = game_service.create_lobby(lobby_name, password=password)
        print(game_service.get_lobbies())
        return {
            "success": True,
            "lobby_id": lobby.lobby_id
            }, 200
    
    @socketio.on("join_lobby")
    def handle_join_lobby(data):
        lobby_id = data["lobby_id"]
        typed_password = data["password"]
        player = socket_to_player.get(request.sid)
        if not player:
            return {"success": False, "error": "Unknown player"}
        try:
            join_room(lobby_id)
            game_service.join_lobby(lobby_id, player.player_id, typed_password)
            lobby = game_service.get_lobbies().get(lobby_id)

            emit("join_lobby_response", {
                "success": True,
                }, room=request.sid)

            emit(
                "lobby_update",
                {"players": [p.to_dict() for p in lobby.players]},
                room=lobby_id)

            emit(
                "assign_symbol",
                {
                    "player_symbol": player.symbol
                },
                room=request.sid)

        except Exception as e:
            emit("join_lobby_response", {"success": False, "error": str(e)}, room=request.sid)

    @app.route("/get_lobbies", methods=["GET"])
    def get_lobbies():
        lobbies = list(game_service.get_lobbies().values())
        lobby_list = []

        for lobby in lobbies:
            lobby_list.append({
                "id": lobby.lobby_id,
                "name": lobby.name,
                "players": len(lobby.players),
            })
        return {"success": True, "lobbies": lobby_list}, 200

    @socketio.on("change_status")
    def handle_toggle_ready(data):
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
            game_service.start_new_game(socket_to_player.get(request.sid))
            socketio.emit("start_game", room=result["lobby_id"])


    @socketio.on("disconnect")
    def handle_disconnect(reason):
        print(f"[DISCONNECT] Socket {request.sid} odłączony", flush=True)

        player = socket_to_player.pop(request.sid, None)
        if not player:
            print(f"[DISCONNECT] Brak przypisanego gracza do socketu {request.sid}", flush=True)
            return

        lobby_id = game_service.remove_player(player)
        if lobby_id:
            print(f"[DISCONNECT] Gracz {player} usunięty z lobby {lobby_id}", flush=True)
            socketio.emit(
                "lobby_update",
                {"players": [p.to_dict() for p in game_service.game.lobbies[lobby_id].players]},
                room=lobby_id
            )

    @socketio.on("click_cell")
    def handle_click_cell(data):
        result = game_service.handle_click_cell(socket_to_player.get(request.sid), data["cell_id"])

        if not result["success"]:
            emit("error", {"message": result["error"]})
            return
        player = game_service.get_player(socket_to_player.get(request.sid).player_id)
        if game_service.game.lobbies.get(player.lobby_id).state_of_game["who_wins"] is not None:
            emit("game_over", {"winner": game_service.game.lobbies.get(player.lobby_id).state_of_game["who_wins"]}, room=player.lobby_id)
            emit(
            "lobby_update",
            {"players": [{"name": p.name, "symbol": p.symbol, "status": p.status} 
                         for p in game_service.game.lobbies.get(player.lobby_id).players]},
            room=player.lobby_id
            )

        socketio.emit(
            "game_update",
            result["game_state"],
            room=result["lobby_id"]
        )


    @socketio.on("get_board")
    def handle_get_board():
        player = game_service.get_player(socket_to_player.get(request.sid).player_id)
        if not player:
            emit("error", {"message": "Nieznany gracz"})
            return

        lobby = next(
            (l for l in game_service.game.lobbies.values()
            if any(p.player_id == player.player_id for p in l.players)),
            None
        )
        if not lobby:
            emit("error", {"message": "Lobby nie znalezione"})
            return
        emit("game_update", lobby.board)

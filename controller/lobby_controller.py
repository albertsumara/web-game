from flask import request
from flask_socketio import emit, join_room

def register_lobby_socket(app, socketio, game_service):

    socket_to_player = {}

    @socketio.on("join")
    def handle_join(data):
        print("Otrzymano event JOIN:", data, flush=True)

        name = data["name"]
        player, lobby = game_service.join_lobby(name)
        socket_to_player[request.sid] = player.player_id
        join_room(str(lobby.lobby_id))
        emit("assign_symbol", {"player_symbol": player.symbol})

        emit(
            "lobby_update",
            {"players": [{"name": p.name, "symbol": p.symbol, "status": p.status} 
                         for p in lobby.players]},
            room=str(lobby.lobby_id)
        )
        print("Wysłano lobby_update do pokoju:", lobby.lobby_id, flush=True)
        return {"room": str(lobby.lobby_id)}

    @app.route("/create_lobby", methods=["POST"])
    def create_lobby_endpoint():
        data = request.get_json()
        lobby_name = data.get("lobby_name")
        password = data.get("password")
        lobby = game_service.create_lobby(lobby_name, password=password)
        print(game_service.get_lobbies())
        return {"success": True, "lobby_id": lobby.lobby_id}, 200

    @app.route("/get_lobbies", methods=["GET"])
    def get_lobbies():
        lobbies = game_service.get_lobbies()  # zwraca słownik lobby_id -> Lobby
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
            # print(f"[DISCONNECT] Wysłano lobby_update do lobby {lobby_id}", flush=True)

            

        # else:
        #     # print(f"[DISCONNECT] Lobby dla gracza {player_id} nie znaleziono", flush=True)

    @socketio.on("click_cell")
    def handle_click_cell(data):
        # print(f"Otrzymano click_cell: {data}", flush=True)
        result = game_service.handle_click_cell(socket_to_player.get(request.sid), data["cell_id"])

        if not result["success"]:
            emit("error", {"message": result["error"]})
            return
        player = game_service.get_player(socket_to_player.get(request.sid))
        # print(f"sprawdzam zwyciezce...", flush=True)
        # print(f"aktualny zwycięzca: {game_service.game.lobbies.get(player.lobby_id).state_of_game['who_wins']}", flush=True)
        if game_service.game.lobbies.get(player.lobby_id).state_of_game["who_wins"] is not None:
            # print(f"Gra zakończona, zwycięzca: {game_service.game.lobbies.get(player.lobby_id).state_of_game['who_wins']}", flush=True)
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
        player = game_service.get_player(socket_to_player.get(request.sid))
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

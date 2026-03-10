import random
from model.lobby import Lobby
from model.player import Player
from model.game import Game
import uuid

class GameService:

    def __init__(self, game: Game):
        self.game = game

    def create_player(self, name):
        player = Player(name)
        self.game.players[player.player_id] = player
        return player

    def create_lobby(self, lobby_name, creator_id=None, password=None):
        lobby_id = str(uuid.uuid4())
        lobby = self.game.create_lobby(lobby_id)
        lobby.name = lobby_name
        lobby.password = password
        lobby.creator_id = creator_id
        self.game.lobbies[lobby_id] = lobby
        return lobby
    
    def join_lobby(self, lobby_id, player_id, typed_password):
        lobby = self.get_lobbies().get(lobby_id)
        if len(lobby.players) >= 2:
            raise Exception("Lobby is full")
        
        if lobby.password:
            if lobby.password != typed_password:
                    raise Exception("Wrong password")

        if lobby:
            player = self.game.get_player(player_id)
            if player:
                player.lobby_id = lobby_id
                print(f"player: {player}, lobby_id: {player.lobby_id}", flush=True)
                if len(lobby.players) == 0:
                    player.symbol = random.choice(["cross", "circle"])
                else:
                    first_player_symbol = lobby.players[0].symbol
                    player.symbol = "circle" if first_player_symbol == "cross" else "cross"
                lobby.add_player(player)


    def get_lobbies(self):
        return self.game.lobbies
    
    def toggle_player_status(self, player):
        player.status = "ready" if player.status == "waiting" else "waiting"

        lobby = self.game.lobbies.get(player.lobby_id)
        if lobby:
            return {
                "success": True,
                "lobby": {
                    "players": [p.to_dict() for p in lobby.players]
                },
                "lobby_id": lobby.lobby_id
            }
        return {"success": False, "error": "Lobby not found"}

    
    def remove_player(self, player):
        lobby = self.game.lobbies.get(player.lobby_id)
        if player in lobby.players:
            lobby.players.remove(player)
            if len(lobby.players) == 0:
                self.game.lobbies.pop(lobby.lobby_id)
                return
            return lobby.lobby_id

    def get_player(self, player):
        for lobby in self.game.lobbies.values():
            player = next((p for p in lobby.players if p.player_id == player), None)
            if player:
                return player
        return None

    def handle_click_cell(self, player, cell_id):
        player_id = player.player_id
        lobby = self.game.lobbies.get(player.lobby_id)

        if not lobby:
            return {"success": False, "error": "Lobby not found"}


        player = next((p for p in lobby.players if p.player_id == player_id), None)
        if not player:
            return {"success": False, "error": "Player not found in lobby"}

        if lobby.current_turn != player_id:
            return {"success": False, "error": "Not your turn"}

        if lobby.board[cell_id] is not None:
            return {"success": False, "error": "Cell already occupied"}


        lobby.board[cell_id] = player.symbol
        lobby.current_turn = next(
            (p.player_id for p in lobby.players if p.player_id != player_id),
            None
        )

        win_combinations = [
            ["cell1", "cell2", "cell3"],
            ["cell4", "cell5", "cell6"],
            ["cell7", "cell8", "cell9"],
            ["cell1", "cell4", "cell7"],
            ["cell2", "cell5", "cell8"],
            ["cell3", "cell6", "cell9"],
            ["cell1", "cell5", "cell9"],
            ["cell3", "cell5", "cell7"]
        ]

        for combo in win_combinations:
            if all(lobby.board[cell] == player.symbol for cell in combo):
                lobby.state_of_game["who_wins"] = player.symbol
                lobby.current_turn = None
                for p in lobby.players:
                    p.status = "waiting"
                break

        print(f"board: {lobby.board}", flush=True)

        return {
            "success": True,
            "game_state": lobby.board,
            "lobby_id": lobby.lobby_id
        }
    
    def start_new_game(self, player):
        lobby = self.game.lobbies.get(player.lobby_id)
        self.clean_board(lobby)
        lobby.current_turn = random.choice(lobby.players).player_id
        lobby.state_of_game["who_wins"] = None
        for p in lobby.players:
            p.status = "waiting"

    def clean_board(self, lobby):
        if lobby:
            lobby.board = {
            "cell1": None,
            "cell2": None,
            "cell3": None,
            "cell4": None,
            "cell5": None,
            "cell6": None,
            "cell7": None,
            "cell8": None,
            "cell9": None
        }
            
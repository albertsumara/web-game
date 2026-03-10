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
    
    def join_lobby(self, lobby_id, player_id):
        lobby = self.get_lobbies().get(lobby_id)
        if lobby:
            player = self.game.get_player(player_id)
            if player:
                player.lobby_id = lobby_id
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

    
    def get_player(self, player):
        for lobby in self.game.lobbies.values():
            player = next((p for p in lobby.players if p.player_id == player), None)
            if player:
                return player
        return None

    def handle_click_cell(self, player_id, cell_id):
        lobby = next(
            (lobby for lobby in self.game.lobbies.values()
            if any(p.player_id == player_id for p in lobby.players)),
            None
        )

        if not lobby:
            return {"success": False, "error": "Lobby not found"}


        player = next(p for p in lobby.players if p.player_id == player_id)

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
                lobby.board["winner"] = player.symbol
                lobby = self.game.lobbies.get(player.lobby_id)
                lobby.state_of_game["who_wins"] = player.symbol
                lobby.reset_turn()
                self.clean_board(lobby.lobby_id)
                for p in lobby.players:
                    p.status = "waiting"

        print(f"board: {lobby.board}", flush=True)

        return {
            "success": True,
            "game_state": lobby.board,
            "lobby_id": lobby.lobby_id
        }
    
    def clean_board(self, lobby_id):
        lobby = self.game.lobbies.get(lobby_id)
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
            
    # def join_lobby(self, player_name):
    #         player = self.create_player(player_name) #tworzenie playera
    #         lobby = self.append_to_exists_lobby(player) #dołączamy/próbujemy dołączyć do istniejącego lobby
    #         return player, lobby

    # def append_to_exists_lobby(self, player):
    #         last_lobby = self.get_last_lobby() #pobieramy ostatnie lobby

    #         if last_lobby is None or self.check_lobby_full(): #jeśli jest pełne bądź nie istnieje (pierwsze lobby) tworzymy je
    #             return self.create_lobby(player)
    #         else:
    #             if len(last_lobby.players) > 0 and last_lobby.players[0].symbol == 'cross':
    #                 player.symbol = 'circle'
    #             else:
    #                 player.symbol = 'cross'
    #             last_lobby.add_player(player)
    #             player.lobby_id = last_lobby.lobby_id
    #             random_player = random.choice(last_lobby.players)
    #             last_lobby.current_turn = random_player.player_id
    #             return last_lobby

    # def create_lobby(self, player):
    #     lobby_id = str(uuid.uuid4())
    #     player.lobby_id = lobby_id
    #     lobby = Lobby(lobby_id)

    #     player.symbol = 'circle'
    #     lobby.add_player(player)

    #     self.game.lobbies[lobby_id] = lobby

    #     print(f"Created lobby {lobby_id} and added player {player.player_id}", flush=True)

    #     return lobby

    

    # def check_lobby_full(self):
    #     last_lobby = self.get_last_lobby()
    #     self.clean_board(last_lobby.lobby_id)
    #     if last_lobby is None:
    #         return False
    #     return len(last_lobby.players) >= 2

    # def get_last_lobby(self):
    #     if not self.game.lobbies:
    #         return None
    #     last_key = max(self.game.lobbies.keys())
    #     return self.game.lobbies[last_key]
    

    # def remove_player(self, player_id):
    #     for lobby in self.game.lobbies.values():
    #         player = next((p for p in lobby.players if p.player_id == player_id), None)
    #         if player:
    #             lobby.players.remove(player)
    #             return lobby.lobby_id
    #     return None
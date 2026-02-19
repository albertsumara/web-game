from model.lobby import Lobby
from model.player import Player
from model.game import Game
import uuid

class GameService:

    def __init__(self, game: Game):
        self.game = game

    def create_player(self, name):
        return Player(name)

    def join_lobby(self, player_name):
            player = self.create_player(player_name) #tworzenie playera
            lobby = self.append_to_exists_lobby(player) #dołączamy/próbujemy dołączyć do istniejącego lobby
            return player, lobby

    def append_to_exists_lobby(self, player):
            last_lobby = self.get_last_lobby() #pobieramy ostatnie lobby

            if last_lobby is None or self.check_lobby_full(): #jeśli jest pełne bądź nie istnieje (pierwsze lobby) tworzymy je
                return self.create_lobby(player)
            else:
                player.symbol = 'cross'
                last_lobby.add_player(player)
                return last_lobby

    def create_lobby(self, player):
        lobby_id = str(uuid.uuid4())
        player.lobby_id = lobby_id
        lobby = Lobby(lobby_id)

        player.symbol = 'circle'
        lobby.add_player(player)

        self.game.lobbies[lobby_id] = lobby
        return lobby

    

    def check_lobby_full(self):
        last_lobby = self.get_last_lobby()
        if last_lobby is None:
            return False
        return len(last_lobby.players) >= 2

    def get_last_lobby(self):
        if not self.game.lobbies:
            return None
        last_key = max(self.game.lobbies.keys())
        return self.game.lobbies[last_key]

    

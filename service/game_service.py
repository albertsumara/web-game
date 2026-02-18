from model.lobby import Lobby
from model.player import Player
from model.game import Game

class GameService:

    def __init__(self, game: Game):
        self.game = game

    def create_player(self, name):
        return Player(name)

    def create_lobby(self, player):
        lobby_id = len(self.game.lobbies)
        lobby = Lobby(lobby_id)
        player.symbol = 'circle'
        lobby.add_player(player)
        self.game.lobbies[lobby_id] = lobby
        return lobby

    def append_to_exists_lobby(self, player):
        last_lobby = self.get_last_lobby()
        if last_lobby is None or self.check_lobby_full():
            self.create_lobby(player)
        else:
            player.symbol = 'cross'
            last_lobby.add_player(player)

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

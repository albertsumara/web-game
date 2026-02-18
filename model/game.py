from .lobby import Lobby
from .player import Player

class Game:

    def __init__(self):
        self.lobbies = {}

    def create_lobby(self, lobby_id):
        lobby = Lobby(lobby_id)
        self.lobbies[lobby_id] = lobby
        return lobby
    
    def get_lobby(self, lobby_id):
        return self.lobbies.get(lobby_id)

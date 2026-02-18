class Lobby:
    def __init__(self, lobby_id):
        self.lobby_id = lobby_id
        self.players = {}



    def add_player(self, player):
        self.players[player.player_id] = player

    def get_player_count(self):
        return len(self.players)
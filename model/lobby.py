import random


class Lobby:
    def __init__(self, lobby_id):
        self.lobby_id = lobby_id
        self.players = []
        self.board = {
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

        self.name = None
        self.password = None
        self.creator_id = None

        self.state_of_game = {"who_wins": None}
        self.current_turn = self.players[0].player_id if self.players else None

    def add_player(self, player):
        self.players.append(player)

    def get_player_count(self):
        return len(self.players)
    
    def reset_turn(self):
        self.current_turn = random.choice(self.players).player_id if self.players else None
import uuid

class Player:
    def __init__(self, name):
        self.name = name
        self.player_id = str(uuid.uuid4())
        self.status = 'waiting'
        self.symbol = 'nothing'

    
import uuid

class Player:
    def __init__(self, name):
        self.name = name
        self.player_id = str(uuid.uuid4())
        self.lobby_id= None
        self.status = 'waiting'
        self.symbol = 'nothing'

    def to_dict(self):
        return {"id": self.player_id, "name": self.name,"symbol": self.symbol, "status": self.status, "lobby_id": self.lobby_id}
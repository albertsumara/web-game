from flask import Flask, render_template
from flask_socketio import SocketIO
from model.game import Game
from service.game_service import GameService
from controller.lobby_controller import register_lobby_socket
import json


app = Flask(__name__)

socketio = SocketIO(app, async_mode='eventlet')

game = Game()
game_service = GameService(Game())
register_lobby_socket(socketio, game_service)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)

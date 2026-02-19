from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from model.game import Game
from service.game_service import GameService
from controller.lobby_controller import register_lobby_socket
import json


app = Flask(__name__)

socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

game = Game()
game_service = GameService(game)
register_lobby_socket(socketio, game_service)

@app.route("/lobby")
def lobby_page():
    return render_template("lobby.html")

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/player/<player_id>', methods=['POST'])
def set_player_ready(player_id):

    for lobby in game.lobbies.values():
        for p in lobby.players.values():
            if p.player_id == player_id:

                p.status = (
                    'ready' if p.status == 'waiting' else 'waiting'
                )

                return jsonify(p.to_dict()), 200

    return jsonify({"error": "Player not found"}), 404

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)

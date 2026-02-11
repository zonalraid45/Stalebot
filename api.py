import requests
import os

class LichessAPI:
    def __init__(self):
        self.token = os.getenv("STALE")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.base_url = "https://lichess.org/api"

    def stream_events(self):
        return requests.get(f"{self.base_url}/stream/event", headers=self.headers, stream=True)

    def stream_game(self, game_id):
        return requests.get(f"{self.base_url}/bot/game/stream/{game_id}", headers=self.headers, stream=True)

    def accept_challenge(self, challenge_id):
        requests.post(f"{self.base_url}/challenge/{challenge_id}/accept", headers=self.headers)

    def make_move(self, game_id, move):
        requests.post(f"{self.base_url}/bot/game/{game_id}/move/{move}", headers=self.headers)

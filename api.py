import requests
import os
import sys

class LichessAPI:
    def __init__(self):
        self.token = os.getenv("STALE")
        if not self.token:
            print("DEBUG: Token 'STALE' not found in environment")
            sys.exit(1)
        
        print(f"DEBUG: Token found (Length: {len(self.token)})")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.base_url = "https://lichess.org/api"

    def stream_events(self):
        print("DEBUG: Connecting to event stream...")
        return requests.get(f"{self.base_url}/stream/event", headers=self.headers, stream=True)

    def stream_game(self, game_id):
        print(f"DEBUG: Streaming game {game_id}")
        return requests.get(f"{self.base_url}/bot/game/stream/{game_id}", headers=self.headers, stream=True)

    def accept_challenge(self, challenge_id):
        print(f"DEBUG: Accepting challenge {challenge_id}")
        requests.post(f"{self.base_url}/challenge/{challenge_id}/accept", headers=self.headers)

    def make_move(self, game_id, move):
        print(f"DEBUG: Submitting move {move} for game {game_id}")
        requests.post(f"{self.base_url}/bot/game/{game_id}/move/{move}", headers=self.headers)

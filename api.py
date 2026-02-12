import requests
import os
import sys

class LichessAPI:
    def __init__(self):
        self.token = os.getenv("STALE")
        if not self.token:
            print("Token 'STALE' not found in environment")
            sys.exit(1)
        
        print(f"Token found (Length: {len(self.token)})")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.base_url = "https://lichess.org/api"

    def stream_events(self):
        print("Connecting to event stream...")
        return requests.get(f"{self.base_url}/stream/event", headers=self.headers, stream=True)

    def stream_game(self, game_id):
        print(f"Streaming game {game_id}")
        return requests.get(f"{self.base_url}/bot/game/stream/{game_id}", headers=self.headers, stream=True)

    def accept_challenge(self, challenge_id):
        print(f"Accepting challenge {challenge_id}")
        requests.post(f"{self.base_url}/challenge/{challenge_id}/accept", headers=self.headers)

    def make_move(self, game_id, move):
        print(f"Submitting move {move} for game {game_id}")
        requests.post(f"{self.base_url}/bot/game/{game_id}/move/{move}", headers=self.headers)

    def upgrade_account(self):
        print("Requesting bot account upgrade")
        response = requests.post(f"{self.base_url}/bot/account/upgrade", headers=self.headers)
        if response.ok:
            print("Upgrade request succeeded. Account should now have BOT title if eligible.")
        else:
            print(f"Upgrade request failed: {response.status_code} {response.text}")
            response.raise_for_status()


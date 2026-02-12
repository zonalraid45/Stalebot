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
        self.session = requests.Session()

    def stream_events(self):
        print("Connecting to event stream...")
        return self.session.get(f"{self.base_url}/stream/event", headers=self.headers, stream=True)

    def stream_game(self, game_id):
        print(f"Streaming game {game_id}")
        return self.session.get(f"{self.base_url}/bot/game/stream/{game_id}", headers=self.headers, stream=True)

    def accept_challenge(self, challenge_id):
        print(f"Accepting challenge {challenge_id}")
        self.session.post(f"{self.base_url}/challenge/{challenge_id}/accept", headers=self.headers)

    def decline_challenge(self, challenge_id, reason="generic"):
        print(f"Declining challenge {challenge_id} ({reason})")
        self.session.post(
            f"{self.base_url}/challenge/{challenge_id}/decline",
            headers=self.headers,
            data={"reason": reason},
        )

    def make_move(self, game_id, move, move_number=None, side=None):
        if move_number is not None and side:
            print(f"Move {move_number:>3} ({side}): {move}     |     game {game_id}")
        self.session.post(f"{self.base_url}/bot/game/{game_id}/move/{move}", headers=self.headers)

    def respond_takeback(self, game_id, accept=True):
        choice = "yes" if accept else "no"
        action = "Accepting" if accept else "Declining"
        print(f"{action} takeback     |     game {game_id}")
        self.session.post(f"{self.base_url}/bot/game/{game_id}/takeback/{choice}", headers=self.headers)

    def upgrade_account(self):
        print("Requesting bot account upgrade")
        response = self.session.post(f"{self.base_url}/bot/account/upgrade", headers=self.headers)
        if response.ok:
            print("Upgrade request succeeded. Account should now have BOT title if eligible.")
        else:
            print(f"Upgrade request failed: {response.status_code} {response.text}")
            response.raise_for_status()

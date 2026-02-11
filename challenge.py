class ChallengeHandler:
    def __init__(self, api):
        self.api = api

    def handle(self, event):
        if event.get("type") == "challenge":
            self.api.accept_challenge(event["challenge"]["id"])

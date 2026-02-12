class ChallengeHandler:
    def __init__(self, api, challenge_settings=None, active_games_getter=None):
        self.api = api
        self.challenge_settings = challenge_settings or {}
        self.active_games_getter = active_games_getter

    def _concurrency_allowed(self):
        concurrency = int(self.challenge_settings.get("concurrency", 1))
        if self.active_games_getter is None:
            return True, None

        active_games = int(self.active_games_getter())
        if active_games >= concurrency:
            return False, "later"
        return True, None

    def _is_bot_challenge(self, challenge):
        challenger = challenge.get("challenger", {})
        return challenger.get("title") == "BOT"

    def _mode_allowed(self, challenge, is_bot):
        rated = challenge.get("rated", False)
        mode = "rated" if rated else "casual"
        mode_key = "bot_modes" if is_bot else "human_modes"
        allowed_modes = self.challenge_settings.get(mode_key, ["casual", "rated"])
        if mode not in allowed_modes:
            return False, "rated" if rated else "casual"
        return True, None

    def _variant_allowed(self, challenge):
        variant_key = challenge.get("variant", {}).get("key")
        allowed_variants = self.challenge_settings.get("variants", ["standard"])
        if variant_key and variant_key not in allowed_variants:
            reason = "standard" if variant_key == "standard" else "variant"
            return False, reason
        return True, None

    def _time_control_allowed(self, challenge, is_bot):
        speed = challenge.get("speed")
        tc = challenge.get("timeControl", {})
        increment = tc.get("increment")
        initial_seconds = tc.get("limit")

        list_key = "bot_time_controls" if is_bot else "human_time_controls"
        allowed_controls = self.challenge_settings.get(list_key, ["bullet", "blitz", "rapid", "classical"])

        control_match = False
        if speed and speed in allowed_controls:
            control_match = True
        if initial_seconds is not None and increment is not None:
            initial_minutes = int(initial_seconds // 60)
            if f"{initial_minutes}+{increment}" in allowed_controls:
                control_match = True
        if not control_match:
            return False, "timeControl"

        min_increment = self.challenge_settings.get("min_increment")
        max_increment = self.challenge_settings.get("max_increment")
        if increment is not None and min_increment is not None and increment < min_increment:
            return False, "tooFast"
        if increment is not None and max_increment is not None and increment > max_increment:
            return False, "tooSlow"

        min_initial = self.challenge_settings.get("min_initial")
        max_initial = self.challenge_settings.get("max_initial")
        if initial_seconds is not None and min_initial is not None and initial_seconds < min_initial:
            return False, "tooFast"
        if initial_seconds is not None and max_initial is not None and initial_seconds > max_initial:
            return False, "tooSlow"

        if is_bot and self.challenge_settings.get("bullet_with_increment_only", False):
            if speed == "bullet" and increment == 0:
                return False, "timeControl"

        return True, None

    def should_accept(self, challenge):
        concurrency_ok, concurrency_reason = self._concurrency_allowed()
        if not concurrency_ok:
            return False, concurrency_reason

        is_bot = self._is_bot_challenge(challenge)

        mode_ok, mode_reason = self._mode_allowed(challenge, is_bot)
        if not mode_ok:
            return False, mode_reason

        variant_ok, variant_reason = self._variant_allowed(challenge)
        if not variant_ok:
            return False, variant_reason

        time_ok, time_reason = self._time_control_allowed(challenge, is_bot)
        if not time_ok:
            return False, time_reason

        return True, None

    def handle(self, event):
        if event.get("type") == "challenge":
            challenge = event["challenge"]
            challenge_id = challenge["id"]
            should_accept, decline_reason = self.should_accept(challenge)
            if should_accept:
                self.api.accept_challenge(challenge_id)
            else:
                self.api.decline_challenge(challenge_id, reason=decline_reason or "generic")

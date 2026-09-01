class AutoRestart:
    def __init__(self, bot):
        self.bot = bot
        self.end_session = False
        self.game_finished = False
        self.game_settled = False
        self.version_mismatch = False

    def reset_session(self):
        self.end_session = False
        self.game_finished = False
        self.game_settled = False
        self.version_mismatch = False
        self.bot.death.run_ended = False

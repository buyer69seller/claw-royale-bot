class DeathDetector:
    def __init__(self, bot):
        self.bot = bot
        self.run_ended = False

    def end_run(self, reason):
        self.run_ended = True
        self.bot.state.alive = False
        self.bot.lifecycle.end_session = True
        self.bot.log.warning("RUN ENDED: %s", reason)

class MovementAnalyzer:
    def __init__(self, bot):
        self.bot = bot

    def destinations(self):
        return self.bot.state.region.get("connections") or []

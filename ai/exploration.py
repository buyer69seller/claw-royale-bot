class ExplorationAnalyzer:
    def __init__(self, bot):
        self.bot = bot

    def safe(self):
        me = self.bot.state.me
        region = self.bot.state.region
        return (
            not region.get("isDeathZone")
            and float(me.get("alertGauge", 0) or 0) < 8
            and region.get("ruinGauge") is not None
        )

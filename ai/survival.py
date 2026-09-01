class SurvivalAnalyzer:
    def __init__(self, bot):
        self.bot = bot

    def urgency(self):
        me = self.bot.state.me
        hp = float(me.get("hp", 0) or 0)
        max_hp = float(me.get("maxHp", 100) or 100)
        alert = float(me.get("alertGauge", 0) or 0)
        return (1 - hp/max_hp) * 100 + alert * 2

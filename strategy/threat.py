class ThreatAnalyzer:
    def __init__(self, bot):
        self.bot = bot

    def score(self):
        me = self.bot.state.me
        enemies = self.bot.state.view.get("visibleAgents") or []
        monsters = self.bot.state.view.get("visibleMonsters") or []
        hp = float(me.get("hp", 0) or 0)
        return len(enemies) * 15 + len(monsters) * 5 + max(0, 100-hp)

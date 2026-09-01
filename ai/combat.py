class CombatAnalyzer:
    def __init__(self, bot):
        self.bot = bot

    def targets(self):
        view = self.bot.state.view
        return [
            x for x in (view.get("visibleAgents") or []) + (view.get("visibleMonsters") or [])
            if x.get("isAlive") is not False and not x.get("isGuardian")
        ]

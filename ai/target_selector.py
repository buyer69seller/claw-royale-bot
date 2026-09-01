class TargetSelector:
    def __init__(self, bot):
        self.bot = bot

    def best(self):
        targets = [
            x for x in (self.bot.state.view.get("visibleAgents") or []) +
                      (self.bot.state.view.get("visibleMonsters") or [])
            if x.get("isAlive") is not False and not x.get("isGuardian")
        ]
        if not targets:
            return None
        return sorted(targets, key=lambda x: float(x.get("hp", 999) or 999))[0]

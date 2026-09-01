class RoutePlanner:
    def __init__(self, bot):
        self.bot = bot

    def next_safe(self):
        pending = {x.get("id") for x in self.bot.state.view.get("pendingDeathzones", [])
                   if isinstance(x, dict)}
        safe = [x for x in self.bot.state.region.get("connections", []) if x not in pending]
        return safe[0] if safe else None

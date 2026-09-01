class DeathZonePlanner:
    def __init__(self, bot):
        self.bot = bot

    def danger(self, region):
        return bool(region.get("isDeathZone"))

    def safe_destinations(self):
        pending = {x.get("id") for x in self.bot.state.view.get("pendingDeathzones", [])
                   if isinstance(x, dict)}
        return [x for x in self.bot.state.region.get("connections", []) if x not in pending]

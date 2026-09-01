class LootAnalyzer:
    def __init__(self, bot):
        self.bot = bot

    def visible_items(self):
        return self.bot.state.region.get("items") or []
